#!/bin/bash

# Cybersecurity AI Agent Platform Setup Script
# For Ubuntu 22.04+ with Python 3.10+

set -e

echo "🚀 Setting up Cybersecurity AI Agent Platform..."

# Create project directories
echo "📁 Creating directory structure..."
mkdir -p logs/{pentestgpt,telegram,rss,finetune}
mkdir -p rag_data/{recon,web,network,exploit,reports}
mkdir -p reports/{daily,weekly,custom}
mkdir -p finetune_data/{raw,processed}
mkdir -p models/{embeddings,lora}
mkdir -p config
mkdir -p temp

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt update
sudo apt install -y python3-pip python3-venv git curl wget

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Create .env template
echo "🔐 Creating .env template..."
cat > .env.template << 'EOF'
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
AUTHORIZED_USER_ID=your_telegram_user_id_here

# AI API Keys
GEMINI_API_KEY=your_gemini_api_key_here
AZURE_OPENAI_API_KEY=your_azure_openai_key_here
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint_here

# Database Configuration
CHROMA_DB_PATH=./rag_data/chroma_db

# RSS Feed Configuration
RSS_FETCH_INTERVAL=3600  # seconds
MAX_ARTICLES_PER_FEED=50

# Model Configuration
EMBEDDING_MODEL=intfloat/e5-small-v2
MAX_TOKENS=4096
TEMPERATURE=0.7

# Logging
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30

# Security
API_RATE_LIMIT=60  # requests per minute
MAX_FILE_SIZE_MB=50
EOF

# Copy template to actual .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.template .env
    echo "⚠️  Please edit .env file with your actual API keys and configuration"
fi

# Set permissions
chmod +x *.py
chmod 600 .env .env.template

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys and configuration"
echo "2. Start the Telegram bot: python telegram_bot.py"
echo "3. Test the system with /help command in Telegram"
echo ""
echo "Optional cron jobs:"
echo "# Add to crontab for automated RSS fetching and training"
echo "0 */6 * * * cd $(pwd) && ./venv/bin/python rss_fetcher.py"
echo "0 2 * * 0 cd $(pwd) && ./venv/bin/python finetune_preparer.py"
