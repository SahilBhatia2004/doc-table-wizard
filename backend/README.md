# PDF Table Extractor - Backend

FastAPI backend for extracting structured tables from PDFs using Docling.

## Setup

### 1. Prerequisites

- Python 3.9+
- PostgreSQL database
- Tesseract OCR (for scanned PDFs)
- Poppler (for pdf2image)

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

**macOS:**
```bash
brew install tesseract poppler
```

**Windows:**
- Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Download Poppler from: https://github.com/osber/pdf2image

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

### 5. Run the Server

```bash
python main.py
# Or with uvicorn:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/extract` | Upload PDF and extract tables |
| GET | `/documents` | List all processed documents |
| GET | `/documents/{id}/tables` | Get tables for a document |
| GET | `/tables/{id}/rows` | Get rows for a table |

## How It Works

1. **Upload PDF** → API receives the file
2. **Scan Detection** → Checks if PDF is image-based (scanned)
3. **OCR (if needed)** → Uses Tesseract to extract text from scanned PDFs
4. **Table Extraction** → Docling extracts structured tables
5. **Database Storage** → Tables stored in PostgreSQL with row-column format

## Database Schema

- `documents` - Uploaded PDF metadata
- `extracted_tables` - Table headers and metadata
- `table_rows` - Individual rows with JSONB data
