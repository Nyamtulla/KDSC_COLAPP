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
from itsdangerous import URLSafeTimedSerializer
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import offline parsing components
try:
    from enhanced_receipt_parser import EnhancedReceiptParser
    OFFLINE_PARSING_AVAILABLE = True
except ImportError:
    OFFLINE_PARSING_AVAILABLE = False
    print("Warning: Offline parsing components not available")

# Import BLS categories
try:
    from bls_categories import get_category_hierarchy, get_all_categories
    BLS_CATEGORIES_AVAILABLE = True
except ImportError:
    BLS_CATEGORIES_AVAILABLE = False
    print("Warning: BLS categories not available")

app = Flask(__name__)

# Apply security headers to all responses
@app.after_request
def apply_security_headers(response):
    """Apply security headers to all responses"""
    return add_security_headers(response)
    
# Configure CORS to allow requests from GitHub Pages and local development
CORS(app, origins=[
    # Production HTTPS origins
    "https://nyamshaik.me",            # Your custom domain (HTTPS) - PRIMARY
    "https://www.nyamshaik.me",        # Your custom domain with www (HTTPS)
    "https://api.nyamshaik.me",        # Your API domain (HTTPS)
    "https://nyamtull.github.io",      # Your GitHub Pages URL (HTTPS)
    "https://nyamtull.github.io/KDSC_COLAPP", # Your specific project URL (HTTPS)
    # Development HTTP origins (local only)
    "http://localhost:3000",           # For local development
    "http://localhost:3001",           # For local development (Flutter web)
    "http://localhost:8080",           # For local development
    "http://127.0.0.1:3000",          # For local development
    "http://127.0.0.1:3001",          # For local development (Flutter web)
    "http://127.0.0.1:8080"           # For local development
], supports_credentials=True, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])

# Handle preflight requests
@app.route('/login', methods=['OPTIONS'])
def handle_login_preflight():
    response = jsonify({'status': 'ok'})
    response = add_cors_headers(response)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# General OPTIONS handler for all routes
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = jsonify({'status': 'ok'})
    response = add_cors_headers(response)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# === Configure DB ===
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'postgresql://postgres:colapp@host.docker.internal:5432/grocery_app_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Change in production!

# CORS helper function
def add_cors_headers(response):
    """Add CORS headers to response based on request origin"""
    origin = request.headers.get('Origin')
    
    # Production HTTPS origins - prioritize these
    allowed_origins = [
        # Production HTTPS origins
        "https://nyamshaik.me",            # PRIMARY - Your custom domain (HTTPS)
        "https://www.nyamshaik.me",        # Your custom domain with www (HTTPS)
        "https://api.nyamshaik.me",        # Your API domain (HTTPS)
        "https://nyamtull.github.io",      # Your GitHub Pages URL (HTTPS)
        "https://nyamtull.github.io/KDSC_COLAPP", # Your specific project URL (HTTPS)
        # Development HTTP origins (local only)
        "http://localhost:3000",           # For local development
        "http://localhost:3001",           # For local development (Flutter web)
        "http://localhost:8080",           # For local development
        "http://127.0.0.1:3000",          # For local development
        "http://127.0.0.1:3001",          # For local development (Flutter web)
        "http://127.0.0.1:8080"           # For local development
    ]
    
    # Always prefer HTTPS over HTTP for the same domain
    if origin and origin.startswith('http://'):
        https_version = origin.replace('http://', 'https://')
        if https_version in allowed_origins:
            response.headers.add('Access-Control-Allow-Origin', https_version)
        elif origin in allowed_origins:
            response.headers.add('Access-Control-Allow-Origin', origin)
        else:
            response.headers.add('Access-Control-Allow-Origin', 'https://nyamshaik.me')
    elif origin in allowed_origins:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Origin', 'https://nyamshaik.me')
    
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Security headers helper function
def add_security_headers(response):
    """Add security headers to all responses"""
    # HSTS (HTTP Strict Transport Security) - 2 years max-age
    response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
    
    # Content Security Policy (CSP) - basic protection
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;"
    
    # X-Content-Type-Options - prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # X-Frame-Options - prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # X-XSS-Protection - enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Referrer Policy - control referrer information
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return response

# === Configure File Upload ===
UPLOAD_FOLDER = os.path.normpath('uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === Email Configuration ===
# Email settings - you can configure these via environment variables
EMAIL_SMTP_SERVER = os.environ.get('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.environ.get('EMAIL_SMTP_PORT', '587'))
EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME', 'your-email@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'your-app-password')
EMAIL_FROM_NAME = os.environ.get('EMAIL_FROM_NAME', 'ColApp Support')
EMAIL_FROM_ADDRESS = os.environ.get('EMAIL_FROM_ADDRESS', EMAIL_USERNAME)

# For development/testing, you can use a service like Mailtrap or just print to console
EMAIL_ENABLED = os.environ.get('EMAIL_ENABLED', 'false').lower() == 'true'

db.init_app(app)
jwt = JWTManager(app)



# === Password Reset Config ===
SECRET_KEY = app.config['JWT_SECRET_KEY']
RESET_TOKEN_EXPIRY = 3600  # 1 hour

# In-memory set to track used password reset tokens (single-process only)
used_reset_tokens = set()

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

def send_email(to_email, subject, body, html_body=None):
    """
    Send email using SMTP or print to console for development
    """
    if not EMAIL_ENABLED:
        # For development: just print the email
        print(f'---\nTo: {to_email}\nSubject: {subject}\n\n{body}\n---')
        return True
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM_ADDRESS}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add plain text body
        text_part = MIMEText(body, 'plain')
        msg.attach(text_part)
        
        # Add HTML body if provided
        if html_body:
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
        
        # Create SMTP session
        server = smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT)
        server.starttls()  # Enable TLS
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        
        # Send email
        text = msg.as_string()
        server.sendmail(EMAIL_FROM_ADDRESS, to_email, text)
        server.quit()
        
        print(f"✅ Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {str(e)}")
        # Fallback to console printing
        print(f'---\nTo: {to_email}\nSubject: {subject}\n\n{body}\n---')
        return False

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

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': True})  # Don't reveal if user exists
    
    token = generate_reset_token(user.email)
    
    # Create reset link - use the frontend URL instead of backend
    frontend_url = "https://nyamshaik.me"  # Your frontend domain (HTTPS)
    reset_link = f'{frontend_url}/reset-password?token={token}'
    
    # Create email content
    subject = "Password Reset Request - ColApp"
    
    # Plain text version
    body = f"""
Hello,

You have requested to reset your password for your ColApp account.

To reset your password, please click on the following link:
{reset_link}

This link will expire in 1 hour for security reasons.

If you did not request this password reset, please ignore this email.

Best regards,
ColApp Support Team
    """.strip()
    
    # HTML version
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f8f9fa; padding: 20px; border-radius: 0 0 5px 5px; }}
            .button {{ display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>You have requested to reset your password for your <strong>ColApp</strong> account.</p>
                <p>To reset your password, please click the button below:</p>
                <p style="text-align: center;">
                    <a href="{reset_link}" class="button">Reset Password</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; background-color: #e9ecef; padding: 10px; border-radius: 3px;">
                    {reset_link}
                </p>
                <p><strong>Important:</strong> This link will expire in 1 hour for security reasons.</p>
                <p>If you did not request this password reset, please ignore this email.</p>
                <div class="footer">
                    <p>Best regards,<br>ColApp Support Team</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Send email
    email_sent = send_email(user.email, subject, body, html_body)
    
    if email_sent:
        return jsonify({'success': True, 'message': 'Password reset email sent successfully'})
    else:
        return jsonify({'success': False, 'error': 'Failed to send password reset email'}), 500

@app.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Reset password using token
    """
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')
    
    if not token or not new_password:
        return jsonify({'success': False, 'error': 'Token and new password are required'}), 400
    
    # Verify token
    email = verify_reset_token(token)
    if not email:
        return jsonify({'success': False, 'error': 'Invalid or expired token'}), 400
    
    # Check if token was already used
    if token in used_reset_tokens:
        return jsonify({'success': False, 'error': 'Token already used'}), 400
    
    # Find user
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    # Hash new password
    hashed_password = pbkdf2_sha256.hash(new_password)
    user.password_hash = hashed_password
    
    # Mark token as used
    used_reset_tokens.add(token)
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Password reset successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to reset password'}), 500

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

@app.route('/api/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Get BLS categories for frontend selection"""
    try:
        if not BLS_CATEGORIES_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'BLS categories not available'
            }), 500
        
        categories = get_all_categories()
        return jsonify({
            'success': True,
            'categories': categories
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/categories/hierarchy', methods=['GET'])
@jwt_required()
def get_categories_hierarchy():
    """Get full BLS category hierarchy"""
    try:
        if not BLS_CATEGORIES_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'BLS categories not available'
            }), 500
        
        hierarchy = get_category_hierarchy()
        return jsonify({
            'success': True,
            'hierarchy': hierarchy
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    response = jsonify({
        'status': 'healthy', 
        'message': 'ColApp API is running',
        'version': '1.0.0',
        'backend_ip': '34.57.48.173'
    }), 200
    return add_cors_headers(response)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
