import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Suppress warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torchvision")
warnings.filterwarnings("ignore", category=UserWarning, module="easyocr")

# Import sklearn warning type
try:
    from sklearn.exceptions import InconsistentVersionWarning
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning, module="sklearn")
except ImportError:
    pass

import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from passlib.hash import pbkdf2_sha256
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import re
from models import db, User, Receipt, ReceiptItem, Category
import json
import io
from redis import Redis
from rq import Queue
from tasks import process_receipt

# Import offline parsing components
try:
    from enhanced_receipt_parser import EnhancedReceiptParser
    OFFLINE_PARSING_AVAILABLE = True
except ImportError:
    OFFLINE_PARSING_AVAILABLE = False
    print("Warning: Offline parsing components not available")

app = Flask(__name__)
CORS(app)

# === Configure DB ===
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'postgresql://postgres:colapp@host.docker.internal:5432/grocery_app_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Change in production!

# === Configure File Upload ===
UPLOAD_FOLDER = os.path.normpath('uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.init_app(app)
jwt = JWTManager(app)

# Redis connection (use Docker Compose service name)
redis_host = os.environ.get('REDIS_HOST', 'redis')
redis_port = int(os.environ.get('REDIS_PORT', 6379))
redis_conn = Redis(host=redis_host, port=redis_port)
q = Queue(connection=redis_conn)

# Initialize Offline Receipt Parser
if OFFLINE_PARSING_AVAILABLE:
    try:
        offline_parser = EnhancedReceiptParser()
        print("✅ Offline receipt parser initialized")
    except Exception as e:
        print(f"⚠️  Failed to initialize offline parser: {e}")
        offline_parser = None
else:
    offline_parser = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_receipt_text(text):
    """Legacy heuristic parsing function - kept for fallback"""
    lines = text.split('\n')
    store_name = 'Unknown Store'
    total_amount = 0.0
    items = []

    # Try to match known store names
    known_stores = ['WALMART', 'TARGET', 'KROGER', 'SAFEWAY', 'COSTCO', 'ALDI', 'CVS', 'WALGREENS']
    for line in lines[:8]:
        for store in known_stores:
            if store in line.upper():
                store_name = store.title()
                break
        if store_name != 'Unknown Store':
            break
    # Fallback: first non-empty line
    if store_name == 'Unknown Store':
        for line in lines[:5]:
            if line.strip():
                store_name = line.strip()
                break

    # Try to find total amount
    total_patterns = [
        re.compile(r'total[\s:]*\$?(\d+\.\d{2})', re.IGNORECASE),
        re.compile(r'amount[\s:]*\$?(\d+\.\d{2})', re.IGNORECASE),
        re.compile(r'\$?(\d+\.\d{2})$')
    ]
    for line in lines:
        for pattern in total_patterns:
            match = pattern.search(line)
            if match:
                try:
                    total_amount = float(match.group(1))
                    break
                except:
                    continue
        if total_amount:
            break

    # Try to extract items (product name + price)
    item_pattern = re.compile(r'(.+?)\s+\$?(\d+\.\d{2})')
    for line in lines:
        match = item_pattern.match(line)
        if match:
            product = match.group(1).strip()
            price = float(match.group(2))
            if product.lower() not in ['total', 'tax', 'subtotal', 'amount']:
                items.append({'product_name': product, 'price': price, 'category': 'Other'})

    return {
        'store_name': store_name,
        'total_amount': total_amount,
        'items': items
    }

def parse_receipt_with_method(image_path, method='auto'):
    """
    Parse receipt using the specified method.
    method: 'llm', 'ocr_only', 'auto', or 'heuristic'
    """
    if offline_parser is None:
        return {"success": False, "error": "Offline parser not available."}
    if method == 'llm' or method == 'auto':
        return offline_parser.parse_receipt(image_path, method='llm')
    elif method == 'ocr_only':
        return offline_parser.parse_receipt(image_path, method='ocr_only')
    else:
        # Default to OCR-only as fallback
        return offline_parser.parse_receipt(image_path, method='ocr_only')

# === Authentication Routes ===
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "User already exists."}), 400
    user = User(
        email=data['email'],
        password_hash=pbkdf2_sha256.hash(data['password']),
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        age=data.get('age'),
        sex=data.get('sex', ''),
        city=data.get('city', ''),
        county=data.get('county', ''),
        state=data.get('state', ''),
        zip_code=data.get('zip_code', '')
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully."})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and pbkdf2_sha256.verify(data['password'], user.password_hash):
        access_token = create_access_token(identity=user.email)
        return jsonify(access_token=access_token)
    return jsonify({"error": "Invalid email or password"}), 401

# === Receipt Routes ===
@app.route('/upload-receipt', methods=['POST'])
@jwt_required()
def upload_receipt():
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No image file selected"}), 400
        if file and allowed_file(file.filename):
            filename = f"{uuid.uuid4()}_{secure_filename(file.filename or 'receipt.jpg')}"
            filepath = os.path.normpath(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file.save(filepath)
            # Convert to POSIX path for Docker
            posix_filepath = filepath.replace("\\", "/")
            # Create receipt record with minimal info
            receipt = Receipt(
                user_id=user.id,
                store_name="Processing...",
                receipt_date=datetime.now().date(),
                total_amount=0.0,
                image_path=filename,
                ocr_processed=False,
                reviewed=False
            )
            db.session.add(receipt)
            db.session.commit()
            # Enqueue background job
            parsing_method = request.form.get('parsing_method', 'auto')
            q.enqueue(process_receipt, receipt.id, posix_filepath, parsing_method)
            return jsonify({
                "success": True,
                "receipt_id": receipt.id
            })
        return jsonify({"error": "Invalid file type"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to upload receipt: {str(e)}"}), 500

@app.route('/receipts', methods=['GET'])
@jwt_required()
def get_receipts():
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        receipts = Receipt.query.filter_by(user_id=user.id).order_by(Receipt.created_at.desc()).all()
        
        receipt_list = []
        for receipt in receipts:
            receipt_data = {
                "id": receipt.id,
                "store_name": receipt.store_name,
                "receipt_date": receipt.receipt_date.strftime('%Y-%m-%d'),
                "total_amount": float(receipt.total_amount),
                "image_path": receipt.image_path,
                "ocr_processed": receipt.ocr_processed,
                "created_at": receipt.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "items": [
                    {
                        "id": item.id,
                        "product_name": item.product_name,
                        "price": float(item.price),
                        "category": item.category
                    } for item in receipt.items
                ]
            }
            receipt_list.append(receipt_data)
        
        return jsonify({"receipts": receipt_list})
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch receipts: {str(e)}"}), 500

@app.route('/receipt/<int:receipt_id>', methods=['GET'])
@jwt_required()
def get_receipt(receipt_id):
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        receipt = Receipt.query.filter_by(id=receipt_id, user_id=user.id).first()
        if not receipt:
            return jsonify({"error": "Receipt not found"}), 404
        
        receipt_data = {
            "id": receipt.id,
            "store_name": receipt.store_name,
            "receipt_date": receipt.receipt_date.strftime('%Y-%m-%d'),
            "total_amount": float(receipt.total_amount),
            "image_path": receipt.image_path,
            "ocr_processed": receipt.ocr_processed,
            "created_at": receipt.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "items": [
                {
                    "id": item.id,
                    "product_name": item.product_name,
                    "price": float(item.price),
                    "category": item.category
                } for item in receipt.items
            ]
        }
        
        return jsonify(receipt_data)
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch receipt: {str(e)}"}), 500

# --- Unreviewed Receipts Endpoint ---
@app.route('/receipts/unreviewed', methods=['GET'])
@jwt_required()
def get_unreviewed_receipts():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    receipts = Receipt.query.filter_by(user_id=user.id, reviewed=False).order_by(Receipt.created_at.desc()).all()
    receipt_list = []
    for receipt in receipts:
        receipt_data = {
            "id": receipt.id,
            "store_name": receipt.store_name,
            "receipt_date": receipt.receipt_date.strftime('%Y-%m-%d'),
            "total_amount": float(receipt.total_amount),
            "image_path": receipt.image_path,
            "items": [
                {
                    "product_name": item.product_name,
                    "price": float(item.price),
                    "category": item.category,
                    "quantity": item.quantity,
                } for item in receipt.items
            ],
            "raw_text": "",  # Fill if you store OCR text
        }
        receipt_list.append(receipt_data)
    return jsonify({"receipts": receipt_list})

# --- Manual Expense Entry Endpoint ---
@app.route('/expense/manual', methods=['POST'])
@jwt_required()
def add_manual_expense():
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json()
    try:
        receipt = Receipt(
            user_id=user.id,
            store_name=data.get('store_name', 'Manual Entry'),
            receipt_date=datetime.now().date(),
            total_amount=data.get('total_amount', 0.0),
            image_path='',  # No image for manual entry
            ocr_processed=True,
            reviewed=True,  # Manual expenses are reviewed by default
        )
        db.session.add(receipt)
        db.session.flush()  # Get receipt.id
        items = data.get('items', [])
        for item in items:
            receipt_item = ReceiptItem(
                receipt_id=receipt.id,
                product_name=item.get('product_name', ''),
                price=item.get('price', 0.0),
                category=item.get('category', 'Other'),
                quantity=item.get('quantity', 1),
            )
            db.session.add(receipt_item)
        db.session.commit()
        return jsonify({"success": True, "expense_id": receipt.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})

# --- Update Receipt: Mark as Reviewed ---
@app.route('/receipt/<int:receipt_id>', methods=['PUT'])
@jwt_required()
def update_receipt(receipt_id):
    current_user_email = get_jwt_identity()
    user = User.query.filter_by(email=current_user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json()
    try:
        receipt = Receipt.query.filter_by(id=receipt_id, user_id=user.id).first()
        if not receipt:
            return jsonify({"error": "Receipt not found"}), 404
        # Update receipt details
        receipt.store_name = data.get('store_name', receipt.store_name)
        receipt.total_amount = data.get('total_amount', receipt.total_amount)
        receipt.updated_at = datetime.utcnow()
        receipt.reviewed = True  # Mark as reviewed
        # Remove old items
        ReceiptItem.query.filter_by(receipt_id=receipt.id).delete()
        # Add new items
        items = data.get('items', [])
        for item in items:
            receipt_item = ReceiptItem(
                receipt_id=receipt.id,
                product_name=item.get('product_name', ''),
                price=item.get('price', 0.0),
                category=item.get('category', 'Other'),
                quantity=item.get('quantity', 1),
            )
            db.session.add(receipt_item)
        db.session.commit()
        return jsonify({"success": True, "message": "Receipt updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update receipt: {str(e)}"}), 500

@app.route('/receipt/<int:receipt_id>', methods=['DELETE'])
@jwt_required()
def delete_receipt(receipt_id):
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        receipt = Receipt.query.filter_by(id=receipt_id, user_id=user.id).first()
        if not receipt:
            return jsonify({"error": "Receipt not found"}), 404
        
        # Delete image file
        if receipt.image_path:
            try:
                os.remove(os.path.normpath(os.path.join(app.config['UPLOAD_FOLDER'], receipt.image_path)))
            except:
                pass  # File might not exist
        
        # Delete receipt (items will be deleted due to cascade)
        db.session.delete(receipt)
        db.session.commit()
        
        return jsonify({"success": True, "message": "Receipt deleted successfully"})
        
    except Exception as e:
        return jsonify({"error": f"Failed to delete receipt: {str(e)}"}), 500

@app.route('/uploads/<filename>')
@jwt_required()
def uploaded_file(filename):
    return send_from_directory(os.path.normpath(app.config['UPLOAD_FOLDER']), filename)

# === Dashboard Analytics Routes ===
@app.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get all receipts for the user
        receipts = Receipt.query.filter_by(user_id=user.id).all()
        
        # Calculate statistics
        total_receipts = len(receipts)
        total_spent = sum(float(receipt.total_amount) for receipt in receipts)
        
        # Category breakdown
        category_totals = {}
        for receipt in receipts:
            for item in receipt.items:
                category = item.category
                if category not in category_totals:
                    category_totals[category] = 0
                category_totals[category] += float(item.price)
        
        # Monthly spending
        monthly_spending = {}
        for receipt in receipts:
            month_key = receipt.receipt_date.strftime('%Y-%m')
            if month_key not in monthly_spending:
                monthly_spending[month_key] = 0
            monthly_spending[month_key] += float(receipt.total_amount)
        
        # Store breakdown
        store_totals = {}
        for receipt in receipts:
            store = receipt.store_name
            if store not in store_totals:
                store_totals[store] = 0
            store_totals[store] += float(receipt.total_amount)
        
        return jsonify({
            "total_receipts": total_receipts,
            "total_spent": total_spent,
            "category_breakdown": category_totals,
            "monthly_spending": monthly_spending,
            "store_breakdown": store_totals
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch dashboard stats: {str(e)}"}), 500

@app.route('/api/ocr-receipt', methods=['POST'])
@jwt_required()
def ocr_receipt():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        print('Image received:', file.filename, 'size:', len(file.read()) if file else 0)
        file.seek(0)  # Reset file pointer after reading
        
        # Save the uploaded file temporarily
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename or 'receipt.jpg')}"
        filepath = os.path.normpath(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file.save(filepath)
        
        # Verify file was saved correctly
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f'File saved successfully: {filepath}, size: {file_size} bytes')
        else:
            print(f'Failed to save file: {filepath}')
            return jsonify({'error': 'Failed to save uploaded file'}), 500
        
        try:
            # Always use the local LLM (offline_parser) for parsing
            if OFFLINE_PARSING_AVAILABLE and offline_parser is not None:
                print(f'Using offline parser with method: llm')
                result = offline_parser.parse_receipt(filepath, method='llm')
                print(f'LLM result: {result.get("success", False)}')
                return jsonify(result)
            else:
                print(f'Offline parser not available, using legacy method')
                # If offline_parser is not available, fallback to legacy method
                parsed_data = parse_receipt_with_method(filepath, 'auto')
                return jsonify(parsed_data)
        finally:
            # Clean up temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f'Cleaned up temporary file: {filepath}')
    except Exception as e:
        print('OCR error:', e)
        return jsonify({'error': f'OCR failed: {str(e)}'}), 500

@app.route('/api/parse-receipt-offline', methods=['POST'])
@jwt_required()
def parse_receipt_offline():
    """Parse receipt using offline methods (OCR + LLM)"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        method = request.form.get('method', 'auto')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Check if offline parsing is available
        if not OFFLINE_PARSING_AVAILABLE or offline_parser is None:
            return jsonify({
                'error': 'Offline parsing not available. Please install required dependencies.'
            }), 503
        
        # Save uploaded file
        filename = secure_filename(file.filename or 'receipt.jpg')
        filepath = os.path.normpath(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file.save(filepath)
        
        try:
            # Parse receipt using offline parser
            result = offline_parser.parse_receipt(filepath, method=method)
            
            if result['success']:
                # Save to database
                receipt_data = result['data']
                receipt = Receipt(
                    user_id=get_jwt_identity(),
                    store_name=receipt_data['store_name'],
                    receipt_date=receipt_data.get('date'),
                    total_amount=receipt_data['total'],
                    image_path=filename,
                    ocr_processed=True
                )
                db.session.add(receipt)
                db.session.commit()
                
                # Add items
                for item_data in receipt_data.get('items', []):
                    item = ReceiptItem(
                        receipt_id=receipt.id,
                        product_name=item_data['name'],
                        price=item_data['total_price'],
                        category=item_data.get('category', 'Other'),
                        quantity=item_data.get('quantity', 1.0)
                    )
                    db.session.add(item)
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'receipt_id': receipt.id,
                    'parsed_data': receipt_data,
                    'method': result['method'],
                    'confidence': result.get('confidence', 0.0),
                    'file_info': {
                        'filename': filename,
                        'size': result.get('file_size', 0),
                        'type': result.get('file_type', '')
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Parsing failed'),
                    'method': result['method']
                }), 400
                
        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/offline-parser-status', methods=['GET'])
@jwt_required()
def get_offline_parser_status():
    """Get status of offline parsing components"""
    try:
        if not OFFLINE_PARSING_AVAILABLE:
            return jsonify({
                'available': False,
                'error': 'Offline parsing components not installed'
            })
        
        if offline_parser is None:
            return jsonify({
                'available': False,
                'error': 'Offline parser failed to initialize'
            })
        
        # Get available methods and service status
        methods = offline_parser.get_available_methods()
        services = offline_parser.test_services()
        
        return jsonify({
            'available': True,
            'methods': methods,
            'services': services,
            'recommended_method': 'llm' if methods.get('llm', {}).get('available', False) else 'ocr_only'
        })
        
    except Exception as e:
        return jsonify({
            'available': False,
            'error': str(e)
        })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
