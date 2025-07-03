#!/usr/bin/env python3
"""
Receipt OCR Script
Extracts store name, total amount, and product details from receipt images.
Returns structured JSON data with product quantities, costs, and categories.
"""

import os
import sys
import json
import re
import argparse
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import pytesseract
from PIL import Image, ImageEnhance
import cv2
import numpy as np

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
    subtotal: float
    tax_amount: float
    date: Optional[str]
    items: List[Product]
    raw_text: str

class ReceiptOCR:
    """Main class for OCR receipt processing"""
    
    def __init__(self):
        # Common store names and their variations
        self.store_patterns = {
            'Walmart': [r'walmart', r'wal-mart', r'wal mart', r'walmart\s+supercenter', r'walmart\s+neighborhood'],
            'Target': [r'target', r'target\s+store', r'target\s+corporation'],
            'Kroger': [r'kroger', r'kroger\s+co', r'kroger\s+company'],
            'Safeway': [r'safeway', r'safeway\s+inc', r'safeway\s+stores'],
            'Costco': [r'costco', r'costco\s+wholesale', r'costco\s+warehouse'],
            'Aldi': [r'aldi', r'aldi\s+inc', r'aldi\s+stores'],
            'CVS': [r'cvs', r'cvs\s+pharmacy', r'cvs\s+caremark'],
            'Walgreens': [r'walgreens', r'walgreens\s+boot', r'walgreens\s+pharmacy'],
            'Home Depot': [r'home\s*depot', r'the\s+home\s*depot', r'home\s*depot\s+inc'],
            'Lowes': [r'lowes', r'lowes\s+companies', r'lowes\s+home'],
            'Best Buy': [r'best\s*buy', r'bestbuy', r'best\s*buy\s+co'],
            'Starbucks': [r'starbucks', r'starbucks\s+coffee', r'starbucks\s+corporation'],
            'McDonalds': [r'mcdonalds', r'mcdonald', r'mcdonalds\s+corp'],
            'Subway': [r'subway', r'subway\s+restaurants', r'subway\s+inc'],
            'Dollar General': [r'dollar\s*general', r'dollargeneral', r'dg\s+market'],
            'Family Dollar': [r'family\s*dollar', r'familydollar', r'fd\s+store'],
            'Dollar Tree': [r'dollar\s*tree', r'dollartree', r'dt\s+store']
        }
        
        # Product categories with keywords
        self.category_keywords = {
            'Dairy': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'sour cream', 'cottage cheese', 'half & half', 'whipping cream', 'heavy cream'],
            'Produce': ['banana', 'apple', 'orange', 'lettuce', 'tomato', 'onion', 'potato', 'carrot', 'broccoli', 'spinach', 'kale', 'cucumber', 'pepper', 'grape', 'strawberry', 'blueberry', 'avocado', 'mushroom', 'celery', 'corn', 'peas', 'beans', 'squash', 'zucchini'],
            'Meat': ['chicken', 'beef', 'pork', 'turkey', 'ham', 'bacon', 'sausage', 'steak', 'ground', 'breast', 'thigh', 'wing', 'roast', 'chop', 'cutlet', 'fillet', 'tenderloin', 'ribs', 'drumstick'],
            'Bakery': ['bread', 'bun', 'roll', 'cake', 'cookie', 'muffin', 'donut', 'pastry', 'croissant', 'bagel', 'tortilla', 'pita', 'english muffin', 'danish', 'eclair'],
            'Beverages': ['soda', 'pop', 'cola', 'juice', 'water', 'coffee', 'tea', 'beer', 'wine', 'drink', 'lemonade', 'iced tea', 'energy drink', 'sports drink', 'sparkling water'],
            'Frozen': ['frozen', 'ice cream', 'pizza', 'french fries', 'nugget', 'frozen dinner', 'frozen vegetables', 'ice cream bar', 'popsicle', 'frozen waffle'],
            'Canned Goods': ['can', 'canned', 'soup', 'beans', 'tuna', 'corn', 'peas', 'tomato sauce', 'pasta sauce', 'chili', 'stew', 'vegetables'],
            'Snacks': ['chip', 'cracker', 'popcorn', 'pretzel', 'nut', 'candy', 'chocolate', 'gum', 'trail mix', 'granola bar', 'protein bar', 'jerky', 'dried fruit'],
            'Household': ['paper towel', 'toilet paper', 'soap', 'detergent', 'cleaner', 'trash bag', 'ziploc', 'dish soap', 'laundry detergent', 'fabric softener', 'bleach', 'all purpose cleaner'],
            'Personal Care': ['shampoo', 'toothpaste', 'deodorant', 'lotion', 'razor', 'makeup', 'vitamin', 'toothbrush', 'mouthwash', 'body wash', 'facial cleanser', 'sunscreen'],
            'Baby': ['diaper', 'formula', 'baby food', 'wipes', 'bottle', 'pacifier', 'baby wash', 'baby lotion', 'baby cereal', 'baby snack'],
            'Pet': ['dog food', 'cat food', 'pet food', 'treat', 'litter', 'pet toy', 'pet shampoo', 'pet treat', 'bird seed', 'fish food'],
            'Pharmacy': ['medicine', 'pill', 'tablet', 'prescription', 'tylenol', 'advil', 'aspirin', 'cold medicine', 'allergy medicine', 'pain reliever', 'vitamin', 'supplement']
        }
        
        # Enhanced price patterns - more flexible matching
        self.price_patterns = [
            r'\$?\s*(\d+\.\d{2})',     # $12.34 or 12.34
            r'\$?\s*(\d+\.\d{1})',     # $12.3 or 12.3
            r'\$?\s*(\d+)',            # $12 or 12 (whole numbers)
            r'(\d+\.\d{2})',           # 12.34
            r'(\d+\.\d{1})',           # 12.3
        ]
        
        # Enhanced quantity patterns
        self.quantity_patterns = [
            r'(\d+)\s*@',              # 2 @
            r'(\d+)\s*x',              # 2 x
            r'(\d+)\s*\*',             # 2 *
            r'(\d+)\s*for',            # 2 for
            r'qty\s*(\d+)',            # qty 2
            r'quantity\s*(\d+)',       # quantity 2
            r'(\d+)\s*ea',             # 2 ea
            r'(\d+)\s*each',           # 2 each
            r'(\d+)\s*pc',             # 2 pc
            r'(\d+)\s*pack',           # 2 pack
            r'(\d+)\s*ct',             # 2 ct
            r'(\d+)\s*count',          # 2 count
        ]
        
        # Enhanced total patterns
        self.total_patterns = [
            r'total[\s:]*\$?\s*(\d+\.\d{2})',
            r'amount[\s:]*\$?\s*(\d+\.\d{2})',
            r'balance[\s:]*\$?\s*(\d+\.\d{2})',
            r'grand[\s]*total[\s:]*\$?\s*(\d+\.\d{2})',
            r'final[\s]*total[\s:]*\$?\s*(\d+\.\d{2})',
            r'card[\s]*total[\s:]*\$?\s*(\d+\.\d{2})',
            r'cash[\s]*total[\s:]*\$?\s*(\d+\.\d{2})',
            r'change[\s:]*\$?\s*(\d+\.\d{2})',
            r'balance[\s]*due[\s:]*\$?\s*(\d+\.\d{2})',
        ]
        
        # Enhanced tax patterns
        self.tax_patterns = [
            r'tax[\s:]*\$?\s*(\d+\.\d{2})',
            r'sales[\s]*tax[\s:]*\$?\s*(\d+\.\d{2})',
            r'state[\s]*tax[\s:]*\$?\s*(\d+\.\d{2})',
            r'local[\s]*tax[\s:]*\$?\s*(\d+\.\d{2})',
            r'city[\s]*tax[\s:]*\$?\s*(\d+\.\d{2})',
        ]
        
        # Enhanced date patterns
        self.date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{2,4})',
            r'(\d{1,2})-(\d{1,2})-(\d{2,4})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
            r'(\d{1,2})\.(\d{1,2})\.(\d{2,4})',
            r'(\d{1,2})\s+(\d{1,2})\s+(\d{2,4})',
        ]
        
        # Skip patterns for lines that are not products
        self.skip_patterns = [
            r'total', r'tax', r'subtotal', r'balance', r'thank', r'receipt', r'date', r'time',
            r'cashier', r'register', r'transaction', r'card', r'change', r'amount', r'payment',
            r'store', r'location', r'phone', r'website', r'email', r'address', r'city', r'state',
            r'zip', r'postal', r'code', r'number', r'reference', r'id', r'customer', r'member',
            r'points', r'rewards', r'coupon', r'discount', r'sale', r'clearance', r'return',
            r'exchange', r'refund', r'void', r'cancelled', r'voided', r'deleted', r'correction'
        ]

    def preprocess_image(self, image_path: str, save_processed: bool = False) -> Image.Image:
        """Preprocess the image for better OCR results"""
        # Load image
        if isinstance(image_path, str):
            image = Image.open(image_path)
        else:
            image = image_path
            
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array for OpenCV processing
        img_array = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply minimal Gaussian blur to reduce noise (reduced from 5x5 to 3x3)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Try different thresholding methods for better character recognition
        # Method 1: Adaptive threshold (often better for varying lighting)
        try:
            thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        except:
            # Fallback to Otsu's method if adaptive fails
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Apply minimal morphological operations to clean up without thickening
        # Use smaller kernel and opening operation to remove noise without thickening
        kernel = np.ones((1, 1), np.uint8)
        
        # Opening operation (erosion followed by dilation) to remove small noise
        opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # Optional: Apply slight erosion to thin characters if they're still too thick
        # kernel_erode = np.ones((1, 1), np.uint8)
        # thinned = cv2.erode(opened, kernel_erode, iterations=1)
        
        # Convert back to PIL Image
        processed_image = Image.fromarray(opened)
        
        # Enhance contrast moderately (reduced from 2.0 to 1.5)
        enhancer = ImageEnhance.Contrast(processed_image)
        processed_image = enhancer.enhance(1.5)
        
        # Additional sharpening to make characters clearer
        enhancer_sharp = ImageEnhance.Sharpness(processed_image)
        processed_image = enhancer_sharp.enhance(1.2)
        
        # Save processed image if requested
        if save_processed:
            try:
                # Create processed_images directory if it doesn't exist
                os.makedirs('processed_images', exist_ok=True)
                
                # Generate filename based on original image
                if isinstance(image_path, str):
                    base_name = os.path.splitext(os.path.basename(image_path))[0]
                else:
                    base_name = "processed"
                
                processed_path = f"processed_images/{base_name}_processed.png"
                processed_image.save(processed_path)
                print(f"Preprocessed image saved to: {processed_path}")
                
                # Also save intermediate steps for debugging
                gray_pil = Image.fromarray(gray)
                gray_pil.save(f"processed_images/{base_name}_gray.png")
                print(f"Grayscale image saved to: processed_images/{base_name}_gray.png")
                
                thresh_pil = Image.fromarray(thresh)
                thresh_pil.save(f"processed_images/{base_name}_threshold.png")
                print(f"Threshold image saved to: processed_images/{base_name}_threshold.png")
                
                opened_pil = Image.fromarray(opened)
                opened_pil.save(f"processed_images/{base_name}_opened.png")
                print(f"Opened image saved to: processed_images/{base_name}_opened.png")
                
            except Exception as e:
                print(f"Warning: Could not save processed image: {e}")
        
        return processed_image

    def preprocess_image_alternative(self, image_path: str, save_processed: bool = False) -> Image.Image:
        """Alternative preprocessing method for thinner characters"""
        # Load image
        if isinstance(image_path, str):
            image = Image.open(image_path)
        else:
            image = image_path
            
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array for OpenCV processing
        img_array = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply very minimal blur
        blurred = cv2.GaussianBlur(gray, (1, 1), 0)
        
        # Use simple binary threshold with higher threshold value for thinner characters
        _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
        
        # Apply erosion to thin characters
        kernel_erode = np.ones((1, 1), np.uint8)
        eroded = cv2.erode(thresh, kernel_erode, iterations=1)
        
        # Convert back to PIL Image
        processed_image = Image.fromarray(eroded)
        
        # Enhance contrast slightly
        enhancer = ImageEnhance.Contrast(processed_image)
        processed_image = enhancer.enhance(1.3)
        
        # Save processed image if requested
        if save_processed:
            try:
                os.makedirs('processed_images', exist_ok=True)
                
                if isinstance(image_path, str):
                    base_name = os.path.splitext(os.path.basename(image_path))[0]
                else:
                    base_name = "processed"
                
                processed_path = f"processed_images/{base_name}_alternative.png"
                processed_image.save(processed_path)
                print(f"Alternative preprocessed image saved to: {processed_path}")
                
            except Exception as e:
                print(f"Warning: Could not save alternative processed image: {e}")
        
        return processed_image

    def extract_text(self, image_path: str, save_processed: bool = False, use_alternative: bool = False) -> str:
        """Extract text from image using OCR"""
        try:
            # Preprocess the image
            if use_alternative:
                processed_image = self.preprocess_image_alternative(image_path, save_processed=save_processed)
            else:
                processed_image = self.preprocess_image(image_path, save_processed=save_processed)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(processed_image, config='--psm 6')
            
            return text.strip()
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""

    def identify_store(self, text: str) -> str:
        """Identify the store name from the receipt text"""
        lines = text.split('\n')
        
        # Check first 15 lines for store names (increased from 10)
        for line in lines[:15]:
            line_upper = line.upper().strip()
            
            # Check against known store patterns
            for store_name, patterns in self.store_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line_upper, re.IGNORECASE):
                        return store_name
            
            # Check for common store indicators
            if any(indicator in line_upper for indicator in ['STORE', 'MARKET', 'SUPERMARKET', 'GROCERY', 'PHARMACY', 'RETAIL']):
                return line.strip()
        
        # Fallback: return first non-empty line that looks like a store name
        for line in lines[:8]:  # Increased from 5
            line = line.strip()
            if line and len(line) > 2 and len(line) < 60:  # Increased max length
                # Avoid lines that are likely not store names
                if not any(re.search(pattern, line.upper(), re.IGNORECASE) for pattern in self.skip_patterns):
                    # Check if line contains typical store name characteristics
                    if any(char.isalpha() for char in line) and not line.isdigit():
                        return line
        
        return "Unknown Store"

    def extract_date(self, text: str) -> Optional[str]:
        """Extract date from receipt text"""
        lines = text.split('\n')
        
        for line in lines:
            for pattern in self.date_patterns:
                match = re.search(pattern, line)
                if match:
                    groups = match.groups()
                    if len(groups) == 3:
                        # Handle different date formats
                        if len(groups[2]) == 2:  # YY format
                            year = '20' + groups[2] if int(groups[2]) < 50 else '19' + groups[2]
                        else:
                            year = groups[2]
                        
                        # Assume MM/DD/YYYY format
                        month, day = groups[0], groups[1]
                        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return None

    def extract_total(self, text: str) -> float:
        """Extract total amount from receipt text"""
        lines = text.split('\n')
        
        # Look for total patterns in the last 15 lines (increased from 10)
        for line in reversed(lines[-15:]):
            for pattern in self.total_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    try:
                        return float(match.group(1))
                    except ValueError:
                        continue
        
        # Fallback: look for the largest price in the last few lines
        prices = []
        for line in lines[-8:]:  # Increased from 5
            for pattern in self.price_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    try:
                        # Handle different price formats
                        if '.' in match:
                            price = float(match)
                        else:
                            if len(match) <= 2:
                                price = float(match) / 100
                            else:
                                price = float(match)
                        prices.append(price)
                    except ValueError:
                        continue
        
        # Filter out unreasonable prices (likely not totals)
        reasonable_prices = [p for p in prices if 0.01 <= p <= 10000]
        
        return max(reasonable_prices) if reasonable_prices else 0.0

    def extract_tax(self, text: str) -> float:
        """Extract tax amount from receipt text"""
        lines = text.split('\n')
        
        for line in lines:
            for pattern in self.tax_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    try:
                        tax_amount = float(match.group(1))
                        # Validate tax amount (should be reasonable)
                        if 0.01 <= tax_amount <= 1000:
                            return tax_amount
                    except ValueError:
                        continue
        
        return 0.0

    def categorize_product(self, product_name: str) -> str:
        """Categorize a product based on its name"""
        product_lower = product_name.lower()
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in product_lower:
                    return category
        
        return "Other"

    def extract_quantity(self, line: str) -> Tuple[int, str]:
        """Extract quantity from a line and return remaining text"""
        for pattern in self.quantity_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                quantity = int(match.group(1))
                # Remove quantity part from line
                cleaned_line = re.sub(pattern, '', line, flags=re.IGNORECASE).strip()
                return quantity, cleaned_line
        
        return 1, line

    def extract_products(self, text: str) -> List[Product]:
        """Extract product information from receipt text"""
        products = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines that are likely not products using enhanced patterns
            line_upper = line.upper()
            if any(re.search(pattern, line_upper, re.IGNORECASE) for pattern in self.skip_patterns):
                continue
            
            # Skip very short lines (likely not products)
            if len(line) < 3:
                continue
            
            # Skip lines that are mostly numbers or special characters
            if sum(c.isdigit() for c in line) > len(line) * 0.7:
                continue
            
            # Look for price patterns with enhanced matching
            price_matches = []
            for pattern in self.price_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    try:
                        # Handle different price formats
                        if '.' in match:
                            price = float(match)
                        else:
                            # If no decimal, assume it's cents or dollars
                            if len(match) <= 2:  # Likely cents
                                price = float(match) / 100
                            else:  # Likely dollars
                                price = float(match)
                        price_matches.append(price)
                    except ValueError:
                        continue
            
            if not price_matches:
                continue
            
            # Extract quantity and clean line
            quantity, cleaned_line = self.extract_quantity(line)
            
            # Remove price from line to get product name - enhanced pattern matching
            product_line = cleaned_line
            
            # Remove various price patterns from the product name
            price_removal_patterns = [
                r'\$?\s*\d+\.\d{2}',      # $12.34 or 12.34
                r'\$?\s*\d+\.\d{1}',      # $12.3 or 12.3
                r'\$?\s*\d+',             # $12 or 12
                r'\d+\.\d{2}',            # 12.34
                r'\d+\.\d{1}',            # 12.3
            ]
            
            for pattern in price_removal_patterns:
                product_line = re.sub(pattern, '', product_line)
            
            # Clean up the product name
            product_line = re.sub(r'\s+', ' ', product_line).strip()  # Remove extra spaces
            product_line = re.sub(r'^\s*[-*]\s*', '', product_line)   # Remove leading dashes/asterisks
            product_line = re.sub(r'\s*[-*]\s*$', '', product_line)   # Remove trailing dashes/asterisks
            
            if not product_line or len(product_line) < 2:
                continue
            
            # Use the most appropriate price (usually the last one, but check for reasonableness)
            total_price = max(price_matches)
            
            # Validate price - if it seems too high for a single item, use a different approach
            if total_price > 100 and len(price_matches) > 1:
                # Try to find a more reasonable price
                reasonable_prices = [p for p in price_matches if p < 50]
                if reasonable_prices:
                    total_price = max(reasonable_prices)
            
            # Calculate unit price
            unit_price = total_price / quantity if quantity > 0 else total_price
            
            # Categorize product
            category = self.categorize_product(product_line)
            
            # Create product object
            product = Product(
                name=product_line,
                quantity=quantity,
                unit_price=round(unit_price, 2),
                total_price=round(total_price, 2),
                category=category
            )
            
            products.append(product)
        
        return products

    def process_receipt(self, image_path: str, save_processed: bool = False, use_alternative: bool = False) -> ReceiptData:
        """Process a receipt image and extract all information"""
        # Extract text from image
        text = self.extract_text(image_path, save_processed=save_processed, use_alternative=use_alternative)
        
        if not text:
            raise ValueError("No text could be extracted from the image")
        
        # Extract store name
        store_name = self.identify_store(text)
        
        # Extract date
        date = self.extract_date(text)
        
        # Extract total amount
        total_amount = self.extract_total(text)
        
        # Extract tax amount
        tax_amount = self.extract_tax(text)
        
        # Extract products
        products = self.extract_products(text)
        
        # Calculate subtotal
        subtotal = sum(product.total_price for product in products)
        
        # Create receipt data object
        receipt_data = ReceiptData(
            store_name=store_name,
            total_amount=round(total_amount, 2),
            subtotal=round(subtotal, 2),
            tax_amount=round(tax_amount, 2),
            date=date,
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
    parser.add_argument('--save-processed', action='store_true', help='Save preprocessed images for debugging')
    parser.add_argument('--alternative', action='store_true', help='Use alternative preprocessing for thinner characters')
    
    args = parser.parse_args()
    
    # Check if image file exists
    if not os.path.exists(args.image_path):
        print(f"Error: Image file '{args.image_path}' not found")
        sys.exit(1)
    
    try:
        # Initialize OCR processor
        ocr = ReceiptOCR()
        
        # Process receipt
        print(f"Processing receipt: {args.image_path}")
        receipt_data = ocr.process_receipt(args.image_path, save_processed=args.save_processed, use_alternative=args.alternative)
        
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
                print(f"Date: {receipt_data.date or 'Unknown'}")
                print(f"Total: ${receipt_data.total_amount:.2f}")
                print(f"Subtotal: ${receipt_data.subtotal:.2f}")
                print(f"Tax: ${receipt_data.tax_amount:.2f}")
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
