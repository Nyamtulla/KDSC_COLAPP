import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, render_template_string
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
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
CORS(app)

# === Configure DB ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:colapp@localhost:5432/grocery_app_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Change in production!

# === Configure File Upload ===
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.init_app(app)
jwt = JWTManager(app)

# === Password Reset Config ===
SECRET_KEY = app.config['JWT_SECRET_KEY']
RESET_TOKEN_EXPIRY = 3600  # 1 hour

# In-memory set to track used password reset tokens (single-process only)
used_reset_tokens = set()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_receipt_data(image_path):
    """Mock OCR function for testing - returns sample data"""
    try:
        # For testing, return mock data instead of actual OCR
        return {
            'store_name': 'Walmart',
            'total_amount': 45.67,
            'items': [
                {
                    'product_name': 'Milk',
                    'price': 3.99,
                    'category': 'Dairy'
                },
                {
                    'product_name': 'Bread',
                    'price': 2.49,
                    'category': 'Bakery'
                },
                {
                    'product_name': 'Bananas',
                    'price': 1.99,
                    'category': 'Produce'
                },
                {
                    'product_name': 'Chicken Breast',
                    'price': 12.99,
                    'category': 'Meat'
                },
                {
                    'product_name': 'Cereal',
                    'price': 4.99,
                    'category': 'Other'
                },
                {
                    'product_name': 'Orange Juice',
                    'price': 3.49,
                    'category': 'Beverages'
                },
                {
                    'product_name': 'Paper Towels',
                    'price': 5.99,
                    'category': 'Household'
                },
                {
                    'product_name': 'Apples',
                    'price': 4.99,
                    'category': 'Produce'
                },
                {
                    'product_name': 'Yogurt',
                    'price': 2.99,
                    'category': 'Dairy'
                },
                {
                    'product_name': 'Pasta',
                    'price': 1.79,
                    'category': 'Other'
                }
            ]
        }
        
    except Exception as e:
        print(f"OCR Error: {e}")
        return {
            'store_name': 'Unknown Store',
            'total_amount': 0.0,
            'items': []
        }

def parse_receipt_text(text):
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

def generate_reset_token(email):
    s = URLSafeTimedSerializer(SECRET_KEY)
    return s.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, max_age=RESET_TOKEN_EXPIRY):
    s = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=max_age)
    except Exception:
        return None
    return email

def send_email(to_email, subject, body):
    # For demo: just print the email
    print(f'---\nTo: {to_email}\nSubject: {subject}\n\n{body}\n---')
    # For production, use smtplib or flask-mail to send real emails

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

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': True})  # Don't reveal if user exists
    token = generate_reset_token(user.email)
    reset_link = f'http://localhost:5000/reset-password?token={token}'
    send_email(user.email, 'Password Reset', f'Click here to reset your password: {reset_link}')
    return jsonify({'success': True})

@app.route('/reset-password', methods=['GET'])
def reset_password_page():
    token = request.args.get('token', '')
    if token in used_reset_tokens:
        # Show a simple HTML page saying password already reset
        html = '''
        <html>
        <head><title>Password Already Reset</title></head>
        <body style="background:#EAF3F9;display:flex;align-items:center;justify-content:center;height:100vh;">
            <div style="background:#fff;padding:32px 24px;border-radius:16px;box-shadow:0 2px 16px rgba(0,0,0,0.08);text-align:center;">
                <h2 style="color:#0051BA;">Password Already Reset</h2>
                <p style="color:#EC944A;">This password reset link has already been used.</p>
                <a href="/" style="color:#0051BA;text-decoration:underline;">Return to app</a>
            </div>
        </body>
        </html>
        '''
        return render_template_string(html)
    # Simple HTML page with inline CSS matching app style
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reset Password</title>
        <style>
            body {{
                background: #EAF3F9;
                font-family: 'Segoe UI', Arial, sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            .container {{
                background: #fff;
                border-radius: 16px;
                box-shadow: 0 2px 16px rgba(0,0,0,0.08);
                padding: 32px 24px;
                max-width: 340px;
                width: 100%;
                text-align: center;
            }}
            h2 {{ color: #0051BA; margin-bottom: 24px; }}
            input[type=password] {{
                width: 100%;
                padding: 12px;
                margin-bottom: 18px;
                border: 1px solid #bcd0e5;
                border-radius: 8px;
                font-size: 16px;
                box-sizing: border-box;
            }}
            button {{
                background: #0051BA;
                color: #fff;
                border: none;
                border-radius: 8px;
                padding: 12px 0;
                width: 100%;
                font-size: 18px;
                font-weight: 600;
                cursor: pointer;
                margin-bottom: 12px;
            }}
            button:disabled {{
                background: #ccc;
                cursor: not-allowed;
            }}
            .msg {{ margin: 12px 0; color: #EC944A; font-weight: 500; }}
            .success {{ color: #4CAF50; }}
            .error {{ color: #E91E63; }}
            .validation {{ font-size: 14px; margin: 8px 0; }}
            .validation.error {{ color: #E91E63; }}
            .validation.success {{ color: #4CAF50; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Reset Password</h2>
            <div id="msg" class="msg"></div>
            <input id="password" type="password" placeholder="New Password (min 6 characters)" oninput="validatePasswords()" />
            <div id="passwordValidation" class="validation"></div>
            <input id="confirmPassword" type="password" placeholder="Re-enter Password" oninput="validatePasswords()" />
            <div id="confirmValidation" class="validation"></div>
            <button id="resetBtn" onclick="resetPassword()" disabled>Set New Password</button>
        </div>
        <script>
            function validatePasswords() {{
                var password = document.getElementById('password').value;
                var confirmPassword = document.getElementById('confirmPassword').value;
                var passwordValidation = document.getElementById('passwordValidation');
                var confirmValidation = document.getElementById('confirmValidation');
                var resetBtn = document.getElementById('resetBtn');
                
                // Reset validation messages
                passwordValidation.textContent = '';
                confirmValidation.textContent = '';
                passwordValidation.className = 'validation';
                confirmValidation.className = 'validation';
                
                var isValid = true;
                
                // Check password length
                if (password.length < 6) {{
                    passwordValidation.textContent = 'Password must be at least 6 characters long';
                    passwordValidation.className = 'validation error';
                    isValid = false;
                }} else {{
                    passwordValidation.textContent = '✓ Password length is good';
                    passwordValidation.className = 'validation success';
                }}
                
                // Check if passwords match
                if (confirmPassword.length > 0) {{
                    if (password !== confirmPassword) {{
                        confirmValidation.textContent = 'Passwords do not match';
                        confirmValidation.className = 'validation error';
                        isValid = false;
                    }} else {{
                        confirmValidation.textContent = '✓ Passwords match';
                        confirmValidation.className = 'validation success';
                    }}
                }}
                
                // Enable/disable button
                resetBtn.disabled = !isValid || password.length === 0 || confirmPassword.length === 0;
            }}
            
            function resetPassword() {{
                var password = document.getElementById('password').value;
                var confirmPassword = document.getElementById('confirmPassword').value;
                var msg = document.getElementById('msg');
                var resetBtn = document.getElementById('resetBtn');
                
                // Final validation
                if (password.length < 6) {{
                    msg.textContent = 'Password must be at least 6 characters long';
                    msg.className = 'msg error';
                    return;
                }}
                
                if (password !== confirmPassword) {{
                    msg.textContent = 'Passwords do not match';
                    msg.className = 'msg error';
                    return;
                }}
                
                msg.textContent = '';
                resetBtn.disabled = true;
                resetBtn.textContent = 'Resetting...';
                
                fetch('/reset-password', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ token: '{token}', new_password: password }})
                }})
                .then(r => r.json())
                .then(data => {{
                    if (data.success) {{
                        msg.textContent = 'Password reset successful! You can now log in.';
                        msg.className = 'msg success';
                        resetBtn.textContent = 'Password Reset!';
                    }} else {{
                        msg.textContent = data.error || 'Failed to reset password.';
                        msg.className = 'msg error';
                        resetBtn.disabled = false;
                        resetBtn.textContent = 'Set New Password';
                    }}
                }})
                .catch(() => {{
                    msg.textContent = 'Network error.';
                    msg.className = 'msg error';
                    resetBtn.disabled = false;
                    resetBtn.textContent = 'Set New Password';
                }});
            }}
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')

    if token in used_reset_tokens:
        return jsonify({'success': False, 'error': 'This reset link has already been used.'})

    email = verify_reset_token(token)
    if not email:
        return jsonify({'success': False, 'error': 'Invalid or expired token'})
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'})
    user.password_hash = pbkdf2_sha256.hash(new_password)
    db.session.commit()

    used_reset_tokens.add(token)  # Mark token as used

    return jsonify({'success': True})

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
            return jsonify({"error": "No file selected"}), 400
        
        # Get receipt data from form fields
        store_name = request.form.get('store_name', 'Unknown Store')
        total_amount = float(request.form.get('total_amount', 0))
        items_json = request.form.get('items', '[]')
        
        try:
            items_data = json.loads(items_json)
        except json.JSONDecodeError:
            items_data = []
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = secure_filename(file.filename or 'receipt.jpg')
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save the file
            file.save(file_path)
            
            # Create receipt record
            receipt = Receipt(
                user_id=user.id,
                store_name=store_name,
                receipt_date=datetime.now().date(),
                total_amount=total_amount,
                image_path=unique_filename,
                ocr_processed=True
            )
            db.session.add(receipt)
            db.session.flush()  # Get the receipt ID
            
            # Add items
            for item_data in items_data:
                item = ReceiptItem(
                    receipt_id=receipt.id,
                    product_name=item_data.get('product_name', ''),
                    price=item_data.get('price', 0),
                    category=item_data.get('category', 'Other')
                )
                db.session.add(item)
            
            db.session.commit()
            
            return jsonify({
                "success": True,
                "receipt_id": receipt.id,
                "message": "Receipt uploaded successfully"
            })
        
        return jsonify({"error": "Invalid file type"}), 400
        
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

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

@app.route('/receipt/<int:receipt_id>', methods=['PUT'])
@jwt_required()
def update_receipt(receipt_id):
    try:
        current_user_email = get_jwt_identity()
        user = User.query.filter_by(email=current_user_email).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        receipt = Receipt.query.filter_by(id=receipt_id, user_id=user.id).first()
        if not receipt:
            return jsonify({"error": "Receipt not found"}), 404
        
        data = request.get_json()
        
        # Update receipt details
        receipt.store_name = data.get('store_name', receipt.store_name)
        receipt.total_amount = data.get('total_amount', receipt.total_amount)
        receipt.updated_at = datetime.utcnow()
        
        # Update items
        if 'items' in data:
            # Remove existing items
            ReceiptItem.query.filter_by(receipt_id=receipt.id).delete()
            
            # Add new items
            for item_data in data['items']:
                item = ReceiptItem(
                    receipt_id=receipt.id,
                    product_name=item_data['product_name'],
                    price=item_data['price'],
                    category=item_data.get('category', 'Other')
                )
                db.session.add(item)
        
        db.session.commit()
        
        return jsonify({"success": True, "message": "Receipt updated successfully"})
        
    except Exception as e:
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
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], receipt.image_path))
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
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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
        print('Image received:', file.filename, 'size:', file.content_length)
        print('PYTHON PATH:', os.environ.get('PATH'))
        import pytesseract
        # Set tesseract_cmd explicitly for Windows
        if os.name == 'nt':
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            print('Set pytesseract.tesseract_cmd to:', pytesseract.pytesseract.tesseract_cmd)
        image = Image.open(file.stream)
        image.save('debug_uploaded_image.jpg')  # Save for debugging
        print('Image saved as debug_uploaded_image.jpg')
        text = pytesseract.image_to_string(image)
        print('OCR result:', repr(text))
        parsed = parse_receipt_text(text)
        parsed['raw_text'] = text
        parsed['success'] = True
        return jsonify(parsed)
    except Exception as e:
        print('OCR error:', e)
        return jsonify({'error': f'OCR failed: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
