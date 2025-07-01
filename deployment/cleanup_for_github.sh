#!/bin/bash

# =============================================================================
# CYBERSECURITY AI PLATFORM - CLEANUP FOR GITHUB SCRIPT
# =============================================================================
# This script cleans up the project by removing:
# - Duplicate files
# - Temporary/backup files  
# - Build artifacts
# - Symlinks (replaced with proper structure)
# - Large unnecessary files
# - Cache directories
# =============================================================================

echo "🧹 Starting project cleanup for GitHub upload..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log actions
log_action() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# =============================================================================
# 1. REMOVE DUPLICATE HEALTH MONITOR FILES
# =============================================================================
echo -e "\n${BLUE}🔍 Step 1: Removing duplicate health monitor files...${NC}"

# Keep only the one in agents/ directory
if [ -f "agents/health_monitor.py" ]; then
    log_info "Keeping agents/health_monitor.py as the main health monitor"
    
    # Remove duplicates
    if [ -f "health_monitor.py" ]; then
        rm "health_monitor.py"
        log_action "Removed duplicate health_monitor.py from root"
    fi
    
    if [ -f "health_monitor_backup.py" ]; then
        rm "health_monitor_backup.py"
        log_action "Removed health_monitor_backup.py"
    fi
    
    if [ -f "health_monitor_new.py" ]; then
        rm "health_monitor_new.py"
        log_action "Removed health_monitor_new.py"
    fi
else
    log_error "Main health_monitor.py not found in agents/ directory!"
fi

# =============================================================================
# 2. REMOVE BUILD ARTIFACTS AND CACHE
# =============================================================================
echo -e "\n${BLUE}🗑️  Step 2: Removing build artifacts and cache files...${NC}"

# Remove __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
log_action "Removed all __pycache__ directories"

# Remove .pyc files
find . -name "*.pyc" -delete 2>/dev/null
log_action "Removed all .pyc files"

# Remove .pyo files
find . -name "*.pyo" -delete 2>/dev/null
log_action "Removed all .pyo files"

# Remove .egg-info directories
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null
log_action "Removed all .egg-info directories"

# Remove build directories
find . -type d -name "build" -exec rm -rf {} + 2>/dev/null
log_action "Removed all build directories"

# Remove dist directories
find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null
log_action "Removed all dist directories"

# =============================================================================
# 3. REMOVE SYMLINKS AND UPDATE STRUCTURE
# =============================================================================
echo -e "\n${BLUE}🔗 Step 3: Cleaning up symlinks...${NC}"

# List of root-level symlinks to remove
symlinks=("main.py" "telegram_bot.py" "task_router.py" "shared_utils.py" "config.yaml")

for symlink in "${symlinks[@]}"; do
    if [ -L "$symlink" ]; then
        rm "$symlink"
        log_action "Removed symlink: $symlink"
    fi
done

# =============================================================================
# 4. CLEAN UP TEMPORARY AND TEST FILES
# =============================================================================
echo -e "\n${BLUE}🧪 Step 4: Removing temporary and test files...${NC}"

# Remove temp files
find . -name "*.tmp" -delete 2>/dev/null
find . -name "*.temp" -delete 2>/dev/null
find . -name "*~" -delete 2>/dev/null
log_action "Removed temporary files"

# Remove log files (keep directory structure)
find ./data/logs -name "*.log" -delete 2>/dev/null || echo "No log files to remove"
log_action "Cleaned up log files"

# Remove any .DS_Store files (macOS)
find . -name ".DS_Store" -delete 2>/dev/null
log_action "Removed .DS_Store files"

# =============================================================================
# 5. OPTIMIZE CAI AND PENTESTGPT FRAMEWORKS
# =============================================================================
echo -e "\n${BLUE}📦 Step 5: Optimizing external frameworks...${NC}"

# Clean CAI framework
if [ -d "CAI" ]; then
    log_info "Cleaning CAI framework..."
    
    # Remove CAI build artifacts
    find CAI -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find CAI -name "*.pyc" -delete 2>/dev/null
    find CAI -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
    find CAI -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null
    
    # Remove large benchmark datasets if they exist
    if [ -d "CAI/benchmarks" ]; then
        find CAI/benchmarks -name "*.json" -size +10M -delete 2>/dev/null
        find CAI/benchmarks -name "*.csv" -size +10M -delete 2>/dev/null
        log_action "Cleaned large benchmark files from CAI"
    fi
    
    log_action "Optimized CAI framework"
fi

# Clean PentestGPT framework  
if [ -d "PentestGPT" ]; then
    log_info "Cleaning PentestGPT framework..."
    
    # Remove PentestGPT build artifacts
    find PentestGPT -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find PentestGPT -name "*.pyc" -delete 2>/dev/null
    find PentestGPT -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
    
    # Remove test artifacts
    find PentestGPT -name "test_*.log" -delete 2>/dev/null
    
    log_action "Optimized PentestGPT framework"
fi

# =============================================================================
# 6. CREATE .gitignore FOR GITHUB
# =============================================================================
echo -e "\n${BLUE}📝 Step 6: Creating comprehensive .gitignore...${NC}"

cat > .gitignore << 'EOF'
# =============================================================================
# CYBERSECURITY AI PLATFORM - GITIGNORE
# =============================================================================

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# API Keys and Secrets
.env
.env.local
.env.production
*.key
*.pem
config/api_keys.yaml
config/secrets.yaml

# Logs
*.log
logs/*.log
data/logs/*.log

# Data directories
data/rag_data/chroma_db/
data/temp/
data/cache/
*.db
*.sqlite

# Model files
models/*.bin
models/*.safetensors
*.gguf
*.h5

# Large files
*.tar.gz
*.zip
*.rar
*.7z

# Backup files
*_backup.*
*_old.*
*.bak

# Test artifacts
.pytest_cache/
.coverage
htmlcov/
.tox/

# Documentation build
docs/_build/
site/

# Jupyter Notebooks
.ipynb_checkpoints

# CAI specific
CAI/logs/
CAI/workspaces/
CAI/.venv*/

# PentestGPT specific
PentestGPT/logs/
PentestGPT/save/

# Platform specific
monitoring/
reports/daily/
reports/weekly/
finetune_data/raw/
finetune_data/processed/
EOF

log_action "Created comprehensive .gitignore"

# =============================================================================
# 7. CREATE GITHUB-READY README
# =============================================================================
echo -e "\n${BLUE}📋 Step 7: Creating GitHub-ready README...${NC}"

cat > README.md << 'EOF'
# 🛡️ Cybersecurity AI Agent Platform

A comprehensive cybersecurity platform that integrates three powerful frameworks for automated security testing, intelligence gathering, and vulnerability assessment.

## 🏗️ Architecture

### Core Platform
- **Custom AI Agent Platform** - Orchestrates security operations
- **CAI Framework Integration** - Advanced cybersecurity AI capabilities  
- **PentestGPT Integration** - Automated penetration testing

### Key Components
- **Agent Orchestrator** - Routes tasks to optimal framework
- **Telegram Bot Interface** - Interactive command and control
- **RAG System** - Knowledge base for security intelligence
- **Report Generator** - Automated security reporting
- **Health Monitor** - System monitoring and alerts

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.8+
python --version

# Install dependencies
pip install -r config/requirements.txt
```

### Configuration
```bash
# Copy environment template
cp config/.env.template .env

# Edit configuration
nano .env
```

### Launch Platform
```bash
# Start the main platform
python core/main.py

# Start Telegram bot
python core/telegram_bot.py

# Health monitoring
python agents/health_monitor.py
```

## 📁 Project Structure

```
├── core/                   # Core platform components
│   ├── main.py            # Main application entry
│   ├── telegram_bot.py    # Telegram interface
│   ├── task_router.py     # Task routing logic
│   └── shared_utils.py    # Shared utilities
├── agents/                 # AI agent modules
│   ├── pentestgpt_gemini.py   # PentestGPT integration
│   ├── rag_embedder.py       # RAG system
│   ├── file_parser.py        # File processing
│   └── health_monitor.py     # System monitoring
├── integrations/           # Framework wrappers
│   ├── cai_integration.py    # CAI wrapper
│   ├── pentestgpt_integration.py # PentestGPT wrapper
│   └── agent_orchestrator.py    # Unified orchestration
├── external/               # External frameworks
│   ├── CAI/               # CAI framework
│   └── PentestGPT/        # PentestGPT framework
├── deployment/             # Deployment scripts
├── config/                 # Configuration files
└── docs/                  # Documentation
```

## 🔧 Features

### Security Testing
- **Automated Penetration Testing** via PentestGPT
- **Vulnerability Assessment** with CAI agents
- **Network Reconnaissance** and mapping
- **Web Application Testing**

### Intelligence Gathering
- **RSS Feed Monitoring** for threat intelligence
- **RAG-based Knowledge Base** for security research
- **Report Generation** and analysis
- **Real-time Monitoring**

### Platform Management
- **Health Monitoring** with alerts
- **Task Routing** between frameworks
- **Telegram Bot** for remote operations
- **Automated Reporting**

## 🛠️ Usage Examples

### Basic Security Scan
```python
from integrations.agent_orchestrator import AgentOrchestrator

orchestrator = AgentOrchestrator()
result = await orchestrator.run_security_scan("target.com")
```

### Telegram Commands
```
/start - Initialize bot
/scan <target> - Run security scan
/report - Generate report  
/status - System health
```

### RAG Query
```python
from agents.rag_embedder import RAGEmbedder

rag = RAGEmbedder()
result = await rag.query("SQL injection techniques")
```

## 📊 Monitoring

The platform includes comprehensive monitoring:
- **Health Checks** - System component status
- **Performance Metrics** - Resource utilization
- **Security Alerts** - Threat notifications
- **Report Generation** - Automated summaries

## 🔐 Security

- **API Key Management** - Secure credential storage
- **Access Control** - Role-based permissions
- **Audit Logging** - Complete operation tracking
- **Encrypted Communications** - Secure data transfer

## 📚 Documentation

- [Deployment Guide](docs/DEPLOYMENT_COMPLETE.md)
- [Framework Comparison](docs/CAI_vs_PentestGPT_GUIDE.md)
- [Project Structure](docs/PROJECT_STRUCTURE.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This platform is for authorized security testing only. Users are responsible for compliance with applicable laws and regulations.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check documentation in `docs/`
- Review logs in `data/logs/`

---

**Built with ❤️ for the cybersecurity community**
EOF

log_action "Created GitHub-ready README.md"

# =============================================================================
# 8. CREATE LICENSE FILE
# =============================================================================
echo -e "\n${BLUE}⚖️  Step 8: Creating LICENSE file...${NC}"

cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2024 Cybersecurity AI Platform

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

log_action "Created LICENSE file"

# =============================================================================
# 9. OPTIMIZE FILE SIZES
# =============================================================================
echo -e "\n${BLUE}📏 Step 9: Checking and optimizing file sizes...${NC}"

# Find large files (>50MB) and list them
log_info "Checking for large files (>50MB)..."
large_files=$(find . -type f -size +50M 2>/dev/null | head -10)

if [ -n "$large_files" ]; then
    log_warning "Large files found (consider removing or using Git LFS):"
    echo "$large_files"
else
    log_action "No problematically large files found"
fi

# =============================================================================
# 10. FINAL STRUCTURE VERIFICATION
# =============================================================================
echo -e "\n${BLUE}🔍 Step 10: Final structure verification...${NC}"

# Check that key files exist
key_files=(
    "core/main.py"
    "core/telegram_bot.py"
    "agents/health_monitor.py"
    "integrations/cai_integration.py"
    "config/requirements.txt"
    "README.md"
    ".gitignore"
    "LICENSE"
)

for file in "${key_files[@]}"; do
    if [ -f "$file" ]; then
        log_action "✓ $file exists"
    else
        log_error "✗ $file missing"
    fi
done

# =============================================================================
# 11. GENERATE CLEANUP SUMMARY
# =============================================================================
echo -e "\n${BLUE}📊 CLEANUP SUMMARY${NC}"

total_files=$(find . -type f | wc -l)
total_dirs=$(find . -type d | wc -l)
project_size=$(du -sh . 2>/dev/null | cut -f1)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📁 Total Files: $total_files"
echo "📂 Total Directories: $total_dirs"  
echo "💾 Project Size: $project_size"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

log_action "Project cleanup completed successfully!"
log_info "Ready for GitHub upload"

echo -e "\n${GREEN}🎉 CLEANUP COMPLETE!${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo "1. Review the generated .gitignore"
echo "2. Test the platform: python core/main.py"
echo "3. Initialize git repository: git init"
echo "4. Add files: git add ."
echo "5. Commit: git commit -m 'Initial commit'"
echo "6. Push to GitHub"

echo -e "\n${YELLOW}⚠️  Remember to:${NC}"
echo "- Configure your API keys in .env"
echo "- Test all integrations before deployment"
echo "- Review the LICENSE terms"
echo "- Update README.md with your specific details"
