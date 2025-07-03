#!/usr/bin/env python3
"""
Example usage of the Simple Receipt OCR Script
Demonstrates how to use the simplified OCR functionality that matches the Flask app.
"""

import json
from ocr import SimpleReceiptOCR

def example_usage():
    """Example of how to use the SimpleReceiptOCR class"""
    
    # Initialize the OCR processor
    ocr = SimpleReceiptOCR()
    
    # Example 1: Process a receipt image
    try:
        # Replace with your actual image path
        image_path = r"backend\debug_uploaded_image.jpg"
        #image_path = r"backend\uploads\fd88fdf8-f850-4f46-bc84-f8b10ae0c4b9_receipt.jpg"
        
        print("Processing receipt with simple OCR (matching Flask app approach)...")
        receipt_data = ocr.process_receipt(image_path)
        
        print("OCR Results:")
        print(f"Store: {receipt_data.store_name}")
        print(f"Total: ${receipt_data.total_amount:.2f}")
        print(f"Items found: {len(receipt_data.items)}")
        print(f"Raw text length: {len(receipt_data.raw_text)}")
        
        print(receipt_data)
        # Convert to JSON
        json_output = ocr.to_json(receipt_data, include_raw_text=False)
        
        # Print the JSON output
        print("Receipt Data (JSON):")
        print(json_output)
        
        # Access individual fields
        print(f"\nStore: {receipt_data.store_name}")
        print(f"Total: ${receipt_data.total_amount:.2f}")
        print(f"Number of items: {len(receipt_data.items)}")
        
        # Print each product
        print("\nProducts:")
        for i, product in enumerate(receipt_data.items, 1):
            print(f"{i}. {product.name}")
            print(f"   Quantity: {product.quantity}")
            print(f"   Unit Price: ${product.unit_price:.2f}")
            print(f"   Total Price: ${product.total_price:.2f}")
            print(f"   Category: {product.category}")
            print()
            
    except FileNotFoundError:
        print(f"Image file not found: {image_path}")
    except Exception as e:
        print(f"Error processing receipt: {e}")

def example_with_mock_data():
    """Example using mock data to show the expected output format"""
    
    # Create a sample receipt data structure
    from ocr import ReceiptData, Product
    
    # Create sample products
    products = [
        Product(
            name="Milk 2%",
            quantity=1,
            unit_price=3.99,
            total_price=3.99,
            category="Other"
        ),
        Product(
            name="Bread Whole Wheat",
            quantity=2,
            unit_price=2.49,
            total_price=4.98,
            category="Other"
        ),
        Product(
            name="Bananas",
            quantity=1,
            unit_price=1.99,
            total_price=1.99,
            category="Other"
        ),
        Product(
            name="Chicken Breast",
            quantity=1,
            unit_price=12.99,
            total_price=12.99,
            category="Other"
        )
    ]
    
    # Create receipt data
    receipt_data = ReceiptData(
        store_name="Walmart",
        total_amount=21.46,
        items=products,
        raw_text="Sample receipt text..."
    )
    
    # Convert to JSON
    ocr = SimpleReceiptOCR()
    json_output = ocr.to_json(receipt_data, include_raw_text=False)
    
    print("Example Receipt Data (JSON):")
    print(json_output)
    
    # Parse JSON back to dictionary
    data_dict = json.loads(json_output)
    
    print(f"\nParsed Data:")
    print(f"Store: {data_dict['store_name']}")
    print(f"Total: ${data_dict['total_amount']}")
    print(f"Items: {len(data_dict['items'])}")
    
    print("\nProducts:")
    for i, item in enumerate(data_dict['items'], 1):
        print(f"{i}. {item['name']}")
        print(f"   Quantity: {item['quantity']}")
        print(f"   Unit Price: ${item['unit_price']}")
        print(f"   Total Price: ${item['total_price']}")
        print(f"   Category: {item['category']}")
        print()

if __name__ == "__main__":
    print("=== Simple Receipt OCR Example Usage ===\n")
    
    print("1. Example with mock data:")
    example_with_mock_data()
    
    print("\n" + "="*50 + "\n")
    
    print("2. Example with actual image:")
    example_usage()
    
    print("\nTo use with an actual image:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
    print("3. Update the image_path in example_usage() function")
    print("4. Run: python example_usage.py") 