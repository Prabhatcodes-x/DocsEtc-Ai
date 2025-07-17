import os
import sys
import logging
from datetime import datetime

# Extend system path to include project root for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.pdf_agent import PDFAgent
from agents.classifier_agent import ClassifierAgent
from agents.email_agent import EmailAgent
from agents.json_agent import JsonAgent
from memory.shared_memory import SharedMemory

# Configure logging to output to both console and file

log_dir = 'output_logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    # This key parameter fixes the encoding issue for the file logger
    encoding='utf-8',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'agent_activity.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Coordinator class for managing document processing using multiple agents."""

    def __init__(self):
        self.pdf_agent = PDFAgent()
        self.classifier_agent = ClassifierAgent()
        self.email_agent = EmailAgent()
        self.json_agent = JsonAgent()
        self.shared_memory = SharedMemory()
        os.makedirs('output_logs', exist_ok=True)

    def process_pdf_document(self, file_path: str) -> dict:
        """Extract and classify content from a PDF document."""
        logger.info(f"=== Processing PDF Document: {file_path} ===")

        try:
            logger.info("Step 1: Extracting text using PDF Agent")
            pdf_result = self.pdf_agent.process_pdf(file_path)

            if not pdf_result['success']:
                logger.error(f"PDF processing failed: {pdf_result['error_message']}")
                return pdf_result

            extracted_text = pdf_result['extracted_text']
            logger.info(f"Extracted text length: {len(extracted_text)} characters")

            logger.info("Step 2: Classifying content using Classifier Agent")
            classification_result = self.classifier_agent.classify_document(extracted_text)

            if not classification_result['success']:
                logger.error(f"Classification failed: {classification_result['error_message']}")
                return classification_result

            logger.info(f"Classification result: {classification_result['document_type']} "
                        f"(confidence: {classification_result['confidence']}, "
                        f"method: {classification_result['method_used']})")

            combined_result = {
                'conversation_id': f"pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'source': file_path,
                'type': 'PDF_DOCUMENT',
                'document_type': classification_result['document_type'],
                'confidence': classification_result['confidence'],
                'classification_method': classification_result['method_used'],
                'extracted_text': extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
                'extracted_info': classification_result.get('extracted_info', {}),
                'pdf_metadata': pdf_result['metadata'],
                'timestamp': datetime.now().isoformat(),
                'processing_agents': ['PDF_Agent', 'Classifier_Agent']
            }

            self.shared_memory.store_result(combined_result)
            logger.info("Stored results in shared memory")

            return {
                'success': True,
                'pdf_processing': pdf_result,
                'classification': classification_result,
                'combined_result': combined_result
            }

        except Exception as e:
            logger.error(f"PDF processing error: {str(e)}")
            return {
                'success': False,
                'error_message': str(e)
            }

    def process_text_file(self, file_path: str) -> dict:
        """Process a plain text or email-like file for classification or parsing."""
        logger.info(f"=== Processing Text File: {file_path} ===")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()

            if 'sample_email' in file_path or self.is_email_format(text_content):
                logger.info("Email format detected. Routing to Email Agent.")
                result = self.email_agent.process_email(text_content)
            else:
                logger.info("Using Classifier Agent for text classification")
                result = self.classifier_agent.classify_document(text_content)

            if result['success']:
                combined_result = {
                    'conversation_id': f"text_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'source': file_path,
                    'type': 'TEXT_DOCUMENT',
                    'content': text_content[:500] + "..." if len(text_content) > 500 else text_content,
                    'timestamp': datetime.now().isoformat()
                }
                combined_result.update(result)
                self.shared_memory.store_result(combined_result)

            return result

        except Exception as e:
            logger.error(f"Text file processing error: {str(e)}")
            return {
                'success': False,
                'error_message': str(e)
            }

    def process_json_file(self, file_path: str) -> dict:
        """Delegate structured data processing to JSON Agent."""
        logger.info(f"=== Processing JSON File: {file_path} ===")

        try:
            result = self.json_agent.process_json(file_path)

            if result['success']:
                combined_result = {
                    'conversation_id': f"json_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'source': file_path,
                    'type': 'JSON_DOCUMENT',
                    'timestamp': datetime.now().isoformat()
                }
                combined_result.update(result)
                self.shared_memory.store_result(combined_result)

            return result

        except Exception as e:
            logger.error(f"JSON file processing error: {str(e)}")
            return {
                'success': False,
                'error_message': str(e)
            }

    def is_email_format(self, text: str) -> bool:
        """Determine if the provided text resembles an email structure."""
        email_indicators = ['from:', 'to:', 'subject:', 'dear', '@', 'sent:', 'date:']
        text_lower = text.lower()
        return sum(1 for indicator in email_indicators if indicator in text_lower) >= 2

    def process_sample_inputs(self):
        """Run processing pipeline on predefined sample files."""
        sample_files = {
            'sample_inputs/sample_invoice.pdf': self.process_pdf_document,
            'sample_inputs/sample_email.txt': self.process_text_file,
            'sample_inputs/sample_invoice.json': self.process_json_file
        }

        results = {}

        for file_path, processor_func in sample_files.items():
            if os.path.exists(file_path):
                logger.info(f"\n{'='*60}")
                logger.info(f"Processing: {file_path}")
                logger.info(f"{'='*60}")

                result = processor_func(file_path)
                results[file_path] = result

                if result['success']:
                    logger.info("✅ Processing completed successfully")
                else:
                    logger.error(f"❌ Processing failed: {result.get('error_message', 'Unknown error')}")
            else:
                logger.warning(f"Sample file not found: {file_path}")
                results[file_path] = {
                    'success': False,
                    'error_message': 'File not found'
                }

        return results

    def print_summary(self, results: dict):
        """Display a concise summary of the processing outcomes."""
        print(f"\n{'='*60}")
        print("PROCESSING SUMMARY")
        print(f"{'='*60}")

        total_files = len(results)
        successful_files = sum(1 for result in results.values() if result['success'])

        print(f"Total files processed: {total_files}")
        print(f"Successful: {successful_files}")
        print(f"Failed: {total_files - successful_files}")

        print(f"\nDetails:")
        for file_path, result in results.items():
            status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
            print(f"  {os.path.basename(file_path)}: {status}")

            if result['success'] and 'classification' in result:
                classification = result['classification']
                print(f"    Type: {classification.get('document_type', 'N/A')}")
                print(f"    Confidence: {classification.get('confidence', 'N/A')}")
                print(f"    Method: {classification.get('method_used', 'N/A')}")

        memory_results = self.shared_memory.get_all_results()
        print(f"\nShared Memory: {len(memory_results)} entries stored")

def main():
    """Entry point for launching the document processing pipeline."""
    logger.info("Starting Multi-Agent Document Processing System")
    logger.info("Architecture: PDF Agent, Classifier Agent, Email Agent, JSON Agent")

    try:
        processor = DocumentProcessor()
        results = processor.process_sample_inputs()
        processor.print_summary(results)
        logger.info("Document processing completed. Review 'output_logs/' for logs.")
    except Exception as e:
        logger.error(f"Fatal system error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
