import logging
import json
import os
from typing import Dict, Any, Optional
import pdfplumber
from datetime import datetime
import re

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

_file_utils_available = False
try:
    from utils.file_utils import validate_file_path, get_file_info
    _file_utils_available = True
    logger.info("File utility 'validate_file_path' and 'get_file_info' found and imported for PDFAgent.")
except ImportError:
    logger.warning("File utilities not found. PDF Agent will use built-in file operations.")


class PDFAgent:
    """
    The PDFAgent class is responsible for handling various operations related to PDF files, including:
    1.  **File Validation**: Ensuring the provided file exists, has a supported PDF extension,
        and is a valid PDF document structure.
    2.  **Text Extraction**: Extracting textual content from PDF pages.
    3.  **Text Preprocessing**: Cleaning and normalizing extracted text for further analysis
        (e.g., removing excess whitespace, truncating for LLM context windows).
    4.  **Metadata Extraction**: Retrieving intrinsic information about the PDF, such as page count,
        creation date, author, and title.
    5.  **Robust Error Handling**: Managing exceptions for file system issues, corrupted PDFs,
        and other processing failures.
    """

    def __init__(self):
        """
        Initializes the PDFAgent.
        Sets the agent's name and defines the supported file extensions.
        It also tracks the availability of external file utility functions.
        """
        self.agent_name = "PDF_Agent"
        self.supported_extensions = ['.pdf']
        self.file_utils_available = _file_utils_available

    def validate_pdf_file(self, file_path: str) -> bool:
        """
        Validates a given file path to ensure it points to an existing and valid PDF document.

        This method first checks for file existence and extension. If external file utilities
        are available, it leverages them for initial path validation. Finally, it attempts
        to open the PDF with `pdfplumber` to confirm its structural integrity.

        Args:
            file_path (str): The path to the PDF file to be validated.

        Returns:
            bool: True if the file is a valid and accessible PDF, False otherwise.
        """
        try:
            # Step 1: Use external file utilities for initial validation if available.
            if self.file_utils_available:
                if not validate_file_path(file_path):
                    logger.error(f"File validation failed (using file_utils): {file_path}")
                    return False
            else:
                # Fallback to built-in Python file existence check.
                if not os.path.exists(file_path):
                    logger.error(f"File not found: {file_path}")
                    return False

            # Step 2: Validate the file extension to ensure it's a PDF.
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in self.supported_extensions:
                logger.error(f"Unsupported file extension: '{ext}' for PDF processing in '{file_path}'")
                return False

            # Step 3: Attempt to open the PDF with pdfplumber to verify its integrity.
            # This implicitly checks for PDF syntax errors or corruption.
            with pdfplumber.open(file_path) as pdf:
                # Log a warning if the PDF contains no pages, but still consider it valid
                # as extraction will handle the absence of text.
                if len(pdf.pages) == 0:
                    logger.warning(f"PDF file '{file_path}' has no pages or appears empty.")
                    # An empty PDF is still technically a valid PDF, just without content.
                    pass

            logger.info(f"PDF validation successful: {file_path}")
            return True

        except pdfplumber.PDFSyntaxError as e:
            # Catch specific errors indicating a malformed or corrupted PDF.
            logger.error(f"PDF syntax error in '{file_path}': {e}. File might be corrupted or not a valid PDF.")
            return False
        except Exception as e:
            # Catch any other unexpected errors during validation.
            logger.error(f"PDF validation failed for '{file_path}': {str(e)}")
            return False

    def extract_text_from_pdf(self, file_path: str) -> Optional[str]:
        """
        Extracts all textual content from a PDF file, page by page.

        Each page's text is appended to a collective string, with page markers
        inserted for potential later processing or debugging.

        Args:
            file_path (str): The path to the PDF file from which to extract text.

        Returns:
            Optional[str]: The concatenated text extracted from all pages,
                           or None if no text could be extracted or the PDF is empty.
        """
        extracted_text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                if len(pdf.pages) == 0:
                    logger.warning(f"No pages found in PDF: {file_path}. No text to extract.")
                    return None

                logger.info(f"Processing PDF with {len(pdf.pages)} pages")

                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()

                    if page_text:
                        # Include page markers for structural awareness in the extracted text.
                        extracted_text += f"\n--- Page {page_num} ---\n"
                        extracted_text += page_text
                        logger.debug(f"Extracted text from page {page_num}")
                    else:
                        logger.warning(f"No text found on page {page_num} of {file_path}")

            # Return None if, after processing all pages, no significant text was found.
            if not extracted_text.strip():
                logger.warning(f"No significant text content extracted from PDF: {file_path}")
                return None

            logger.info(f"Successfully extracted {len(extracted_text)} characters from {file_path}")
            return extracted_text.strip()

        except Exception as e:
            # Catch and log any errors occurring during the text extraction process.
            logger.error(f"Text extraction failed for '{file_path}': {str(e)}")
            return None

    def preprocess_text(self, text: str) -> str:
        """
        Performs basic preprocessing on the extracted text to normalize it.
        This includes removing excessive whitespace, stripping custom page markers,
        and truncating the text if it exceeds a specified maximum length.

        Args:
            text (str): The raw text extracted from the PDF.

        Returns:
            str: The preprocessed and potentially truncated text.
        """
        try:
            # Normalize whitespace: replace multiple spaces/newlines with a single space.
            processed_text = ' '.join(text.split())

            # Remove custom page markers added during the extraction phase.
            processed_text = re.sub(r'--- Page \d+ ---', '', processed_text).strip()

            # Define a maximum length for the text, useful for LLM context windows.
            max_length = 4000
            if len(processed_text) > max_length:
                processed_text = processed_text[:max_length] + "..."
                logger.info(f"Text truncated to {max_length} characters for processing")

            return processed_text

        except Exception as e:
            # Log errors during preprocessing and return the original text as a fallback.
            logger.error(f"Text preprocessing failed: {str(e)}")
            return text

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extracts various metadata fields from a PDF file using `pdfplumber` and OS file system.

        Args:
            file_path (str): The path to the PDF file.

        Returns:
            Dict[str, Any]: A dictionary containing extracted metadata such as file size,
                            page count, creation date, author, and title.
        """
        metadata = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'file_size': None,
            'pages_count': 0,
            'creation_date': None,
            'author': None,
            'title': None
        }

        try:
            # Retrieve file size using OS utilities.
            if os.path.exists(file_path):
                metadata['file_size'] = os.path.getsize(file_path)
            else:
                logger.warning(f"File not found when trying to get size for metadata: {file_path}")

            with pdfplumber.open(file_path) as pdf:
                metadata['pages_count'] = len(pdf.pages)

                # Extract standard PDF metadata fields.
                if pdf.metadata:
                    # Access metadata using common key variations (e.g., 'CreationDate' or 'creationdate').
                    metadata['creation_date'] = pdf.metadata.get('CreationDate') or pdf.metadata.get('creationdate')
                    metadata['author'] = pdf.metadata.get('Author') or pdf.metadata.get('author')
                    metadata['title'] = pdf.metadata.get('Title') or pdf.metadata.get('title')

        except Exception as e:
            # Log any errors encountered during metadata extraction.
            logger.error(f"Metadata extraction failed for '{file_path}': {str(e)}")

        return metadata

    def process_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        The main orchestration method for processing a PDF file.

        This method integrates all the functionalities of the PDFAgent:
        validation, text extraction, text preprocessing, and metadata extraction.
        It provides a structured result indicating success or failure and includes
        all extracted information.

        Args:
            file_path (str): The path to the PDF file to be processed.

        Returns:
            Dict[str, Any]: A comprehensive dictionary containing the results of the PDF processing,
                            including extracted text, metadata, and error details if any.
        """
        result = {
            'success': False,
            'agent': self.agent_name,
            'timestamp': datetime.now().isoformat(),
            'file_path': file_path,
            'extracted_text': None,
            'metadata': None,
            'error_message': None
        }

        try:
            logger.info(f"Starting PDF processing: {file_path}")

            # Step 1: Validate the PDF file before proceeding.
            if not self.validate_pdf_file(file_path):
                # If validation fails, an error message would have been logged by validate_pdf_file.
                result['error_message'] = result.get('error_message', "PDF validation failed for unknown reason.")
                return result

            # Step 2: Extract raw text content from the PDF.
            raw_text = self.extract_text_from_pdf(file_path)
            if raw_text is None:
                # If no text is extracted (e.g., image-only PDF), still attempt metadata extraction
                # as it might be relevant even without textual content.
                result['error_message'] = "Text extraction failed or no readable text found in PDF."
                result['metadata'] = self.extract_metadata(file_path)
                return result

            # Step 3: Preprocess the extracted raw text for normalization.
            processed_text = self.preprocess_text(raw_text)

            # Step 4: Extract metadata from the PDF.
            metadata = self.extract_metadata(file_path)

            # Mark the process as successful and populate the result dictionary.
            result.update({
                'success': True,
                'extracted_text': processed_text,
                'metadata': metadata,
                'text_length': len(processed_text)
            })

            logger.info(f"PDF processing completed successfully: {file_path}")
            return result

        except Exception as e:
            # Catch any unexpected errors during the overall PDF processing workflow.
            logger.error(f"An unexpected error occurred during PDF processing for '{file_path}': {str(e)}")
            result['error_message'] = str(e)
            return result

if __name__ == "__main__":
    # Configure basic logging to output informational messages to the console
    # when this script is run directly. This is useful for testing and debugging.
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

    pdf_agent = PDFAgent()

    # Create a 'sample_inputs' directory if it doesn't already exist.
    # This directory will store test PDF files.
    if not os.path.exists('sample_inputs'):
        os.makedirs('sample_inputs')

    # Define paths for test PDF files.
    sample_pdf_path = "sample_inputs/sample_invoice.pdf"
    dummy_pdf_path = "sample_inputs/test_dummy_pdf.pdf"

    # Attempt to create a dummy PDF if 'sample_invoice.pdf' is not found.
    # This ensures that tests can run even without a pre-existing sample.
    if not os.path.exists(sample_pdf_path):
        try:
            # Use ReportLab to generate a simple PDF for testing purposes.
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(dummy_pdf_path, pagesize=letter)
            c.drawString(100, 750, "This is a test PDF document.")
            c.drawString(100, 730, "It contains some sample text.")
            c.showPage() # Start a new page
            c.drawString(100, 750, "This is the second page.")
            c.save()
            logger.info(f"Created dummy PDF for testing: {dummy_pdf_path}")
            sample_pdf_to_test = dummy_pdf_path
        except ImportError:
            # Inform the user if ReportLab is not installed, advising manual PDF creation.
            logger.warning("ReportLab not installed. Cannot create dummy PDF. Please ensure 'sample_inputs/sample_invoice.pdf' exists manually for testing.")
            sample_pdf_to_test = sample_pdf_path
    else:
        # If 'sample_invoice.pdf' exists, use it for testing.
        sample_pdf_to_test = sample_pdf_path

    # --- Test Case 1: Processing an existing PDF file ---
    print("\n--- Testing with an existing PDF file ---")
    if os.path.exists(sample_pdf_to_test):
        result = pdf_agent.process_pdf(sample_pdf_to_test)

        if result['success']:
            print("PDF Processing Successful!")
            print(f"Text Length: {result['text_length']}")
            print(f"Pages: {result['metadata'].get('pages_count', 'N/A')}")
            print(f"Preview (first 200 chars): {result['extracted_text'][:200]}...")
            print(f"Metadata: {json.dumps(result['metadata'], indent=2)}")
        else:
            print(f"PDF Processing Failed: {result['error_message']}")
    else:
        print(f"Skipping PDF test as neither '{sample_pdf_path}' nor '{dummy_pdf_path}' exists.")

    # --- Test Case 2: Processing a non-existent file ---
    print("\n--- Testing with a non-existent file ---")
    non_existent_file = "sample_inputs/non_existent.pdf"
    result_non_existent = pdf_agent.process_pdf(non_existent_file)
    print(f"Processing non-existent file: {'Success' if result_non_existent['success'] else 'Failed'} - {result_non_existent['error_message']}")

    # --- Test Case 3: Processing a non-PDF file (e.g., a dummy text file) ---
    print("\n--- Testing with a non-PDF file (dummy text file) ---")
    dummy_txt_file = "sample_inputs/dummy.txt"
    try:
        with open(dummy_txt_file, "w") as f:
            f.write("This is a dummy text file, not a PDF.")
        result_non_pdf = pdf_agent.process_pdf(dummy_txt_file)
        print(f"Processing non-PDF file: {'Success' if result_non_pdf['success'] else 'Failed'} - {result_non_pdf['error_message']}")
    finally:
        # Ensure the dummy text file is removed after the test.
        if os.path.exists(dummy_txt_file):
            os.remove(dummy_txt_file)

    # Clean up any created dummy PDF file after all tests are completed.
    if os.path.exists(dummy_pdf_path):
        os.remove(dummy_pdf_path)
