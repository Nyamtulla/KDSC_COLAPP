# Receipt OCR Script

A comprehensive Python script that extracts structured information from receipt images using OCR (Optical Character Recognition). The script identifies store names, total amounts, and detailed product information including quantities, costs, and categories.

## Features

- **Store Recognition**: Automatically identifies common store names (Walmart, Target, Kroger, etc.)
- **Product Extraction**: Extracts individual products with quantities, unit prices, and total prices
- **Smart Categorization**: Automatically categorizes products into logical categories (Dairy, Produce, Meat, etc.)
- **Date Extraction**: Identifies and parses receipt dates
- **Tax Detection**: Separates tax amounts from subtotals
- **Image Preprocessing**: Advanced image processing for better OCR accuracy
- **JSON Output**: Returns structured data in JSON format
- **Command Line Interface**: Easy-to-use CLI for batch processing

## Installation

### Prerequisites

1. **Python 3.7+**
2. **Tesseract OCR Engine**

### Install Tesseract OCR

#### Windows:
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location: `C:\Program Files\Tesseract-OCR\`
3. Add to PATH environment variable

#### macOS:
```bash
brew install tesseract
```

#### Ubuntu/Debian:
```bash
sudo apt-get install tesseract-ocr
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Usage

```bash
# Basic usage
python ocr.py path/to/receipt.jpg

# Save output to JSON file
python ocr.py path/to/receipt.jpg --output result.json

# Include raw OCR text in output
python ocr.py path/to/receipt.jpg --include-raw-text

# Pretty print JSON output
python ocr.py path/to/receipt.jpg --pretty

# Combine options
python ocr.py path/to/receipt.jpg --output result.json --pretty
```

### Programmatic Usage

```python
from ocr import ReceiptOCR

# Initialize OCR processor
ocr = ReceiptOCR()

# Process receipt image
receipt_data = ocr.process_receipt("path/to/receipt.jpg")

# Convert to JSON
json_output = ocr.to_json(receipt_data)

# Access individual fields
print(f"Store: {receipt_data.store_name}")
print(f"Total: ${receipt_data.total_amount}")
print(f"Items: {len(receipt_data.items)}")

# Access product details
for product in receipt_data.items:
    print(f"{product.name}: {product.quantity} x ${product.unit_price} = ${product.total_price}")
```

## Output Format

The script returns JSON data with the following structure:

```json
{
  "store_name": "Walmart",
  "total_amount": 45.67,
  "subtotal": 43.67,
  "tax_amount": 2.00,
  "date": "2024-01-15",
  "items": [
    {
      "name": "Milk 2%",
      "quantity": 1,
      "unit_price": 3.99,
      "total_price": 3.99,
      "category": "Dairy"
    },
    {
      "name": "Bread Whole Wheat",
      "quantity": 2,
      "unit_price": 2.49,
      "total_price": 4.98,
      "category": "Bakery"
    }
  ]
}
```

## Supported Store Recognition

The script recognizes common store names including:
- Walmart, Target, Kroger, Safeway, Costco
- Aldi, CVS, Walgreens, Home Depot, Lowes
- Best Buy, Starbucks, McDonalds, Subway
- Dollar General, Family Dollar, Dollar Tree

## Product Categories

Products are automatically categorized into:
- **Dairy**: Milk, cheese, yogurt, butter, etc.
- **Produce**: Fruits, vegetables, fresh produce
- **Meat**: Chicken, beef, pork, turkey, etc.
- **Bakery**: Bread, buns, cakes, cookies, etc.
- **Beverages**: Soda, juice, water, coffee, etc.
- **Frozen**: Frozen foods, ice cream, pizza
- **Canned Goods**: Canned soups, beans, vegetables
- **Snacks**: Chips, crackers, nuts, candy
- **Household**: Paper towels, cleaning supplies
- **Personal Care**: Toiletries, hygiene products
- **Baby**: Diapers, formula, baby food
- **Pet**: Pet food, treats, supplies
- **Pharmacy**: Medicine, prescriptions
- **Other**: Uncategorized items

## Image Requirements

For best results:
- **Format**: JPG, PNG, BMP, TIFF
- **Resolution**: At least 300 DPI
- **Quality**: Clear, well-lit images
- **Orientation**: Receipt should be straight and readable
- **Background**: High contrast (dark text on light background)

## Error Handling

The script includes robust error handling:
- Invalid image files
- OCR processing failures
- Missing or corrupted text
- Unrecognized store names
- Malformed price data

## Example Output

```
Receipt Summary:
Store: Walmart
Date: 2024-01-15
Total: $45.67
Subtotal: $43.67
Tax: $2.00
Items: 8

Products:
1. Milk 2%
   Quantity: 1
   Unit Price: $3.99
   Total Price: $3.99
   Category: Dairy

2. Bread Whole Wheat
   Quantity: 2
   Unit Price: $2.49
   Total Price: $4.98
   Category: Bakery

3. Bananas
   Quantity: 1
   Unit Price: $1.99
   Total Price: $1.99
   Category: Produce
```

## Troubleshooting

### Common Issues

1. **"Tesseract not found" error**
   - Ensure Tesseract is installed and in PATH
   - For Windows, verify installation at `C:\Program Files\Tesseract-OCR\`

2. **Poor OCR accuracy**
   - Use higher resolution images
   - Ensure good lighting and contrast
   - Clean the image before processing

3. **Missing products**
   - Check if receipt text is clear and readable
   - Verify price format matches expected patterns

4. **Incorrect store recognition**
   - Store name may not be in the recognized patterns
   - Check the raw OCR text for store name accuracy

### Performance Tips

- Use images with at least 300 DPI resolution
- Ensure good contrast between text and background
- Avoid blurry or skewed images
- Process images in good lighting conditions

## Dependencies

- `pytesseract`: Python wrapper for Tesseract OCR
- `Pillow`: Image processing library
- `opencv-python`: Computer vision library for image preprocessing
- `numpy`: Numerical computing library

## License

This script is provided as-is for educational and development purposes.

## Contributing

Feel free to submit issues and enhancement requests! 