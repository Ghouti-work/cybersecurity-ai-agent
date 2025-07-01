#!/bin/bash

# ========================================
# Cybersecurity AI Agent Platform
# QUICK DEPLOYMENT SCRIPT (NON-INTERACTIVE)
# ========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Quick Deployment...${NC}"

# Get current directory
PROJECT_DIR=$(pwd)

# Check if we're in the right directory
if [[ ! -f "core/main.py" ]] || [[ ! -f "launch.py" ]]; then
    echo -e "${RED}❌ Please run this script from the project root directory${NC}"
    exit 1
fi

echo -e "${CYAN}📍 Project directory: $PROJECT_DIR${NC}"

# Step 1: Install system dependencies
echo -e "${BLUE}📦 Installing system dependencies...${NC}"
sudo apt update -y > /dev/null 2>&1
sudo apt install -y python3-pip python3-venv python3-dev git curl nginx supervisor > /dev/null 2>&1

# Step 2: Setup Python environment
echo -e "${BLUE}🐍 Setting up Python environment...${NC}"
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1

# Install requirements
if [[ -f "config/requirements.txt" ]]; then
    echo -e "${BLUE}📚 Installing Python dependencies...${NC}"
    pip install -r config/requirements.txt > /dev/null 2>&1
else
    echo -e "${YELLOW}⚠️ No requirements.txt found, installing basic dependencies...${NC}"
    pip install -q loguru python-telegram-bot python-dotenv pyyaml google-generativeai requests aiohttp
fi

# Step 3: Setup configuration
echo -e "${BLUE}⚙️ Setting up configuration...${NC}"
if [[ ! -f ".env" ]]; then
    if [[ -f "config/.env.template" ]]; then
        cp config/.env.template .env
        echo -e "${YELLOW}📝 Created .env file from template - please configure with your API keys${NC}"
    else
        # Create minimal .env
        cat > .env << 'EOF'
# Cybersecurity AI Agent Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
AUTHORIZED_USER_ID=your_telegram_user_id_here
GEMINI_API_KEY=your_gemini_api_key_here
WEBHOOK_URL=https://your-domain.com/webhook

# Optional settings
DEBUG=false
LOG_LEVEL=INFO
EOF
        echo -e "${YELLOW}📝 Created minimal .env file - please configure with your API keys${NC}"
    fi
fi

# Step 4: Create necessary directories
echo -e "${BLUE}📁 Creating directory structure...${NC}"
mkdir -p data/{rag_data,reports,logs} temp config/vpn logs/{main,telegram,agents}

# Step 5: Make scripts executable
chmod +x launch.py deployment/*.sh scripts/*.sh

# Step 6: Test basic functionality
echo -e "${BLUE}🧪 Testing basic functionality...${NC}"
if python launch.py --test > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Basic functionality test passed${NC}"
else
    echo -e "${YELLOW}⚠️ Basic test failed - check configuration${NC}"
fi

echo
echo -e "${GREEN}✅ QUICK DEPLOYMENT COMPLETE!${NC}"
echo
echo -e "${CYAN}📋 Next Steps:${NC}"
echo "1. Configure .env file with your API keys:"
echo "   nano .env"
echo
echo "2. Start the platform:"
echo "   python launch.py"
echo
echo "3. For production deployment:"
echo "   ./deployment/deploy.sh"
echo
echo -e "${CYAN}🔗 Important Files:${NC}"
echo "• Configuration: .env"
echo "• Launch script: launch.py"
echo "• Logs directory: logs/"
echo "• Data directory: data/"
echo
