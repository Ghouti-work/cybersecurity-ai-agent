#!/bin/bash

# ========================================
# Cybersecurity AI Agent Platform
# Quick Setup & Deployment Verification
# ========================================

set -e

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${BLUE}"
echo "🛡️  =============================================="
echo "    Cybersecurity AI Agent Platform"
echo "    🚀 Quick Setup & Verification"
echo "==============================================="
echo -e "${NC}"

PROJECT_DIR="$(pwd)"
PYTHON_CMD="python3"

# Function to check if command exists
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✅ $1 is installed${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 is not installed${NC}"
        return 1
    fi
}

# Function to check Python package
check_python_package() {
    if $PYTHON_CMD -c "import $1" &> /dev/null; then
        echo -e "${GREEN}✅ Python package '$1' is available${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Python package '$1' is missing${NC}"
        return 1
    fi
}

# System check
echo -e "${CYAN}🔍 System Requirements Check${NC}"
echo "=================================="

# Check operating system
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "${GREEN}✅ Linux system detected${NC}"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${YELLOW}⚠️  macOS detected (some features may differ)${NC}"
else
    echo -e "${RED}❌ Unsupported operating system${NC}"
fi

# Check system resources
MEMORY_GB=$(free -g 2>/dev/null | awk '/^Mem:/{print $2}' || echo "unknown")
CORES=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo "unknown")

echo "💾 Memory: ${MEMORY_GB}GB"
echo "🔢 CPU Cores: ${CORES}"

if [[ "$MEMORY_GB" != "unknown" && "$MEMORY_GB" -lt 6 ]]; then
    echo -e "${YELLOW}⚠️  Low memory detected. Consider enabling swap.${NC}"
fi

# Check required system commands
echo ""
echo -e "${CYAN}📦 System Dependencies${NC}"
echo "========================"

check_command "python3" || MISSING_DEPS=1
check_command "pip3" || MISSING_DEPS=1
check_command "git" || MISSING_DEPS=1
check_command "curl" || MISSING_DEPS=1

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "🐍 Python Version: $PYTHON_VERSION"
    
    # Check if Python version is compatible (3.8+)
    if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
        echo -e "${GREEN}✅ Python version is compatible${NC}"
    else
        echo -e "${RED}❌ Python 3.8+ required${NC}"
        MISSING_DEPS=1
    fi
fi

# Quick setup if missing dependencies
if [[ "$MISSING_DEPS" == "1" ]]; then
    echo ""
    echo -e "${YELLOW}⚠️  Missing dependencies detected!${NC}"
    read -p "Install missing dependencies? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ -f "/etc/debian_version" ]]; then
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv git curl
        elif [[ -f "/etc/redhat-release" ]]; then
            sudo yum install -y python3 python3-pip git curl
        else
            echo -e "${RED}❌ Automatic installation not supported for this OS${NC}"
            echo "Please install Python 3.8+, pip, git, and curl manually"
            exit 1
        fi
    else
        echo -e "${RED}❌ Cannot proceed without required dependencies${NC}"
        exit 1
    fi
fi

# Check if virtual environment exists
echo ""
echo -e "${CYAN}🐍 Python Environment${NC}"
echo "====================="

if [[ -d "venv" ]]; then
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
else
    echo -e "${YELLOW}⚠️  Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Check if requirements are installed
echo ""
echo -e "${CYAN}📚 Python Packages${NC}"
echo "=================="

if [[ -f "requirements.txt" ]]; then
    # Check key packages
    MISSING_PACKAGES=0
    
    packages=("telegram" "yaml" "loguru" "asyncio" "transformers")
    for package in "${packages[@]}"; do
        if ! check_python_package "$package"; then
            MISSING_PACKAGES=1
        fi
    done
    
    if [[ "$MISSING_PACKAGES" == "1" ]]; then
        echo ""
        echo -e "${YELLOW}⚠️  Installing missing Python packages...${NC}"
        pip install --upgrade pip
        pip install -r requirements.txt
        echo -e "${GREEN}✅ Python packages installed${NC}"
    else
        echo -e "${GREEN}✅ All required packages are installed${NC}"
    fi
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi

# Check configuration files
echo ""
echo -e "${CYAN}⚙️  Configuration Files${NC}"
echo "========================"

if [[ -f "config.yaml" ]]; then
    echo -e "${GREEN}✅ config.yaml exists${NC}"
else
    echo -e "${RED}❌ config.yaml missing${NC}"
    exit 1
fi

if [[ -f ".env.template" ]]; then
    echo -e "${GREEN}✅ .env.template exists${NC}"
    
    if [[ ! -f ".env" ]]; then
        echo -e "${YELLOW}⚠️  Creating .env from template...${NC}"
        cp .env.template .env
        echo -e "${YELLOW}📝 Please edit .env file with your API keys${NC}"
    else
        echo -e "${GREEN}✅ .env file exists${NC}"
    fi
else
    echo -e "${RED}❌ .env.template missing${NC}"
    exit 1
fi

# Check required directories
echo ""
echo -e "${CYAN}📁 Directory Structure${NC}"
echo "======================"

required_dirs=("logs" "rag_data" "reports" "finetune_data" "models" "config" "temp")
for dir in "${required_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        echo -e "${GREEN}✅ $dir/ exists${NC}"
    else
        echo -e "${YELLOW}⚠️  Creating $dir/...${NC}"
        mkdir -p "$dir"
        echo -e "${GREEN}✅ $dir/ created${NC}"
    fi
done

# Create necessary subdirectories
mkdir -p logs/{main,pentestgpt,telegram,rss,finetune,file_parser,rag,reports,local_llm,testing}
mkdir -p rag_data/{recon,web,network,exploit,reports,raw,processed,chroma_db}
mkdir -p reports/{daily,weekly,custom,automated}
mkdir -p finetune_data/{raw,processed,checkpoints}
mkdir -p models/{embeddings,lora,local}
mkdir -p config/{prompts,feeds,templates}
mkdir -p temp/{uploads,processing}

# Test basic imports
echo ""
echo -e "${CYAN}🧪 Basic Component Test${NC}"
echo "======================="

# Test core module imports
modules=("pentestgpt_gemini" "rag_embedder" "telegram_bot" "task_router" "rss_fetcher" "file_parser" "report_generator" "finetune_preparer")

for module in "${modules[@]}"; do
    if [[ -f "${module}.py" ]]; then
        if python3 -c "import ${module}" 2>/dev/null; then
            echo -e "${GREEN}✅ ${module}.py imports successfully${NC}"
        else
            echo -e "${YELLOW}⚠️  ${module}.py has import issues (expected until packages are installed)${NC}"
        fi
    else
        echo -e "${RED}❌ ${module}.py missing${NC}"
    fi
done

# Check environment variables
echo ""
echo -e "${CYAN}🔐 Environment Configuration${NC}"
echo "============================"

source .env 2>/dev/null || true

required_vars=("TELEGRAM_BOT_TOKEN" "AUTHORIZED_USER_ID" "GEMINI_API_KEY")
for var in "${required_vars[@]}"; do
    if [[ -n "${!var}" && "${!var}" != *"your_"* ]]; then
        echo -e "${GREEN}✅ $var is configured${NC}"
    else
        echo -e "${YELLOW}⚠️  $var needs to be configured in .env${NC}"
    fi
done

# Test network connectivity
echo ""
echo -e "${CYAN}🌐 Network Connectivity${NC}"
echo "======================="

if curl -s --connect-timeout 5 "https://api.telegram.org" > /dev/null; then
    echo -e "${GREEN}✅ Telegram API reachable${NC}"
else
    echo -e "${YELLOW}⚠️  Telegram API not reachable (check internet connection)${NC}"
fi

if curl -s --connect-timeout 5 "https://generativelanguage.googleapis.com" > /dev/null; then
    echo -e "${GREEN}✅ Gemini API reachable${NC}"
else
    echo -e "${YELLOW}⚠️  Gemini API not reachable (check internet connection)${NC}"
fi

# Quick functionality test
echo ""
echo -e "${CYAN}⚡ Quick Functionality Test${NC}"
echo "=========================="

# Test YAML loading
if python3 -c "import yaml; yaml.safe_load(open('config.yaml'))" 2>/dev/null; then
    echo -e "${GREEN}✅ config.yaml is valid${NC}"
else
    echo -e "${RED}❌ config.yaml is invalid${NC}"
fi

# Test .env loading
if python3 -c "from dotenv import load_dotenv; load_dotenv(); print('✓')" 2>/dev/null; then
    echo -e "${GREEN}✅ .env loading works${NC}"
else
    echo -e "${YELLOW}⚠️  .env loading failed (expected if python-dotenv not installed)${NC}"
fi

# Create quick start script
echo ""
echo -e "${CYAN}🚀 Creating Quick Start Scripts${NC}"
echo "==============================="

# Create run script
cat > run.sh << 'EOF'
#!/bin/bash
# Quick run script for Cybersecurity AI Agent Platform

cd "$(dirname "$0")"
source venv/bin/activate

echo "🚀 Starting Cybersecurity AI Agent Platform..."
python main.py
EOF

chmod +x run.sh
echo -e "${GREEN}✅ run.sh created${NC}"

# Create test script
cat > test.sh << 'EOF'
#!/bin/bash
# Quick test script

cd "$(dirname "$0")"
source venv/bin/activate

echo "🧪 Running integration tests..."
python test_integration.py
EOF

chmod +x test.sh
echo -e "${GREEN}✅ test.sh created${NC}"

# Final summary
echo ""
echo -e "${GREEN}"
echo "🎉 =============================================="
echo "   Setup Verification Complete!"
echo "==============================================="
echo -e "${NC}"

echo -e "${WHITE}📋 Summary:${NC}"
echo "✅ System requirements checked"
echo "✅ Virtual environment ready"
echo "✅ Directory structure created"
echo "✅ Configuration files present"
echo "✅ Quick start scripts created"
echo ""

echo -e "${CYAN}📝 Next Steps:${NC}"
echo "1. Edit .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. Configure your settings in config.yaml if needed:"
echo "   nano config.yaml"
echo ""
echo "3. Run the platform:"
echo "   ./run.sh"
echo "   # OR for full featured installation:"
echo "   ./install_azure.sh"
echo ""
echo "4. Test the system:"
echo "   ./test.sh"
echo ""

echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo "• Make sure to configure your Telegram bot token"
echo "• Add your Telegram user ID as authorized user"
echo "• Get a Gemini API key from Google AI Studio"
echo "• For production deployment, run install_azure.sh"
echo ""

echo -e "${PURPLE}🛡️  Your Cybersecurity AI Agent Platform is ready for configuration!${NC}"
