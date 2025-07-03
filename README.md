# Cost of Living App (ColApp)

A Flutter application with Flask backend for managing cost of living data in Kansas. Features OCR receipt processing, spending analytics, and data visualization.

## Project Structure

```
colapp/
├── backend/          # Flask API server
│   ├── app.py       # Main Flask application with OCR
│   ├── models.py    # Database models
│   ├── init_db.py   # Database initialization script
│   ├── requirements.txt # Python dependencies
│   ├── uploads/     # Receipt image storage
│   └── venv/        # Python virtual environment
└── frontend/        # Flutter application
    ├── lib/
    │   ├── screens/     # UI screens
    │   └── services/    # API services
    └── pubspec.yaml     # Flutter dependencies
```

## Features

### 🔐 Authentication
- User registration and login
- JWT-based authentication
- Secure password hashing

### 📸 Receipt Processing
- Image upload from camera or gallery
- OCR (Optical Character Recognition) for automatic data extraction
- Image cropping and optimization
- Store name, total amount, and item detection

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

## Backend Setup

### Prerequisites
- Python 3.8+
- PostgreSQL database
- Tesseract OCR (for receipt text extraction)

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

4. **Set up PostgreSQL database:**
   - Create a database named `grocery_app_db`
   - Update the database URI in `app.py` if needed:
     ```python
     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/grocery_app_db'
     ```

5. **Initialize database:**
   ```bash
   python init_db.py
   ```

6. **Run the Flask server:**
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
- **GET /receipts** - Get all user receipts
- **GET /receipt/{id}** - Get specific receipt
- **PUT /receipt/{id}** - Update receipt data
- **DELETE /receipt/{id}** - Delete receipt

### Analytics
- **GET /dashboard-stats** - Get spending analytics and statistics

## Workflow

1. **User Registration/Login**
   - Register with personal information
   - Login with email and password

2. **Receipt Upload**
   - Take photo or select from gallery
   - Crop image if needed
   - Upload to backend for OCR processing

3. **OCR Processing**
   - Backend extracts text from image
   - Identifies store name, total amount, and items
   - Stores image and metadata in database

4. **Data Verification**
   - User reviews extracted data
   - Edits store name, total, and items
   - Categorizes items appropriately
   - Saves final data

5. **Analytics Dashboard**
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

## Development Notes

- **OCR Engine**: Uses Tesseract OCR for text extraction
- **Image Storage**: Receipt images stored in `uploads/` folder
- **Security**: JWT tokens for authentication, password hashing
- **CORS**: Enabled for cross-origin requests
- **Error Handling**: Comprehensive error handling and user feedback

## Troubleshooting

1. **OCR Issues:**
   - Ensure Tesseract is installed and in PATH
   - Check image quality and format
   - Verify OCR dependencies are installed

2. **Database Connection:**
   - Ensure PostgreSQL is running
   - Check database credentials in `app.py`
   - Verify database `grocery_app_db` exists

3. **Image Upload Issues:**
   - Check `uploads/` folder permissions
   - Verify file size limits
   - Ensure supported image formats

4. **Flutter Dependencies:**
   - Run `flutter pub get` to install dependencies
   - Check `pubspec.yaml` for correct package versions

5. **API Connection:**
   - Ensure Flask server is running on port 5000
   - Check CORS configuration if testing on web
   - Verify network connectivity between frontend and backend

## Testing the Application

1. **Start Backend:**
   ```bash
   cd colapp/backend
   python app.py
   ```

2. **Start Frontend:**
   ```bash
   cd colapp/frontend
   flutter run
   ```

3. **Test Flow:**
   - Register a new user
   - Login with credentials
   - Upload a receipt image
   - Verify and edit extracted data
   - View analytics dashboard

## Future Enhancements

- Advanced OCR with machine learning
- Receipt image enhancement
- Export data to CSV/PDF
- Budget tracking and alerts
- Receipt sharing and collaboration
- Mobile app optimization 