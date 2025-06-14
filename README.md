# Multi-Agent AI System 🤖

A multi-agent AI system that can handle different types of documents (PDFs, JSON files, and emails) and process them intelligently. It figures out what type of document you're dealing with and sends it to the right agent for processing.

## What it does 📋

This system takes your documents and:
- 📄 Classifies PDFs (like invoices, contracts, reports)
- 🔍 Validates and processes JSON data
- 📧 Analyzes emails for intent and urgency
- 🧠 Keeps track of everything in a shared memory so all agents can work together

## How it works ⚙️

The system has three main agents:

**Classifier Agent** 📊 - Takes PDF documents and figures out what they are (invoice, contract, etc.)

**JSON Agent** 🔧 - Handles JSON files, validates them, and extracts important data

**Email Agent** 📮 - Reads emails and determines what the sender wants and how urgent it is

All agents share information through a memory system so they can work together on complex tasks.

## What you need 📋

- Python 3.8 or newer 🐍
- At least 4GB of RAM (for running the AI model) 💾
- Ollama installed on your computer 🛠️

## Setup 🚀

### 1. Install Ollama 📥

Go to https://ollama.com/download and install Ollama for your operating system.

After installing, run these commands:

```bash
ollama pull mistral
ollama serve
```

The server will run in the background.

### 2. Get the code 📂

```bash
git clone https://github.com/Prabhatcodes-x/Multi-Agent-AI-System.git
cd Multi-Agent-AI-System
pip install -r requirements.txt
```

### 3. Run it ▶️

```bash
python main.py
```

## What happens when you run it ✨

The system will:
1. Process the sample files in the `sample_inputs` folder 📁
2. Show you what it's doing in the terminal 💻
3. Save detailed logs to `output_logs/agent_activity.log` 📝
4. Keep track of all processed documents in `output_logs/shared_memory.json` 🗄️

## Project structure 📁

```
multi_agent_system/
├── agents/                 # The three main agents
│   ├── classifier_agent.py
│   ├── email_agent.py
│   └── json_agent.py
├── memory/                 # Shared memory system
│   └── shared_memory.py
├── output_logs/           # Logs and results (created when you run it)
├── sample_inputs/         # Test files to try it out
├── utils/                 # Helper functions
├── main.py               # Main file to run
└── requirements.txt      # Python packages needed
```

## Adding your own files 📄

Put your files in the `sample_inputs` folder:
- PDFs: Any PDF document you want classified 📄
- JSON files: Structured data you want validated 🔧
- Text files: Email content you want analyzed 📧

The system will automatically detect what type of file it is and process it accordingly.

## If something goes wrong 🚨

**"Connection refused" error**: Make sure Ollama is running with `ollama serve` ⚠️

**"Model not found"**: Download the model with `ollama pull mistral` 📥

**Permission errors**: Make sure the `output_logs` folder can be written to 📝

**Import errors**: Reinstall requirements with `pip install -r requirements.txt` 🔄

## How to customize it 🛠️

You can modify the agents to handle different types of documents or add new processing logic. Each agent is in its own file in the `agents` folder.

The system uses the Mistral AI model through Ollama, but you can change this in the configuration if you want to use a different model.

## What makes it useful ⭐

- **Works offline**: Everything runs on your computer, no data sent to external servers 🔒
- **Handles multiple formats**: PDFs, JSON, and emails all in one system 📚
- **Smart fallbacks**: If the AI model fails, it falls back to rule-based processing 🧠
- **Keeps context**: All agents share information so they can work together 🤝
- **Easy to extend**: Add new agents or modify existing ones 🔧

## Performance ⚡

- PDF processing: Usually takes 2-5 seconds per document 📄
- JSON validation: Very fast, under 1 second ⚡
- Email analysis: 1-3 seconds per email 📧
- Memory usage: About 1-2GB when running (mostly for the AI model) 💾

## Contributing 🤝

If you want to improve this project:
1. Fork the repository 🍴
2. Make your changes ✏️
3. Test them with the sample files 🧪
4. Submit a pull request 📤

Try to keep the code simple and well-commented so others can understand it.

## License 📄

MIT License - you can use this code for whatever you want. 🎉

## Credits 🙏

Built using:
- Ollama for running AI models locally 🤖
- Mistral AI for the language model 🧠
- pdfplumber for reading PDF files 📄
- Standard Python libraries for everything else 🐍
