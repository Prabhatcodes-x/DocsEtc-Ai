import json
import logging  # Enable logging
from utils.llm_utils import call_ollama_llm
# from memory.shared_memory import SharedMemory  # Remove if not directly used here
# from datetime import datetime  # Remove if not directly used here

def rule_based_email_intent(email_text):
    """
    Simple rule-based classifier to determine the intent and urgency of an email.
    """

    # Extract text from dict input, or use string directly
    if isinstance(email_text, dict):
        email_text_content = email_text.get('body') or email_text.get('text') or ""
    else:
        email_text_content = email_text

    email_text_lower = email_text_content.lower()
    
    # Default intent and urgency
    intent = "General Inquiry"
    urgency = "Normal"

    # Intent classification rules
    if "quote" in email_text_lower or "quotation" in email_text_lower:
        intent = "Quote Request"
    elif "order" in email_text_lower or "purchase" in email_text_lower:
        intent = "Order"
    elif "support" in email_text_lower or "help" in email_text_lower:
        intent = "Support"
    
    # Urgency classification rules
    if "urgent" in email_text_lower or "asap" in email_text_lower or "immediately" in email_text_lower:
        urgency = "High"
    elif "critical" in email_text_lower or "down" in email_text_lower:
        urgency = "Critical"

    logging.info(f"Rule-based email classification: Intent='{intent}', Urgency='{urgency}'")
    return {"intent": intent, "urgency": urgency}


def classify_email_intent_with_llm(email_input):
    """
    Uses a Large Language Model (LLM) to classify email intent and urgency.
    Requires the response in a strict JSON format.
    """

    # Extract text from dict input, or use string directly
    if isinstance(email_input, dict):
        email_text = email_input.get('body') or email_input.get('text') or ""
    else:
        email_text = email_input

    # Prompt LLM for a strict JSON response
    prompt = f"""
    Classify the intent and urgency of the following email.
    Possible intents: 'Quote Request', 'Order', 'General Inquiry', 'Support', 'Feedback', 'Other'.
    Possible urgencies: 'Low', 'Normal', 'High', 'Critical'.

    Provide your response as a strict JSON object with 'intent' and 'urgency' keys.
    Example Valid JSON Response:
    {{"intent": "Quote Request", "urgency": "High"}}

    Email:
    ---
    {email_text}
    ---
    """
    
    logging.info("Attempting LLM classification for email intent.")
    try:
        # Call LLM to get classification response
        llm_raw_response = call_ollama_llm(prompt, model="mistral:latest")  # Adjust model name if needed
        logging.debug(f"Raw LLM response for email: {llm_raw_response}")
        
        # Try parsing response as JSON
        result = json.loads(llm_raw_response)
        
        # Check required keys and types
        if "intent" in result and "urgency" in result and \
           isinstance(result['intent'], str) and isinstance(result['urgency'], str):
            logging.info(f"LLM email classification successful: {result}")
            return result
        else:
            logging.warning(f"LLM response for email missing 'intent'/'urgency' keys or invalid type. Raw: {llm_raw_response}")
            raise ValueError("LLM response format invalid for email intent.")
            
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse LLM response for email as JSON: '{llm_raw_response}'. Error: {e}")
        raise  # Propagate exception to main.py for fallback
    except Exception as e:  # Catch other errors from call_ollama_llm
        logging.error(f"Error during LLM email intent classification: {e}")
        raise  # Propagate exception to main.py for fallback
