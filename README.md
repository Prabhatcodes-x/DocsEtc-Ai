# DocFlow AI
# 🤖 Multi-Agent AI System for Document Processing

> A powerful multi-agent AI system that intelligently processes PDFs, JSON files, and emails using specialized AI agents working together seamlessly.

## 🎯 What Does This Do?

Ever wished you had a smart assistant that could automatically understand and process different types of documents? That's exactly what this system does! 

Whether you throw a PDF invoice, a JSON data file, or an email at it, the system figures out what it is and processes it using the right specialized agent. Think of it as having four different AI experts working together on your documents.

## 🏗️ System Architecture

Our system has **four smart agents** that work together like a well-coordinated team:

### 📄 PDF Agent
- **What it does**: Reads PDF files and extracts all the text content
- **Superpower**: Can handle multi-page documents and messy PDFs
- **Tech magic**: Uses pdfplumber to extract text like a pro

### 🎯 Classifier Agent  
- **What it does**: Figures out what type of document you've got
- **Smart features**: Knows if it's an invoice, contract, quote, or general document
- **How it works**: Uses AI (Mistral model) first, falls back to rules if needed
- **Output**: Tells you the document type with confidence score

### 📧 Email Agent
- **What it does**: Processes emails and extracts key information
- **Smart features**: Detects urgency levels and formats data for CRM systems
- **Bonus**: Automatically identifies email structure and intent

### 📊 JSON Agent
- **What it does**: Handles structured data files with validation
- **Smart features**: Checks for missing fields and data quality issues
- **Output**: Clean, validated data ready for use

### 🧠 Shared Memory
- **The coordinator**: Keeps track of everything that happens
- **Storage**: Saves all results in `output_logs/shared_memory.json`
- **Why it's cool**: Complete traceability of who did what and when

## 🛠️ Tech Stack

- 🐍 **Python 3.8+**: Our foundation
- 🦙 **Ollama**: Runs AI models locally (no cloud needed!)
- 🤖 **Mistral**: The smart AI brain for classification
- 📖 **pdfplumber**: PDF text extraction wizard
- 🌐 **requests**: Talks to the AI model
- 📝 **logging**: Keeps detailed records of everything

## 🚀 Getting Started

### Step 1: Check Your Python
```bash
python --version
# Should be 3.8 or newer
```

### Step 2: Get Ollama Running
1. 📥 Download from: https://ollama.com/download
2. 🔧 Install it on your system
3. 🤖 Download the AI model:
   ```bash
   ollama pull mistral:latest
   ```
4. 🚀 Start the server:
   ```bash
   ollama serve
   ```
   
💡 **Pro tip**: Keep this running in a separate terminal window!

### Step 3: Set Up the Project
```bash
# Get the code
git clone https://github.com/Prabhatcodes-x/Multi-Agent-AI-System.git
cd Multi-Agent-AI-System

# Install dependencies (just 2 packages!)
pip install -r requirements.txt
```

## 🎮 How to Use

### Quick Demo
1. ✅ Make sure Ollama is running (`ollama serve`)
2. 📁 Add your test files to `sample_inputs/`:
   - `sample_invoice.pdf`
   - `sample_email.txt` 
   - `sample_invoice.json`
3. 🚀 Run the magic:
   ```bash
   python main.py
   ```

### What You'll See
- 💬 **Live updates** in your terminal showing what each agent is doing
- 📋 **Detailed logs** saved to `output_logs/agent_activity.log`
- 🧠 **Smart results** stored in `output_logs/shared_memory.json`

## 📁 Project Structure

```
Multi-Agent-AI-System/
├── 🤖 agents/                  # The AI workforce
│   ├── pdf_agent.py           # PDF processing specialist
│   ├── classifier_agent.py    # Document type detective
│   ├── email_agent.py         # Email processing expert
│   └── json_agent.py          # Data validation guru
├── 🧠 memory/                  # Shared knowledge base
│   └── shared_memory.py       # Cross-agent communication
├── 🔧 utils/                   # Helper tools
│   ├── file_utils.py          # File handling utilities
│   └── llm_utils.py           # AI model communication
├── 📂 sample_inputs/           # Test files go here
├── 📊 output_logs/             # Results and logs
├── 🚀 main.py                  # The orchestrator
├── 📋 requirements.txt         # Dependencies list
└── 📖 README.md               # You are here!
```

## ✨ Cool Features

- 🎯 **Smart Routing**: Automatically detects file types and sends them to the right agent
- 🛡️ **Bulletproof**: Handles errors gracefully with backup systems
- 👀 **Full Visibility**: See exactly what's happening at every step
- 💾 **Memory**: Remembers everything across sessions
- 🔄 **Reliable**: Falls back to rule-based processing if AI is down

## 📦 Dependencies

Create `requirements.txt` with just these two:
```txt
requests>=2.28.0
pdfplumber>=0.7.0
```

## 💻 System Requirements

- 🐍 **Python**: 3.8+
- 🧠 **RAM**: 4GB minimum (8GB recommended)
- 💽 **Storage**: 2GB for Ollama and models
- 🌐 **Internet**: Just for initial setup

## 🚨 Troubleshooting

### 🔧 Common Fixes

**Can't connect to Ollama?**
- Make sure it's running: `ollama serve`
- Check if something else is using port 11434

**AI model missing?**
- List what you have: `ollama list`
- Download again: `ollama pull mistral:latest`

**Files not found?**
- Double-check your `sample_inputs/` folder
- Make sure file permissions are correct

## 🤝 Want to Contribute?

We'd love your help! Here's how:

1. 🍴 Fork this repo
2. 🌿 Create a new branch for your feature
3. ✨ Make your awesome changes
4. 🧪 Test everything works
5. 🚀 Submit a pull request

## 📄 License

MIT License - feel free to use this however you want!

---

**Made with ❤️ for smarter document processing**

*Questions? Issues? Ideas? Open an issue and let's chat!* 💬
