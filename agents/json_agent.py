import logging  # Enable logging
from memory.shared_memory import SharedMemory
from datetime import datetime

class JSONAgent:
    # Example target schema; you can expand it with nested fields or types if needed
    TARGET_SCHEMA = ['id', 'date', 'amount', 'customer']

    def process(self, conversation_id, json_data):
        logging.info(f"JSONAgent: Processing data for conversation_id: {conversation_id}")
        
        # Check for any missing fields from the target schema
        missing_fields = [field for field in self.TARGET_SCHEMA if field not in json_data]

        if missing_fields:
            logging.warning(f"JSONAgent: Missing required fields in input data: {missing_fields}")
            # Here, you can choose how to handle missing fields.
            # Currently, we just log a warning and proceed with partial data.
            # Alternatively, you could send an intent like "data_incomplete".

        # Extract and reformat fields according to the target schema
        reformatted_data = {field: json_data.get(field, None) for field in self.TARGET_SCHEMA}

        # Example: Deeper validation for the 'customer' field (should be a dictionary)
        if 'customer' in reformatted_data and reformatted_data['customer'] is not None:
            if not isinstance(reformatted_data['customer'], dict):
                logging.warning(f"JSONAgent: 'customer' field is not a dictionary. Type: {type(reformatted_data['customer'])}")
                # You can optionally add validation errors here
                # result['validation_errors'] = result.get('validation_errors', []) + ["Customer field is not a dictionary"]
            else:
                # Nested field check: ensure 'name' and 'email' exist
                if 'name' not in reformatted_data['customer'] or 'email' not in reformatted_data['customer']:
                    logging.warning("JSONAgent: 'customer' dictionary is missing 'name' or 'email'.")
                    # result['validation_errors'] = result.get('validation_errors', []) + ["Customer name or email missing"]
        
        # Construct the result dictionary
        result = {
            'status': 'processed',  # Processing status
            'missing_fields': missing_fields,
            'reformatted_data': reformatted_data,
            # 'validation_errors': result.get('validation_errors', [])  # Optional
        }

        # Log the result to SharedMemory
        # Store timestamp in ISO 8601 format
        SharedMemory.log(conversation_id, {
            'json_agent_result': result,
            'timestamp': datetime.now().isoformat()
        })

        logging.info(f"JSONAgent: Successfully processed data for conversation_id: {conversation_id}. Result: {result['status']}")
        
        return result
