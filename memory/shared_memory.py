import logging
import json
import os
from typing import List, Dict, Any
from datetime import datetime

# Initialize module-level logger
logger = logging.getLogger(__name__)

class SharedMemory:
    # Static variables for log file path and in-memory log storage
    _log_file = os.path.join("output_logs", "shared_memory.json")
    logs = []

    @staticmethod
    def initialize():
        """
        Set up the logging directory and load existing data from file into memory.
        Should be called once during application startup.
        """
        log_dir = os.path.dirname(SharedMemory._log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            logger.info(f"Created log directory: {log_dir}")

        if os.path.exists(SharedMemory._log_file):
            try:
                with open(SharedMemory._log_file, 'r', encoding='utf-8') as f:
                    SharedMemory.logs = json.load(f)
                logger.info(f"Loaded {len(SharedMemory.logs)} log entries from {SharedMemory._log_file}")
            except json.JSONDecodeError:
                logger.warning("Failed to decode log file JSON. Initializing with empty logs.")
                SharedMemory.logs = []
            except Exception as e:
                logger.error(f"Error reading log file: {e}")
                SharedMemory.logs = []
        else:
            logger.info("No existing log file found. Starting with empty logs.")

    @staticmethod
    def store_result(data: Dict[str, Any]):
        """
        Add a single log entry to memory. Requires a 'conversation_id' key.
        """
        if not isinstance(data, dict):
            logger.error(f"Invalid data type: {type(data)}. Expected a dictionary.")
            return

        if 'conversation_id' not in data:
            logger.warning("Missing 'conversation_id'. Assigning fallback ID.")
            data['conversation_id'] = f"generic_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        SharedMemory.logs.append(data)
        logger.info(f"Appended log for conversation_id: {data.get('conversation_id')}. Total logs: {len(SharedMemory.logs)}")

    @staticmethod
    def _save_to_file():
        """
        Persist in-memory log data to the JSON file.
        """
        try:
            with open(SharedMemory._log_file, 'w', encoding='utf-8') as f:
                json.dump(SharedMemory.logs, f, indent=4)
            logger.info(f"Saved {len(SharedMemory.logs)} logs to {SharedMemory._log_file}")
        except IOError as e:
            logger.error(f"I/O error during save: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during save: {e}")

    @staticmethod
    def get_conversation_results(conversation_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all logs matching a specific conversation ID.
        """
        return [entry for entry in SharedMemory.logs if entry.get('conversation_id') == conversation_id]

    @staticmethod
    def get_all_results() -> List[Dict[str, Any]]:
        """
        Return all stored log entries.
        """
        return SharedMemory.logs

if __name__ == "__main__":
    # Setup logger for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

    # Remove previous log file for clean testing
    if os.path.exists(SharedMemory._log_file):
        os.remove(SharedMemory._log_file)
        logger.info(f"Removed existing log file: {SharedMemory._log_file}")

    SharedMemory.initialize()

    # Sample log entries for testing
    test_data1 = {'conversation_id': 'conv_001', 'type': 'PDF', 'status': 'processed', 'data_field': 'value1'}
    test_data2 = {'conversation_id': 'conv_002', 'type': 'Email', 'status': 'classified', 'data_field': 'value2'}
    test_data3 = {'conversation_id': 'conv_001', 'type': 'PDF', 'status': 'validated', 'data_field': 'value3'}

    SharedMemory.store_result(test_data1)
    SharedMemory.store_result(test_data2)
    SharedMemory.store_result(test_data3)

    print("\n--- All results after storing ---")
    all_results = SharedMemory.get_all_results()
    print(f"Total results in memory: {len(all_results)}")

    print("\n--- Results for conv_001 ---")
    conv1_results = SharedMemory.get_conversation_results('conv_001')
    print(f"Results for 'conv_001': {len(conv1_results)} entries")
    print(json.dumps(conv1_results, indent=2))

    SharedMemory._save_to_file()
    print(f"\nResults saved to {SharedMemory._log_file}")

    print("\n--- Re-initializing SharedMemory to load from file ---")
    SharedMemory.logs = []
    SharedMemory.initialize()
    reloaded_results = SharedMemory.get_all_results()
    print(f"Total results after re-initialization: {len(reloaded_results)}")
    print(json.dumps(reloaded_results, indent=2))

    print("\n--- Testing with invalid data type ---")
    SharedMemory.store_result("this is a string, not a dict")
    print(f"Total results after invalid store attempt: {len(SharedMemory.get_all_results())}")
