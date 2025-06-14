import requests
import logging
import json
from typing import Optional

logger = logging.getLogger(__name__)

def call_ollama_llm(prompt: str, model: str = "mistral:latest", timeout: int = 180) -> Optional[str]:
    """
    Generate a response from the specified Ollama LLM based on the input prompt.

    Args:
        prompt (str): Input query for the model.
        model (str): Ollama model identifier.
        timeout (int): Request timeout in seconds.

    Returns:
        Optional[str]: Generated text response or None if failed.

    Raises:
        requests.exceptions.RequestException: For network or server errors.
        json.JSONDecodeError: For malformed JSON.
        ValueError: For missing or empty responses.
    """
    url = "http://localhost:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 512
        }
    }

    try:
        logger.info(f"Calling Ollama LLM with model '{model}'")
        response = requests.post(url, json=data, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        text = result.get("response", "").strip()

        if not text:
            logger.warning("Received empty response from LLM.")
            raise ValueError("Empty response from LLM.")

        logger.info("LLM response received successfully.")
        return text

    except requests.exceptions.Timeout:
        logger.error(f"Request timed out after {timeout} seconds.")
        raise
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error: Unable to reach Ollama server at {url}")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Unexpected request error: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}. Response: {response.text if 'response' in locals() else 'N/A'}")
        raise
    except ValueError as e:
        logger.error(f"Invalid response: {e}")
        raise
    except Exception as e:
        logger.error(f"Unhandled exception during LLM call: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )

    print("--- Testing Ollama LLM Call ---")
    test_prompt = "What is the capital of France? Respond concisely."
    test_model = "llama2:latest"

    try:
        print(f"Calling model '{test_model}'...")
        response_text = call_ollama_llm(test_prompt, model=test_model, timeout=60)
        print("\n--- LLM Response ---")
        print(response_text)
    except Exception as e:
        print("\n--- LLM Call Failed ---")
        print(f"Error: {e}")
        print("Ensure Ollama is running and the model is available.")

    print("\n--- Testing LLM Call with Empty Response (Simulated) ---")
    class MockResponse:
        def __init__(self, status_code, json_data):
            self._json_data = json_data
            self.status_code = status_code
            self.text = json.dumps(json_data)
        def json(self):
            return self._json_data
        def raise_for_status(self):
            if self.status_code >= 400:
                raise requests.exceptions.HTTPError(response=self)

    original_post = requests.post
    def mock_post(*args, **kwargs):
        if "simulated empty" in kwargs.get("json", {}).get("prompt", ""):
            print("[SIMULATED] Returning empty response from Ollama.")
            return MockResponse(200, {"response": ""})
        return original_post(*args, **kwargs)

    requests.post = mock_post

    try:
        call_ollama_llm("This is a simulated empty response prompt", model="mistral:latest")
    except ValueError as e:
        print(f"Caught expected error: {e}")
    finally:
        requests.post = original_post
