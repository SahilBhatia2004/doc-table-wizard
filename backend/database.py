import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    """Create and return a database connection."""
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "pdf_tables"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        cursor_factory=RealDictCursor
    )


def init_db():
    """Initialize database tables."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create documents table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            is_scanned BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create extracted_tables table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS extracted_tables (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
            table_index INTEGER NOT NULL,
            table_name VARCHAR(255),
            headers JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create table_rows table for actual data
    cur.execute("""
        CREATE TABLE IF NOT EXISTS table_rows (
            id SERIAL PRIMARY KEY,
            table_id INTEGER REFERENCES extracted_tables(id) ON DELETE CASCADE,
            row_index INTEGER NOT NULL,
            row_data JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()


def insert_document(filename: str, is_scanned: bool = False) -> int:
    """Insert a document record and return its ID."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(
        "INSERT INTO documents (filename, is_scanned) VALUES (%s, %s) RETURNING id",
        (filename, is_scanned)
    )
    doc_id = cur.fetchone()["id"]
    
    conn.commit()
    cur.close()
    conn.close()
    
    return doc_id


def insert_table(document_id: int, table_index: int, table_name: str, headers: list) -> int:
    """Insert a table record and return its ID."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(
        """INSERT INTO extracted_tables (document_id, table_index, table_name, headers) 
           VALUES (%s, %s, %s, %s) RETURNING id""",
        (document_id, table_index, table_name, psycopg2.extras.Json(headers))
    )
    table_id = cur.fetchone()["id"]
    
    conn.commit()
    cur.close()
    conn.close()
    
    return table_id


def insert_rows(table_id: int, rows: list):
    """Insert multiple rows for a table."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    for idx, row_data in enumerate(rows):
        cur.execute(
            "INSERT INTO table_rows (table_id, row_index, row_data) VALUES (%s, %s, %s)",
            (table_id, idx, psycopg2.extras.Json(row_data))
        )
    
    conn.commit()
    cur.close()
    conn.close()


def get_all_documents():
    """Get all documents with their table counts."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT d.*, COUNT(et.id) as table_count
        FROM documents d
        LEFT JOIN extracted_tables et ON d.id = et.document_id
        GROUP BY d.id
        ORDER BY d.created_at DESC
    """)
    
    documents = cur.fetchall()
    cur.close()
    conn.close()
    
    return documents


def get_tables_for_document(document_id: int):
    """Get all tables for a specific document."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(
        "SELECT * FROM extracted_tables WHERE document_id = %s ORDER BY table_index",
        (document_id,)
    )
    
    tables = cur.fetchall()
    cur.close()
    conn.close()
    
    return tables


def get_rows_for_table(table_id: int):
    """Get all rows for a specific table."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(
        "SELECT * FROM table_rows WHERE table_id = %s ORDER BY row_index",
        (table_id,)
    )
    
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return rows
