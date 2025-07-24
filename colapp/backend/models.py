from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    sex = db.Column(db.String(20))
    city = db.Column(db.String(100))
    county = db.Column(db.String(100))
    state = db.Column(db.String(30))
    zip_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with receipts
    receipts = db.relationship('Receipt', backref='user', lazy=True)

    def __init__(self, email, password_hash, first_name=None, last_name=None, age=None, sex=None, city=None, county=None, state=None, zip_code=None):
        self.email = email
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.sex = sex
        self.city = city
        self.county = county
        self.state = state
        self.zip_code = zip_code

class Receipt(db.Model):
    __tablename__ = 'receipts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    store_name = db.Column(db.String(200), nullable=False)
    receipt_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)
    ocr_processed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed = db.Column(db.Boolean, default=False)
    
    # Relationship with items
    items = db.relationship('ReceiptItem', backref='receipt', lazy=True, cascade='all, delete-orphan')

    def __init__(self, user_id, store_name, receipt_date, total_amount, image_path, ocr_processed=False, reviewed=False):
        self.user_id = user_id
        self.store_name = store_name
        self.receipt_date = receipt_date
        self.total_amount = total_amount
        self.image_path = image_path
        self.ocr_processed = ocr_processed
        self.reviewed = reviewed

class ReceiptItem(db.Model):
    __tablename__ = 'receipt_items'
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(100), default='Other')
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, receipt_id, product_name, price, category='Other', quantity=1):
        self.receipt_id = receipt_id
        self.product_name = product_name
        self.price = price
        self.category = category
        self.quantity = quantity

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, description=None):
        self.name = name
        self.description = description
