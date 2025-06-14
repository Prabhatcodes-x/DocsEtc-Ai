import logging
import json
import os
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class JsonAgent:
    """
    The JsonAgent class is designed to process JSON files. Its primary responsibilities include:
    1. Loading JSON data from a specified file path.
    2. Validating the loaded data against a predefined target schema.
    3. Identifying any missing fields based on the schema.
    4. Performing deeper validation for specific field types and structures (e.g., nested objects).
    5. Reformatting the data to align with the target schema.
    6. Providing a comprehensive report of the processing outcome, including success status,
       processed data, missing fields, validation errors, and any encountered exceptions.
    """

    # Defines the expected keys in the JSON data for validation and extraction.
    # This schema can be expanded to include nested fields or enforce specific types.
    TARGET_SCHEMA = ['id', 'date', 'amount', 'customer', 'items', 'currency']

    def __init__(self):
        """
        Initializes the JsonAgent.
        """
        self.agent_name = "JSON_Agent"
        logger.info(f"{self.agent_name} initialized.")

    def process_json(self, file_path: str) -> Dict[str, Any]:
        """
        Loads, validates, and reformats JSON data from a specified file path.

        This method encapsulates the entire JSON processing workflow, from file existence
        checks to data parsing, schema validation, and detailed error reporting.

        Args:
            file_path (str): The absolute or relative path to the JSON file to be processed.

        Returns:
            Dict[str, Any]: A dictionary containing the comprehensive processing result:
                            - 'success' (bool): True if processing completed without critical errors.
                            - 'agent' (str): The name of the processing agent.
                            - 'timestamp' (str): ISO formatted timestamp of when processing occurred.
                            - 'file_path' (str): The path of the file that was processed.
                            - 'processed_data' (Dict[str, Any]): The data extracted and reformatted
                                                                 according to the TARGET_SCHEMA.
                            - 'missing_fields' (List[str]): A list of fields from TARGET_SCHEMA
                                                            that were not found in the input JSON.
                            - 'validation_errors' (List[str]): A list of specific validation issues
                                                               found within the data (e.g., incorrect types,
                                                               missing nested keys).
                            - 'error_message' (Optional[str]): A general error description if a critical
                                                               processing failure occurred.
                            - 'status' (str): A descriptive status of the processing outcome
                                              ('processed', 'file_not_found', 'invalid_json', 'processing_failed').
        """
        result = {
            'success': False,
            'agent': self.agent_name,
            'timestamp': datetime.now().isoformat(),
            'file_path': file_path,
            'processed_data': {},
            'missing_fields': [],
            'validation_errors': [],
            'error_message': None,
            'status': 'failed'
        }

        logger.info(f"JSONAgent: Starting processing for file: {file_path}")

        try:
            # Step 1: Verify the existence of the specified JSON file.
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"JSON file not found at: {file_path}")

            # Step 2: Read and parse the JSON data from the file.
            # Using 'utf-8' encoding is a good practice for broad compatibility.
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            logger.info(f"JSONAgent: Successfully loaded JSON data from {file_path}.")

            # Step 3: Identify any top-level fields from the TARGET_SCHEMA that are missing
            # in the loaded JSON data.
            missing_fields = [field for field in self.TARGET_SCHEMA if field not in json_data]
            if missing_fields:
                logger.warning(f"JSONAgent: Missing required fields in input data: {missing_fields}")
                result['missing_fields'] = missing_fields

            # Step 4: Extract and reformat data based on the TARGET_SCHEMA.
            # This ensures that only relevant fields are carried forward, with `None` for missing ones.
            reformatted_data = {field: json_data.get(field, None) for field in self.TARGET_SCHEMA}

            # Step 5: Perform deeper, specific validation for individual fields.

            # Validate the 'customer' field: ensure it's a dictionary and contains expected nested keys.
            if 'customer' in reformatted_data and reformatted_data['customer'] is not None:
                if not isinstance(reformatted_data['customer'], dict):
                    warning_msg = f"JSONAgent: 'customer' field is not a dictionary. Type: {type(reformatted_data['customer'])}"
                    logger.warning(warning_msg)
                    result['validation_errors'].append(warning_msg)
                else:
                    # Check for essential nested fields within the 'customer' dictionary.
                    if 'name' not in reformatted_data['customer'] or 'email' not in reformatted_data['customer']:
                        warning_msg = "JSONAgent: 'customer' dictionary is missing 'name' or 'email'."
                        logger.warning(warning_msg)
                        result['validation_errors'].append(warning_msg)

            # Validate the 'amount' field: attempt to convert it to a float.
            if 'amount' in reformatted_data and reformatted_data['amount'] is not None:
                try:
                    reformatted_data['amount'] = float(reformatted_data['amount'])
                except (ValueError, TypeError):
                    warning_msg = f"JSONAgent: 'amount' field '{reformatted_data['amount']}' is not a valid number."
                    logger.warning(warning_msg)
                    result['validation_errors'].append(warning_msg)

            # Validate the 'id' field: ensure it is either a string or an integer.
            if 'id' in reformatted_data and reformatted_data['id'] is not None:
                if not isinstance(reformatted_data['id'], (str, int)):
                    warning_msg = f"JSONAgent: 'id' field '{reformatted_data['id']}' is not a valid string or integer."
                    logger.warning(warning_msg)
                    result['validation_errors'].append(warning_msg)

            # If execution reaches here, the file was successfully loaded and basic processing completed.
            # Set success to True, even if validation errors or missing non-critical fields exist.
            result['success'] = True
            result['status'] = 'processed'
            result['processed_data'] = reformatted_data

            logger.info(f"JSONAgent: Successfully processed data for {file_path}. Status: {result['status']}")
            return result

        except FileNotFoundError as e:
            # Handle cases where the specified file does not exist.
            logger.error(f"JSONAgent: {e}")
            result['error_message'] = str(e)
            result['status'] = 'file_not_found'
            return result
        except json.JSONDecodeError as e:
            # Handle cases where the file contains invalid JSON syntax.
            logger.error(f"JSONAgent: Invalid JSON format in {file_path}: {e}")
            result['error_message'] = f"Invalid JSON format: {e}"
            result['status'] = 'invalid_json'
            return result
        except Exception as e:
            # Catch any other unexpected errors during the processing.
            logger.error(f"JSONAgent: An unexpected error occurred while processing JSON file {file_path}: {str(e)}")
            result['error_message'] = str(e)
            result['status'] = 'processing_failed'
            return result

if __name__ == "__main__":
    # Configure basic logging to display informative messages to the console
    # when the script is executed directly for testing purposes.
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

    json_agent = JsonAgent()

    # Ensure the 'sample_inputs' directory exists to store test JSON files.
    if not os.path.exists('sample_inputs'):
        os.makedirs('sample_inputs')

    # --- Test Cases ---

    # Test Case 1: Valid JSON file with all expected fields.
    valid_json_path = "sample_inputs/valid_invoice.json"
    valid_json_content = {
        "id": "INV-001-2024",
        "date": "2024-06-14",
        "amount": 1500.75,
        "currency": "USD",
        "customer": {
            "name": "Acme Corp",
            "email": "info@acmecorp.com"
        },
        "items": [
            {"product": "Laptop", "qty": 1, "price": 1200.00},
            {"product": "Mouse", "qty": 2, "price": 15.37}
        ]
    }
    with open(valid_json_path, 'w', encoding='utf-8') as f:
        json.dump(valid_json_content, f, indent=4)
    print(f"\n--- Testing Valid JSON: {valid_json_path} ---")
    result_valid = json_agent.process_json(valid_json_path)
    print(json.dumps(result_valid, indent=2))

    # Test Case 2: JSON file with some required fields missing from TARGET_SCHEMA.
    missing_fields_json_path = "sample_inputs/missing_fields_invoice.json"
    missing_fields_json_content = {
        "id": "INV-002-2024",
        "date": "2024-06-14",
        "customer": {
            "name": "Beta Inc",
            "email": "beta@example.com"
        }
        # 'amount' and 'items' are intentionally omitted here.
    }
    with open(missing_fields_json_path, 'w', encoding='utf-8') as f:
        json.dump(missing_fields_json_content, f, indent=4)
    print(f"\n--- Testing JSON with Missing Fields: {missing_fields_json_path} ---")
    result_missing = json_agent.process_json(missing_fields_json_path)
    print(json.dumps(result_missing, indent=2))

    # Test Case 3: JSON file with invalid format (e.g., incorrect syntax).
    invalid_json_path = "sample_inputs/invalid_format.json"
    with open(invalid_json_path, 'w', encoding='utf-8') as f:
        f.write("{'id': 'INV-003', 'amount': 100.00,}") # Deliberately invalid JSON (single quotes, trailing comma)
    print(f"\n--- Testing Invalid JSON Format: {invalid_json_path} ---")
    result_invalid_format = json_agent.process_json(invalid_json_path)
    print(json.dumps(result_invalid_format, indent=2))

    # Test Case 4: Attempt to process a file that does not exist.
    non_existent_path = "sample_inputs/non_existent.json"
    print(f"\n--- Testing Non-Existent File: {non_existent_path} ---")
    result_non_existent = json_agent.process_json(non_existent_path)
    print(json.dumps(result_non_existent, indent=2))

    # Test Case 5: JSON file where 'customer' field is of an incorrect type (string instead of dict).
    invalid_customer_json_path = "sample_inputs/invalid_customer.json"
    invalid_customer_json_content = {
        "id": "INV-004",
        "date": "2024-06-15",
        "amount": 200.00,
        "customer": "customer_string_instead_of_dict" # Invalid customer type
    }
    with open(invalid_customer_json_path, 'w', encoding='utf-8') as f:
        json.dump(invalid_customer_json_content, f, indent=4)
    print(f"\n--- Testing JSON with Invalid Customer Format: {invalid_customer_json_path} ---")
    result_invalid_customer = json_agent.process_json(invalid_customer_json_path)
    print(json.dumps(result_invalid_customer, indent=2))

    # Test Case 6: JSON file with 'customer' as a dictionary but missing required nested fields ('email').
    missing_nested_customer_json_path = "sample_inputs/missing_nested_customer.json"
    missing_nested_customer_json_content = {
        "id": "INV-005",
        "date": "2024-06-16",
        "amount": 300.00,
        "customer": {
            "name": "Charlie" # 'email' is intentionally missing.
        }
    }
    with open(missing_nested_customer_json_path, 'w', encoding='utf-8') as f:
        json.dump(missing_nested_customer_json_content, f, indent=4)
    print(f"\n--- Testing JSON with Missing Nested Customer Fields: {missing_nested_customer_json_path} ---")
    result_missing_nested_customer = json_agent.process_json(missing_nested_customer_json_path)
    print(json.dumps(result_missing_nested_customer, indent=2))

    # Clean up all created test files after execution.
    for f in [valid_json_path, missing_fields_json_path, invalid_json_path, invalid_customer_json_path, missing_nested_customer_json_path]:
        if os.path.exists(f):
            os.remove(f)
            logging.info(f"Cleaned up test file: {f}")
