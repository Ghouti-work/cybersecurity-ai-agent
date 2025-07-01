# 🛡️ Cybersecurity AI Agent Platform

**Intelligent Pentesting Assistant with 24/7 Telegram Bot Access**

A comprehensive AI-powered cybersecurity platform that runs on Azure VM (2 vCPU, 8GB RAM) providing:
- 🤖 **24/7 Telegram Bot Access** - Always available intelligent assistant
- 🧠 **Gemini API Integration** - Advanced reasoning and analysis
- 📡 **RSS Feed Processing** - Automated threat intelligence gathering
- 📄 **File Analysis** - Multi-format document processing and classification
- 🔍 **RAG Knowledge Base** - Searchable cybersecurity knowledge
- 🎯 **PentestGPT Reasoning** - Multi-step security analysis
- 📊 **Automated Reporting** - Comprehensive security reports
- 🧪 **Fine-tuning Preparation** - Training data for custom models
- 🖥️ **Local LLM Fallback** - DeepSeek/Phi-2 for offline processing

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure VM (8GB RAM)                      │
├─────────────────────────────────────────────────────────────┤
│  🤖 Telegram Bot (main interface)                          │
│  ├── /scan - Network/web scanning                          │
│  ├── /think - PentestGPT reasoning                         │
│  ├── /report - Generate reports                            │
│  ├── /file - Upload & analyze files                        │
│  ├── /rss - Fetch security feeds                           │
│  └── /fine_tune - Prepare training data                    │
├─────────────────────────────────────────────────────────────┤
│  🧠 PentestGPT (Gemini API)                               │
│  ├── Multi-step security analysis                          │
│  ├── Risk assessment                                       │
│  ├── Attack vector identification                          │
│  └── Mitigation strategies                                 │
├─────────────────────────────────────────────────────────────┤
│  📡 RSS Fetcher & Intelligence Gathering                   │
│  ├── CVE feeds (NVD, CVE Trends)                          │
│  ├── Security news (Krebs, Dark Reading)                   │
│  ├── Research feeds (SANS ISC, Exploit-DB)                │
│  └── AI-powered classification                             │
├─────────────────────────────────────────────────────────────┤
│  📄 File Parser & Analysis Engine                          │
│  ├── PDF, Markdown, HTML, JSON support                     │
│  ├── AI-powered categorization                             │
│  ├── Metadata extraction                                   │
│  └── RAG integration                                       │
├─────────────────────────────────────────────────────────────┤
│  🔍 RAG Knowledge Base (ChromaDB)                          │
│  ├── Vector embeddings (e5-small-v2)                       │
│  ├── Semantic search                                       │
│  ├── Document collections                                  │
│  └── Context retrieval                                     │
├─────────────────────────────────────────────────────────────┤
│  🎯 Fine-tuning Data Preparation                           │
│  ├── LoRA adapter training                                 │
│  ├── Quality metrics                                       │
│  ├── Data validation                                       │
│  └── Export formats                                        │
├─────────────────────────────────────────────────────────────┤
│  🖥️ Local LLM Server (DeepSeek/Phi-2)                     │
│  ├── CPU-optimized inference                               │
│  ├── Memory-efficient quantization                         │
│  ├── Fallback processing                                   │
│  └── Offline capabilities                                  │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. **Clone & Setup**
```bash
# Clone the repository
git clone <your-repo-url>
cd cybersecurity-ai-agent

# Make installation script executable
chmod +x install_azure.sh

# Run complete Azure VM setup
./install_azure.sh
```

### 2. **Configure Environment**
```bash
# Edit .env file with your credentials
nano .env

# Required settings:
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
AUTHORIZED_USER_ID=your_telegram_user_id
GEMINI_API_KEY=your_gemini_api_key
```

### 3. **Start the Platform**
```bash
# Option 1: Direct launch
python main.py

# Option 2: As systemd service
./manage_service.sh start
./manage_service.sh enable  # Auto-start on boot
```

### 4. **Test Integration**
```bash
# Run comprehensive tests
python test_integration.py

# Check system status
./check_environment.sh
```

## 📱 Telegram Bot Commands

### Core Commands
- `/help` - Show available commands and usage
- `/status` - Display system status and statistics

### Analysis Commands
- `/scan <target>` - Trigger network/web scanning of target
- `/think <query>` - Use PentestGPT reasoning for security analysis
- `/file` - Upload and analyze security-related files

### Intelligence Commands
- `/rss` - Fetch and process latest security RSS feeds
- `/report [type]` - Generate comprehensive security reports

### Training Commands
- `/fine_tune` - Prepare fine-tuning data from collected logs

## 🛠️ Core Components

### 1. **PentestGPT Reasoning Engine** (`pentestgpt_gemini.py`)
Advanced multi-step security analysis using Gemini API:
- **Initial Analysis** - Reconnaissance strategy and target assessment
- **Detailed Analysis** - Technical vulnerability identification
- **Attack Vector Analysis** - Exploitation methodology and prioritization
- **Mitigation Strategies** - Defensive recommendations and risk assessment

### 2. **RSS Intelligence Fetcher** (`rss_fetcher.py`)
Automated threat intelligence gathering:
- **Vulnerability Feeds** - NVD CVEs, CVE Trends, security advisories
- **Security News** - KrebsOnSecurity, Dark Reading, The Hacker News
- **Research Feeds** - SANS ISC Diary, Exploit-DB, academic sources
- **AI Classification** - Automatic categorization and metadata extraction

### 3. **File Analysis Engine** (`file_parser.py`)
Multi-format document processing:
- **Supported Formats** - PDF, TXT, MD, HTML, JSON, XML, CSV
- **Content Extraction** - Text, metadata, structure analysis
- **AI Classification** - Automatic categorization into security domains
- **RAG Integration** - Seamless knowledge base integration

### 4. **RAG Knowledge Base** (`rag_embedder.py`)
Searchable cybersecurity knowledge system:
- **Vector Embeddings** - e5-small-v2 model for semantic understanding
- **Document Collections** - Vulnerabilities, techniques, intelligence, reports
- **Semantic Search** - Context-aware information retrieval
- **Memory Optimization** - Efficient processing for 8GB RAM systems

### 5. **Task Router** (`task_router.py`)
Intelligent command routing and orchestration:
- **Command Analysis** - Intent recognition and parameter extraction
- **Component Routing** - Optimal task distribution
- **System Status** - Health monitoring and performance metrics
- **Error Handling** - Graceful failure recovery

### 6. **Report Generator** (`report_generator.py`)
Comprehensive security reporting:
- **Multiple Formats** - Markdown, HTML, JSON export
- **Report Types** - Scan results, threat intelligence, assessments
- **Template System** - Customizable report structures
- **Automation** - Scheduled report generation

### 7. **Fine-tuning Preparer** (`finetune_preparer.py`)
Training data preparation for custom models:
- **Data Collection** - Aggregate logs and interactions
- **Quality Metrics** - Validation and scoring
- **LoRA Format** - Efficient fine-tuning preparation
- **Export Options** - Multiple training formats

### 8. **Local LLM Server** (`local_llm_server.py`)
Offline AI processing capabilities:
- **Model Support** - DeepSeek-Coder, DialoGPT, DistilGPT2
- **Memory Optimization** - 8-bit quantization and CPU offloading
- **Fallback Processing** - When external APIs are unavailable
- **Resource Management** - Automatic memory cleanup

## ⚙️ Configuration

### Main Configuration (`config.yaml`)
```yaml
# Core system settings
telegram:
  commands: { scan, think, report, file, rss, fine_tune, help, status }

# AI model configuration
models:
  gemini:
    model: "gemini-pro"
    temperature: 0.7
    max_tokens: 4096

# RSS feed sources
rss_feeds:
  vulnerability_databases: [NVD, CVE Trends]
  security_news: [KrebsOnSecurity, Dark Reading]
  research: [SANS ISC, Exploit-DB]

# File processing
file_processing:
  supported_formats: [".pdf", ".txt", ".md", ".html", ".json"]
  classification_categories: [reconnaissance, web_security, network_security]

# RAG configuration
rag:
  embedding_model: "intfloat/e5-small-v2"
  chunk_size: 512
  similarity_threshold: 0.7
```

### Environment Variables (`.env`)
```bash
# Required API keys
TELEGRAM_BOT_TOKEN=your_bot_token
AUTHORIZED_USER_ID=your_user_id
GEMINI_API_KEY=your_gemini_key

# Performance tuning for 8GB RAM
MAX_MEMORY_MB=6144
MAX_CONCURRENT_REQUESTS=3
EMBEDDING_BATCH_SIZE=32
TORCH_THREADS=2

# Security settings
API_RATE_LIMIT=60
MAX_FILE_SIZE_MB=50
SCAN_UPLOADS=true
```

## 🤖 Memory Optimization

The platform is specifically optimized for 8GB RAM Azure VMs:

### Memory Management
- **Model Quantization** - 8-bit quantization for transformer models
- **CPU Offloading** - Intelligent GPU memory management
- **Batch Processing** - Limited batch sizes for embeddings
- **Lazy Loading** - Components loaded on-demand
- **Memory Cleanup** - Automatic garbage collection

### Performance Tuning
```bash
# Environment optimizations
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=2

# System limits in systemd service
MemoryMax=6G
MemoryHigh=5G
CPUQuota=80%
```

## 📊 Monitoring & Maintenance

### Health Monitoring
```bash
# System health check
./monitor_system.sh

# Service status
./manage_service.sh status

# View real-time logs
./manage_service.sh logs
```

### Automated Tasks (Cron Jobs)
- **Health Monitoring** - Every 30 minutes
- **RSS Feed Updates** - Every 6 hours
- **Daily Backups** - 2 AM daily
- **Weekly Fine-tuning** - Sunday 3 AM
- **Log Cleanup** - Saturday 1 AM

### Backup System
```bash
# Manual backup
./backup_data.sh

# Backup locations
backup/daily/      # Daily backups (7 day retention)
backup/weekly/     # Weekly backups (4 week retention)
```

## 🔧 Management Scripts

### Service Management
```bash
./manage_service.sh start     # Start the service
./manage_service.sh stop      # Stop the service
./manage_service.sh restart   # Restart the service
./manage_service.sh status    # Check status
./manage_service.sh logs      # View logs
./manage_service.sh enable    # Enable auto-start
```

### System Monitoring
```bash
./monitor_system.sh           # Run health check
./check_environment.sh        # Verify configuration
./backup_data.sh             # Create backup
```

## 🧪 Testing

### Integration Tests
```bash
# Run comprehensive test suite
python test_integration.py

# Test specific components
python -c "from pentestgpt_gemini import PentestGPT; print('✅ PentestGPT OK')"
python -c "from rag_embedder import RAGEmbedder; print('✅ RAG OK')"
```

### Component Testing
```bash
# Test local LLM
python local_llm_server.py

# Test RSS fetching
python -c "
import asyncio
from rss_fetcher import RSSFetcher
import yaml
config = yaml.safe_load(open('config.yaml'))
rss = RSSFetcher(config)
asyncio.run(rss.fetch_all_feeds())
"
```

## 🔒 Security Features

### Access Control
- **Authorized Users** - Telegram user ID whitelist
- **Rate Limiting** - Request throttling (60/minute)
- **Content Filtering** - Malicious content detection
- **File Validation** - Upload scanning and type checking

### Data Protection
- **Encrypted Storage** - Sensitive data encryption
- **Secure Logging** - Sanitized log outputs
- **Backup Encryption** - Encrypted backup storage
- **API Key Protection** - Environment variable isolation

## 📈 Performance Metrics

### Expected Performance (8GB RAM)
- **Bot Response Time** - < 3 seconds for simple queries
- **PentestGPT Analysis** - 10-30 seconds for complex analysis
- **RSS Processing** - 5-15 minutes for all feeds
- **File Analysis** - 5-30 seconds per document
- **RAG Search** - < 1 second for semantic queries

### Resource Usage
- **Memory** - 4-6GB during peak operation
- **CPU** - 60-80% during intensive processing
- **Disk** - ~2GB for complete installation
- **Network** - Minimal (API calls only)

## 🚨 Troubleshooting

### Common Issues

#### Memory Issues
```bash
# Check memory usage
free -h
./monitor_system.sh

# Restart if memory is high
./manage_service.sh restart
```

#### API Rate Limits
```bash
# Check API usage in logs
tail -f logs/main/platform_*.log | grep "rate"

# Adjust limits in .env
nano .env  # Modify API_RATE_LIMIT
```

#### Service Won't Start
```bash
# Check service status
systemctl status cyberagent

# Check logs for errors
journalctl -u cyberagent -f

# Verify environment
./check_environment.sh
```

#### Telegram Bot Not Responding
```bash
# Verify bot token
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"

# Check authorized user ID
echo $AUTHORIZED_USER_ID

# Restart bot
./manage_service.sh restart
```

### Log Analysis
```bash
# Main platform logs
tail -f logs/main/platform_*.log

# Component-specific logs
tail -f logs/pentestgpt/reasoning_*.log
tail -f logs/telegram/bot_*.log
tail -f logs/rss/feeds_*.log

# Error grep
grep -r "ERROR" logs/ | tail -20
```

## 🎯 Advanced Usage

### Custom RSS Feeds
Add new feeds to `config.yaml`:
```yaml
rss_feeds:
  custom_category:
    - name: "Your Custom Feed"
      url: "https://example.com/rss.xml"
      category: "custom"
```

### Custom Prompts
Modify prompts in `config.yaml`:
```yaml
pentestgpt:
  custom_prompt: |
    Your custom PentestGPT prompt here...
```

### Fine-tuning Integration
```bash
# Prepare training data
python -c "
import asyncio
from finetune_preparer import FineTunePreparer
import yaml
config = yaml.safe_load(open('config.yaml'))
ft = FineTunePreparer(config)
asyncio.run(ft.prepare_training_data())
"

# Training data located in: finetune_data/processed/
```

## 📋 Deployment Checklist

### Pre-deployment
- [ ] Azure VM provisioned (2 vCPU, 8GB RAM)
- [ ] Ubuntu 22.04+ installed
- [ ] Internet connectivity verified
- [ ] Telegram bot created via @BotFather
- [ ] Gemini API key obtained

### Installation
- [ ] Run `./install_azure.sh`
- [ ] Configure `.env` file
- [ ] Test with `./check_environment.sh`
- [ ] Run integration tests
- [ ] Start service

### Post-deployment
- [ ] Enable auto-start
- [ ] Verify cron jobs
- [ ] Test Telegram commands
- [ ] Monitor resource usage
- [ ] Setup log rotation

## 🤝 Contributing

### Development Setup
```bash
# Clone for development
git clone <repo> cybersecurity-ai-dev
cd cybersecurity-ai-dev

# Create development environment
python -m venv venv-dev
source venv-dev/bin/activate
pip install -r requirements.txt

# Run tests
python test_integration.py
```

### Adding Components
1. Create module in main directory
2. Import in `main.py`
3. Add configuration to `config.yaml`
4. Add tests to `test_integration.py`
5. Update documentation

## 📞 Support

### Documentation
- **README.md** - This comprehensive guide
- **config.yaml** - Configuration reference
- **logs/** - Detailed operation logs
- **test_integration.py** - Component testing

### Monitoring
- **Health Checks** - Automated system monitoring
- **Performance Metrics** - Resource usage tracking
- **Error Logging** - Comprehensive error tracking
- **Status Dashboard** - Real-time system status

---

**🛡️ Your intelligent cybersecurity AI agent is ready for deployment!**

**Connect via Telegram and start with `/help` to begin your AI-powered security analysis journey.**
