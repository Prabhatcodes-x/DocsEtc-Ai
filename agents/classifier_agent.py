import json
import logging  # Enable logging to track events and errors
from utils.llm_utils import call_ollama_llm  # Import your LLM utility function

def classify_pdf_intent_with_llm(pdf_text):
    """
    Use a Large Language Model (LLM) to classify the primary intent of a PDF document text.
    The LLM is prompted to respond with a strict JSON containing the 'intent' key.
    """

    # Prepare prompt for the LLM with instructions for strict JSON output
    prompt = f"""
    You are an intelligent document classifier. Analyze the following text extracted from a PDF document and determine its primary intent.
    Choose one of the following categories: 'Invoice', 'Quote Request', 'Contract', 'General Inquiry', 'Other'.
    Return your answer as a strict JSON object with a single key 'intent' and the chosen category as its value.

    Example Valid JSON Response:
    {{"intent": "Invoice"}}

    Document Text:
    ---
    {pdf_text[:2000]}  # Send only the initial portion for very long text
    ---
    """

    logging.info("Attempting LLM classification for PDF intent.")
    
    try:
        # Call the LLM and receive raw JSON response as a string
        llm_raw_response = call_ollama_llm(prompt, model="mistral:latest")  # Adjust model name if needed
        logging.debug(f"Raw LLM response for PDF: {llm_raw_response}")

        # Parse the LLM response from JSON string to dictionary
        result = json.loads(llm_raw_response)
        
        # Validate presence and type of 'intent' key in parsed result
        if 'intent' in result and isinstance(result['intent'], str):
            logging.info(f"LLM PDF classification successful: {result['intent']}")
            return {"intent": result['intent']}
        else:
            logging.warning(f"LLM response for PDF missing 'intent' key or invalid type. Raw: {llm_raw_response}")
            # Raise error if response format is invalid
            raise ValueError("LLM response format invalid: missing 'intent' key or incorrect type.")
            
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse LLM response for PDF as JSON: '{llm_raw_response}'. Error: {e}")
        raise  # Propagate exception to main.py for fallback handling
    except Exception as e:  # Catch any other exceptions from LLM call
        logging.error(f"Error during LLM PDF intent classification: {e}")
        raise  # Propagate exception to main.py for fallback handling

def rule_based_pdf_intent(pdf_text):
    """
    Simple rule-based PDF document intent classification.
    Checks presence of keywords in text to determine intent.
    Always returns a dictionary with an 'intent' key.
    """
    
    pdf_text_lower = pdf_text.lower()
    
    if "invoice" in pdf_text_lower or "bill" in pdf_text_lower:
        logging.info("Rule-based PDF classification: Identified as Invoice.")
        return {"intent": "Invoice"}
    elif "quote" in pdf_text_lower or "quotation" in pdf_text_lower:
        logging.info("Rule-based PDF classification: Identified as Quote Request.")
        return {"intent": "Quote Request"}
    elif "contract" in pdf_text_lower or "agreement" in pdf_text_lower:
        logging.info("Rule-based PDF classification: Identified as Contract.")
        return {"intent": "Contract"}
    else:
        logging.info("Rule-based PDF classification: Identified as General Inquiry.")
        return {"intent": "General Inquiry"}  # Always return a dictionary for consistency
