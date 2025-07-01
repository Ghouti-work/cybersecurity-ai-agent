# Cybersecurity AI Agent Platform - Installation & Usage Guide

🛡️ **Comprehensive Guide for the Enhanced Cybersecurity AI Agent Platform**

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installation Methods](#installation-methods)
4. [Configuration](#configuration)
5. [Usage Guide](#usage-guide)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)
8. [Development](#development)

---

## 🎯 Overview

The Cybersecurity AI Agent Platform is an advanced, AI-powered cybersecurity toolkit that combines multiple AI frameworks for comprehensive security analysis, penetration testing, and threat intelligence.

### 🌟 Key Features

- **🤖 Local AI Models**: DeepSeek Coder 1.3B for secure, offline processing
- **🔮 Gemini Integration**: Advanced reasoning for document processing and PentestGPT
- **📡 RAG Knowledge Base**: Intelligent information retrieval and analysis
- **🔒 VPN Management**: Multi-provider VPN support (TryHackMe, HackTheBox, custom)
- **🛡️ Enhanced CAI**: Local LLM-powered cybersecurity agents
- **📊 Intelligent Reports**: Automated analysis and reporting
- **💬 Telegram Interface**: Easy interaction via Telegram bot

### 🏗️ Architecture

```
📁 cybersecurity-ai-agent/
├── 🎯 core/                    # Main application logic
├── 🤖 agents/                  # Specialized AI agents
├── 🔗 integrations/            # External service integrations
├── ⚙️ config/                  # Configuration files
├── 📊 data/                    # Data storage and processing
├── 📝 logs/                    # Application logs
├── 🚀 deployment/              # Deployment scripts
├── 🧪 tests/                   # Test suite
├── 📚 CAI/                     # CAI framework
└── 🛡️ PentestGPT/             # PentestGPT framework
```

---

## 💻 System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **RAM**: 8GB (16GB recommended for local LLM)
- **Storage**: 50GB free space
- **CPU**: 4 cores (8 cores recommended)
- **Python**: 3.8+
- **Internet**: Stable connection for API calls

### Recommended Production Setup
- **RAM**: 32GB+ 
- **Storage**: 100GB+ SSD
- **CPU**: 8+ cores
- **GPU**: Optional (NVIDIA with CUDA for faster local LLM)

### Required Accounts & API Keys
- **Google AI Studio**: For Gemini API access
- **Telegram**: Bot token from @BotFather
- **Optional**: OpenAI API key (fallback)

---

## 🚀 Installation Methods

### Method 1: Quick Local Setup (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/h7ck3r/cybersecurity-ai-agent.git
cd cybersecurity-ai-agent

# Run quick setup
chmod +x deployment/deploy.sh
./deployment/deploy.sh
# Select option 1: Quick Setup

# Configure environment
cp .env.template .env
nano .env  # Add your API keys

# Activate virtual environment
source venv/bin/activate

# Start the platform
python core/main.py
```

### Method 2: Production Azure VM Deployment

```bash
# On Azure VM or production server
curl -O https://raw.githubusercontent.com/h7ck3r/cybersecurity-ai-agent/main/deployment/deploy.sh
chmod +x deploy.sh
./deploy.sh
# Select option 2: Production Azure VM

# The script will:
# - Install all system dependencies
# - Setup systemd services
# - Configure nginx proxy
# - Setup log rotation
# - Create production configuration
```

### Method 3: Manual Installation

<details>
<summary>Click to expand manual installation steps</summary>

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv git curl nginx supervisor \
    openvpn wireguard-tools nmap masscan sqlite3 build-essential \
    libssl-dev libffi-dev poppler-utils tesseract-ocr

# 2. Clone repository
git clone https://github.com/h7ck3r/cybersecurity-ai-agent.git
cd cybersecurity-ai-agent

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install Python dependencies
pip install --upgrade pip
pip install -r config/requirements.txt

# 5. Install additional components
pip install google-generativeai transformers torch sentence-transformers \
    chromadb faiss-cpu peft accelerate bitsandbytes datasets

# 6. Setup configuration
cp .env.template .env
# Edit .env with your API keys

# 7. Create directories
mkdir -p data/{rag_data,documents,processed,models} \
         logs/{main,telegram,gemini,deepseek} \
         config/vpn temp/{uploads,processing}

# 8. Initialize components
python -c "
import asyncio
from integrations.deepseek_finetune import DeepSeekFineTuner
from integrations.local_llm_server import LocalLLMAPI
# Additional initialization if needed
"
```

</details>

---

## ⚙️ Configuration

### 1. Environment Variables (.env)

```bash
# Required API Keys
GEMINI_API_KEY=your_gemini_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
AUTHORIZED_USER_ID=your_telegram_user_id_here

# Optional APIs
OPENAI_API_KEY=optional_openai_key_for_fallback

# Webhook Configuration
WEBHOOK_URL=https://your-domain.com/webhook

# Resource Configuration
MAX_MEMORY_MB=4096
MAX_CONCURRENT_TASKS=10

# Development Settings
DEBUG=false
LOG_LEVEL=INFO
```

### 2. Main Configuration (core/config.yaml)

Key configuration sections:

```yaml
# Local LLM Configuration
local_llm:
  enabled: true
  model_name: "deepseek-ai/deepseek-coder-1.3b-instruct"
  max_memory_mb: 4096
  use_quantization: true

# VPN Configuration
vpn:
  tryhackme:
    type: "openvpn"
    config_path: "config/vpn/tryhackme.ovpn"
  hackthebox:
    type: "openvpn"
    config_path: "config/vpn/hackthebox.ovpn"

# Fine-tuning Configuration
fine_tuning:
  enabled: true
  data_sources:
    - "data/rag_data/**/*.json"
    - "data/processed/**/*.json"
```

### 3. VPN Setup

```bash
# Add your VPN configs
cp your_tryhackme.ovpn config/vpn/tryhackme.ovpn
cp your_hackthebox.ovpn config/vpn/hackthebox.ovpn

# Create auth files if needed
echo "username" > config/vpn/tryhackme_auth.txt
echo "password" >> config/vpn/tryhackme_auth.txt
chmod 600 config/vpn/*_auth.txt
```

---

## 📖 Usage Guide

### 1. Starting the Platform

#### Development Mode
```bash
source venv/bin/activate
python core/main.py
```

#### Production Mode (Systemd)
```bash
# Start services
sudo systemctl start cybersec-main-agent
sudo systemctl start cybersec-task-router
sudo systemctl start cybersec-local-llm

# Enable auto-start
sudo systemctl enable cybersec-main-agent
sudo systemctl enable cybersec-task-router
sudo systemctl enable cybersec-local-llm

# Check status
sudo systemctl status cybersec-main-agent
```

### 2. Telegram Bot Commands

#### Basic Commands
```
/start          - Initialize bot and show welcome
/help           - Show all available commands
/status         - Platform health status
/config         - Current configuration
```

#### Security Analysis
```
/scan <target>              - Basic target reconnaissance
/vuln <target>              - Vulnerability assessment
/pentest <target>           - Full penetration test
/analyze_file <file>        - Analyze uploaded file
/threat_intel <indicator>   - Threat intelligence lookup
```

#### Advanced Features
```
/finetune                   - Start model fine-tuning
/vpn_list                   - List available VPN configs
/vpn_connect <name>         - Connect to VPN
/vpn_disconnect <name>      - Disconnect from VPN
/generate_report <session>  - Generate detailed report
```

### 3. Direct API Usage

#### Python API
```python
import asyncio
from core.task_router import TaskRouter
from integrations.gemini_integration import GeminiDocumentProcessor
from agents.pentestgpt_gemini import PentestGPTGemini

# Initialize components
gemini_processor = GeminiDocumentProcessor()
pentest_agent = PentestGPTGemini()

# Process document
result = await gemini_processor.process_cybersecurity_book("path/to/book.pdf")

# Start pentest session
session = await pentest_agent.start_pentest_session({
    "target": "test-webapp.com",
    "type": "web_application"
})
```

#### REST API Endpoints
```bash
# Health check
curl http://localhost:8080/health

# Submit analysis task
curl -X POST http://localhost:8080/api/analyze \
     -H "Content-Type: application/json" \
     -d '{"target": "example.com", "type": "reconnaissance"}'

# Get task status
curl http://localhost:8080/api/task/{task_id}
```

---

## 🔧 Advanced Features

### 1. Fine-Tuning DeepSeek Coder

```bash
# Prepare training data
python integrations/deepseek_finetune.py

# Start fine-tuning process
python -c "
import asyncio
from integrations.deepseek_finetune import DeepSeekFineTuner
import yaml

async def main():
    config = yaml.safe_load(open('core/config.yaml'))
    finetuner = DeepSeekFineTuner(config)
    
    # Prepare dataset
    dataset_file = await finetuner.prepare_cybersecurity_dataset()
    
    # Fine-tune model
    model_path = await finetuner.fine_tune_model(dataset_file)
    print(f'Model saved to: {model_path}')

asyncio.run(main())
"
```

### 2. VPN Management

```python
from integrations.vpn_manager import VPNManager

# Initialize VPN manager
vpn_manager = VPNManager()

# List available configs
configs = await vpn_manager.list_available_configs()

# Connect to TryHackMe
result = await vpn_manager.connect_vpn("tryhackme")

# Check connection status
status = await vpn_manager.get_connection_status()
```

### 3. Document Processing with Gemini

```python
from integrations.gemini_integration import GeminiDocumentProcessor

processor = GeminiDocumentProcessor()

# Process cybersecurity book
book_result = await processor.process_cybersecurity_book("security_guide.pdf")

# Extract file metadata
metadata = await processor.extract_file_metadata("report.docx")

# Process vulnerability report
vuln_report = await processor.process_vulnerability_report("pentest_report.pdf")
```

### 4. Enhanced PentestGPT with Gemini

```python
from agents.pentestgpt_gemini import PentestGPTGemini

pentest = PentestGPTGemini()

# Start comprehensive pentest session
target_info = {
    "target": "webapp.example.com",
    "type": "web_application",
    "scope": "Single application",
    "authorization": "Written authorization obtained"
}

session = await pentest.start_pentest_session(target_info)

# Execute reconnaissance phase
recon_result = await pentest.execute_pentest_phase(
    "reconnaissance", 
    "Focus on subdomain enumeration and technology stack identification"
)

# Generate final report
report = await pentest.generate_final_report(session["session_id"])
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Memory Issues with Local LLM
```bash
# Reduce model memory usage
export MAX_MEMORY_MB=2048

# Use CPU-only mode
export CUDA_VISIBLE_DEVICES=""

# Enable 8-bit quantization
# Edit core/config.yaml:
local_llm:
  use_quantization: true
  device: "cpu"
```

#### 2. VPN Connection Problems
```bash
# Check VPN configuration
python -c "
from integrations.vpn_manager import VPNManager
import asyncio
async def check():
    vpn = VPNManager()
    configs = await vpn.list_available_configs()
    print(configs)
asyncio.run(check())
"

# Verify OpenVPN installation
sudo apt install openvpn
which openvpn
```

#### 3. Gemini API Errors
```bash
# Verify API key
python -c "
import os
import google.generativeai as genai
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content('Hello')
print(response.text)
"
```

#### 4. Telegram Bot Issues
```bash
# Test bot token
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"

# Check webhook
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"
```

### Log Analysis
```bash
# View main application logs
tail -f logs/main/main.log

# View component-specific logs
tail -f logs/gemini/gemini.log
tail -f logs/deepseek/deepseek.log
tail -f logs/vpn/vpn.log

# System service logs
journalctl -u cybersec-main-agent -f
journalctl -u cybersec-local-llm -f
```

### Performance Monitoring
```bash
# Check system resources
python agents/health_monitor.py

# Monitor GPU usage (if available)
nvidia-smi

# Check memory usage
free -h
df -h
```

---

## 👨‍💻 Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/h7ck3r/cybersecurity-ai-agent.git
cd cybersecurity-ai-agent

# Create development environment
python3 -m venv venv
source venv/bin/activate
pip install -r config/requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy pre-commit

# Setup pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_integration.py
python tests/final_integration.py

# Run with coverage
python -m pytest --cov=core --cov=agents --cov=integrations
```

### Adding New Components

#### 1. Create New Agent
```python
# agents/your_new_agent.py
import asyncio
from shared_utils import ConfigManager, LoggerManager

class YourNewAgent:
    def __init__(self, config):
        self.config = config
        self.logger = LoggerManager.setup_logger('your_agent')
    
    async def process_task(self, task_data):
        # Your implementation
        pass
```

#### 2. Register with Task Router
```python
# core/task_router.py
from agents.your_new_agent import YourNewAgent

# Add to agent initialization
self.your_agent = YourNewAgent(self.config)
```

#### 3. Add Configuration
```yaml
# core/config.yaml
agents:
  your_new_agent:
    enabled: true
    setting1: value1
    setting2: value2
```

### Code Style Guidelines

- Use type hints for all function parameters and returns
- Follow PEP 8 style guidelines  
- Add docstrings for all public methods
- Use async/await for I/O operations
- Handle exceptions gracefully with proper logging

---

## 📚 Additional Resources

### Documentation
- [CAI vs PentestGPT Guide](docs/CAI_vs_PentestGPT_GUIDE.md)
- [Project Structure](docs/PROJECT_STRUCTURE.md)
- [Deployment Guide](docs/DEPLOYMENT_COMPLETE.md)

### External Links
- [Google AI Studio](https://makersuite.google.com/app/apikey) - Get Gemini API key
- [Telegram Bot API](https://core.telegram.org/bots/api) - Bot documentation
- [DeepSeek Models](https://huggingface.co/deepseek-ai) - Model information
- [TryHackMe](https://tryhackme.com/) - Practice platform
- [HackTheBox](https://www.hackthebox.com/) - Practice platform

### Community
- GitHub Issues: Report bugs and request features
- Discussions: Share use cases and tips
- Contributing: Submit pull requests

---

## 🔐 Security Considerations

### Production Deployment
- Always use HTTPS for webhooks
- Restrict API access with proper authentication
- Regularly update dependencies
- Monitor system resources and logs
- Use strong encryption for sensitive data
- Implement proper backup strategies

### Ethical Usage
- Only test on authorized systems
- Respect rate limits and terms of service
- Follow responsible disclosure practices
- Maintain proper documentation of activities
- Ensure compliance with local laws and regulations

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🛡️ Happy ethical hacking! Stay secure! 🛡️**
