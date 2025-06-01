import time
import logging
import os  # For handling file paths

# Import agents and utilities
from agents.email_agent import classify_email_intent_with_llm, rule_based_email_intent
from agents.json_agent import JSONAgent
from agents.classifier_agent import classify_pdf_intent_with_llm, rule_based_pdf_intent
from memory.shared_memory import SharedMemory  # Confirm that this path is correct
from utils.file_utils import load_text, load_json, load_pdf_text  # New load functions

# --- Logging Configuration ---
# Set up logging at application start
logging.basicConfig(
    level=logging.INFO,  # Log INFO level messages and above
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format: timestamp - level - message
    handlers=[
        logging.FileHandler(os.path.join("output_logs", "agent_activity.log")),  # Save logs to file
        logging.StreamHandler()  # Also print logs to console
    ]
)

def run_email_agent():
    logging.info("----- Running Email input -----")
    email_input_path = os.path.join("sample_inputs", "sample_email.txt")
    email_text = ""
    try:
        email_text = load_text(email_input_path)  # Load email text using FileUtils
        logging.info(f"Loaded email from: {email_input_path}")
    except FileNotFoundError:
        logging.error(f"Error: Sample email file not found at {email_input_path}. Skipping email agent.")
        return  # Skip agent if file is not found
    except Exception as e:
        logging.error(f"Error loading sample email from {email_input_path}: {e}. Skipping email agent.")
        return

    result = {}  # Default empty dictionary
    try:
        # Try classification using LLM
        result = classify_email_intent_with_llm(email_text)
        logging.info("Email classified using LLM.")
    except Exception as e:
        # If LLM fails, fallback to rule-based classification
        logging.warning(f"[LLM Fallback] Using rule-based email intent classification due to error: {e}")
        result = rule_based_email_intent(email_text)
    
    # Ensure result is always a dictionary for consistent logging to SharedMemory
    if not isinstance(result, dict):
        logging.error(f"Email classification result is not a dictionary: {result}. Converting to generic.")
        result = {"intent": str(result), "status": "fallback_string_conversion"}

    logging.info(f"=== Email Result ===\n{result}")
    SharedMemory.log('email_conversation', {'format': 'Email', **result, 'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")})

def run_json_agent():
    logging.info("----- Running JSON input -----")
    json_input_path = os.path.join("sample_inputs", "sample_invoice.json")
    json_data = {}
    try:
        json_data = load_json(json_input_path)  # Load JSON data using FileUtils
        logging.info(f"Loaded JSON from: {json_input_path}")
    except FileNotFoundError:
        logging.error(f"Error: Sample JSON file not found at {json_input_path}. Skipping JSON agent.")
        return
    except json.JSONDecodeError:  # Specific error for JSON parsing
        logging.error(f"Error: Invalid JSON format in {json_input_path}. Skipping JSON agent.")
        return
    except Exception as e:
        logging.error(f"Error loading sample JSON from {json_input_path}: {e}. Skipping JSON agent.")
        return

    agent = JSONAgent()
    result = agent.process('json_conversation', json_data)
    logging.info(f"=== JSON Result ===\n{result}")
    # JSONAgent logs to SharedMemory internally

def run_pdf_agent():
    logging.info("----- Running PDF input -----")
    pdf_input_path = os.path.join("sample_inputs", "sample_invoice.pdf")
    pdf_text = ""
    try:
        pdf_text = load_pdf_text(pdf_input_path)  # Extract PDF text using FileUtils
        logging.info(f"Loaded PDF from: {pdf_input_path}")
    except FileNotFoundError:
        logging.error(f"Error: Sample PDF file not found at {pdf_input_path}. Skipping PDF agent.")
        return
    except Exception as e:  # Any pdfplumber-related error
        logging.error(f"Error loading sample PDF from {pdf_input_path}: {e}. Skipping PDF agent.")
        return

    result = {}  # Default empty dictionary
    try:
        # Try classification using LLM
        result = classify_pdf_intent_with_llm(pdf_text)
        logging.info("PDF classified using LLM.")
    except Exception as e:
        # If LLM fails, fallback to rule-based classification
        logging.warning(f"[LLM Fallback] Using rule-based PDF intent classification due to error: {e}")
        result = rule_based_pdf_intent(pdf_text)

    # Ensure result is always a dictionary for consistent logging to SharedMemory
    if not isinstance(result, dict):
        logging.error(f"PDF classification result is not a dictionary: {result}. Converting to generic.")
        result = {"intent": str(result), "status": "fallback_string_conversion"}

    log_entry = {"format": "PDF", **result, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
    logging.info(f"=== PDF Result ===\n{result}")
    SharedMemory.log('pdf_conversation', log_entry)
    logging.info(f"SharedMemory Log for PDF: {log_entry}")  # Shows what was logged to SharedMemory

if __name__ == "__main__":
    SharedMemory.initialize()  # Initialize SharedMemory (with persistence support)
    
    run_email_agent()
    run_json_agent()
    run_pdf_agent()

    # If you implemented persistence in SharedMemory and want to save at the end:
    # SharedMemory._save_to_file()  # If not already saving after each log
    
    logging.info("--- Application finished ---")
