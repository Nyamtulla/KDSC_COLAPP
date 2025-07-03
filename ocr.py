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
        
        # Multiple regex patterns for different receipt formats
        self.regex_patterns = [
            # Pattern 1: Store product format (e.g., "E 673919 FF BS BREAST 23.99 E")
            re.compile(r'^[A-Z]\s+\d+\s+([A-Z\s]+)\s+(\d+\.\d{2})\s+[A-Z]$'),
            
            # Pattern 2: Product with barcode and price (e.g., "404609 ECO HALF PAN 6.49 A")
            re.compile(r'^\d+\s+([A-Z\s]+)\s+(\d+\.\d{2})\s+[A-Z]$'),
            
            # Pattern 3: Product name with barcode (e.g., "RUFFLES 002840020942 F")
            re.compile(r'^([A-Z\s]+)\s+(\d{12,13})\s+[A-Z]$'),
            
            # Pattern 4: Product name with short code (e.g., "BAGELS 001", "GV SLIDERS")
            re.compile(r'^([A-Z\s]+)\s+(\d{1,6})$'),
            
            # Pattern 5: Product name with price and suffix (e.g., "SEA SALT POT CHP $1.29 §")
            re.compile(r'^([A-Z\s]+)\s+\$?(\d+\.\d{2})\s*[§A-Z]?$'),
            
            # Pattern 6: Product name with price and letter suffix (e.g., "BRAIDED BRIOCHE $6.99 F")
            re.compile(r'^([A-Z\s]+)\s+\$?(\d+\.\d{2})\s+[A-Z]$'),
            
            # Pattern 7: Product name with price and colon (e.g., "CHEF PLATE MEAL $10 :")
            re.compile(r'^([A-Z\s]+)\s+\$?(\d+\.?\d*)\s*:?$'),
            
            # Pattern 8: Quantity @ Unit Price ea Total (e.g., "2 @ $10.00 ea $20.00 F")
            re.compile(r'^(\d+)\s+@\s+\$?(\d+\.\d{2})\s+ea\s+\$?(\d+\.\d{2})\s*[A-Z]?$'),
            
            # Pattern 9: Product with barcode and price (e.g., "Su HRO FGHTR 06305094073 6.94 T")
            re.compile(r'^(.+?)\s+(\d{11,12})\s+(\d+\.\d{2})\s+[A-Z]$'),
            
            # Pattern 10: Quantity + Product Name + Price with commas (e.g., "2 Ham Cheese 74, 000")
            re.compile(r'^\s*(\d+)\s+([A-Za-z\s&()]+)\s+([\d,\s]+)$'),
            
            # Pattern 11: Quantity + Product Name + Price (e.g., "2 MILK 3.98")
            re.compile(r'^\s*(\d+)\s+([A-Za-z\s&]+)\s+([\d,]+\.?\d*)$'),
            
            # Pattern 12: Product Name + Price (e.g., "MILK $1.99")
            re.compile(r'^([A-Za-z\s&]+)\s+\$?(\d+\.\d{2})$'),
            
            # Pattern 13: Product Name + Weight + @ + Unit Price + Total (e.g., "BANANAS 2.5 lb @ 0.99 2.48")
            re.compile(r'^(.+?)\s+(\d+\.\d+)\s+lb\s+@\s+(\d+\.\d+)\s+.*?(\d+\.\d+)$'),
            
            # Pattern 14: Product Name + Price (fallback)
            re.compile(r'^(.+?)\s+\$?(\d+\.\d{2})$'),
            
            # Pattern 15: Product Name + Quantity @ Unit Price + Total (e.g., "MILK 2 @ $1.99 $3.98")
            re.compile(r'^(.+?)\s+(\d+)\s*@\s*\$?(\d+\.\d{2})\s+\$?(\d+\.\d{2})\s*$'),
            
            # Pattern 16: Product Name + Quantity @ Unit Price + Char + Total (e.g., "BREAD 2 @ $2.49 T$4.98")
            re.compile(r'^(.+?)\s+(\d+)\s*@\s*\$?(\d+\.\d{2})\s+[A-Za-z]?\$?(\d+\.\d{2})\s*$'),
            
            # Pattern 17: Product Name + Quantity @ Unit Price + ... + Total (flexible)
            re.compile(r'^(.+?)\s+(\d+)\s*@\s*\$?(\d+\.\d{2}).*?(\d+\.\d{2})\s*$'),
            
            # Pattern 18: Product Name + Unit Price x Quantity = Total (e.g., "MILK $1.99 x 2 = $3.98")
            re.compile(r'^(.+?)\s+\$?(\d+\.\d{2})\s+x\s+(\d+)\s*=\s*\$?(\d+\.\d{2})$'),
            
            # Pattern 19: Product Name + Quantity for Unit Price Total (e.g., "BREAD 2 for $2.49 $4.98")
            re.compile(r'^(.+?)\s+(\d+)\s+for\s+\$?(\d+\.\d{2})\s+\$?(\d+\.\d{2})$'),
            
            # Pattern 20: Handle lines starting with "]" (OCR error) - treat as quantity 1
            re.compile(r'^\s*\]\s+([A-Za-z\s&()]+)\s+([\d,\s]+)$')
        ]

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
        """Extract product information from receipt text using multiple regex patterns"""
        products = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines that are likely not products
            if any(skip in line.upper() for skip in ['TOTAL', 'TAX', 'SUBTOTAL', 'BALANCE', 'THANK', 'RECEIPT', 'DATE', 'TIME', 'CHANGE', 'CHECK', 'MEMBER', 'PRNTD', 'NUMBER', 'SOLD', 'WHSE', 'TRM', 'TRN', 'OP', 'NET SALES', 'TAK', 'CASH TEND', 'EFT DEBIT', 'ACCOUNT', 'REF', 'NETWORK', 'TERMINAL', 'ITEMS SOLD', 'TCR']):
                continue
            
            # Skip lines that are just numbers (like "38 4.29")
            if re.match(r'^\s*\d+\s+\d+\.\d{2}\s*$', line):
                continue
            
            # Try each regex pattern
            for pattern in self.regex_patterns:
                match = pattern.match(line)
                if match:
                    groups = match.groups()

                    
                    # Pattern 1: Store product format (e.g., "E 673919 FF BS BREAST 23.99 E")
                    if len(groups) == 2 and line.startswith('E ') and line.endswith(' E'):
                        product_name = groups[0].strip()
                        price = float(groups[1])
                        quantity = 1
                        unit_price = price
                        total_price = price
                        
                    # Pattern 2: Product with barcode and price (e.g., "404609 ECO HALF PAN 6.49 A")
                    elif len(groups) == 2 and line[0].isdigit() and line.endswith(' A'):
                        product_name = groups[0].strip()
                        price = float(groups[1])
                        quantity = 1
                        unit_price = price
                        total_price = price
                        
                    # Pattern 3: Product name with barcode (e.g., "RUFFLES 002840020942 F")
                    elif len(groups) == 2 and len(groups[1]) >= 12 and groups[1].isdigit():
                        product_name = groups[0].strip()
                        # For barcode items without price, skip
                        continue
                        
                    # Pattern 4: Product name with short code (e.g., "BAGELS 001", "GV SLIDERS")
                    elif len(groups) == 2 and len(groups[1]) <= 6 and groups[1].isdigit():
                        product_name = groups[0].strip()
                        # For items without price, skip
                        continue
                        
                    # Pattern 5: Product name with price and suffix (e.g., "SEA SALT POT CHP $1.29 §")
                    elif len(groups) == 2 and '.' in groups[1] and groups[1].replace('.', '').isdigit():
                        product_name = groups[0].strip()
                        price = float(groups[1])
                        quantity = 1
                        unit_price = price
                        total_price = price
                        
                    # Pattern 6: Product name with price and letter suffix (e.g., "BRAIDED BRIOCHE $6.99 F")
                    elif len(groups) == 2 and '.' in groups[1] and groups[1].replace('.', '').isdigit():
                        product_name = groups[0].strip()
                        price = float(groups[1])
                        quantity = 1
                        unit_price = price
                        total_price = price
                        
                    # Pattern 7: Product name with price and colon (e.g., "CHEF PLATE MEAL $10 :")
                    elif len(groups) == 2 and '.' in groups[1] and groups[1].replace('.', '').isdigit():
                        product_name = groups[0].strip()
                        price = float(groups[1])
                        quantity = 1
                        unit_price = price
                        total_price = price
                        
                    # Pattern 8: Quantity @ Unit Price ea Total (e.g., "2 @ $10.00 ea $20.00 F")
                    elif len(groups) == 3 and groups[0].isdigit() and '@' in line and 'ea' in line:
                        quantity = int(groups[0])
                        unit_price = float(groups[1])
                        total_price = float(groups[2])
                        product_name = f"Item {len(products) + 1}"  # Generic name
                        
                    # Pattern 9: Product with barcode and price (e.g., "Su HRO FGHTR 06305094073 6.94 T")
                    elif len(groups) == 3 and len(groups[1]) >= 11 and groups[1].isdigit():
                        product_name = groups[0].strip()
                        price = float(groups[2])
                        quantity = 1
                        unit_price = price
                        total_price = price
                        
                    # Pattern 10/11/11b/11c: Quantity + Product Name + Price (e.g., "2 MILK 3.98", "1 Woman 0", "2 Ham Cheese 74, 000")
                    elif len(groups) == 3 and groups[0].isdigit():
                        quantity = int(groups[0])
                        product_name = groups[1].strip()
                        try:
                            total_price = float(groups[2].replace(',', '').replace(' ', ''))
                        except ValueError:
                            continue
                        unit_price = total_price / quantity if quantity > 0 else total_price
                        
                    # Pattern 12: Product Name + Price
                    elif len(groups) == 2 and '.' in groups[1] and groups[1].replace('.', '').isdigit():
                        product_name = groups[0].strip()
                        price = float(groups[1])
                        quantity = 1
                        unit_price = price
                        total_price = price
                        
                    # Pattern 13: Product Name + Weight + @ + Unit Price + Total
                    elif len(groups) == 4 and 'lb' in line:
                        product_name = groups[0].strip()
                        weight = float(groups[1])
                        unit_price = float(groups[2])
                        total_price = float(groups[3])
                        quantity = 1  # Treat weight as quantity for pricing
                        
                    # Pattern 14: Product Name + Price (fallback)
                    elif len(groups) == 2 and '.' in groups[1] and groups[1].replace('.', '').isdigit():
                        product_name = groups[0].strip()
                        price = float(groups[1])
                        quantity = 1
                        unit_price = price
                        total_price = price
                        
                    # Pattern 15: Product Name + Quantity @ Unit Price + Total
                    elif len(groups) == 4 and groups[1].isdigit():
                        product_name = groups[0].strip()
                        quantity = int(groups[1])
                        unit_price = float(groups[2])
                        total_price = float(groups[3])
                        
                    # Pattern 16: Product Name + Quantity @ Unit Price + Char + Total
                    elif len(groups) == 4 and groups[1].isdigit():
                        product_name = groups[0].strip()
                        quantity = int(groups[1])
                        unit_price = float(groups[2])
                        total_price = float(groups[3])
                        
                    # Pattern 17: Product Name + Quantity @ Unit Price + ... + Total (flexible)
                    elif len(groups) == 4 and groups[1].isdigit():
                        product_name = groups[0].strip()
                        quantity = int(groups[1])
                        unit_price = float(groups[2])
                        total_price = float(groups[3])
                        
                    # Pattern 18: Product Name + Unit Price x Quantity = Total
                    elif len(groups) == 4 and 'x' in line and '=' in line:
                        product_name = groups[0].strip()
                        unit_price = float(groups[1])
                        quantity = int(groups[2])
                        total_price = float(groups[3])
                        
                    # Pattern 19: Product Name + Quantity for Unit Price Total
                    elif len(groups) == 4 and 'for' in line:
                        product_name = groups[0].strip()
                        quantity = int(groups[1])
                        unit_price = float(groups[2])
                        total_price = float(groups[3])
                        
                    # Pattern 20: Handle lines starting with "]" (OCR error) - treat as quantity 1
                    elif len(groups) == 2 and line.strip().startswith(']'):
                        quantity = 1
                        product_name = groups[0].strip()
                        # Remove commas and spaces from price
                        price_str = groups[1].replace(',', '').replace(' ', '')
                        total_price = float(price_str)
                        unit_price = total_price
                        
                    else:
                        continue
                    
                    # Validate product name
                    if product_name.lower() not in ['total', 'tax', 'subtotal', 'amount'] and len(product_name.strip()) > 0:
                        products.append(Product(
                            name=product_name,
                            quantity=quantity,
                            unit_price=round(unit_price, 2),
                            total_price=round(total_price, 2),
                            category='Other'
                        ))
                    break

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
