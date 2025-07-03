#!/usr/bin/env python3
"""
Simple Receipt OCR Script
Extracts store name, total amount, and product details from receipt images.
Returns structured JSON data - simplified version matching the Flask app approach.
"""

import os
import sys
import json
import re
import argparse
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import pytesseract
from PIL import Image

# Configure Tesseract path for Windows
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@dataclass
class Product:
    """Represents a product item from the receipt"""
    name: str
    quantity: int
    unit_price: float
    total_price: float
    category: str

@dataclass
class ReceiptData:
    """Represents the complete receipt data"""
    store_name: str
    total_amount: float
    items: List[Product]
    raw_text: str

class SimpleReceiptOCR:
    """Simple OCR receipt processing - matches Flask app approach"""
    
    def __init__(self):
        # Known store names (same as in Flask app)
        self.known_stores = ['WALMART', 'TARGET', 'KROGER', 'SAFEWAY', 'COSTCO', 'ALDI', 'CVS', 'WALGREENS']
        
        # Total patterns (same as in Flask app)
        self.total_patterns = [
            re.compile(r'total[\s:]*\$?(\d+\.\d{2})', re.IGNORECASE),
            re.compile(r'amount[\s:]*\$?(\d+\.\d{2})', re.IGNORECASE),
            re.compile(r'\$?(\d+\.\d{2})$')
        ]
        
        # Item pattern for @ format: [product name] [count] @ [unit price] [total price at end]
        self.item_pattern_at = re.compile(r'(.+?)\s+(\d+)\s*@\s*\$?(\d+\.\d{2})\s+\$?(\d+\.\d{2})\s*$')
        
        # Alternative pattern for @ format with possible single char before total: [product name] [count] @ [unit price] [char][total price]
        self.item_pattern_at_alt = re.compile(r'(.+?)\s+(\d+)\s*@\s*\$?(\d+\.\d{2})\s+[A-Za-z]?\$?(\d+\.\d{2})\s*$')
        
        # Flexible pattern for @ format: [product name] [count] @ [unit price] ... [total price]
        self.item_pattern_at_flexible = re.compile(r'(.+?)\s+(\d+)\s*@\s*\$?(\d+\.\d{2}).*?(\d+\.\d{2})\s*$')
        
        # Fallback item pattern (same as in Flask app)
        self.item_pattern_fallback = re.compile(r'(.+?)\s+\$?(\d+\.\d{2})')

    def extract_text(self, image_path: str) -> str:
        """Extract text from image using OCR - simple approach like Flask app"""
        try:
            # Load image directly without preprocessing
            image = Image.open(image_path)
            
            # Extract text using Tesseract (same as Flask app)
            text = pytesseract.image_to_string(image)
            
            return text.strip()
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""

    def identify_store(self, text: str) -> str:
        """Identify the store name from the receipt text - same logic as Flask app"""
        lines = text.split('\n')
        store_name = 'Unknown Store'

        # Try to match known store names (same as Flask app)
        for line in lines[:8]:
            for store in self.known_stores:
                if store in line.upper():
                    store_name = store.title()
                    break
            if store_name != 'Unknown Store':
                break
        
        # Fallback: first non-empty line (same as Flask app)
        if store_name == 'Unknown Store':
            for line in lines[:5]:
                if line.strip():
                    store_name = line.strip()
                    break

        return store_name

    def extract_total(self, text: str) -> float:
        """Extract total amount from receipt text - same logic as Flask app"""
        lines = text.split('\n')
        total_amount = 0.0

        # Try to find total amount (same as Flask app)
        for line in lines:
            for pattern in self.total_patterns:
                match = pattern.search(line)
                if match:
                    try:
                        total_amount = float(match.group(1))
                        break
                    except:
                        continue
            if total_amount:
                break

        return total_amount

    def extract_products(self, text: str) -> List[Product]:
        """Extract product information from receipt text - handles @ format"""
        products = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines that are likely not products
            if any(skip in line.upper() for skip in ['TOTAL', 'TAX', 'SUBTOTAL', 'BALANCE', 'THANK', 'RECEIPT', 'DATE', 'TIME']):
                continue
            
            # Try @ format first: [product name] [count] @ [unit price] [total price]
            match = self.item_pattern_at.match(line)
            if match:
                product_name = match.group(1).strip()
                quantity = int(match.group(2))
                unit_price = float(match.group(3))
                total_price = float(match.group(4))
                
                if product_name.lower() not in ['total', 'tax', 'subtotal', 'amount']:
                    products.append(Product(
                        name=product_name,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price,
                        category='Other'
                    ))
                continue
            
            # Try alternative @ format
            match = self.item_pattern_at_alt.match(line)
            if match:
                product_name = match.group(1).strip()
                quantity = int(match.group(2))
                unit_price = float(match.group(3))
                total_price = float(match.group(4))
                
                if product_name.lower() not in ['total', 'tax', 'subtotal', 'amount']:
                    products.append(Product(
                        name=product_name,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price,
                        category='Other'
                    ))
                continue
            
            # Try flexible @ format
            match = self.item_pattern_at_flexible.match(line)
            if match:
                product_name = match.group(1).strip()
                quantity = int(match.group(2))
                unit_price = float(match.group(3))
                total_price = float(match.group(4))
                
                if product_name.lower() not in ['total', 'tax', 'subtotal', 'amount']:
                    products.append(Product(
                        name=product_name,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price,
                        category='Other'
                    ))
                continue
            
            # Fallback to simple format: [product name] [price]
            match = self.item_pattern_fallback.match(line)
            if match:
                product_name = match.group(1).strip()
                price = float(match.group(2))
                
                if product_name.lower() not in ['total', 'tax', 'subtotal', 'amount']:
                    products.append(Product(
                        name=product_name,
                        quantity=1,
                        unit_price=price,
                        total_price=price,
                        category='Other'
                    ))

        return products

    def process_receipt(self, image_path: str) -> ReceiptData:
        """Process a receipt image and extract all information - simplified approach"""
        # Extract text from image
        text = self.extract_text(image_path)
        
        if not text:
            raise ValueError("No text could be extracted from the image")
        
        # Extract store name
        store_name = self.identify_store(text)
        
        # Extract total amount
        total_amount = self.extract_total(text)
        
        # Extract products
        products = self.extract_products(text)
        
        # Create receipt data object
        receipt_data = ReceiptData(
            store_name=store_name,
            total_amount=total_amount,
            items=products,
            raw_text=text
        )
        
        return receipt_data

    def to_json(self, receipt_data: ReceiptData, include_raw_text: bool = False) -> str:
        """Convert receipt data to JSON string"""
        data = asdict(receipt_data)
        
        if not include_raw_text:
            data.pop('raw_text', None)
        
        return json.dumps(data, indent=2, default=str)

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description='Extract receipt information from image')
    parser.add_argument('image_path', help='Path to the receipt image')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    parser.add_argument('--include-raw-text', action='store_true', help='Include raw OCR text in output')
    parser.add_argument('--pretty', action='store_true', help='Pretty print JSON output')
    
    args = parser.parse_args()
    
    # Check if image file exists
    if not os.path.exists(args.image_path):
        print(f"Error: Image file '{args.image_path}' not found")
        sys.exit(1)
    
    try:
        # Initialize OCR processor
        ocr = SimpleReceiptOCR()
        
        # Process receipt
        print(f"Processing receipt: {args.image_path}")
        receipt_data = ocr.process_receipt(args.image_path)
        
        # Convert to JSON
        json_output = ocr.to_json(receipt_data, include_raw_text=args.include_raw_text)
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                f.write(json_output)
            print(f"Results saved to: {args.output}")
        else:
            if args.pretty:
                print(json_output)
            else:
                # Print summary
                print(f"\nReceipt Summary:")
                print(f"Store: {receipt_data.store_name}")
                print(f"Total: ${receipt_data.total_amount:.2f}")
                print(f"Items: {len(receipt_data.items)}")
                
                print(f"\nProducts:")
                for i, product in enumerate(receipt_data.items, 1):
                    print(f"{i}. {product.name}")
                    print(f"   Quantity: {product.quantity}")
                    print(f"   Unit Price: ${product.unit_price:.2f}")
                    print(f"   Total Price: ${product.total_price:.2f}")
                    print(f"   Category: {product.category}")
                    print()
        
    except Exception as e:
        print(f"Error processing receipt: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
