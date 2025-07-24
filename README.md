<<<<<<< HEAD
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
=======
# Colapp V3

## Getting Started (Dockerized Setup)

### 1. Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop) and Docker Compose installed
- (Optional) [Git](https://git-scm.com/) for cloning the repository

### 2. Clone the Repository
```sh
git clone https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 3. Build and Start All Services
```sh
docker-compose build
docker-compose up -d
```
- This will start the backend API, worker, Redis, Postgres, and Ollama containers.

### 4. Initialize the Database Schema
If your app does not auto-create tables, run:
```sh
docker-compose exec backend python init_db.py
```

### 5. Access the App
- **Backend API:** http://localhost:5000
- **Ollama (LLM):** http://localhost:11434
- **Postgres:** localhost:5432 (for DB tools)

### 6. Stopping the App
```sh
docker-compose down
```

### 7. Viewing Database Tables (Postgres)
#### Option 1: Using psql in Docker
```sh
docker-compose exec db bash
psql -U postgres -d grocery_app_db
```
- List tables: `\dt`
- View data: `SELECT * FROM receipts;`
- Exit: `\q`

#### Option 2: Using a GUI Tool
- Connect to `localhost:5432` with user `postgres`, password `colapp`, database `grocery_app_db`.

### 8. Cleaning Up Test/Invalid Receipts
To delete receipts with store name 'Processing...' or 'Unknown Store':
```sql
DELETE FROM receipt_items WHERE receipt_id IN (SELECT id FROM receipts WHERE store_name = 'Processing...' OR store_name = 'Unknown Store');
DELETE FROM receipts WHERE store_name = 'Processing...' OR store_name = 'Unknown Store';
```

### 9. Logs and Debugging
- View logs for a service:
  ```sh
  docker-compose logs backend
  docker-compose logs worker
  ```
- Watch all logs live:
  ```sh
  docker-compose logs -f
  ```

### 10. Frontend
- For development, run Flutter frontend natively:
  ```sh
  cd colapp/frontend
  flutter run -d chrome
  ```
- For production, see instructions to Dockerize the frontend.

---

## Notes
- Make sure to update environment variables and secrets for production.
- For deployment on a new server, repeat steps 1–6 above.

---

For further help, see the documentation or contact the maintainer. 
>>>>>>> v3-dockerized
