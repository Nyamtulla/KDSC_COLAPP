#!/usr/bin/env python3
"""
Example usage of the Simple Receipt OCR Script
"""

from ocr import SimpleReceiptOCR
import json

def test_with_sample_text():
    """Test the OCR with sample text that was causing issues"""
    print("Testing with sample text that was causing issues...")
    
    # Sample text that was extracted from OCR
    sample_text = """1 Woman 0
2 Ham Cheese 74, 000
1 Ice Java Tea 16, 000
] Mineral Water 13, 000
1 Black SHBG) Dale alee 72, 000
SUBTOTAL ____105, 000
TOTAL 175, 000"""
    
    print("\nSample Receipt Text:")
    print("-" * 50)
    # Print sample text with line numbers for better readability
    lines = sample_text.split('\n')
    for i, line in enumerate(lines, 1):
        if line.strip():  # Only print non-empty lines
            print(f"{i:2d}: {line}")
    print("-" * 50)
    
    # Create a mock receipt data object
    ocr = SimpleReceiptOCR()
    
    # Test the product extraction directly
    products = ocr.extract_products(sample_text)
    
    print(f"\nExtracted {len(products)} products:")
    for i, product in enumerate(products, 1):
        print(f"{i}. {product.name}")
        print(f"   Quantity: {product.quantity}")
        print(f"   Unit Price: ${product.unit_price:.2f}")
        print(f"   Total Price: ${product.total_price:.2f}")
        print(f"   Category: {product.category}")
        print()

def example_usage():
    """Example of how to use the SimpleReceiptOCR class with actual images"""
    
    # Initialize the OCR processor
    ocr = SimpleReceiptOCR()
    
    # Example 1: Process a receipt image
    try:
        # Replace with your actual image path
        #image_path = r"backend\debug_uploaded_image.jpg"
        #image_path = r"backend\uploads\e2f6d0e0-006e-4437-bd0b-eaea1e980cea_scaled_6.jpg"
        #image_path = r"backend\uploads\cdf09c3b-e2ec-49d0-ae3b-b335aa9ad65c_receipt.jpg.jpg"
        image_path = r"backend\uploads\47010ad0-66fe-49b4-9778-e3d97d0546a4_receipt.jpg"
        
        print("Processing receipt with simple OCR (matching Flask app approach)...")
        receipt_data = ocr.process_receipt(image_path)
        
        print("OCR Results:")
        print(f"Store: {receipt_data.store_name}")
        print(f"Total: ${receipt_data.total_amount:.2f}")
        print(f"Items found: {len(receipt_data.items)}")
        print(f"Raw text length: {len(receipt_data.raw_text)}")
        
        print("\nRaw Receipt Text:")
        print("-" * 50)
        # Print raw text with line numbers for better readability
        lines = receipt_data.raw_text.split('\n')
        for i, line in enumerate(lines, 1):
            if line.strip():  # Only print non-empty lines
                print(f"{i:2d}: {line}")
        print("-" * 50)
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
        print("Please provide a valid image path.")
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

def process_images(image_paths):
    ocr = SimpleReceiptOCR()
    for image_path in image_paths:
        print(f"\n{'='*60}\nProcessing: {image_path}\n{'='*60}")
        try:
            receipt_data = ocr.process_receipt(image_path)
            print(f"Store: {receipt_data.store_name}")
            print(f"Total: ${receipt_data.total_amount:.2f}")
            print(f"Number of items: {len(receipt_data.items)}")
            print("\nRaw Receipt Text:")
            print("-" * 50)
            lines = receipt_data.raw_text.split('\n')
            for i, line in enumerate(lines, 1):
                if line.strip():
                    print(f"{i:2d}: {line}")
            print("-" * 50)
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
            print(f"Error processing {image_path}: {e}")

def main():
    """Main function demonstrating OCR usage"""
    print("=== Simple Receipt OCR Example Usage ===\n")
    
    # Test with sample text first
    test_with_sample_text()
    
    print("\n" + "="*50 + "\n")
    
    print("1. Example with mock data:")
    example_with_mock_data()
    
    print("\n" + "="*50 + "\n")
    
    print("2. Example with actual images:")
    image_paths = [
        r"backend\\debug_uploaded_image.jpg",
        r"backend\\uploads\\e2f6d0e0-006e-4437-bd0b-eaea1e980cea_scaled_6.jpg",
        r"backend\\uploads\\b7764c53-5997-43d3-b0b9-5cab818013d5_receipt.jpg",
        r"backend\\uploads\\cdf09c3b-e2ec-49d0-ae3b-b335aa9ad65c_receipt.jpg",
        r"backend\uploads\88f9fad9-5f27-4ba5-9faf-bf2e3ee6a8ce_scaled_4.jpg"
    ]
    process_images(image_paths)
    
    print("\nTo use with an actual image:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
    print("3. Update the image_path in example_usage() function")
    print("4. Run: python example_usage.py")

if __name__ == "__main__":
    main() 