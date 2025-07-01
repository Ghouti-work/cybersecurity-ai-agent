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

PROJECT_DIR="$(pwd)"
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

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
    pip install -r requirements.txt > /dev/null 2>&1
    
    # Step 3: Configuration
    ((current_step++))
    show_progress $current_step $total_steps "Creating production configuration..."
    if [[ ! -f ".env" ]]; then
        cp .env.template .env
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
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/main.py
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
*/30 * * * * cd $PROJECT_DIR && python health_monitor.py
0 */6 * * * cd $PROJECT_DIR && venv/bin/python -c "import asyncio; from rss_fetcher import RSSFetcher; import yaml; asyncio.run(RSSFetcher(yaml.safe_load(open('config.yaml'))).fetch_all_feeds())"
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
    
    if [[ -f "health_monitor.py" ]] && [[ -d "venv" ]]; then
        source venv/bin/activate
        python health_monitor.py
    else
        echo -e "${RED}❌ Health monitor not available${NC}"
    fi
fi

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
