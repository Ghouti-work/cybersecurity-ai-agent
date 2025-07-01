# 🛡️ Cybersecurity AI Agent Platform

A comprehensive cybersecurity platform that integrates three powerful frameworks for automated security testing, intelligence gathering, and vulnerability assessment.

## 🏗️ Architecture

The platform combines:
- **Custom AI Agent Platform** - Orchestrates security operations
- **CAI Framework Integration** - Advanced cybersecurity AI capabilities  
- **PentestGPT Integration** - Automated penetration testing

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r config/requirements.txt

# Configure environment
cp config/.env.template .env
nano .env

# Start platform
python core/main.py
```

## 📁 Project Structure

```
├── core/                   # Core platform components
├── agents/                 # AI agent modules
├── integrations/           # Framework wrappers
├── CAI/                    # CAI framework
├── PentestGPT/            # PentestGPT framework
├── deployment/            # Deployment scripts
├── config/                # Configuration files
└── docs/                  # Documentation
```

## 🔧 Features

- **Automated Penetration Testing** via PentestGPT
- **Vulnerability Assessment** with CAI agents
- **RSS Feed Monitoring** for threat intelligence
- **RAG-based Knowledge Base** for security research
- **Telegram Bot Interface** for remote operations
- **Health Monitoring** with alerts

## 📚 Documentation

- [Deployment Guide](docs/DEPLOYMENT_COMPLETE.md)
- [Framework Comparison](docs/CAI_vs_PentestGPT_GUIDE.md)
- [Project Structure](docs/PROJECT_STRUCTURE.md)

## ⚠️ Disclaimer

This platform is for authorized security testing only. Users are responsible for compliance with applicable laws and regulations.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
