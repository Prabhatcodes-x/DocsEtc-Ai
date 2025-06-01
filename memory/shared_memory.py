import logging
import json
import os  # For file operations

class SharedMemory:
    _log_file = os.path.join("output_logs", "shared_memory.json")  # Path to the log file
    logs = []  # In-memory cache of logs

    @staticmethod
    def initialize():
        # Check if directory exists, create it if it doesn't
        log_dir = os.path.dirname(SharedMemory._log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            logging.info(f"Created log directory: {log_dir}")

        # Load existing logs from the file, if available
        if os.path.exists(SharedMemory._log_file):
            try:
                with open(SharedMemory._log_file, 'r', encoding='utf-8') as f:
                    SharedMemory.logs = json.load(f)
                logging.info(f"SharedMemory initialized and loaded {len(SharedMemory.logs)} entries from {SharedMemory._log_file}")
            except json.JSONDecodeError:
                logging.warning(f"SharedMemory: Could not decode JSON from {SharedMemory._log_file}. File might be corrupted or empty. Starting with empty logs.")
                SharedMemory.logs = []
            except Exception as e:
                logging.error(f"Error loading SharedMemory from {SharedMemory._log_file}: {e}. Starting with empty logs.")
                SharedMemory.logs = []
        else:
            logging.info("SharedMemory initialized. No existing log file found. Starting fresh.")

    @staticmethod
    def log(conversation_id, data):
        """
        Append data to the in-memory log list.
        Each entry contains a conversation ID and associated data.
        """
        SharedMemory.logs.append({"conversation_id": conversation_id, "data": data})
        logging.info(f"Logged for {conversation_id}: {data}")
        SharedMemory._save_to_file()  # Save after each log (can be optimized to save periodically)

    @staticmethod
    def _save_to_file():
        """
        Save current in-memory logs to a JSON file.
        """
        try:
            with open(SharedMemory._log_file, 'w', encoding='utf-8') as f:
                json.dump(SharedMemory.logs, f, indent=4)  # Save in readable JSON format
        except IOError as e:
            logging.error(f"Error saving SharedMemory to file {SharedMemory._log_file}: {e}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while saving SharedMemory: {e}")

    @staticmethod
    def get_conversation(conversation_id):
        """
        Retrieve all log entries for a specific conversation ID.
        """
        return [entry['data'] for entry in SharedMemory.logs if entry['conversation_id'] == conversation_id]

    @staticmethod
    def get_all_logs():
        """
        Retrieve all logged entries from memory.
        """
        return SharedMemory.logs
