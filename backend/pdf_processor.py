import os
import tempfile
from pathlib import Path
from typing import Tuple, List, Dict, Any

import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat


def is_scanned_pdf(pdf_path: str, sample_pages: int = 3) -> bool:
    """
    Check if a PDF is scanned (image-based) by analyzing text content.
    Returns True if the PDF appears to be scanned.
    """
    try:
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        
        # Get text content
        text = result.document.export_to_text()
        
        # If very little text is extracted, it's likely scanned
        if len(text.strip()) < 100:
            return True
        
        return False
    except Exception:
        # If docling fails, assume it's scanned
        return True


def perform_ocr(pdf_path: str) -> str:
    """
    Perform OCR on a scanned PDF and return path to the OCR'd PDF.
    """
    # Convert PDF to images
    images = convert_from_path(pdf_path)
    
    # Create a temporary directory for OCR output
    temp_dir = tempfile.mkdtemp()
    ocr_text_path = os.path.join(temp_dir, "ocr_output.txt")
    
    all_text = []
    
    for i, image in enumerate(images):
        # Perform OCR on each page
        text = pytesseract.image_to_string(image)
        all_text.append(f"--- Page {i + 1} ---\n{text}")
    
    # Save combined text
    with open(ocr_text_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_text))
    
    return ocr_text_path


def extract_tables_with_docling(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract tables from a PDF using Docling.
    Returns a list of tables with headers and rows.
    """
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    
    tables = []
    
    # Iterate through document elements to find tables
    for element_idx, element in enumerate(result.document.tables):
        table_data = {
            "index": element_idx,
            "name": f"Table_{element_idx + 1}",
            "headers": [],
            "rows": []
        }
        
        # Export table to pandas DataFrame for easier processing
        try:
            df = element.export_to_dataframe()
            
            # Get headers
            table_data["headers"] = df.columns.tolist()
            
            # Get rows
            for _, row in df.iterrows():
                row_dict = {}
                for col in df.columns:
                    row_dict[col] = str(row[col]) if row[col] is not None else ""
                table_data["rows"].append(row_dict)
            
        except Exception as e:
            # Fallback: try to extract as markdown and parse
            md_table = element.export_to_markdown()
            table_data["raw_markdown"] = md_table
            
            # Parse markdown table
            lines = md_table.strip().split("\n")
            if len(lines) >= 2:
                # First line is headers
                headers = [h.strip() for h in lines[0].split("|") if h.strip()]
                table_data["headers"] = headers
                
                # Skip separator line (line with dashes)
                for line in lines[2:]:
                    cells = [c.strip() for c in line.split("|") if c.strip()]
                    if cells:
                        row_dict = {}
                        for i, cell in enumerate(cells):
                            header = headers[i] if i < len(headers) else f"col_{i}"
                            row_dict[header] = cell
                        table_data["rows"].append(row_dict)
        
        tables.append(table_data)
    
    return tables


def process_pdf(pdf_path: str) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Main function to process a PDF.
    Returns (is_scanned, extracted_tables).
    """
    is_scanned = is_scanned_pdf(pdf_path)
    
    if is_scanned:
        # Perform OCR first
        print(f"PDF appears to be scanned. Performing OCR...")
        ocr_path = perform_ocr(pdf_path)
        print(f"OCR complete. Text saved to: {ocr_path}")
    
    # Extract tables using Docling
    print(f"Extracting tables using Docling...")
    tables = extract_tables_with_docling(pdf_path)
    print(f"Found {len(tables)} tables")
    
    return is_scanned, tables
