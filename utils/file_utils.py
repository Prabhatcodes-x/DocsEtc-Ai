import json
import pdfplumber
import logging  # Add logging
import os  # For directory creation

def load_json(file_path):
    """
    Load and return JSON data from the given file path.
    Logs errors if file not found or invalid JSON.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logging.info(f"Successfully loaded JSON from: {file_path}")
            return data
    except FileNotFoundError as e:
        logging.error(f"Error: {e}")
        raise  # Propagate error to the caller
    except json.JSONDecodeError as e:
        logging.error(f"Error: Could not decode JSON from {file_path}. Invalid JSON format: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred while loading JSON from {file_path}: {e}")
        raise

def load_text(file_path):
    """
    Load and return plain text content from a file.
    Logs errors if file not found.
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File does not exist: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            logging.info(f"Successfully loaded text from: {file_path}")
            return content
    except FileNotFoundError as e:
        logging.error(f"Error: {e}")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred while loading text from {file_path}: {e}")
        raise

def load_pdf_text(pdf_path):
    """
    Extract and return text content from a PDF file using pdfplumber.
    Logs errors if file not found or PDF extraction fails.
    """
    text = ''
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File does not exist: {pdf_path}")
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
        logging.info(f"Successfully extracted text from PDF: {pdf_path}")
        return text.strip()
    except FileNotFoundError as e:
        logging.error(f"Error: {e}")
        raise
    except Exception as e:  # Catch pdfplumber related errors
        logging.error(f"An error occurred while extracting text from PDF {pdf_path}: {e}")
        raise

# Optional: Add file write functions
def save_json(data, file_path):
    """Saves dictionary data to a JSON file."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Create directory
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logging.info(f"JSON data saved to {file_path}")
    except Exception as e:
        logging.error(f"Error saving JSON to {file_path}: {e}")
        raise

def save_text(text_content, file_path):
    """Saves string content to a text file."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Create directory
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        logging.info(f"Text content saved to {file_path}")
    except Exception as e:
        logging.error(f"Error saving text to {file_path}: {e}")
        raise
