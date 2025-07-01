#!/bin/bash

# ========================================
# Cybersecurity AI Agent Platform 
# Azure VM Deployment Script
# For Ubuntu 22.04+ with Python 3.10+
# ========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "🛡️  =============================================="
echo "    Cybersecurity AI Agent Platform"
echo "    🤖 Intelligent Pentesting Assistant"
echo "    📡 24/7 Telegram Bot Access"
echo "    🧠 Powered by Gemini API"
echo "==============================================="
echo -e "${NC}"

# Get system information
MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
CORES=$(nproc)
ARCH=$(uname -m)

echo -e "${CYAN}🖥️  System Information:${NC}"
echo "   Memory: ${MEMORY_GB}GB RAM"
echo "   CPU Cores: ${CORES}"
echo "   Architecture: ${ARCH}"
echo ""

# Verify minimum requirements
if [ "$MEMORY_GB" -lt 6 ]; then
    echo -e "${YELLOW}⚠️  Warning: Low memory detected (${MEMORY_GB}GB). Performance may be affected.${NC}"
fi

# Create project directories with proper permissions
echo -e "${BLUE}📁 Creating directory structure...${NC}"
mkdir -p logs/{main,pentestgpt,telegram,rss,finetune,file_parser,rag,reports}
mkdir -p rag_data/{recon,web,network,exploit,reports,raw,processed}
mkdir -p reports/{daily,weekly,custom,automated}
mkdir -p finetune_data/{raw,processed,checkpoints}
mkdir -p models/{embeddings,lora,local}
mkdir -p config/{prompts,feeds,templates}
mkdir -p temp/{uploads,processing}
mkdir -p backup/{daily,weekly}
mkdir -p monitoring/{health,performance}

# Set proper permissions
chmod 755 logs rag_data reports finetune_data models config temp
chmod 700 backup  # More restrictive for backups

echo -e "${GREEN}✅ Directory structure created${NC}"

# Update system packages
echo -e "${BLUE}📦 Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo -e "${BLUE}📦 Installing system dependencies...${NC}"
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    curl \
    wget \
    htop \
    nginx \
    supervisor \
    cron \
    logrotate \
    unzip \
    build-essential \
    sqlite3 \
    poppler-utils \
    tesseract-ocr

echo -e "${GREEN}✅ System dependencies installed${NC}"

# Create Python virtual environment with system isolation
echo -e "${BLUE}🐍 Creating Python virtual environment...${NC}"
python3 -m venv venv --system-site-packages
source venv/bin/activate

# Upgrade pip and install wheel
pip install --upgrade pip wheel setuptools

echo -e "${GREEN}✅ Virtual environment created${NC}"

# Install Python dependencies with optimizations for limited memory
echo -e "${BLUE}📚 Installing Python packages (optimized for 8GB RAM)...${NC}"

# Install core dependencies first
pip install --no-cache-dir python-telegram-bot==20.7
pip install --no-cache-dir python-dotenv==1.0.0
pip install --no-cache-dir pydantic==2.5.3
pip install --no-cache-dir pyyaml==6.0.1
pip install --no-cache-dir loguru==0.7.2

# Install AI/ML dependencies with CPU-only torch
pip install --no-cache-dir torch==2.1.2+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install --no-cache-dir google-generativeai==0.3.2
pip install --no-cache-dir sentence-transformers==2.2.2
pip install --no-cache-dir transformers==4.36.2
pip install --no-cache-dir peft==0.7.1

# Install data processing dependencies
pip install --no-cache-dir feedparser==6.0.10
pip install --no-cache-dir requests==2.31.0
pip install --no-cache-dir beautifulsoup4==4.12.2
pip install --no-cache-dir pypdf2==3.0.1
pip install --no-cache-dir markdown==3.5.2

# Install vector DB and utilities
pip install --no-cache-dir chromadb==0.4.22
pip install --no-cache-dir aiofiles==23.2.0
pip install --no-cache-dir schedule==1.2.0
pip install --no-cache-dir rich==13.7.0
pip install --no-cache-dir jinja2==3.1.2
pip install --no-cache-dir psutil==5.9.6

# Optional utilities
pip install --no-cache-dir numpy==1.24.3

echo -e "${GREEN}✅ Python packages installed${NC}"

# Create environment configuration
echo -e "${BLUE}🔐 Creating environment configuration...${NC}"

if [ ! -f .env ]; then
    cp .env.template .env
    echo -e "${YELLOW}⚠️  Created .env file from template${NC}"
    echo -e "${WHITE}📝 Please edit .env file with your actual API keys:${NC}"
    echo "   - TELEGRAM_BOT_TOKEN (get from @BotFather)"
    echo "   - AUTHORIZED_USER_ID (your Telegram user ID)"
    echo "   - GEMINI_API_KEY (get from Google AI Studio)"
    echo ""
fi

# Create systemd service for automatic startup
echo -e "${BLUE}🔧 Creating systemd service...${NC}"

sudo tee /etc/systemd/system/cyberagent.service > /dev/null << EOF
[Unit]
Description=Cybersecurity AI Agent Platform
After=network.target
Wants=network.target

[Service]
Type=simple
User=$(whoami)
Group=$(whoami)
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$(pwd)/venv/bin/python $(pwd)/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=cyberagent

# Resource limits for 8GB RAM system
MemoryMax=6G
MemoryHigh=5G
TasksMax=100
CPUQuota=80%

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
echo -e "${GREEN}✅ Systemd service created${NC}"

# Create nginx configuration for webhook (optional)
echo -e "${BLUE}🌐 Creating nginx configuration...${NC}"

sudo tee /etc/nginx/sites-available/cyberagent > /dev/null << EOF
server {
    listen 80;
    server_name _;

    location /webhook {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /health {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/cyberagent /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
echo -e "${GREEN}✅ Nginx configuration created${NC}"

# Create log rotation configuration
echo -e "${BLUE}📋 Setting up log rotation...${NC}"

sudo tee /etc/logrotate.d/cyberagent > /dev/null << EOF
$(pwd)/logs/*/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 $(whoami) $(whoami)
    postrotate
        systemctl reload cyberagent
    endscript
}
EOF

echo -e "${GREEN}✅ Log rotation configured${NC}"

# Create monitoring and health check scripts
echo -e "${BLUE}🏥 Creating health monitoring...${NC}"

cat > monitor_system.sh << 'EOF'
#!/bin/bash

# System monitoring for Cybersecurity AI Agent Platform

LOG_FILE="monitoring/health/system_$(date +%Y-%m-%d).log"
mkdir -p monitoring/health

echo "$(date): Starting health check" >> "$LOG_FILE"

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
echo "Memory Usage: ${MEMORY_USAGE}%" >> "$LOG_FILE"

# Check disk usage
DISK_USAGE=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
echo "Disk Usage: ${DISK_USAGE}%" >> "$LOG_FILE"

# Check if main service is running
if systemctl is-active --quiet cyberagent; then
    echo "Service Status: Running" >> "$LOG_FILE"
else
    echo "Service Status: Stopped" >> "$LOG_FILE"
    # Auto-restart if stopped
    sudo systemctl start cyberagent
    echo "Auto-restart attempted" >> "$LOG_FILE"
fi

# Check log file sizes
LOG_SIZE=$(du -sh logs/ | cut -f1)
echo "Log Directory Size: $LOG_SIZE" >> "$LOG_FILE"

# Alert if high resource usage
if (( $(echo "$MEMORY_USAGE > 85" | bc -l) )); then
    echo "⚠️ HIGH MEMORY USAGE: ${MEMORY_USAGE}%" >> "$LOG_FILE"
fi

if (( DISK_USAGE > 90 )); then
    echo "⚠️ HIGH DISK USAGE: ${DISK_USAGE}%" >> "$LOG_FILE"
fi
EOF

chmod +x monitor_system.sh
echo -e "${GREEN}✅ System monitoring created${NC}"

# Create backup script
echo -e "${BLUE}💾 Creating backup system...${NC}"

cat > backup_data.sh << 'EOF'
#!/bin/bash

# Backup script for Cybersecurity AI Agent Platform

BACKUP_DATE=$(date +%Y-%m-%d)
BACKUP_DIR="backup/daily/$BACKUP_DATE"

mkdir -p "$BACKUP_DIR"

echo "Starting backup: $BACKUP_DATE"

# Backup configuration
cp -r config/ "$BACKUP_DIR/"
cp .env "$BACKUP_DIR/" 2>/dev/null || true
cp config.yaml "$BACKUP_DIR/"

# Backup RAG data
tar -czf "$BACKUP_DIR/rag_data.tar.gz" rag_data/

# Backup important logs (last 7 days)
find logs/ -name "*.log" -mtime -7 -exec cp {} "$BACKUP_DIR/" \;

# Backup reports
tar -czf "$BACKUP_DIR/reports.tar.gz" reports/

# Clean old backups (keep 7 days)
find backup/daily/ -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null || true

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x backup_data.sh
echo -e "${GREEN}✅ Backup system created${NC}"

# Set up cron jobs for automation
echo -e "${BLUE}⏰ Setting up cron jobs...${NC}"

# Create cron job entries
cat > crontab_entries << EOF
# Cybersecurity AI Agent Platform Automation

# System health monitoring (every 30 minutes)
*/30 * * * * cd $(pwd) && ./monitor_system.sh

# Daily backup (every day at 2 AM)
0 2 * * * cd $(pwd) && ./backup_data.sh

# RSS feed updates (every 6 hours)
0 */6 * * * cd $(pwd) && ./venv/bin/python -c "import asyncio; from rss_fetcher import RSSFetcher; import yaml; config = yaml.safe_load(open('config.yaml')); rss = RSSFetcher(config); asyncio.run(rss.fetch_all_feeds())"

# Weekly fine-tune data preparation (Sunday at 3 AM)
0 3 * * 0 cd $(pwd) && ./venv/bin/python -c "import asyncio; from finetune_preparer import FineTunePreparer; import yaml; config = yaml.safe_load(open('config.yaml')); ft = FineTunePreparer(config); asyncio.run(ft.prepare_training_data())"

# Clean temp files (daily at 4 AM)
0 4 * * * find $(pwd)/temp/ -type f -mtime +1 -delete

# Log cleanup (weekly on Saturday at 1 AM)
0 1 * * 6 find $(pwd)/logs/ -name "*.log" -mtime +30 -delete
EOF

# Install cron jobs
crontab crontab_entries
rm crontab_entries

echo -e "${GREEN}✅ Cron jobs configured${NC}"

# Create quick management scripts
echo -e "${BLUE}🔧 Creating management scripts...${NC}"

# Service management script
cat > manage_service.sh << 'EOF'
#!/bin/bash

case "$1" in
    start)
        sudo systemctl start cyberagent
        echo "✅ Service started"
        ;;
    stop)
        sudo systemctl stop cyberagent
        echo "🛑 Service stopped"
        ;;
    restart)
        sudo systemctl restart cyberagent
        echo "🔄 Service restarted"
        ;;
    status)
        systemctl status cyberagent
        ;;
    logs)
        journalctl -u cyberagent -f
        ;;
    enable)
        sudo systemctl enable cyberagent
        echo "✅ Service enabled for auto-start"
        ;;
    disable)
        sudo systemctl disable cyberagent
        echo "🛑 Service disabled from auto-start"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|enable|disable}"
        exit 1
        ;;
esac
EOF

chmod +x manage_service.sh

# Environment check script
cat > check_environment.sh << 'EOF'
#!/bin/bash

echo "🔍 Environment Check"
echo "==================="

# Check Python
echo "Python version: $(python3 --version)"

# Check virtual environment
if [ -d "venv" ]; then
    echo "✅ Virtual environment exists"
else
    echo "❌ Virtual environment missing"
fi

# Check .env file
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    # Check for required variables
    if grep -q "TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here" .env; then
        echo "⚠️  TELEGRAM_BOT_TOKEN needs to be configured"
    fi
    if grep -q "GEMINI_API_KEY=your_gemini_api_key_here" .env; then
        echo "⚠️  GEMINI_API_KEY needs to be configured"
    fi
else
    echo "❌ .env file missing"
fi

# Check service status
if systemctl is-enabled --quiet cyberagent; then
    echo "✅ Service enabled for auto-start"
else
    echo "⚠️  Service not enabled for auto-start"
fi

# Check system resources
echo ""
echo "System Resources:"
echo "Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
echo "Disk: $(df -h . | tail -1 | awk '{print $3 "/" $2 " (" $5 ")"}')"
echo "CPU Load: $(uptime | awk -F'load average:' '{ print $2 }')"
EOF

chmod +x check_environment.sh

echo -e "${GREEN}✅ Management scripts created${NC}"

# Set proper file permissions
echo -e "${BLUE}🔒 Setting file permissions...${NC}"
chmod +x *.py *.sh
chmod 600 .env .env.template 2>/dev/null || true
chmod 644 config.yaml requirements.txt

echo -e "${GREEN}✅ Permissions set${NC}"

# Final setup summary
echo -e "${GREEN}"
echo "🎉 =============================================="
echo "   Azure VM Setup Complete!"
echo "==============================================="
echo -e "${NC}"

echo -e "${WHITE}📋 Setup Summary:${NC}"
echo "✅ System dependencies installed"
echo "✅ Python environment configured"
echo "✅ All packages installed"
echo "✅ Systemd service created"
echo "✅ Nginx proxy configured"
echo "✅ Log rotation configured"
echo "✅ Monitoring scripts created"
echo "✅ Backup system configured"
echo "✅ Cron jobs scheduled"
echo ""

echo -e "${YELLOW}⚠️  IMPORTANT NEXT STEPS:${NC}"
echo "1. Edit .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. Test the configuration:"
echo "   ./check_environment.sh"
echo ""
echo "3. Start the service:"
echo "   ./manage_service.sh start"
echo ""
echo "4. Enable auto-start:"
echo "   ./manage_service.sh enable"
echo ""
echo "5. Monitor the service:"
echo "   ./manage_service.sh logs"
echo ""

echo -e "${CYAN}🔧 Management Commands:${NC}"
echo "• Check status: ./manage_service.sh status"
echo "• View logs: ./manage_service.sh logs"
echo "• Restart: ./manage_service.sh restart"
echo "• Monitor system: ./monitor_system.sh"
echo "• Check environment: ./check_environment.sh"
echo "• Manual backup: ./backup_data.sh"
echo ""

echo -e "${BLUE}📡 Service Information:${NC}"
echo "• Service name: cyberagent"
echo "• Main script: main.py"
echo "• Webhook URL: http://your-vm-ip/webhook"
echo "• Health check: http://your-vm-ip/health"
echo ""

echo -e "${PURPLE}🛡️  Your Cybersecurity AI Agent Platform is ready!${NC}"
echo -e "${WHITE}Connect via Telegram and use /help to get started.${NC}"
