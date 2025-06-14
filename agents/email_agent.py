import json
import logging
import re
from typing import Dict, Any, Optional

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

_llm_utils_available = False
try:
    from utils.llm_utils import call_ollama_llm
    _llm_utils_available = True
    logger.info("LLM utility 'call_ollama_llm' found and imported for EmailAgent.")
except ImportError:
    logger.warning("LLM utility 'call_ollama_llm' not found. LLM-based email classification will be unavailable.")

class EmailAgent:
    """
    The EmailAgent class is designed to classify the intent and urgency of incoming emails.
    It employs a sophisticated hybrid approach, prioritizing classification via a Large Language Model (LLM)
    and falling back to a rule-based system if the LLM is unavailable or fails to provide a valid response.
    """
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """
        Initializes the EmailAgent with configuration for LLM interaction.

        Args:
            ollama_url (str): The base URL for the Ollama server, which hosts the LLM.
                              This URL is used by the `llm_utils` module to communicate with the LLM.
        """
        self.agent_name = "Email_Agent"
        self.ollama_url = ollama_url
        self.llm_model = "mistral:latest"
        self.llm_utils_available = _llm_utils_available

    def _rule_based_email_intent(self, email_text: str) -> Dict[str, str]:
        """
        Applies a set of predefined rules to determine the intent and urgency of an email.
        This method serves as a resilient fallback mechanism when LLM classification is not feasible
        or does not yield a satisfactory result. The rules are based on keyword matching.

        Args:
            email_text (str): The full text content of the email to be classified.

        Returns:
            Dict[str, str]: A dictionary containing the classified 'intent' and 'urgency' as strings.
                            Example: {"intent": "Support", "urgency": "High"}
        """
        email_text_lower = email_text.lower()

        intent = "General Inquiry"
        urgency = "Normal"

        # Define and apply rules for email intent classification.
        # These rules are ordered and can be expanded for more granular classification.
        if any(keyword in email_text_lower for keyword in ["quote", "quotation", "estimate", "pricing"]):
            intent = "Quote Request"
        elif any(keyword in email_text_lower for keyword in ["order", "purchase", "procure", "buy"]):
            intent = "Order"
        elif any(keyword in email_text_lower for keyword in ["support", "help", "issue", "problem", "bug", "trouble"]):
            intent = "Support"
        elif any(keyword in email_text_lower for keyword in ["feedback", "suggestion", "review", "complaint"]):
            intent = "Feedback"

        # Define and apply rules for email urgency classification.
        # More specific keywords are used for higher urgency levels.
        if any(keyword in email_text_lower for keyword in ["urgent", "asap", "immediately", "critical", "down", "halted"]):
            urgency = "High"
        elif any(keyword in email_text_lower for keyword in ["blocker", "outage"]):
            urgency = "Critical"

        logger.info(f"Rule-based email classification: Intent='{intent}', Urgency='{urgency}'")
        return {"intent": intent, "urgency": urgency}

    def _classify_email_intent_with_llm(self, email_text: str) -> Dict[str, str]:
        """
        Leverages a Large Language Model (LLM) to classify the intent and urgency of an email.
        This method constructs a specific prompt to guide the LLM to return a strict JSON format,
        which is then parsed and validated.

        Args:
            email_text (str): The full text content of the email to be classified.

        Returns:
            Dict[str, str]: A dictionary containing the LLM-classified 'intent' and 'urgency'.

        Raises:
            RuntimeError: If the LLM utility is not available, preventing LLM classification.
            json.JSONDecodeError: If the LLM's response cannot be parsed as valid JSON.
            ValueError: If the LLM's JSON response is missing required keys or contains invalid types.
            Exception: For any other unexpected errors during the LLM classification process.
        """
        if not self.llm_utils_available:
            logger.error("LLM utility not available. Cannot perform LLM classification.")
            raise RuntimeError("LLM utility not available.")

        # Construct the prompt for the LLM, specifying desired output format and categories.
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

        logger.info("Attempting LLM classification for email intent.")
        llm_raw_response = None
        try:
            # Call the LLM with the prepared prompt and model.
            llm_raw_response = call_ollama_llm(prompt, model=self.llm_model)
            logger.debug(f"Raw LLM response for email: {llm_raw_response[:200]}...")

            # Parse the LLM's raw response as a JSON object.
            result = json.loads(llm_raw_response)

            # Validate that the essential 'intent' and 'urgency' keys are present and are strings.
            if "intent" in result and "urgency" in result and \
               isinstance(result['intent'], str) and isinstance(result['urgency'], str):

                # Further validate that the LLM's output matches allowed categories.
                allowed_intents = ['Quote Request', 'Order', 'General Inquiry', 'Support', 'Feedback', 'Other']
                allowed_urgencies = ['Low', 'Normal', 'High', 'Critical']

                # Default to 'Other' or 'Normal' if the LLM generates an unrecognized category.
                if result['intent'] not in allowed_intents:
                    logger.warning(f"LLM returned unknown intent: '{result['intent']}'. Mapping to 'Other'.")
                    result['intent'] = 'Other'
                if result['urgency'] not in allowed_urgencies:
                    logger.warning(f"LLM returned unknown urgency: '{result['urgency']}'. Mapping to 'Normal'.")
                    result['urgency'] = 'Normal'

                logger.info(f"LLM email classification successful: Intent='{result['intent']}', Urgency='{result['urgency']}'")
                return result
            else:
                # Log a warning and raise an error if the LLM's JSON structure is incorrect.
                logger.warning(f"LLM response for email missing 'intent'/'urgency' keys or invalid type. Raw: {llm_raw_response}")
                raise ValueError("LLM response format invalid for email intent.")

        except json.JSONDecodeError as e:
            # Handle cases where the LLM's response is not valid JSON.
            logger.error(f"Failed to parse LLM response for email as JSON: '{llm_raw_response}'. Error: {e}")
            raise
        except Exception as e:
            # Catch any other unforeseen errors during the LLM process.
            logger.error(f"Error during LLM email intent classification: {e}")
            raise

    def process_email(self, email_input: Any) -> Dict[str, Any]:
        """
        The main public method for classifying email intent and urgency.
        It orchestrates the classification process, attempting LLM classification first,
        and gracefully falling back to rule-based classification if necessary.
        It can accept email content as a string or as a dictionary.

        Args:
            email_input (Any): The email content. This can be a string (the email body)
                               or a dictionary (e.g., `{'body': '...', 'subject': '...'}`).

        Returns:
            Dict[str, Any]: A dictionary containing the classification results:
                            - 'success' (bool): True if classification was successful, False otherwise.
                            - 'agent' (str): The name of the agent.
                            - 'intent' (str): The classified intent of the email (e.g., 'Support', 'Order').
                            - 'urgency' (str): The classified urgency of the email (e.g., 'High', 'Normal').
                            - 'method_used' (str): Indicates whether 'LLM' or 'Rule-based' method was used.
                            - 'error_message' (Optional[str]): A description of any error that occurred.
        """
        result = {
            'success': False,
            'agent': self.agent_name,
            'intent': 'Unknown',
            'urgency': 'Unknown',
            'method_used': None,
            'error_message': None
        }

        # Extract the textual content of the email from various input formats.
        email_text = ""
        if isinstance(email_input, dict):
            email_text = email_input.get('body') or email_input.get('text') or ""
        elif isinstance(email_input, str):
            email_text = email_input
        else:
            result['error_message'] = f"Invalid email input type: {type(email_input)}. Expected str or dict."
            logger.error(result['error_message'])
            return result

        if not email_text or not email_text.strip():
            result['error_message'] = "Empty or invalid email content provided for processing."
            logger.warning(result['error_message'])
            return result

        llm_classification_success = False
        # Attempt LLM classification if the LLM utility is available.
        if self.llm_utils_available:
            try:
                llm_classification_output = self._classify_email_intent_with_llm(email_text)
                result.update({
                    'success': True,
                    'intent': llm_classification_output['intent'],
                    'urgency': llm_classification_output['urgency'],
                    'method_used': 'LLM'
                })
                logger.info("Using LLM for email classification.")
                llm_classification_success = True
            except Exception as e:
                # Log any failure from the LLM and proceed to rule-based fallback.
                logger.warning(f"LLM email classification failed ({e}). Falling back to rule-based.")
        else:
            logger.info("LLM utility not available. Directly performing rule-based email classification.")

        # If LLM classification was not successful (either failed or not available), use rule-based.
        if not llm_classification_success:
            rule_classification_output = self._rule_based_email_intent(email_text)
            result.update({
                'success': True,
                'intent': rule_classification_output['intent'],
                'urgency': rule_classification_output['urgency'],
                'method_used': 'Rule-based'
            })
            logger.info("Using rule-based for email classification.")
        
        return result

if __name__ == "__main__":
    # Configure basic logging for console output when the script is run directly.
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

    agent = EmailAgent()
    
    # Define a series of test emails to demonstrate the agent's capabilities.
    test_emails = [
        "Hi, can I get a quote for 100 widgets? This is urgent.",
        {"subject": "New Order", "body": "Please process a new purchase order for item XYZ. It's not critical."},
        "Just a general question about your services.",
        "Our system is down, critical support needed immediately!",
        "I have some feedback regarding your recent update.",
        "Empty email",
        {"text": "I would like to inquire about partnership opportunities."}
    ]

    print("\n--- Testing Email Agent with Sample Emails ---")
    for i, email_content in enumerate(test_emails, 1):
        print(f"\n--- Test Case {i} ---")
        # Display a snippet of the input email for context in the test output.
        display_text = email_content if isinstance(email_content, str) else email_content.get('body', email_content.get('text', str(email_content)))
        print(f"Input: {display_text[:100]}...")
        
        # Process the email and print the classification result.
        result = agent.process_email(email_content)
        
        if result['success']:
            print(f"  Result: Success")
            print(f"  Intent: {result['intent']}")
            print(f"  Urgency: {result['urgency']}")
            print(f"  Method: {result['method_used']}")
        else:
            print(f"  Result: Failed - {result['error_message']}")
