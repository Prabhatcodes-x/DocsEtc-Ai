import os
import sys
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)

_llm_utils_available = False
try:
    from utils.llm_utils import call_ollama_llm
    _llm_utils_available = True
    logger.info("LLM utility 'call_ollama_llm' imported successfully.")
except ImportError:
    logger.warning("LLM utility 'call_ollama_llm' not found. LLM-based classification will be unavailable.")

class ClassifierAgent:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        """
        Initializes the ClassifierAgent.

        Args:
            ollama_url (str): The URL of the Ollama server for LLM interactions.
        """
        self.agent_name = "Classifier_Agent"
        self.ollama_url = ollama_url
        self.model_name = "mistral:latest"
        self.llm_utils_available = _llm_utils_available

        self.document_types = {
            'INVOICE': {
                'keywords': ['invoice', 'bill', 'payment', 'amount', 'total', 'due', 'tax', 'subtotal', 'billing', 'remit'],
                'patterns': [r'invoice\s*#?\s*\d+', r'bill\s*#?\s*\d+', r'total\s*:?\s*\$?\s*[\d,]+\.?\d{0,2}', r'amount\s*due']
            },
            'QUOTE_REQUEST': {
                'keywords': ['quote', 'quotation', 'estimate', 'proposal', 'request', 'rfq', 'bid'],
                'patterns': [r'request\s*for\s*quote', r'rfq', r'estimate\s*request']
            },
            'CONTRACT': {
                'keywords': ['contract', 'agreement', 'terms', 'conditions', 'party', 'whereas', 'liability', 'effective date'],
                'patterns': [r'this\s*agreement', r'terms\s*and\s*conditions', r'contract\s*#?\s*\w+']
            },
            'PURCHASE_ORDER': {
                'keywords': ['purchase', 'order', 'po', 'procurement', 'vendor', 'supplier', 'delivery'],
                'patterns': [r'purchase\s*order', r'po\s*#?\s*\d+', r'order\s*#?\s*\d+']
            },
            'RECEIPT': {
                'keywords': ['receipt', 'paid', 'transaction', 'payment received', 'thank you for your purchase', 'change due'],
                'patterns': [r'receipt\s*#?\s*\d+', r'transaction\s*id', r'payment\s*received', r'total\s*paid']
            },
            'GENERAL_INQUIRY': {
                'keywords': ['inquiry', 'question', 'help', 'support', 'information', 'request', 'query', 'assistance'],
                'patterns': [r'can\s*you\s*help', r'i\s*have\s*a\s*question', r'could\s*you\s*provide', r'seeking\s*information']
            }
        }

    def check_ollama_connection(self) -> bool:
        """
        Verifies connectivity to the Ollama server.

        This method attempts to connect to the configured Ollama URL to ensure the LLM service
        is operational and accessible. It is only executed if LLM utilities are available.

        Returns:
            bool: True if the Ollama server is accessible, False otherwise.
        """
        if not self.llm_utils_available:
            logger.warning("LLM utility not available; skipping Ollama connection check.")
            return False

        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("Ollama server is accessible.")
                return True
            else:
                logger.warning(f"Ollama server returned status: {response.status_code}.")
                return False
        except requests.exceptions.ConnectionError:
            logger.warning(f"Ollama server connection refused or host unreachable at {self.ollama_url}.")
            return False
        except requests.exceptions.Timeout:
            logger.warning(f"Ollama server connection timed out after 5 seconds at {self.ollama_url}.")
            return False
        except Exception as e:
            logger.warning(f"Ollama server accessibility check failed: {str(e)}.")
            return False

    def classify_with_llm(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Classifies document content using a Large Language Model (LLM) via Ollama.

        This method sends the document text to the LLM and expects a JSON response
        containing the document type, confidence, and reasoning. It handles potential
        failures in LLM response generation or parsing.

        Args:
            text (str): The text content of the document to classify.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing 'document_type', 'confidence',
                                      and 'reasoning' if classification is successful and valid,
                                      otherwise None.
        """
        if not self.llm_utils_available:
            logger.warning("LLM utility not available; skipping LLM classification.")
            return None

        try:
            # Construct the prompt for the LLM, limiting text length to fit context window.
            prompt = f"""
            Analyze the following document text and classify it into one of these categories:
            - INVOICE: Bills, invoices, payment requests
            - QUOTE_REQUEST: Quotation requests, estimates, proposals
            - CONTRACT: Agreements, contracts, legal documents
            - PURCHASE_ORDER: Purchase orders, procurement documents
            - RECEIPT: Payment confirmations, receipts, sales slips
            - GENERAL_INQUIRY: General questions, support requests, inquiries, informal communications

            Document text:
            {text[:2000]}

            Respond with ONLY a strict JSON object in this format. Ensure keys are exactly as specified.
            {{
                "document_type": "CATEGORY_NAME",
                "confidence": 0.85,
                "reasoning": "Brief explanation of why this classification was chosen"
            }}
            """

            response_text = call_ollama_llm(prompt, self.model_name)

            if response_text:
                try:
                    classification_result = json.loads(response_text)
                    # Validate the essential keys and their types in the LLM's JSON response.
                    if (all(key in classification_result and isinstance(classification_result[key], (str, float, int))
                            for key in ['document_type', 'confidence']) and 'reasoning' in classification_result):

                        if classification_result['document_type'] in self.document_types.keys():
                            logger.info(f"LLM classification successful: {classification_result['document_type']} (confidence: {classification_result['confidence']:.2f})")
                            return classification_result
                        else:
                            logger.warning(f"LLM returned an invalid document_type: '{classification_result['document_type']}'. Falling back to rule-based.")
                            return None
                    else:
                        logger.warning(f"LLM response missing required fields or has invalid types: {response_text}. Falling back to rule-based.")
                        return None
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse LLM JSON response: '{response_text}'. Falling back to rule-based.")
                    return None
            return None
        except Exception as e:
            logger.error(f"LLM classification attempt failed unexpectedly: {str(e)}. Falling back to rule-based.")
            return None

    def classify_with_rules(self, text: str) -> Dict[str, Any]:
        """
        Performs rule-based document classification using predefined keywords and regex patterns.

        This method serves as a fallback mechanism if LLM classification is not available or fails.
        It scores document types based on the presence of specific keywords and the matching of regex patterns.

        Args:
            text (str): The text content of the document to classify.

        Returns:
            Dict[str, Any]: A dictionary containing the 'document_type', 'confidence',
                            'reasoning', and the calculated 'scores' for each type.
        """
        text_lower = text.lower()
        scores = {}

        for doc_type, config in self.document_types.items():
            score = 0
            for keyword in config['keywords']:
                count = text_lower.count(keyword.lower())
                score += count * 2
            for pattern in config['patterns']:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches * 3
            scores[doc_type] = score

        if not scores or max(scores.values()) == 0:
            # Assign a default type and low confidence if no matches are found.
            best_type = 'GENERAL_INQUIRY'
            confidence = 0.3
        else:
            best_type = max(scores, key=scores.get)
            max_score = scores[best_type]
            total_score = sum(scores.values())
            # Calculate confidence as a ratio, capping it to indicate rule-based limitations.
            confidence = min(0.9, max_score / max(total_score, 1))

        logger.info(f"Rule-based classification: {best_type} (confidence: {confidence:.2f}). Scores: {scores}")

        return {
            'document_type': best_type,
            'confidence': round(confidence, 2),
            'reasoning': 'Rule-based classification based on keyword and pattern matching',
            'scores': scores
        }

    def extract_key_information(self, text: str, document_type: str) -> Dict[str, Any]:
        """
        Extracts specific key information from the document text based on its classified type.

        This method uses regular expressions to find relevant data points like invoice numbers,
        amounts, due dates, and purchase order details, depending on the identified document type.

        Args:
            text (str): The document text from which to extract information.
            document_type (str): The classified type of the document.

        Returns:
            Dict[str, Any]: A dictionary containing the extracted key-value pairs.
        """
        extracted_info = {}
        text_lower = text.lower()

        try:
            if document_type == 'INVOICE':
                invoice_num_match = re.search(r'(?:invoice|bill)\s*(?:#|no\.?|num(?:ber)?\s*)?([a-z0-9\-/_]+)', text_lower, re.IGNORECASE)
                amount_match = re.search(r'(?:total|amount|subtotal|balance due|net amount)\s*:?\s*(?:usd|eur|gbp|\$|€|£)?\s*([\d,]+\.?\d{0,2})', text_lower, re.IGNORECASE)
                due_date_match = re.search(r'(?:due\s*date|payment\s*due|due)\s*:?\s*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}|\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2})', text_lower, re.IGNORECASE)

                extracted_info.update({
                    'invoice_number': invoice_num_match.group(1).strip() if invoice_num_match else None,
                    'amount': amount_match.group(1).replace(',', '') if amount_match else None,
                    'due_date': due_date_match.group(1).strip() if due_date_match else None
                })

            elif document_type == 'PURCHASE_ORDER':
                po_num_match = re.search(r'(?:purchase\s*order|po)\s*(?:#|no\.?|num(?:ber)?\s*)?([a-z0-9\-/_]+)', text_lower, re.IGNORECASE)
                vendor_match = re.search(r'(?:vendor|supplier|sold\s*to|ship\s*to)\s*:?\s*([^\n\r]+)', text_lower, re.IGNORECASE)

                extracted_info.update({
                    'po_number': po_num_match.group(1).strip() if po_num_match else None,
                    'vendor': vendor_match.group(1).strip() if vendor_match else None
                })
        except Exception as e:
            logger.warning(f"Key information extraction failed for type '{document_type}': {str(e)}")

        return extracted_info

    def classify_document(self, text: str) -> Dict[str, Any]:
        """
        The primary method to classify a given document text.

        This method attempts LLM-based classification first. If the LLM is unavailable,
        unresponsive, or provides an invalid response, it falls back to rule-based classification.
        After classification, it extracts key information based on the identified document type.

        Args:
            text (str): The document text to be classified.

        Returns:
            Dict[str, Any]: A comprehensive dictionary detailing the classification result,
                            including success status, agent name, timestamp, document type,
                            confidence, method used, reasoning, extracted information, and
                            any error messages.
        """
        result = {
            'success': False,
            'agent': self.agent_name,
            'timestamp': datetime.now().isoformat(),
            'document_type': None,
            'confidence': 0.0,
            'method_used': None,
            'reasoning': None,
            'extracted_info': {},
            'error_message': None
        }

        try:
            logger.info("Starting document classification.")

            if not text or not text.strip():
                result['error_message'] = "Empty or invalid text provided for classification."
                return result

            llm_result = None
            # Attempt LLM classification if the utility is available and Ollama is connected.
            if self.llm_utils_available and self.check_ollama_connection():
                llm_result = self.classify_with_llm(text)

            # Prioritize LLM result if it's successful and valid.
            if llm_result and llm_result.get('document_type') and llm_result.get('confidence') is not None:
                result.update({
                    'success': True,
                    'document_type': llm_result['document_type'],
                    'confidence': llm_result['confidence'],
                    'method_used': 'LLM',
                    'reasoning': llm_result.get('reasoning', 'LLM-based classification')
                })
                logger.info("Using LLM classification result.")
            else:
                # Fallback to rule-based classification.
                logger.info("LLM classification failed or unavailable. Falling back to rule-based classification.")
                rule_result = self.classify_with_rules(text)
                result.update({
                    'success': True,
                    'document_type': rule_result['document_type'],
                    'confidence': rule_result['confidence'],
                    'method_used': 'Rule-based',
                    'reasoning': rule_result['reasoning']
                })
                logger.info("Using rule-based classification result.")

            # Extract key information regardless of the classification method used.
            extracted_info = self.extract_key_information(text, result['document_type'])
            result['extracted_info'] = extracted_info

            logger.info(f"Document classification completed: {result['document_type']} (confidence: {result['confidence']:.2f}).")
            return result
        except Exception as e:
            logger.error(f"An unexpected error occurred during document classification: {str(e)}.")
            result['error_message'] = str(e)
            return result

if __name__ == "__main__":
    # Configure basic logging for console output during standalone execution.
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

    classifier = ClassifierAgent()

    sample_texts = [
        "Invoice #INV-2023-001\nTotal Amount: $1250.75\nDue Date: 11/15/2024\nCustomer: ABC Corp",
        "Request for Quotation: We need pricing for 500 units of widgets, ASAP.",
        "This Agreement is made this 1st day of January, 2024, between Party A and Party B.",
        "Purchase Order No. PO-45678 from Vendor Solutions for 100 keyboards.",
        "Thank you for your payment. Receipt #REC-99887. Total Paid: €50.00.",
        "Hi, I have a general question about your service uptime. Could you provide some details?",
        "Just a casual hello.",
        "Invoice No: 554321, Amount Due: $345.67",
        "Urgent support needed, my system is completely down, fix immediately!"
    ]

    print("\n--- Testing Classifier Agent with Sample Texts ---")
    for i, text in enumerate(sample_texts, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input Text: {text[:100]}...")
        result = classifier.classify_document(text)

        if result['success']:
            print(f"  Classification Type: {result['document_type']}")
            print(f"  Confidence: {result['confidence']:.2f}")
            print(f"  Method Used: {result['method_used']}")
            if result['extracted_info']:
                print(f"  Extracted Info: {json.dumps(result['extracted_info'], indent=2)}")
            print(f"  Reasoning: {result['reasoning']}")
        else:
            print(f"  Classification Failed: {result['error_message']}")

    print("\n--- Test Case: Empty Text ---")
    result_empty = classifier.classify_document("")
    print(f"  Processing empty text: {'Success' if result_empty['success'] else 'Failed'} - {result_empty['error_message']}")
