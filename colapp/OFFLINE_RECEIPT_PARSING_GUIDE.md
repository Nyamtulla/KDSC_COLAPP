# Offline Receipt Parsing System Guide

A comprehensive guide for building a zero-cost, fully offline receipt parsing system using open-source tools and local LLMs.

## 🎯 Overview

This system provides **completely offline** receipt parsing with:
- **Zero API costs** - No cloud dependencies
- **High accuracy** - Multiple parsing methods with fallbacks
- **Privacy-first** - All processing happens locally
- **Robust handling** - Works with noisy OCR and various receipt formats

## 🏗️ Architecture

### Core Components

1. **OCR Service** (`ocr_service.py`)
   - Tesseract OCR for text extraction
   - EasyOCR for enhanced accuracy
   - PDF support (digital + scanned)
   - Image preprocessing for better results

2. **Offline LLM Service** (`offline_llm_service.py`)
   - Ollama integration for local LLM inference
   - Structured JSON output parsing
   - Intelligent receipt understanding

3. **Custom NLP Service** (`custom_nlp_service.py`)
   - Trained models for specific tasks
   - Store name classification
   - Item extraction and categorization
   - Total amount detection

4. **Enhanced Parser** (`enhanced_receipt_parser.py`)
   - Orchestrates all services
   - Automatic method selection
   - Robust error handling and fallbacks

## 🚀 Quick Start

### 1. Automated Setup

```bash
# Run the automated setup script
cd colapp/backend
python setup_offline_system.py
```

This script will:
- Install system dependencies (Tesseract, Poppler)
- Install Python packages
- Set up Ollama and download LLM models
- Create configuration files
- Test the complete system

### 2. Manual Setup

#### System Dependencies

**Windows:**
```bash
# Install Tesseract
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR

# Install Poppler (optional, for PDF support)
# Download from: https://blog.alivate.com.au/poppler-windows/
```

**macOS:**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install tesseract poppler
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils
```

#### Python Dependencies

```bash
cd colapp/backend
pip install -r requirements.txt
```

#### Install Ollama

```bash
# Unix-like systems
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.ai/download
```

#### Download LLM Model

```bash
# Start Ollama
ollama serve

# Download Llama 2 7B (recommended)
ollama pull llama2:7b

# Alternative models
ollama pull mistral:7b    # Faster, smaller
ollama pull llama2:13b    # More accurate, larger
```

## 📋 Usage

### Basic Usage

```python
from enhanced_receipt_parser import EnhancedReceiptParser

# Initialize parser
parser = EnhancedReceiptParser()

# Parse a receipt
result = parser.parse_receipt('path/to/receipt.jpg')

if result['success']:
    print(f"Store: {result['data']['store_name']}")
    print(f"Total: ${result['data']['total']}")
    print(f"Items: {len(result['data']['items'])}")
else:
    print(f"Error: {result['error']}")
```

### API Usage

```python
# Flask endpoint
@app.route('/parse-receipt', methods=['POST'])
def parse_receipt():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    method = request.form.get('method', 'auto')
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Parse receipt
    parser = EnhancedReceiptParser()
    result = parser.parse_receipt(filepath, method=method)
    
    # Clean up
    os.remove(filepath)
    
    return jsonify(result)
```

### Command Line Usage

```bash
# Test the system
python test_offline_system.py

# Parse a specific file
python -c "
from enhanced_receipt_parser import EnhancedReceiptParser
parser = EnhancedReceiptParser()
result = parser.parse_receipt('receipt.jpg')
print(result)
"
```

## 🔧 Configuration

### Configuration File (`offline_config.json`)

```json
{
  "ocr": {
    "engine": "auto",
    "tesseract_config": "--oem 3 --psm 6"
  },
  "llm": {
    "model": "llama2:7b",
    "host": "http://localhost:11434",
    "temperature": 0.1,
    "max_tokens": 2048
  },
  "custom_nlp": {
    "enabled": true,
    "confidence_threshold": 0.7
  },
  "file_processing": {
    "max_file_size": 10485760,
    "supported_formats": [".jpg", ".jpeg", ".png", ".pdf"],
    "temp_dir": "./temp"
  }
}
```

### Environment Variables

```bash
# Optional: Override default settings
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=llama2:7b
export OCR_ENGINE=auto
export CUSTOM_NLP_ENABLED=true
```

## 📊 Parsing Methods

### 1. LLM Parsing (Highest Accuracy)

**Pros:**
- Best understanding of receipt structure
- Handles complex layouts
- Intelligent categorization
- Robust to OCR errors

**Cons:**
- Requires more computational resources
- Slower processing
- Needs LLM model downloaded

**Usage:**
```python
result = parser.parse_receipt('receipt.jpg', method='llm')
```

### 2. Custom NLP Parsing (Good Accuracy)

**Pros:**
- Fast processing
- Trained on specific receipt types
- Good balance of speed/accuracy
- No external dependencies

**Cons:**
- Requires training data
- Less flexible than LLM
- May need retraining for new formats

**Usage:**
```python
result = parser.parse_receipt('receipt.jpg', method='custom_nlp')
```

### 3. OCR + Heuristics (Basic Accuracy)

**Pros:**
- Fastest processing
- No external dependencies
- Works with any receipt format
- Lightweight

**Cons:**
- Basic accuracy
- Limited understanding
- May miss complex items

**Usage:**
```python
result = parser.parse_receipt('receipt.jpg', method='ocr_only')
```

### 4. Auto Selection (Recommended)

Automatically chooses the best available method:

```python
result = parser.parse_receipt('receipt.jpg', method='auto')
# Priority: LLM > Custom NLP > OCR Only
```

## 🛠️ Advanced Features

### Custom Model Training

Train custom NLP models on your specific receipt types:

```python
from custom_nlp_service import CustomNLPService

# Prepare training data
training_data = {
    'store': [
        ['WALMART SUPERCENTER', 'Walmart'],
        ['TARGET STORE', 'Target']
    ],
    'item': [
        ['MILK 2% 1GAL', True],
        ['TOTAL', False]
    ],
    'category': [
        ['milk', 'Dairy'],
        ['apple', 'Produce']
    ]
}

# Train models
service = CustomNLPService()
service.train_store_classifier(training_data['store'])
service.train_item_extractor(training_data['item'])
service.train_category_classifier(training_data['category'])
```

### PDF Processing

The system supports both digital and scanned PDFs:

```python
# Digital PDF (text extraction)
result = parser.parse_receipt('receipt.pdf')

# Scanned PDF (OCR processing)
# Automatically detected and handled
```

### Image Preprocessing

Automatic image enhancement for better OCR:

- Noise reduction
- Adaptive thresholding
- Morphological operations
- Contrast enhancement

### Robust Error Handling

Multiple fallback mechanisms:

1. **Method Fallback**: LLM → Custom NLP → OCR Only
2. **Engine Fallback**: EasyOCR → Tesseract
3. **Model Fallback**: Primary model → Alternative models
4. **Graceful Degradation**: Partial results with confidence scores

## 📈 Performance Optimization

### Hardware Requirements

**Minimum:**
- 4GB RAM
- 2GB free disk space
- CPU: Any modern processor

**Recommended:**
- 8GB+ RAM
- 10GB+ free disk space
- GPU: NVIDIA GPU (for faster LLM inference)

### Optimization Tips

1. **Use appropriate LLM model:**
   ```bash
   # Fast processing
   ollama pull mistral:7b
   
   # Better accuracy
   ollama pull llama2:13b
   ```

2. **Batch processing:**
   ```python
   # Process multiple receipts efficiently
   receipts = ['receipt1.jpg', 'receipt2.jpg', 'receipt3.jpg']
   results = [parser.parse_receipt(r) for r in receipts]
   ```

3. **Caching:**
   ```python
   # Cache parsed results
   import hashlib
   import pickle
   
   def get_cached_result(file_path):
       file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
       cache_file = f"cache/{file_hash}.pkl"
       
       if os.path.exists(cache_file):
           with open(cache_file, 'rb') as f:
               return pickle.load(f)
       return None
   ```

## 🔍 Troubleshooting

### Common Issues

**1. Tesseract not found:**
```bash
# Windows: Add to PATH
# macOS: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr
```

**2. Ollama connection failed:**
```bash
# Start Ollama service
ollama serve

# Check if running
ollama list
```

**3. Model not found:**
```bash
# Download required model
ollama pull llama2:7b
```

**4. Memory issues:**
```bash
# Use smaller model
ollama pull mistral:7b

# Or use OCR-only parsing
result = parser.parse_receipt('receipt.jpg', method='ocr_only')
```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Test individual components
from ocr_service import OCRService
ocr = OCRService()
result = ocr.extract_text('receipt.jpg')
print(result)
```

### Performance Monitoring

```python
import time

start_time = time.time()
result = parser.parse_receipt('receipt.jpg')
end_time = time.time()

print(f"Processing time: {end_time - start_time:.2f} seconds")
print(f"Method used: {result['method']}")
print(f"Confidence: {result.get('confidence', 'N/A')}")
```

## 📚 Examples

### Example Receipt Output

```json
{
  "success": true,
  "method": "llm",
  "data": {
    "store_name": "Walmart Supercenter",
    "date": "2024-01-15",
    "time": "14:30",
    "items": [
      {
        "name": "Milk 2% 1 Gallon",
        "quantity": 1,
        "unit_price": 3.99,
        "total_price": 3.99,
        "category": "Dairy"
      },
      {
        "name": "Bananas",
        "quantity": 2.5,
        "unit_price": 0.59,
        "total_price": 1.48,
        "category": "Produce"
      }
    ],
    "subtotal": 15.97,
    "tax": 1.28,
    "total": 17.25,
    "change": 2.75,
    "payment_method": "CASH"
  },
  "confidence": 0.85,
  "file_path": "receipt.jpg",
  "file_size": 245760,
  "file_type": ".jpg"
}
```

### Integration with Flask App

```python
# Add to your existing Flask app
from enhanced_receipt_parser import EnhancedReceiptParser

@app.route('/api/parse-receipt-offline', methods=['POST'])
@jwt_required()
def parse_receipt_offline():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        method = request.form.get('method', 'auto')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf'}
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Parse receipt
            parser = EnhancedReceiptParser()
            result = parser.parse_receipt(filepath, method=method)
            
            if result['success']:
                # Save to database
                receipt_data = result['data']
                receipt = Receipt(
                    user_id=get_jwt_identity(),
                    store_name=receipt_data['store_name'],
                    receipt_date=receipt_data.get('date'),
                    total_amount=receipt_data['total'],
                    image_path=filename,
                    ocr_processed=True
                )
                db.session.add(receipt)
                db.session.commit()
                
                # Add items
                for item_data in receipt_data.get('items', []):
                    item = ReceiptItem(
                        receipt_id=receipt.id,
                        product_name=item_data['name'],
                        price=item_data['total_price'],
                        category=item_data.get('category', 'Other'),
                        quantity=item_data.get('quantity', 1.0)
                    )
                    db.session.add(item)
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'receipt_id': receipt.id,
                    'parsed_data': receipt_data,
                    'method': result['method'],
                    'confidence': result.get('confidence', 0.0)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Parsing failed')
                }), 400
                
        finally:
            # Clean up temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## 🤝 Contributing

### Adding New OCR Engines

```python
# Add to ocr_service.py
def _extract_with_new_engine(self, image: np.ndarray) -> Dict[str, Any]:
    """Extract text using new OCR engine"""
    try:
        # Your implementation here
        text = new_engine.extract_text(image)
        
        return {
            'success': True,
            'text': text,
            'method': 'new_engine',
            'engine': 'new_engine'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'text': ''
        }
```

### Adding New LLM Models

```python
# Add to offline_llm_service.py
def __init__(self, model_name: str = "llama2:7b", host: str = "http://localhost:11434"):
    # Add new model support
    if model_name == "new_model":
        self.model_name = "new_model:latest"
    else:
        self.model_name = model_name
```

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the test results: `python test_offline_system.py`
3. Check system requirements and dependencies
4. Enable debug logging for detailed error messages

---

**Happy parsing! 🧾✨** 