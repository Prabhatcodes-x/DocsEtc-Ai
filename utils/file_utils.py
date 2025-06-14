import json
import pdfplumber
import logging
import os
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

def validate_file_path(file_path: str) -> bool:
    """
    Check if the given path exists and is a valid file.
    """
    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return False
    if not os.path.isfile(file_path):
        logger.error(f"Path is not a file: {file_path}")
        return False
    logger.debug(f"File path validated: {file_path}")
    return True

def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    Return metadata for a given file path including size and modification timestamp.
    """
    info = {
        'exists': False,
        'size_bytes': None,
        'last_modified_timestamp': None,
        'last_modified_datetime': None
    }
    if os.path.exists(file_path) and os.path.isfile(file_path):
        info['exists'] = True
        info['size_bytes'] = os.path.getsize(file_path)
        last_mod_ts = os.path.getmtime(file_path)
        info['last_modified_timestamp'] = last_mod_ts
        info['last_modified_datetime'] = datetime.fromtimestamp(last_mod_ts).isoformat()
    return info

def load_json(file_path: str) -> Dict[str, Any]:
    """
    Load JSON content from a file and return it as a dictionary.
    """
    try:
        if not validate_file_path(file_path):
            raise FileNotFoundError(f"File does not exist or is not a file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Successfully loaded JSON from: {file_path}")
            return data
    except FileNotFoundError as e:
        logger.error(f"Error loading JSON: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format in {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while loading JSON from {file_path}: {e}")
        raise

def load_text(file_path: str) -> str:
    """
    Load and return plain text content from a file.
    """
    try:
        if not validate_file_path(file_path):
            raise FileNotFoundError(f"File does not exist or is not a file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            logger.info(f"Successfully loaded text from: {file_path}")
            return content
    except FileNotFoundError as e:
        logger.error(f"Error loading text: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while loading text from {file_path}: {e}")
        raise

def load_pdf_text(pdf_path: str) -> Optional[str]:
    """
    Extract and return text from a PDF file using pdfplumber.
    """
    text = ''
    try:
        if not validate_file_path(pdf_path):
            raise FileNotFoundError(f"PDF file does not exist or is not a file: {pdf_path}")
        
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) == 0:
                logger.warning(f"No pages found in PDF: {pdf_path}")
                return None
            
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num} ---\n" + page_text
            
        if not text.strip():
            logger.warning(f"No readable text extracted from PDF: {pdf_path}")
            return None

        logger.info(f"Successfully extracted text from PDF: {pdf_path}")
        return text.strip()
    except FileNotFoundError as e:
        logger.error(f"Error extracting PDF text: {e}")
        raise
    except Exception as e:
        logger.error(f"Error while extracting text from PDF {pdf_path}: {e}")
        raise

def save_json(data: Dict[str, Any], file_path: str):
    """
    Save dictionary data to a JSON file at the specified path.
    """
    try:
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logger.info(f"JSON data saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {e}")
        raise

def save_text(text_content: str, file_path: str):
    """
    Save string content to a text file at the specified path.
    """
    try:
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        logger.info(f"Text content saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving text to {file_path}: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

    test_dir = "test_output_files"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    print("\n--- Testing load_text and save_text ---")
    test_text_path = os.path.join(test_dir, "my_test_text.txt")
    sample_text = "Hello, this is a test text file.\nIt has multiple lines."
    save_text(sample_text, test_text_path)
    loaded_text = load_text(test_text_path)
    print(f"Loaded Text: \n{loaded_text}")
    assert loaded_text == sample_text

    print("\n--- Testing load_json and save_json ---")
    test_json_path = os.path.join(test_dir, "my_test_data.json")
    sample_json = {"name": "Test Item", "id": 123, "details": {"version": "1.0", "status": "active"}}
    save_json(sample_json, test_json_path)
    loaded_json = load_json(test_json_path)
    print(f"Loaded JSON: {loaded_json}")
    assert loaded_json == sample_json

    print("\n--- Testing load_pdf_text ---")
    dummy_pdf_path = os.path.join(test_dir, "dummy_test.pdf")
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(dummy_pdf_path, pagesize=letter)
        c.drawString(100, 750, "This is a dummy PDF for testing file_utils.")
        c.drawString(100, 730, "It contains some sample text on two pages.")
        c.showPage()
        c.drawString(100, 750, "Second page text.")
        c.save()
        print(f"Created dummy PDF for testing: {dummy_pdf_path}")
        pdf_text = load_pdf_text(dummy_pdf_path)
        print(f"Loaded PDF Text: \n{pdf_text[:100]}...")
        assert "dummy PDF" in pdf_text
    except ImportError:
        print("ReportLab not installed. Skipping dummy PDF creation and PDF text loading test.")
    except Exception as e:
        print(f"Error during PDF test: {e}")

    print("\n--- Testing non-existent file ---")
    try:
        load_text(os.path.join(test_dir, "non_existent.txt"))
    except FileNotFoundError:
        print("Caught expected FileNotFoundError for non-existent file.")
    
    print("\n--- Cleaning up test files ---")
    for f in os.listdir(test_dir):
        os.remove(os.path.join(test_dir, f))
    os.rmdir(test_dir)
    print("Test files and directory cleaned up.")
