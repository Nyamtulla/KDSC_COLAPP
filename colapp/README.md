# Cost of Living App (ColApp)

A Flutter application with Flask backend for managing cost of living data in Kansas. Features advanced OCR receipt processing with machine learning capabilities, spending analytics, and data visualization.

## Project Structure

```
colapp/
├── backend/          # Flask API server
│   ├── app.py       # Main Flask application with OCR
│   ├── ml_ocr_service.py # ML-based OCR service
│   ├── models.py    # Database models
│   ├── init_db.py   # Database initialization script
│   ├── requirements.txt # Python dependencies
│   ├── test_ml_ocr.py # ML OCR testing script
│   ├── env_example.txt # Environment variables template
│   ├── uploads/     # Receipt image storage
│   └── venv/        # Python virtual environment
├── frontend/        # Flutter application
│   ├── lib/
│   │   ├── screens/     # UI screens
│   │   └── services/    # API services
│   └── pubspec.yaml     # Flutter dependencies
└── ML_OCR_SETUP.md     # Detailed ML OCR setup guide
```

## Features

### 🔐 Authentication
- User registration and login
- JWT-based authentication
- Secure password hashing

### 📸 Advanced Receipt Processing
- **Multiple OCR Methods**: Choose from heuristic, Google Cloud Vision, OpenAI GPT-4 Vision, Azure Form Recognizer, or hybrid approaches
- **Machine Learning**: AI-powered receipt parsing for better accuracy
- **Configurable Parsing**: Users can select their preferred parsing method
- Image upload from camera or gallery
- Image cropping and optimization
- Store name, total amount, and item detection with ML-enhanced categorization

### ✏️ Data Management
- Edit and verify extracted receipt data
- Categorize items (Dairy, Bakery, Produce, etc.)
- Add/remove items from receipts
- Update store names and totals

### 📊 Analytics Dashboard
- Total spending overview
- Category breakdown with progress bars
- Monthly spending trends
- Recent receipts list
- Interactive charts and visualizations

## OCR Methods

The app now supports multiple OCR parsing methods:

| Method | Accuracy | Speed | Cost | Best For |
|--------|----------|-------|------|----------|
| **Heuristic** | Basic | Fast | Free | Simple receipts, offline use |
| **Google Cloud Vision** | Very Good | Medium | Paid | General purpose, good accuracy |
| **OpenAI GPT-4 Vision** | Excellent | Slow | Paid | Complex receipts, intelligent parsing |
| **Azure Form Recognizer** | Excellent | Medium | Paid | Receipt-specialized parsing |
| **Hybrid** | Best | Slow | Paid | Maximum accuracy, multiple APIs |
| **Auto** | Adaptive | Variable | Variable | Automatic method selection |

## Backend Setup

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Tesseract OCR (for legacy heuristic parsing)

### Install Tesseract OCR

**Windows:**
```bash
# Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH: C:\Program Files\Tesseract-OCR
```

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

### Installation

1. **Navigate to backend directory:**
   ```bash
   cd colapp/backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure ML OCR APIs (Optional):**
   ```bash
   # Copy environment template
   cp env_example.txt .env
   
   # Edit .env file and add your API keys:
   # - Google Cloud Vision API key
   # - OpenAI API key  
   # - Azure Form Recognizer credentials
   ```

5. **Set up PostgreSQL database:**
   - Create a database named `grocery_app_db`
   - Update the database URI in `app.py` if needed:
     ```python
     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/grocery_app_db'
     ```

6. **Initialize database:**
   ```bash
   python init_db.py
   ```

7. **Test ML OCR (Optional):**
   ```bash
   python test_ml_ocr.py
   ```

8. **Run the Flask server:**
   ```bash
   python app.py
   ```
   The server will start on `http://localhost:5000`

## Frontend Setup

### Prerequisites
- Flutter SDK
- Android Studio / VS Code with Flutter extension

### Installation

1. **Navigate to frontend directory:**
   ```bash
   cd colapp/frontend
   ```

2. **Get Flutter dependencies:**
   ```bash
   flutter pub get
   ```

3. **Run the Flutter app:**
   ```bash
   flutter run
   ```

## API Endpoints

### Authentication
- **POST /register** - Register a new user
- **POST /login** - Login user

### Receipt Management
- **POST /upload-receipt** - Upload receipt image with OCR processing
- **POST /api/ocr-receipt** - OCR processing with configurable parsing method
- **GET /receipts** - Get all user receipts
- **GET /receipt/{id}** - Get specific receipt
- **PUT /receipt/{id}** - Update receipt data
- **DELETE /receipt/{id}** - Delete receipt

### Analytics
- **GET /dashboard-stats** - Get spending analytics and statistics

## OCR API Usage

### Backend API
```bash
# Use specific parsing method
curl -X POST http://localhost:5000/api/ocr-receipt \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@receipt.jpg" \
  -F "parsing_method=google"
```

### Frontend
```dart
// Use specific parsing method
final result = await OcrService.extractReceiptData(
  imageFile: file,
  parsingMethod: 'google'
);
```

## Workflow

1. **User Registration/Login**
   - Register with personal information
   - Login with email and password

2. **OCR Method Selection**
   - Choose preferred parsing method in OCR Settings
   - Configure API keys for ML-based methods

3. **Receipt Upload**
   - Take photo or select from gallery
   - Crop image if needed
   - Upload to backend for OCR processing

4. **Advanced OCR Processing**
   - Backend uses selected ML method for text extraction
   - AI-powered parsing identifies store name, total amount, and items
   - Enhanced categorization using ML insights
   - Stores image and metadata in database

5. **Data Verification**
   - User reviews extracted data
   - Edits store name, total, and items
   - Categorizes items appropriately
   - Saves final data

6. **Analytics Dashboard**
   - View spending overview
   - Analyze spending by category
   - Track monthly trends
   - Review recent receipts

## Database Schema

### Users Table
- id, email, password_hash, first_name, last_name, age, sex, city, county, state, zip_code

### Receipts Table
- id, user_id, store_name, receipt_date, total_amount, image_path, ocr_processed, created_at, updated_at

### Receipt Items Table
- id, receipt_id, product_name, price, category, quantity, created_at

### Categories Table
- id, name, description, created_at

## ML OCR Configuration

### API Setup

**Google Cloud Vision:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Cloud Vision API
3. Create API key
4. Add to `.env`: `GOOGLE_CLOUD_API_KEY=your_key`

**OpenAI GPT-4 Vision:**
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Get API key
3. Add to `.env`: `OPENAI_API_KEY=your_key`

**Azure Form Recognizer:**
1. Go to [Azure Portal](https://portal.azure.com/)
2. Create Form Recognizer resource
3. Add to `.env`: `AZURE_FORM_RECOGNIZER_ENDPOINT=url` and `AZURE_FORM_RECOGNIZER_KEY=key`

### Cost Considerations

- **Google Cloud Vision**: First 1000 requests/month free, then $1.50/1000
- **OpenAI GPT-4 Vision**: ~$0.01-0.03 per 1K tokens
- **Azure Form Recognizer**: First 500 pages/month free, then $1.50/1000 pages

## Development Notes

- **OCR Engine**: Multiple engines supported (Tesseract, Google Vision, OpenAI, Azure)
- **Image Storage**: Receipt images stored in `uploads/` folder
- **Security**: JWT tokens for authentication, password hashing
- **CORS**: Enabled for cross-origin requests
- **Error Handling**: Comprehensive error handling with fallback to heuristic parsing
- **ML Integration**: Modular design allows easy addition of new OCR providers

## Troubleshooting

For detailed ML OCR setup and troubleshooting, see [ML_OCR_SETUP.md](ML_OCR_SETUP.md).

Common issues:
1. **API Key Errors**: Check environment variables and API key validity
2. **OCR Failures**: System automatically falls back to heuristic parsing
3. **Performance**: ML methods are slower but more accurate than heuristic 