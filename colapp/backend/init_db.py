from app import app, db
from models import User, Receipt, ReceiptItem, Category

def init_database():
    with app.app_context():
        print("Dropping all database tables...")
        db.drop_all()
        print("Tables dropped.")
        
        # Create all tables
        print("Creating all database tables...")
        db.create_all()
        print("Tables created.")
        
        # Insert default categories
        print("Adding default categories...")
        default_categories = [
            'Dairy',
            'Bakery', 
            'Produce',
            'Meat',
            'Frozen Foods',
            'Canned Goods',
            'Beverages',
            'Snacks',
            'Household',
            'Personal Care',
            'Other'
        ]
        
        for category_name in default_categories:
            existing = Category.query.filter_by(name=category_name).first()
            if not existing:
                category = Category(name=category_name)
                db.session.add(category)
        
        db.session.commit()
        print("Database has been initialized successfully!")

if __name__ == "__main__":
    init_database() 