You got it! Here's the README.md file in English for your GitHub repository.

Multi-Agent AI System for Document and Email Processing
Project Objective
This project builds a multi-agent AI system designed to accept inputs in PDF, JSON, or Email (plain text) formats. It classifies the format and intent of the input, then routes it to the appropriate agent for processing. The system maintains a shared context (e.g., sender, topic, last extracted fields) to enable chaining and traceability across different processing steps.

System Overview
This system is orchestrated through three primary agents, complemented by a shared memory module that maintains context:

Classifier Agent:

Input: Raw text extracted from PDF documents.
Classifies: The intent of the document (e.g., Invoice, Quote Request, Contract, General Inquiry).
Mechanism: Utilizes LLM-based classification. If the LLM call fails, it gracefully falls back to a rule-based mechanism to determine intent.
JSON Agent:

Input: Structured JSON payloads.
Processes: Extracts and reformats data to a predefined target schema.
Validation: Flags any anomalies or missing required fields within the input JSON data.
Email Agent:

Input: Email content (plain text).
Extracts: The email's intent and urgency (e.g., High, Normal).
Formatting: Presents the extracted data in a format suitable for CRM-style usage. Like the Classifier Agent, it uses LLM-based classification with a rule-based fallback if the LLM is unavailable or fails.
Shared Memory Module:
This is a lightweight module responsible for storing crucial information from all agents in an output_logs/shared_memory.json file. It records details such as source, type, timestamp, extracted values, and conversation IDs, ensuring context and traceability are maintained across the entire system.

Technology Stack
Python: The primary programming language for the entire system.
Ollama: Utilized to run open-source Large Language Models (LLMs) locally. Specifically, the mistral:latest model is used for intent classification.
pdfplumber: A robust library for extracting text content from PDF files.
requests: Used for making HTTP requests to interact with the Ollama API.
logging: Employed for tracking and logging application activities, including successes, warnings, and errors.
Setup Instructions
Follow these steps to get the system up and running on your machine:

Install Python:

Ensure you have Python 3.8 or a newer version installed on your system. You can verify this by running python --version or python3 --version in your terminal.
Install Ollama and Download the Model:

Download and Install Ollama: Get Ollama from their official website: https://ollama.com/download. Follow the installation instructions specific to your operating system.
Pull the mistral model: After installing Ollama, open a command prompt or terminal and download the mistral model:
Bash

ollama pull mistral
Important: Ensure the Ollama server is running before you execute the script. It typically runs in the background, but you can manually start it by running ollama serve in your terminal.
Clone the Project and Install Dependencies:

Clone this GitHub repository to your local machine, or download it as a ZIP file and extract it.
Navigate into the project directory (multi_agent_system):
Bash

cd path/to/your/multi_agent_system
Install all necessary Python dependencies. These are listed in the requirements.txt file:
Bash

pip install -r requirements.txt
How to Run the Project
Once all setup steps are complete and the Ollama server is running:

Ensure that your sample_inputs/ folder contains sample_email.txt, sample_invoice.json, and sample_invoice.pdf files.
Open a command prompt or terminal within the project directory (multi_agent_system).
Execute the following command:
Bash

python main.py
Expected Output and Logs
Output will be displayed directly in your terminal as the application runs, providing information about each agent's processing, messages about successful LLM calls or fallbacks, and warnings from the JSON agent regarding any missing fields.
All detailed logs will be saved in a file named output_logs/agent_activity.log.
Shared context and processing results logged by the agents will be persisted in a JSON file named output_logs/shared_memory.json, making it available across application runs.
Project Structure
multi_agent_system/
├── agents/             # Code for the different agents (Classifier, Email, JSON)
│   ├── classifier_agent.py
│   ├── email_agent.py
│   └── json_agent.py
├── memory/             # Shared Memory module
│   └── shared_memory.py
├── output_logs/        # This folder is created at runtime to store logs and persisted memory
├── sample_inputs/      # Sample input files (email, json, pdf)
│   ├── sample_email.txt
│   ├── sample_invoice.json
│   └── sample_invoice.pdf
├── utils/              # General utility functions (for LLM interaction and file operations)
│   ├── file_utils.py
│   └── llm_utils.py
├── main.py             # The main entry point and orchestrator of the system
├── README.md           # This documentation file
└── requirements.txt    # List of Python dependencies
