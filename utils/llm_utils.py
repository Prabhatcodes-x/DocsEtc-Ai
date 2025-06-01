import requests
import logging  # Add logging

def call_ollama_llm(prompt, model="mistral:latest", timeout=90):  # Increased timeout
    url = "http://localhost:11434/api/generate"  # New API endpoint for Ollama
    # Note: Use /api/generate instead of /v1/generate for simpler single-turn interactions with Ollama
    # If using chat models, /api/chat is also an option.
    
    # Data structure for Ollama's /api/generate endpoint
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,  # We want the complete response at once
        "options": {
            "temperature": 0.3,
            "num_predict": 512  # Use num_predict instead of max_tokens
        }
    }

    try:
        logging.info(f"Calling Ollama LLM with model: {model}, prompt (start): {prompt[:100]}...")
        response = requests.post(url, json=data, timeout=timeout)
        response.raise_for_status()  # Will raise exception for HTTP errors (4xx or 5xx)
        result = response.json()
        
        # Ollama's /api/generate response contains a 'response' key
        text = result.get("response", "").strip()

        if not text:
            logging.error(f"Empty response from Ollama LLM for prompt: {prompt[:100]}...")
            raise ValueError("Empty response from LLM")  # Raise exception

        logging.info("Ollama LLM call successful.")
        return text

    except requests.exceptions.Timeout:
        logging.error(f"[Ollama Error] Request timed out after {timeout} seconds.")
        raise  # Raise exception on timeout
    except requests.exceptions.RequestException as e:
        # Handle network errors (connection refused, DNS errors, bad status codes)
        logging.error(f"[Ollama Error] Network or HTTP error: {e}. Response text: {response.text if 'response' in locals() else 'N/A'}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"[Ollama Error] Could not decode JSON response from Ollama: {e}. Raw response: {response.text if 'response' in locals() else 'N/A'}")
        raise
    except ValueError as e:  # Will catch 'Empty response from LLM'
        logging.error(f"[Ollama Error] Data processing error: {e}")
        raise
    except Exception as e:
        # Catch any other unexpected errors
        logging.error(f"[Ollama Error] An unexpected error occurred: {e}")
        raise
