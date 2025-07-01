#!/bin/bash

# ========================================
# Cybersecurity AI Agent Platform
# ONE-CLICK DEPLOYMENT SCRIPT
# ========================================

set -e

# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ASCII Art Banner
echo -e "${BLUE}${BOLD}"
cat << 'EOF'
 ██████╗██╗   ██╗██████╗ ███████╗██████╗      █████╗  ██████╗ ███████╗███╗   ██╗████████╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   
╚██████╗   ██║   ██████╔╝███████╗██║  ██║    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   
                                                                                          
🛡️  INTELLIGENT CYBERSECURITY AI PLATFORM 🛡️
🤖 24/7 Telegram Bot • 🧠 Gemini API • 📡 RSS Intelligence • 🔍 RAG Knowledge Base
EOF
echo -e "${NC}"

# Project configuration with new structure
PROJECT_NAME="cybersecurity-ai-agent"
PROJECT_DIR="/opt/cybersecurity-ai-agent"
GITHUB_REPO="https://github.com/Ghouti-work/cybersecurity-ai-agent.git"
USER="cybersec"
GROUP="cybersec"

# Service configuration for new components
SERVICES=(
    "cybersec-main-agent"
    "cybersec-telegram-bot" 
    "cybersec-task-router"
    "cybersec-health-monitor"
    "cybersec-local-llm"
    "cybersec-vpn-manager"
    "cybersec-gemini-processor"
)

# New structure paths
CORE_DIR="$PROJECT_DIR/core"
AGENTS_DIR="$PROJECT_DIR/agents"
INTEGRATIONS_DIR="$PROJECT_DIR/integrations"
CONFIG_DIR="$PROJECT_DIR/config"
DATA_DIR="/var/lib/cybersec-agent"
LOG_DIR="/var/log/cybersec-agent"
MODELS_DIR="$DATA_DIR/models"
VPN_CONFIG_DIR="$CONFIG_DIR/vpn"

# Additional configuration
DEEPSEEK_MODEL="deepseek-ai/deepseek-coder-1.3b-instruct"
GEMINI_MODEL="gemini-2.5-flash-latest"

# Deployment mode selection
echo -e "${WHITE}${BOLD}🚀 DEPLOYMENT MODE SELECTION${NC}"
echo "==========================================="
echo ""
echo "Choose your deployment option:"
echo ""
echo -e "${GREEN}1. ${CYAN}Quick Setup${NC}          - Fast local development setup"
echo -e "${GREEN}2. ${YELLOW}Production Azure VM${NC}  - Full Azure VM deployment with monitoring"
echo -e "${GREEN}3. ${PURPLE}Testing & Validation${NC} - Run integration tests only"
echo -e "${GREEN}4. ${BLUE}Health Check${NC}         - Monitor existing installation"
echo ""

read -p "Select option (1-4): " -n 1 -r
echo
echo

case $REPLY in
    1)
        echo -e "${CYAN}🚀 Starting Quick Setup...${NC}"
        DEPLOYMENT_MODE="quick"
        ;;
    2)
        echo -e "${YELLOW}🌐 Starting Azure Production Deployment...${NC}"
        DEPLOYMENT_MODE="azure"
        ;;
    3)
        echo -e "${PURPLE}🧪 Starting Testing & Validation...${NC}"
        DEPLOYMENT_MODE="test"
        ;;
    4)
        echo -e "${BLUE}🏥 Starting Health Check...${NC}"
        DEPLOYMENT_MODE="health"
        ;;
    *)
        echo -e "${RED}❌ Invalid option. Exiting.${NC}"
        exit 1
        ;;
esac

# Function to show progress
show_progress() {
    local current=$1
    local total=$2
    local message=$3
    local percent=$((current * 100 / total))
    local bar_length=30
    local filled_length=$((percent * bar_length / 100))
    
    echo -ne "\r${GREEN}["
    for ((i=0; i<filled_length; i++)); do echo -ne "█"; done
    for ((i=filled_length; i<bar_length; i++)); do echo -ne "░"; done
    echo -ne "] ${percent}% ${message}${NC}"
    
    if [[ $current -eq $total ]]; then
        echo
    fi
}

# Quick Setup Mode
if [[ "$DEPLOYMENT_MODE" == "quick" ]]; then
    echo -e "${CYAN}🔧 QUICK SETUP MODE${NC}"
    echo "======================"
    echo
    
    total_steps=6
    current_step=0
    
    # Step 1: Check system
    ((current_step++))
    show_progress $current_step $total_steps "Checking system requirements..."
    ./quick_setup.sh > /tmp/quick_setup.log 2>&1 && echo -e "\n✅ System check complete" || echo -e "\n⚠️  See /tmp/quick_setup.log for details"
    
    # Step 2: Setup environment
    ((current_step++))
    show_progress $current_step $total_steps "Setting up virtual environment..."
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install --upgrade pip > /dev/null 2>&1
    
    # Step 3: Install packages
    ((current_step++))
    show_progress $current_step $total_steps "Installing Python packages..."
    pip install -r requirements.txt > /dev/null 2>&1
    
    # Step 4: Create config
    ((current_step++))
    show_progress $current_step $total_steps "Creating configuration..."
    if [[ ! -f ".env" ]]; then
        cp .env.template .env
    fi
    
    # Step 5: Create directories
    ((current_step++))
    show_progress $current_step $total_steps "Creating directories..."
    mkdir -p logs/{main,telegram,pentestgpt,rss,integration}
    mkdir -p rag_data/{recon,web,network,exploit,reports,chroma_db}
    mkdir -p reports/{daily,weekly,custom}
    mkdir -p temp/{uploads,processing}
    
    # Step 6: Final check
    ((current_step++))
    show_progress $current_step $total_steps "Finalizing setup..."
    chmod +x *.py *.sh
    
    echo
    echo -e "${GREEN}✅ QUICK SETUP COMPLETE!${NC}"
    echo
    echo -e "${WHITE}📝 Next Steps:${NC}"
    echo "1. Edit .env file: nano .env"
    echo "2. Add your API keys (Telegram bot token, Gemini API key)"
    echo "3. Run the platform: python main.py"
    echo "4. Test with Telegram: /help"
    echo
    echo -e "${YELLOW}⚠️  Remember to configure:${NC}"
    echo "• TELEGRAM_BOT_TOKEN (from @BotFather)"
    echo "• AUTHORIZED_USER_ID (your Telegram user ID)"  
    echo "• GEMINI_API_KEY (from Google AI Studio)"
    echo
    
# Azure Production Deployment
elif [[ "$DEPLOYMENT_MODE" == "azure" ]]; then
    echo -e "${YELLOW}🌐 AZURE PRODUCTION DEPLOYMENT${NC}"
    echo "================================="
    echo
    
    # Check if we're on Azure VM
    if curl -s -H "Metadata:true" "http://169.254.169.254/metadata/instance?api-version=2021-02-01" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Azure VM detected${NC}"
    else
        echo -e "${YELLOW}⚠️  Not running on Azure VM (proceeding anyway)${NC}"
    fi
    
    total_steps=8
    current_step=0
    
    # Step 1: System setup
    ((current_step++))
    show_progress $current_step $total_steps "Installing system dependencies..."
    sudo apt update > /dev/null 2>&1
    sudo apt install -y python3-pip python3-venv git curl nginx supervisor > /dev/null 2>&1
    
    # Step 2: Python environment
    ((current_step++))
    show_progress $current_step $total_steps "Setting up Python environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r config/requirements.txt > /dev/null 2>&1
    
    # Step 3: Configuration
    ((current_step++))
    show_progress $current_step $total_steps "Creating production configuration..."
    if [[ ! -f ".env" ]]; then
        cp config/.env.template .env
        echo -e "\n${YELLOW}📝 Please configure .env file with production values${NC}"
    fi
    
    # Step 4: Systemd service
    ((current_step++))
    show_progress $current_step $total_steps "Creating systemd service..."
    sudo tee /etc/systemd/system/cyberagent.service > /dev/null << EOF
[Unit]
Description=Cybersecurity AI Agent Platform
After=network.target
Wants=network.target

[Service]
Type=simple
User=$(whoami)
Group=$(whoami)
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/launch.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Resource limits for production
MemoryMax=6G
MemoryHigh=5G
TasksMax=100
CPUQuota=80%

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    
    # Step 5: Nginx configuration
    ((current_step++))
    show_progress $current_step $total_steps "Configuring nginx..."
    sudo tee /etc/nginx/sites-available/cyberagent > /dev/null << EOF
server {
    listen 80;
    server_name _;

    location /webhook {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /health {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
    }
}
EOF
    
    sudo ln -sf /etc/nginx/sites-available/cyberagent /etc/nginx/sites-enabled/
    sudo nginx -t > /dev/null 2>&1 && sudo systemctl reload nginx
    
    # Step 6: Log rotation
    ((current_step++))
    show_progress $current_step $total_steps "Setting up log rotation..."
    sudo tee /etc/logrotate.d/cyberagent > /dev/null << EOF
$PROJECT_DIR/logs/*/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 $(whoami) $(whoami)
}
EOF
    
    # Step 7: Cron jobs
    ((current_step++))
    show_progress $current_step $total_steps "Setting up automation..."
    (crontab -l 2>/dev/null || echo "") | cat - << EOF | crontab -
# Cybersecurity AI Agent automation
*/30 * * * * cd $PROJECT_DIR && venv/bin/python agents/health_monitor.py
0 */6 * * * cd $PROJECT_DIR && venv/bin/python -c "import asyncio; from agents.rss_fetcher import RSSFetcher; import yaml; asyncio.run(RSSFetcher(yaml.safe_load(open('config/config.yaml'))).fetch_all_feeds())"
0 2 * * * cd $PROJECT_DIR && find temp/ -type f -mtime +1 -delete
EOF
    
    # Step 8: Final setup
    ((current_step++))
    show_progress $current_step $total_steps "Finalizing production setup..."
    mkdir -p logs/{main,telegram,pentestgpt,rss,integration,health}
    mkdir -p rag_data/{recon,web,network,exploit,reports,chroma_db}
    mkdir -p reports/{daily,weekly,custom}
    mkdir -p monitoring/{health,performance}
    mkdir -p backup/{daily,weekly}
    
    chmod +x *.py *.sh
    
    echo
    echo -e "${GREEN}✅ AZURE PRODUCTION DEPLOYMENT COMPLETE!${NC}"
    echo
    echo -e "${WHITE}🚀 Service Management:${NC}"
    echo "• Start service: sudo systemctl start cyberagent"
    echo "• Enable auto-start: sudo systemctl enable cyberagent"
    echo "• Check status: sudo systemctl status cyberagent"
    echo "• View logs: journalctl -u cyberagent -f"
    echo
    echo -e "${WHITE}📝 Configuration:${NC}"
    echo "• Edit .env file: nano .env"
    echo "• Configure API keys before starting"
    echo "• Test configuration: python final_integration.py"
    echo
    echo -e "${WHITE}🌐 Endpoints:${NC}"
    echo "• Health check: http://$(curl -s ifconfig.me)/health"
    echo "• Webhook: http://$(curl -s ifconfig.me)/webhook"
    echo

# Testing & Validation Mode
elif [[ "$DEPLOYMENT_MODE" == "test" ]]; then
    echo -e "${PURPLE}🧪 TESTING & VALIDATION MODE${NC}"
    echo "=============================="
    echo
    
    total_steps=4
    current_step=0
    
    # Step 1: Environment check
    ((current_step++))
    show_progress $current_step $total_steps "Checking environment..."
    if [[ -d "venv" ]]; then
        source venv/bin/activate
    else
        echo -e "\n${RED}❌ Virtual environment not found. Run quick setup first.${NC}"
        exit 1
    fi
    
    # Step 2: Quick integration test
    ((current_step++))
    show_progress $current_step $total_steps "Running quick integration tests..."
    python test_integration.py > /tmp/integration_test.log 2>&1
    
    # Step 3: Comprehensive validation
    ((current_step++))
    show_progress $current_step $total_steps "Running comprehensive validation..."
    python final_integration.py > /tmp/final_integration.log 2>&1
    
    # Step 4: Generate report
    ((current_step++))
    show_progress $current_step $total_steps "Generating test report..."
    
    echo
    echo -e "${GREEN}✅ TESTING COMPLETE!${NC}"
    echo
    echo -e "${WHITE}📊 Test Results:${NC}"
    echo "• Integration test log: /tmp/integration_test.log"
    echo "• Final validation log: /tmp/final_integration.log"
    echo "• Detailed results: logs/integration/"
    echo
    
    # Show summary from final integration
    if [[ -f "logs/integration/final_integration_results.json" ]]; then
        echo -e "${WHITE}📋 Quick Summary:${NC}"
        python3 -c "
import json
try:
    with open('logs/integration/final_integration_results.json', 'r') as f:
        results = json.load(f)
    
    deployment = results.get('deployment', {})
    ready = deployment.get('ready_for_deployment', False)
    
    if ready:
        print('✅ PLATFORM READY FOR DEPLOYMENT')
    else:
        print('❌ ISSUES DETECTED - NOT READY')
        issues = deployment.get('critical_issues', [])
        if issues:
            print('Critical issues:')
            for issue in issues[:3]:
                print(f'  • {issue}')
except:
    print('⚠️  Could not parse test results')
"
    fi
    echo

# Health Check Mode
elif [[ "$DEPLOYMENT_MODE" == "health" ]]; then
    echo -e "${BLUE}🏥 HEALTH CHECK MODE${NC}"
    echo "===================="
    echo
    
    # Check if platform is running
    if pgrep -f "python.*main.py" > /dev/null; then
        echo -e "${GREEN}✅ Platform is running${NC}"
    else
        echo -e "${YELLOW}⚠️  Platform is not running${NC}"
    fi
    
    # Check systemd service
    if systemctl is-active --quiet cyberagent 2>/dev/null; then
        echo -e "${GREEN}✅ Systemd service is active${NC}"
    else
        echo -e "${YELLOW}⚠️  Systemd service is not active${NC}"
    fi
    
    # Run health monitor
    echo
    echo -e "${BLUE}🔍 Running health monitor...${NC}"
    echo
    
    if [[ -f "agents/health_monitor.py" ]] && [[ -d "venv" ]]; then
        source venv/bin/activate
        python agents/health_monitor.py
    else
        echo -e "${RED}❌ Health monitor not available${NC}"
    fi
fi

# Function to clone/update project from GitHub
setup_project_from_github() {
    local target_dir=$1
    local mode=$2
    
    echo -e "${CYAN}📥 Setting up project from GitHub...${NC}"
    
    if [[ "$mode" == "production" ]]; then
        # Production deployment - fresh clone
        if [[ -d "$target_dir" ]]; then
            echo -e "${YELLOW}⚠️  Existing installation found. Creating backup...${NC}"
            sudo mv "$target_dir" "${target_dir}_backup_$(date +%Y%m%d_%H%M%S)"
        fi
        
        echo -e "${BLUE}🔄 Cloning repository...${NC}"
        sudo git clone "$GITHUB_REPO" "$target_dir"
        sudo chown -R "$USER:$GROUP" "$target_dir"
        
    else
        # Local/development mode
        if [[ ! -d ".git" ]]; then
            echo -e "${YELLOW}⚠️  Not a git repository. Initializing...${NC}"
            git init
            git remote add origin "$GITHUB_REPO" 2>/dev/null || true
        fi
        
        echo -e "${BLUE}🔄 Updating from remote...${NC}"
        git fetch origin 2>/dev/null || echo -e "${YELLOW}⚠️  Could not fetch from remote (proceeding with local files)${NC}"
    fi
}

# Function to install system dependencies for new components
install_system_dependencies() {
    echo -e "${BLUE}📦 Installing system dependencies...${NC}"
    
    # Core system packages
    sudo apt update
    sudo apt install -y \
        python3-pip python3-venv python3-dev \
        git curl wget nginx supervisor \
        openvpn wireguard-tools \
        nmap masscan \
        sqlite3 postgresql-client \
        build-essential \
        libssl-dev libffi-dev \
        fonts-liberation \
        poppler-utils \
        tesseract-ocr
    
    # Install Docker for containerized tools
    if ! command -v docker &> /dev/null; then
        echo -e "${BLUE}🐳 Installing Docker...${NC}"
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker "$USER"
        rm get-docker.sh
    fi
    
    # Install Rust for some security tools
    if ! command -v cargo &> /dev/null; then
        echo -e "${BLUE}🦀 Installing Rust...${NC}"
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        source ~/.cargo/env
    fi
}

# Function to setup Python environment with all dependencies
setup_python_environment() {
    local project_dir=$1
    
    echo -e "${BLUE}🐍 Setting up Python environment...${NC}"
    
    cd "$project_dir"
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip wheel setuptools
    
    # Install core requirements
    if [[ -f "config/requirements.txt" ]]; then
        pip install -r config/requirements.txt
    fi
    
    # Install additional packages for new components
    pip install \
        google-generativeai \
        transformers \
        torch \
        sentence-transformers \
        chromadb \
        faiss-cpu \
        peft \
        accelerate \
        bitsandbytes \
        datasets \
        psutil \
        PyPDF2 \
        python-docx \
        python-pptx \
        Pillow \
        python-magic \
        networkx \
        scapy \
        requests-oauthlib
    
    # Install PentestGPT dependencies
    if [[ -d "PentestGPT" ]]; then
        cd PentestGPT
        pip install -e .
        cd ..
    fi
    
    # Install CAI dependencies
    if [[ -d "CAI" ]]; then
        cd CAI
        pip install -e .
        cd ..
    fi
    
    echo -e "${GREEN}✅ Python environment setup complete${NC}"
}

# Function to create new directory structure
create_directory_structure() {
    local project_dir=$1
    
    echo -e "${BLUE}📁 Creating directory structure...${NC}"
    
    # Core directories
    mkdir -p "$project_dir"/{core,agents,integrations,config,data,logs,temp}
    
    # Data directories  
    mkdir -p "$project_dir/data"/{rag_data,documents,processed,pentest_sessions,pentest_reports,finetune_data,models}
    
    # Config directories
    mkdir -p "$project_dir/config"/{vpn,templates,prompts}
    
    # Log directories
    mkdir -p "$project_dir/logs"/{main,telegram,pentestgpt,rss,integration,health,gemini,deepseek,vpn}
    
    # Model storage
    mkdir -p "$project_dir/data/models"/{local,deepseek,cache}
    
    # VPN configs
    mkdir -p "$project_dir/config/vpn"/{openvpn,wireguard,custom}
    
    # Processing directories
    mkdir -p "$project_dir/temp"/{uploads,processing,reports,analysis}
    
    # External tool directories  
    mkdir -p "$project_dir/external"/{tools,wordlists,exploits}
    
    # Set permissions
    if [[ "$project_dir" != "$(pwd)" ]]; then
        sudo chown -R "$USER:$GROUP" "$project_dir"
    fi
    
    chmod -R 755 "$project_dir"
    chmod -R 700 "$project_dir/config/vpn"
    
    echo -e "${GREEN}✅ Directory structure created${NC}"
}

# Function to setup systemd services for new components
setup_systemd_services() {
    local project_dir=$1
    
    echo -e "${BLUE}⚙️ Setting up systemd services...${NC}"
    
    # Main agent service
    sudo tee /etc/systemd/system/cybersec-main-agent.service > /dev/null << EOF
[Unit]
Description=Cybersecurity AI Agent - Main Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
Group=$GROUP
WorkingDirectory=$project_dir
Environment=PATH=$project_dir/venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=$project_dir
ExecStart=$project_dir/venv/bin/python $project_dir/launch.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Resource limits
MemoryMax=4G
MemoryHigh=3G
TasksMax=100
CPUQuota=70%

[Install]
WantedBy=multi-user.target
EOF

    # Task router service
    sudo tee /etc/systemd/system/cybersec-task-router.service > /dev/null << EOF
[Unit]
Description=Cybersecurity AI Agent - Task Router
After=network.target cybersec-main-agent.service
Wants=network.target

[Service]
Type=simple
User=$USER
Group=$GROUP
WorkingDirectory=$project_dir
Environment=PATH=$project_dir/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$project_dir/venv/bin/python $project_dir/core/task_router.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Resource limits
MemoryMax=2G
MemoryHigh=1.5G
TasksMax=50

[Install]
WantedBy=multi-user.target
EOF

    # Local LLM service
    sudo tee /etc/systemd/system/cybersec-local-llm.service > /dev/null << EOF
[Unit]
Description=Cybersecurity AI Agent - Local LLM Server
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
Group=$GROUP
WorkingDirectory=$project_dir
Environment=PATH=$project_dir/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$project_dir/venv/bin/python $project_dir/integrations/local_llm_server.py
Restart=always
RestartSec=15
StandardOutput=journal
StandardError=journal

# Higher memory for LLM
MemoryMax=6G
MemoryHigh=5G
TasksMax=20
CPUQuota=80%

[Install]
WantedBy=multi-user.target
EOF

    # Health monitor service
    sudo tee /etc/systemd/system/cybersec-health-monitor.service > /dev/null << EOF
[Unit]
Description=Cybersecurity AI Agent - Health Monitor
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
Group=$GROUP
WorkingDirectory=$project_dir
Environment=PATH=$project_dir/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$project_dir/venv/bin/python $project_dir/agents/health_monitor.py
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

# Minimal resources for monitoring
MemoryMax=512M
MemoryHigh=256M
TasksMax=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    
    echo -e "${GREEN}✅ Systemd services configured${NC}"
}

# Function to setup configuration files
setup_configuration() {
    local project_dir=$1
    
    echo -e "${BLUE}⚙️ Setting up configuration...${NC}"
    
    cd "$project_dir"
    
    # Create main config if it doesn't exist
    if [[ ! -f "core/config.yaml" ]]; then
        cat > "core/config.yaml" << EOF
# Cybersecurity AI Agent Platform Configuration
# Updated for new structure with enhanced components

# Core settings
debug: false
log_level: "INFO"
max_concurrent_tasks: 10

# API Configuration
apis:
  gemini:
    model: "gemini-1.5-pro-latest"
    api_key: "\${GEMINI_API_KEY}"
    safety_settings: "none"  # For cybersecurity content
  
  telegram:
    bot_token: "\${TELEGRAM_BOT_TOKEN}"
    authorized_users: ["\${AUTHORIZED_USER_ID}"]
    webhook_url: "\${WEBHOOK_URL}"

# Local LLM Configuration
local_llm:
  enabled: true
  model_name: "deepseek-ai/deepseek-coder-1.3b-instruct"
  device: "auto"
  max_memory_mb: 4096
  use_quantization: true

# Fine-tuning Configuration
fine_tuning:
  enabled: true
  data_sources:
    - "data/rag_data/**/*.json"
    - "data/processed/**/*.json"
    - "logs/**/*.log"
  validation_split: 0.1
  max_sequence_length: 512
  lora_config:
    r: 16
    lora_alpha: 32
    lora_dropout: 0.1

# VPN Configuration
vpn:
  tryhackme:
    type: "openvpn"
    config_path: "config/vpn/tryhackme.ovpn"
    auto_connect: false
  hackthebox:
    type: "openvpn" 
    config_path: "config/vpn/hackthebox.ovpn"
    auto_connect: false

# CAI Configuration
cai:
  use_local_llm: true
  rag_enabled: true
  agent_types:
    - "reconnaissance"
    - "vulnerability_assessment"
    - "code_analysis" 
    - "threat_intelligence"

# PentestGPT Configuration
pentestgpt:
  use_gemini_only: true
  model: "gemini-1.5-pro-latest"
  session_timeout: 3600
  max_phases: 7

# RAG Configuration
rag:
  embedding_model: "all-MiniLM-L6-v2"
  vector_db: "chromadb"
  chunk_size: 1000
  chunk_overlap: 100
  max_documents: 10000

# Agent Configuration
agents:
  rss_fetcher:
    enabled: true
    update_interval: 3600
    sources:
      - "https://feeds.feedburner.com/eset/blog"
      - "https://krebsonsecurity.com/feed/"
      - "https://threatpost.com/feed/"
  
  file_parser:
    enabled: true
    supported_formats: ["pdf", "docx", "txt", "md", "html"]
    max_file_size_mb: 50
  
  report_generator:
    enabled: true
    output_formats: ["json", "html", "pdf"]
    template_dir: "config/templates"

# Health Monitor Configuration
health_monitor:
  check_interval: 300
  memory_threshold: 80
  disk_threshold: 85
  cpu_threshold: 90
  alert_webhook: "\${HEALTH_ALERT_WEBHOOK}"

# Security Settings
security:
  rate_limiting: true
  request_timeout: 300
  max_file_upload_mb: 100
  allowed_ips: []  # Empty = allow all
  
# Logging Configuration
logging:
  level: "INFO"
  max_file_size_mb: 100
  backup_count: 5
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
EOF
    fi
    
    # Create environment template
    if [[ ! -f ".env.template" ]]; then
        cat > ".env.template" << EOF
# Cybersecurity AI Agent Platform Environment Variables
# Copy this file to .env and fill in your values

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
AUTHORIZED_USER_ID=your_telegram_user_id_here

# Optional APIs
OPENAI_API_KEY=optional_openai_key_for_fallback
ANTHROPIC_API_KEY=optional_claude_key

# Webhook Configuration
WEBHOOK_URL=https://your-domain.com/webhook
HEALTH_ALERT_WEBHOOK=https://your-monitoring-webhook.com

# Database Configuration (if using external DB)
DATABASE_URL=postgresql://user:pass@localhost/cybersec_agent

# Security Configuration
SECRET_KEY=your_secret_key_for_encryption
ALLOWED_HOSTS=localhost,your-domain.com

# Resource Configuration
MAX_MEMORY_MB=4096
MAX_CONCURRENT_TASKS=10

# Development Settings
DEBUG=false
LOG_LEVEL=INFO
EOF
    fi
    
    # Copy template to .env if it doesn't exist
    if [[ ! -f ".env" ]]; then
        cp ".env.template" ".env"
        echo -e "${YELLOW}📝 Created .env file - please configure your API keys${NC}"
    fi
    
    echo -e "${GREEN}✅ Configuration setup complete${NC}"
}

# Final message
echo
echo -e "${BOLD}${BLUE}"
echo "=============================================="
echo "🛡️  CYBERSECURITY AI AGENT PLATFORM"
echo "=============================================="
echo -e "${NC}"
echo -e "${WHITE}Thank you for using the Cybersecurity AI Agent Platform!${NC}"
echo -e "${CYAN}For support and documentation: README.md${NC}"
echo -e "${GREEN}Happy hacking! 🛡️🤖${NC}"
echo
