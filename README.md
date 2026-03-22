# `THIS IS A "VIBE-CODED" PROJECT THROWN TOGETHER VERY QUICKLY. DO NOT EXPECT THE DOCS TO BE ACCURATE.`

# Sikh Temple Membership Processing System
A web-based application to process handwritten membership forms using OCR (Optical Character Recognition) with human validation. The system helps digitize hundreds of scanned forms efficiently while maintaining data accuracy through a human-in-the-loop validation workflow.

## Features

- **Upload Forms**: Support for PDF and image files (JPG, PNG, TIFF)
- **OCR Processing**: Google Cloud Vision API for handwriting recognition
- **Human Validation**: Side-by-side image viewer and editable form for corrections
- **Duplicate Detection**: Fuzzy matching to prevent duplicate member entries
- **Member Management**: Search, filter, and manage member records
- **Export**: Export member data to Excel/CSV formats
- **SQLite Database**: Simple, file-based database with no server required

## Technology Stack

### Backend
- Python 3.10+
- Flask (Web framework)
- SQLAlchemy (ORM)
- Google Cloud Vision API (OCR)
- pandas (Excel/CSV export)
- fuzzywuzzy (Duplicate detection)

### Frontend
- Vue.js 3 (Frontend framework)
- PrimeVue (UI components)
- Vite (Build tool)
- Axios (HTTP client)

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.10 or higher**
   ```bash
   python3 --version
   ```

2. **Node.js 18 or higher**
   ```bash
   node --version
   npm --version
   ```

3. **poppler-utils** (for PDF processing)
   ```bash
   # Ubuntu/Debian
   sudo apt-get install poppler-utils

   # macOS
   brew install poppler
   ```

4. **Google Cloud Vision API Authentication**
   - Install gcloud CLI: https://cloud.google.com/sdk/docs/install
   - Authenticate with Application Default Credentials (recommended)
   - **See: [GCLOUD_AUTH_SETUP.md](./GCLOUD_AUTH_SETUP.md) for detailed setup instructions**
   - Alternative: Service account key (if your organization allows)
     - See: [VISION_API_SETUP_SERVICE_ACCOUNT.md](./VISION_API_SETUP_SERVICE_ACCOUNT.md)

## Installation

### 1. Clone or Navigate to Project Directory

```bash
cd /home/sanjotbains/Documents/sikh_temple_membership
```

### 2. Backend Setup

```bash
# Create a virtual environment
cd backend
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install
```

### 4. Configuration

#### Backend Configuration

```bash
# Copy the example environment file
cd ../backend
cp .env.example .env

# Edit .env and set your configuration
nano .env  # or use your preferred editor
```

**Important settings in `.env`:**
- `GOOGLE_APPLICATION_CREDENTIALS`: Leave commented out to use Application Default Credentials (recommended)
  - Or set to path of service account JSON key file if using that method
- `SECRET_KEY`: Change to a random secret key for production
- `UPLOAD_FOLDER`: Directory for uploaded files (default: ./data/uploads)

#### Google Cloud Authentication Setup

**Recommended: Use Application Default Credentials**
```bash
# Install gcloud CLI and authenticate
gcloud auth application-default login
```

**See [GCLOUD_AUTH_SETUP.md](./GCLOUD_AUTH_SETUP.md) for complete instructions**

#### Create Environment File

Create a `.env` file in the `backend` directory. For ADC (recommended), leave `GOOGLE_APPLICATION_CREDENTIALS` commented:
```
# GOOGLE_APPLICATION_CREDENTIALS=
SECRET_KEY=your-random-secret-key-here
```

### 5. Initialize Database

```bash
# Make sure you're in the backend directory with venv activated
cd backend
source venv/bin/activate

# Run the database initialization script
python3 scripts/init_database.py
```

This will create the SQLite database at `backend/data/database.db` with all necessary tables.

## Running the Application

You need to run both the backend and frontend servers.

### Start Backend Server

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python app.py
```

The backend API will start on `http://localhost:5000`

### Start Frontend Server

```bash
# Terminal 2 - Frontend
cd frontend
npm run dev
```

The frontend will start on `http://localhost:5173`

### Access the Application

Open your browser and navigate to: **http://localhost:5173**

## Usage

### 1. Upload Forms
1. Navigate to "Upload Forms" in the sidebar
2. Drag and drop or select PDF/image files
3. Click upload to process the forms
4. OCR processing will begin automatically in the background

### 2. Validate Forms
1. Navigate to "Validate" in the sidebar
2. Select a pending submission from the list
3. Review the OCR-extracted data against the original form image
4. Correct any errors in the form fields
5. If duplicates are detected, resolve them (merge or create new)
6. Save to create the member record

### 3. Manage Members
1. Navigate to "Members" in the sidebar
2. Search and filter member records
3. View member details
4. Export selected members to Excel/CSV

### 4. Settings
1. Navigate to "Settings" in the sidebar
2. Configure API keys and system settings
3. Adjust duplicate detection thresholds

## Project Structure

```
sikh_temple_membership/
├── backend/
│   ├── app.py                    # Flask application entry point
│   ├── config.py                 # Configuration
│   ├── requirements.txt          # Python dependencies
│   ├── models/                   # Database models
│   ├── services/                 # Business logic
│   ├── routes/                   # API endpoints
│   ├── utils/                    # Utility functions
│   └── data/                     # Database and uploads
├── frontend/
│   ├── src/
│   │   ├── main.js              # Vue app entry
│   │   ├── App.vue              # Root component
│   │   ├── router.js            # Routes
│   │   ├── components/          # Vue components
│   │   ├── views/               # Page views
│   │   └── services/            # API services
│   ├── package.json
│   └── vite.config.js
├── scripts/
│   └── init_database.py         # Database initialization
└── README.md
```

## Development

### Database Management

```bash
# Initialize database (create all tables)
python scripts/init_database.py

# Drop all tables
python scripts/init_database.py drop

# Reset database (drop and recreate)
python scripts/init_database.py reset
```

### Code Formatting

```bash
# Backend (Python)
cd backend
black .
flake8 .

# Frontend (JavaScript)
cd frontend
npm run lint
```

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## Troubleshooting

### Backend won't start
- Ensure virtual environment is activated
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version: `python --version` (should be 3.10+)

### Frontend won't start
- Check Node.js version: `node --version` (should be 18+)
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

### OCR not working
- **First, run the test script**: `python backend/test_vision_api.py`
- If using Application Default Credentials (recommended):
  - Run: `gcloud auth application-default login`
  - Verify: `gcloud config get-value project`
  - Enable API: `gcloud services enable vision.googleapis.com`
- If using service account key:
  - Verify the key file path in `.env` is correct and absolute
  - Check that the file exists and is readable
- Ensure the Vision API is enabled in your Google Cloud project
- Check API quotas and billing in Google Cloud Console
- **See [GCLOUD_AUTH_SETUP.md](./GCLOUD_AUTH_SETUP.md) for detailed troubleshooting**

### PDF upload fails
- Ensure `poppler-utils` is installed
- Check file size is under the maximum (50MB default)
- Verify the PDF is not corrupted

## Next Steps

Now that Phase 1 (Foundation) is complete, the next phases are:

**Phase 2: Upload & OCR Implementation**
- Implement file upload service
- Google Vision API integration
- Field extraction from OCR results

**Phase 3: Validation UI**
- Build the validation editor with split-pane layout
- Image viewer with zoom/pan
- Form validation and correction

**Phase 4: Duplicate Detection**
- Fuzzy matching algorithm
- Duplicate resolution interface

**Phase 5: Member Management & Export**
- Search and filtering
- Excel/CSV export functionality

## Support

For issues or questions, please refer to the project documentation or contact the development team.

## License

Proprietary - Sikh Temple Membership System

---

**Note**: This is Phase 1 (Foundation) of the project. Core functionality (OCR processing, validation UI, duplicate detection) will be implemented in subsequent phases.
