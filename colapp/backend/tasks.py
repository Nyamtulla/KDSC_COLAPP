from models import Receipt, ReceiptItem
from enhanced_receipt_parser import EnhancedReceiptParser
import os

def process_receipt(receipt_id, filepath, parsing_method):
    from app import app, db  # Import here to avoid circular import
    filepath = os.path.normpath(filepath)
    with app.app_context():
        receipt = Receipt.query.get(receipt_id)
        if not receipt:
            return
        parser = EnhancedReceiptParser()
        parsed_data = parser.parse_receipt(filepath, method=parsing_method)
        print("RAW/PARSED DATA DEBUG:")
        print("Raw output:", getattr(parser, 'last_raw_output', None))
        print("Parsed data:", parsed_data)
        items = parsed_data.get('data', {}).get('items', [])
        receipt_data = parsed_data.get('data', {})
        print("Items to save:", items)
        # Update receipt fields from parsed data
        store_name = receipt_data.get('store_name', 'Unknown Store')
        print(f"Original store name length: {len(store_name)}")
        print(f"Original store name: {store_name}")
        
        # Truncate store name to fit database field (200 characters)
        if store_name and len(store_name) > 200:
            store_name = store_name[:197] + "..."
            print(f"Truncated store name length: {len(store_name)}")
            print(f"Truncated store name: {store_name}")
        
        receipt.store_name = store_name
        receipt.total_amount = receipt_data.get('total', 0.0)
        receipt.ocr_processed = True
        db.session.commit()
        # Remove old items if any
        ReceiptItem.query.filter_by(receipt_id=receipt.id).delete()
        for item_data in items:
            # Truncate product name and category to fit database fields
            product_name = item_data.get('name', '')
            if product_name and len(product_name) > 200:
                product_name = product_name[:197] + "..."
            
            category = item_data.get('category', 'Other')
            if category and len(category) > 100:
                category = category[:97] + "..."
            
            item = ReceiptItem(
                receipt_id=receipt.id,
                product_name=product_name,
                price=item_data.get('total_price', 0.0),
                category=category,
                quantity=item_data.get('quantity', 1)
            )
            print("Saving item:", item.product_name, item.price, item.category, item.quantity)
            db.session.add(item)
        db.session.commit() 