#!/usr/bin/env python3
"""
Example usage of the Receipt OCR Script
Demonstrates how to use the OCR functionality programmatically.
"""

import json
from ocr import ReceiptOCR

def example_usage():
    """Example of how to use the ReceiptOCR class"""
    
    # Initialize the OCR processor
    ocr = ReceiptOCR()
    
    # Example 1: Process a receipt image
    try:
        # Replace with your actual image path
        image_path = r"backend\debug_uploaded_image.jpg"
        #image_path = r"backend\uploads\fd88fdf8-f850-4f46-bc84-f8b10ae0c4b9_receipt.jpg"
        
        print("Processing receipt with standard preprocessing...")
        # Try standard preprocessing first
        receipt_data = ocr.process_receipt(image_path, save_processed=True, use_alternative=False)
        
        print("Standard preprocessing results:")
        print(f"Store: {receipt_data.store_name}")
        print(f"Total: ${receipt_data.total_amount:.2f}")
        print(f"Items found: {len(receipt_data.items)}")
        print(f"Raw text length: {len(receipt_data.raw_text)}")
        
        print("\n" + "="*50 + "\n")
        
        print("Processing receipt with alternative preprocessing (thinner characters)...")
        # Try alternative preprocessing for thinner characters
        receipt_data_alt = ocr.process_receipt(image_path, save_processed=True, use_alternative=True)
        
        print("Alternative preprocessing results:")
        print(f"Store: {receipt_data_alt.store_name}")
        print(f"Total: ${receipt_data_alt.total_amount:.2f}")
        print(f"Items found: {len(receipt_data_alt.items)}")
        print(f"Raw text length: {len(receipt_data_alt.raw_text)}")
        
        # Compare results
        print("\n" + "="*50 + "\n")
        print("COMPARISON:")
        print(f"Standard preprocessing - Items: {len(receipt_data.items)}, Text length: {len(receipt_data.raw_text)}")
        print(f"Alternative preprocessing - Items: {len(receipt_data_alt.items)}, Text length: {len(receipt_data_alt.raw_text)}")
        
        # Use the better result (more items or longer text)
        if len(receipt_data_alt.items) > len(receipt_data.items) or len(receipt_data_alt.raw_text) > len(receipt_data.raw_text):
            receipt_data = receipt_data_alt
            print("Using alternative preprocessing results (better OCR)")
        else:
            print("Using standard preprocessing results")
        
        print(receipt_data)
        # Convert to JSON
        json_output = ocr.to_json(receipt_data, include_raw_text=False)
        
        # Print the JSON output
        print("Receipt Data (JSON):")
        print(json_output)
        
        # Access individual fields
        print(f"\nStore: {receipt_data.store_name}")
        print(f"Total: ${receipt_data.total_amount:.2f}")
        print(f"Date: {receipt_data.date}")
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
            category="Dairy"
        ),
        Product(
            name="Bread Whole Wheat",
            quantity=2,
            unit_price=2.49,
            total_price=4.98,
            category="Bakery"
        ),
        Product(
            name="Bananas",
            quantity=1,
            unit_price=1.99,
            total_price=1.99,
            category="Produce"
        ),
        Product(
            name="Chicken Breast",
            quantity=1,
            unit_price=12.99,
            total_price=12.99,
            category="Meat"
        )
    ]
    
    # Create receipt data
    receipt_data = ReceiptData(
        store_name="Walmart",
        total_amount=25.95,
        subtotal=23.95,
        tax_amount=2.00,
        date="2024-01-15",
        items=products,
        raw_text="Sample receipt text..."
    )
    
    # Convert to JSON
    ocr = ReceiptOCR()
    json_output = ocr.to_json(receipt_data, include_raw_text=False)
    
    print("Example Receipt Data (JSON):")
    print(json_output)
    
    # Parse JSON back to dictionary
    data_dict = json.loads(json_output)
    
    print(f"\nParsed Data:")
    print(f"Store: {data_dict['store_name']}")
    print(f"Total: ${data_dict['total_amount']}")
    print(f"Subtotal: ${data_dict['subtotal']}")
    print(f"Tax: ${data_dict['tax_amount']}")
    print(f"Date: {data_dict['date']}")
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
    print("=== Receipt OCR Example Usage ===\n")
    
    # print("1. Example with mock data:")
    # #example_with_mock_data()
    
    # print("\n" + "="*50 + "\n")
    
    # print("2. Example with actual image (commented out):")
    # print("# Uncomment the line below and provide a valid image path")
    example_usage()
    
    print("\nTo use with an actual image:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
    print("3. Update the image_path in example_usage() function")
    print("4. Run: python example_usage.py") 