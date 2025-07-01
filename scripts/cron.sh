#!/bin/bash

# Cron Job Setup Script for Cybersecurity AI Agent
# Sets up automated tasks for RSS fetching, fine-tuning, and system maintenance

set -e

echo "🕒 Setting up cron jobs for Cybersecurity AI Agent..."

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Warning: Not in a virtual environment. Using system Python."
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    echo "✓ Virtual environment detected: $VIRTUAL_ENV"
    PYTHON_CMD="$VIRTUAL_ENV/bin/python"
    PIP_CMD="$VIRTUAL_ENV/bin/pip"
fi

# Create log directory for cron jobs
mkdir -p "$PROJECT_DIR/logs/cron"

# Function to add cron job safely
add_cron_job() {
    local schedule="$1"
    local command="$2"
    local job_name="$3"
    
    echo "Adding cron job: $job_name"
    
    # Check if job already exists
    if crontab -l 2>/dev/null | grep -q "$job_name"; then
        echo "⚠️  Cron job '$job_name' already exists, skipping..."
        return
    fi
    
    # Add new cron job
    (crontab -l 2>/dev/null; echo "$schedule $command # $job_name") | crontab -
    echo "✓ Added cron job: $job_name"
}

# 1. RSS Feed Fetching - Every 6 hours
RSS_COMMAND="cd $PROJECT_DIR && $PYTHON_CMD rss_fetcher.py >> logs/cron/rss_cron.log 2>&1"
add_cron_job "0 */6 * * *" "$RSS_COMMAND" "cyberagent_rss_fetch"

# 2. Fine-tuning Data Preparation - Weekly on Sunday at 2 AM
FINETUNE_COMMAND="cd $PROJECT_DIR && $PYTHON_CMD finetune_preparer.py >> logs/cron/finetune_cron.log 2>&1"
add_cron_job "0 2 * * 0" "$FINETUNE_COMMAND" "cyberagent_finetune_prep"

# 3. Daily Report Generation - Every day at 6 AM
REPORT_COMMAND="cd $PROJECT_DIR && $PYTHON_CMD -c \"import asyncio; from report_generator import ReportGenerator; import yaml; config = yaml.safe_load(open('config.yaml')); asyncio.run(ReportGenerator(config).generate_report('daily'))\" >> logs/cron/report_cron.log 2>&1"
add_cron_job "0 6 * * *" "$REPORT_COMMAND" "cyberagent_daily_report"

# 4. System Health Check - Every 2 hours
HEALTH_COMMAND="cd $PROJECT_DIR && $PYTHON_CMD -c \"import asyncio; from task_router import TaskRouter; import yaml; config = yaml.safe_load(open('config.yaml')); asyncio.run(TaskRouter(config).health_check())\" >> logs/cron/health_cron.log 2>&1"
add_cron_job "0 */2 * * *" "$HEALTH_COMMAND" "cyberagent_health_check"

# 5. Log Cleanup - Weekly on Saturday at 3 AM
LOG_CLEANUP_COMMAND="find $PROJECT_DIR/logs -name '*.log' -mtime +30 -delete && find $PROJECT_DIR/temp -name '*' -mtime +7 -delete 2>/dev/null || true"
add_cron_job "0 3 * * 6" "$LOG_CLEANUP_COMMAND" "cyberagent_log_cleanup"

# 6. RAG Database Optimization - Monthly on 1st at 4 AM
RAG_OPTIMIZE_COMMAND="cd $PROJECT_DIR && $PYTHON_CMD -c \"import asyncio; from rag_embedder import RAGEmbedder; import yaml; config = yaml.safe_load(open('config.yaml')); rag = RAGEmbedder(config); print('RAG optimization placeholder')\" >> logs/cron/rag_optimize_cron.log 2>&1"
add_cron_job "0 4 1 * *" "$RAG_OPTIMIZE_COMMAND" "cyberagent_rag_optimize"

# 7. Security Intelligence Update - Daily at 1 AM
INTEL_UPDATE_COMMAND="cd $PROJECT_DIR && $PYTHON_CMD -c \"import asyncio; from rss_fetcher import RSSFetcher; import yaml; config = yaml.safe_load(open('config.yaml')); asyncio.run(RSSFetcher(config).fetch_all_feeds())\" >> logs/cron/intel_cron.log 2>&1"
add_cron_job "0 1 * * *" "$INTEL_UPDATE_COMMAND" "cyberagent_intel_update"

# Create cron job management script
cat > "$PROJECT_DIR/manage_cron.sh" << 'EOF'
#!/bin/bash

# Cron Job Management Script

show_help() {
    echo "Cybersecurity AI Agent - Cron Job Manager"
    echo ""
    echo "Usage: ./manage_cron.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  list     - List all cyberagent cron jobs"
    echo "  status   - Show status of cron jobs"
    echo "  remove   - Remove all cyberagent cron jobs"
    echo "  logs     - Show recent cron job logs"
    echo "  help     - Show this help message"
}

list_jobs() {
    echo "Current Cybersecurity AI Agent cron jobs:"
    crontab -l 2>/dev/null | grep "cyberagent_" || echo "No cyberagent cron jobs found"
}

show_status() {
    echo "Cron Job Status:"
    echo "================"
    
    # Check if cron service is running
    if systemctl is-active --quiet cron 2>/dev/null || service cron status >/dev/null 2>&1; then
        echo "✓ Cron service is running"
    else
        echo "✗ Cron service is not running"
    fi
    
    # Show recent log entries
    echo ""
    echo "Recent cron activity:"
    if [ -d "logs/cron" ]; then
        find logs/cron -name "*.log" -mtime -1 -exec echo "=== {} ===" \; -exec tail -5 {} \; 2>/dev/null || echo "No recent log files found"
    else
        echo "No cron log directory found"
    fi
}

remove_jobs() {
    echo "Removing all cyberagent cron jobs..."
    crontab -l 2>/dev/null | grep -v "cyberagent_" | crontab -
    echo "✓ All cyberagent cron jobs removed"
}

show_logs() {
    echo "Recent cron job logs:"
    echo "===================="
    
    if [ -d "logs/cron" ]; then
        for logfile in logs/cron/*.log; do
            if [ -f "$logfile" ]; then
                echo ""
                echo "=== $(basename $logfile) ==="
                tail -10 "$logfile" 2>/dev/null || echo "Could not read $logfile"
            fi
        done
    else
        echo "No cron log directory found"
    fi
}

case "$1" in
    list)
        list_jobs
        ;;
    status)
        show_status
        ;;
    remove)
        remove_jobs
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        show_help
        exit 1
        ;;
esac
EOF

chmod +x "$PROJECT_DIR/manage_cron.sh"

# Create systemd service file for the Telegram bot (optional)
cat > "$PROJECT_DIR/cyberagent-bot.service" << EOF
[Unit]
Description=Cybersecurity AI Agent Telegram Bot
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PATH
ExecStart=$PYTHON_CMD telegram_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create log rotation configuration
cat > "$PROJECT_DIR/logrotate.conf" << EOF
$PROJECT_DIR/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 $(whoami) $(whoami)
}

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

# Create monitoring script
cat > "$PROJECT_DIR/monitor.sh" << 'EOF'
#!/bin/bash

# System Monitoring Script for Cybersecurity AI Agent

echo "🔍 Cybersecurity AI Agent - System Monitor"
echo "=========================================="

# Check system resources
echo "📊 System Resources:"
echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
echo "Disk: $(df -h . | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')"
echo "CPU Load: $(uptime | awk -F'load average:' '{print $2}')"
echo ""

# Check Python processes
echo "🐍 Python Processes:"
ps aux | grep python | grep -E "(telegram_bot|rss_fetcher|pentestgpt)" | grep -v grep || echo "No cyberagent processes running"
echo ""

# Check log file sizes
echo "📝 Log Files:"
if [ -d "logs" ]; then
    find logs -name "*.log" -exec ls -lh {} \; | tail -10
else
    echo "No logs directory found"
fi
echo ""

# Check database status
echo "🗄️  Database Status:"
if [ -d "rag_data/chroma_db" ]; then
    echo "ChromaDB directory exists: $(du -sh rag_data/chroma_db | cut -f1)"
else
    echo "ChromaDB directory not found"
fi
echo ""

# Check recent activity
echo "📈 Recent Activity:"
if [ -d "logs" ]; then
    echo "Last RSS fetch: $(find logs -name "*rss*" -type f -exec stat -c '%y %n' {} \; 2>/dev/null | sort | tail -1 | cut -d' ' -f1-2 || echo 'Never')"
    echo "Last analysis: $(find logs -name "*pentestgpt*" -type f -exec stat -c '%y %n' {} \; 2>/dev/null | sort | tail -1 | cut -d' ' -f1-2 || echo 'Never')"
else
    echo "No activity logs found"
fi
EOF

chmod +x "$PROJECT_DIR/monitor.sh"

# Display summary
echo ""
echo "✅ Cron job setup complete!"
echo ""
echo "📋 Summary of scheduled tasks:"
echo "• RSS fetching: Every 6 hours"
echo "• Fine-tuning prep: Weekly (Sunday 2 AM)"
echo "• Daily reports: Daily at 6 AM"
echo "• Health checks: Every 2 hours"
echo "• Log cleanup: Weekly (Saturday 3 AM)"
echo "• RAG optimization: Monthly (1st at 4 AM)"
echo "• Intel updates: Daily at 1 AM"
echo ""
echo "🛠️  Management commands:"
echo "• View jobs: ./manage_cron.sh list"
echo "• Check status: ./manage_cron.sh status"
echo "• View logs: ./manage_cron.sh logs"
echo "• Remove all: ./manage_cron.sh remove"
echo "• Monitor system: ./monitor.sh"
echo ""
echo "📁 Created files:"
echo "• manage_cron.sh - Cron job management"
echo "• monitor.sh - System monitoring"
echo "• cyberagent-bot.service - Systemd service file"
echo "• logrotate.conf - Log rotation configuration"
echo ""

# Optional: Install as systemd service
read -p "Install Telegram bot as systemd service? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo cp "$PROJECT_DIR/cyberagent-bot.service" /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable cyberagent-bot.service
    echo "✓ Systemd service installed and enabled"
    echo "  Start with: sudo systemctl start cyberagent-bot"
    echo "  Check status: sudo systemctl status cyberagent-bot"
fi

echo ""
echo "🚀 Cron jobs are now active! Check status with: ./manage_cron.sh status"
