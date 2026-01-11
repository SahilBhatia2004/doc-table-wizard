import os
import tempfile
import shutil
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import (
    init_db,
    insert_document,
    insert_table,
    insert_rows,
    get_all_documents,
    get_tables_for_document,
    get_rows_for_table,
)
from pdf_processor import process_pdf

app = FastAPI(
    title="PDF Table Extractor",
    description="Extract structured tables from PDFs using Docling",
    version="1.0.0"
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for responses
class TableRow(BaseModel):
    id: int
    row_index: int
    row_data: dict


class ExtractedTable(BaseModel):
    id: int
    document_id: int
    table_index: int
    table_name: str
    headers: List[str]


class Document(BaseModel):
    id: int
    filename: str
    is_scanned: bool
    table_count: int


class ExtractionResult(BaseModel):
    document_id: int
    filename: str
    is_scanned: bool
    tables_extracted: int
    tables: List[dict]


class HealthCheck(BaseModel):
    status: str
    database: str


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Failed to initialize database: {e}")


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Check API and database health."""
    try:
        from database import get_db_connection
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "healthy", "database": f"error: {str(e)}"}


@app.post("/extract", response_model=ExtractionResult)
async def extract_tables(file: UploadFile = File(...)):
    """
    Upload a PDF and extract tables from it.
    Automatically detects scanned PDFs and performs OCR if needed.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Save uploaded file temporarily
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process PDF
        is_scanned, tables = process_pdf(temp_path)
        
        # Insert document into database
        doc_id = insert_document(file.filename, is_scanned)
        
        # Insert tables and rows
        result_tables = []
        for table in tables:
            table_id = insert_table(
                document_id=doc_id,
                table_index=table["index"],
                table_name=table["name"],
                headers=table["headers"]
            )
            
            if table["rows"]:
                insert_rows(table_id, table["rows"])
            
            result_tables.append({
                "id": table_id,
                "name": table["name"],
                "headers": table["headers"],
                "row_count": len(table["rows"]),
                "preview_rows": table["rows"][:5]  # First 5 rows as preview
            })
        
        return ExtractionResult(
            document_id=doc_id,
            filename=file.filename,
            is_scanned=is_scanned,
            tables_extracted=len(tables),
            tables=result_tables
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temp files
        shutil.rmtree(temp_dir, ignore_errors=True)


@app.get("/documents", response_model=List[dict])
async def list_documents():
    """Get all processed documents."""
    documents = get_all_documents()
    return [dict(doc) for doc in documents]


@app.get("/documents/{document_id}/tables", response_model=List[dict])
async def get_document_tables(document_id: int):
    """Get all tables for a specific document."""
    tables = get_tables_for_document(document_id)
    return [dict(table) for table in tables]


@app.get("/tables/{table_id}/rows", response_model=List[dict])
async def get_table_rows(table_id: int):
    """Get all rows for a specific table."""
    rows = get_rows_for_table(table_id)
    return [dict(row) for row in rows]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
