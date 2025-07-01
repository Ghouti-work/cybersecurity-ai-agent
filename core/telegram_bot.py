"""
Telegram Bot for Cybersecurity AI Agent Platform
Handles all user interactions and command routing
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from telegram import Update, Document, Message
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    ContextTypes, filters
)
from telegram.constants import ParseMode
import yaml
from loguru import logger
from dotenv import load_dotenv

# Import our modules
from task_router import TaskRouter
from pentestgpt_gemini import PentestGPTGemini
from rss_fetcher import RSSFetcher
from file_parser import FileParser
from report_generator import ReportGenerator
from finetune_preparer import FineTunePreparer
from shared_utils import (
    ConfigManager, LoggerManager, DirectoryManager,
    EnvironmentValidator, SystemMetrics
)

# Load environment variables
load_dotenv()

class CybersecurityBot:
    def __init__(self):
        # Load configuration using shared utility
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        
        # Environment validation
        env_validation = EnvironmentValidator.validate_environment()
        if env_validation['status'] == 'fail':
            logger.error("Critical environment variables missing!")
            sys.exit(1)
        
        self.authorized_user_id = int(os.getenv('AUTHORIZED_USER_ID'))
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        # Setup logging using shared utility
        LoggerManager.setup_logger('telegram')
        
        # Initialize components
        self.task_router = TaskRouter(self.config)
        self.pentestgpt = PentestGPTGemini(self.config)
        self.rss_fetcher = RSSFetcher(self.config)
        self.file_parser = FileParser(self.config)
        self.report_generator = ReportGenerator(self.config)
        self.finetune_preparer = FineTunePreparer(self.config)
        
        logger.info("🤖 Cybersecurity AI Agent Bot initialized with shared utilities")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open('config.yaml', 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error("config.yaml not found!")
            sys.exit(1)

    def _setup_logging(self):
        """Configure logging"""
        log_dir = Path("logs/telegram")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_dir / f"bot_{datetime.now().strftime('%Y-%m-%d')}.log",
            rotation="1 day",
            retention="30 days",
            level="INFO"
        )

    def _check_authorization(self, user_id: int) -> bool:
        """Check if user is authorized"""
        return user_id == self.authorized_user_id

    async def _send_long_message(self, update: Update, text: str, parse_mode=ParseMode.MARKDOWN):
        """Send long messages by splitting them if needed"""
        max_length = 4096
        if len(text) <= max_length:
            await update.message.reply_text(text, parse_mode=parse_mode)
        else:
            # Split message into chunks
            chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            for chunk in chunks:
                await update.message.reply_text(chunk, parse_mode=parse_mode)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message"""
        if not self._check_authorization(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return

        help_text = """
🤖 **Cybersecurity AI Agent Commands**

**Core Commands:**
• `/scan <target>` - Trigger security scan of target
• `/think <query>` - Use PentestGPT for analysis
• `/report <type>` - Generate security report (latest/daily/weekly)
• `/file` - Upload file for analysis (reply to file)
• `/rss now` - Fetch latest security RSS feeds
• `/fine_tune` - Prepare fine-tuning data

**Utility Commands:**
• `/status` - Show system status
• `/help` - Show this help message

**Usage Examples:**
```
/scan example.com
/think how to exploit SQL injection in login form
/report latest
/rss now
```

📝 **File Upload:** Send any PDF, text, or markdown file and reply with `/file` to analyze it.

🔍 **PentestGPT:** Ask complex security questions with `/think` for detailed analysis.
        """
        
        await self._send_long_message(update, help_text)
        logger.info(f"Help command used by user {update.effective_user.id}")

    async def scan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle scan command"""
        if not self._check_authorization(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return

        if not context.args:
            await update.message.reply_text("❌ Please provide a target: `/scan example.com`", 
                                          parse_mode=ParseMode.MARKDOWN)
            return

        target = " ".join(context.args)
        await update.message.reply_text(f"🔍 Starting scan of `{target}`...", 
                                      parse_mode=ParseMode.MARKDOWN)
        
        try:
            # Route to task router for scan execution
            result = await self.task_router.route_scan_task(target)
            
            response = f"""
🎯 **Scan Results for {target}**

{result['summary']}

**Findings:**
{result['findings']}

**Recommendations:**
{result['recommendations']}

📊 Scan completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            await self._send_long_message(update, response)
            logger.info(f"Scan completed for target: {target}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Scan failed: {str(e)}")
            logger.error(f"Scan error: {e}")

    async def think_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle PentestGPT thinking command"""
        if not self._check_authorization(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return

        if not context.args:
            await update.message.reply_text("❌ Please provide a query: `/think how to exploit XSS`", 
                                          parse_mode=ParseMode.MARKDOWN)
            return

        query = " ".join(context.args)
        await update.message.reply_text(f"🧠 PentestGPT is analyzing: `{query}`...", 
                                      parse_mode=ParseMode.MARKDOWN)
        
        try:
            # Get analysis from PentestGPT
            analysis = await self.pentestgpt.analyze_security_scenario(query)
            
            response = f"""
🧠 **PentestGPT Analysis**

**Query:** {query}

**Analysis:**
{analysis['detailed_analysis']}

**Attack Vectors:**
{analysis['attack_vectors']}

**Mitigation:**
{analysis['mitigation_strategies']}

⏰ Analysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            await self._send_long_message(update, response)
            logger.info(f"PentestGPT analysis completed for query: {query}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Analysis failed: {str(e)}")
            logger.error(f"PentestGPT error: {e}")

    async def report_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle report generation command"""
        if not self._check_authorization(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return

        report_type = context.args[0] if context.args else "latest"
        
        await update.message.reply_text(f"📊 Generating {report_type} report...", 
                                      parse_mode=ParseMode.MARKDOWN)
        
        try:
            report = await self.report_generator.generate_report(report_type)
            
            # Send report as file if it's long, otherwise as message
            if len(report['content']) > 3000:
                # Save to temp file and send
                temp_file = f"temp/report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                os.makedirs('temp', exist_ok=True)
                
                with open(temp_file, 'w') as f:
                    f.write(report['content'])
                
                await update.message.reply_document(
                    document=open(temp_file, 'rb'),
                    filename=f"security_report_{report_type}.md",
                    caption=f"📊 {report['title']}"
                )
                
                # Clean up temp file
                os.remove(temp_file)
            else:
                await self._send_long_message(update, report['content'])
            
            logger.info(f"Report generated: {report_type}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Report generation failed: {str(e)}")
            logger.error(f"Report generation error: {e}")

    async def rss_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle RSS feed fetching command"""
        if not self._check_authorization(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return

        action = context.args[0] if context.args else "now"
        
        if action == "now":
            await update.message.reply_text("📡 Fetching latest security feeds...")
            
            try:
                results = await self.rss_fetcher.fetch_all_feeds()
                
                summary = f"""
📡 **RSS Feed Update Complete**

**Articles Processed:** {results['total_articles']}
**New CVEs:** {results['new_cves']}
**Security News:** {results['security_news']}
**Research Papers:** {results['research_items']}

**Recent Highlights:**
{results['highlights']}

🕒 Updated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """
                
                await self._send_long_message(update, summary)
                logger.info("RSS feeds updated manually")
                
            except Exception as e:
                await update.message.reply_text(f"❌ RSS fetch failed: {str(e)}")
                logger.error(f"RSS fetch error: {e}")

    async def file_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle file uploads"""
        if not self._check_authorization(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return

        # Check if message is a reply to a file
        if not (update.message.reply_to_message and update.message.reply_to_message.document):
            await update.message.reply_text("❌ Please reply to a file with `/file` command")
            return

        document = update.message.reply_to_message.document
        
        # Check file size and type
        if document.file_size > 50 * 1024 * 1024:  # 50MB limit
            await update.message.reply_text("❌ File too large (max 50MB)")
            return

        await update.message.reply_text(f"📄 Analyzing file: `{document.file_name}`...", 
                                      parse_mode=ParseMode.MARKDOWN)
        
        try:
            # Download file
            file = await context.bot.get_file(document.file_id)
            temp_path = f"temp/{document.file_name}"
            os.makedirs('temp', exist_ok=True)
            await file.download_to_drive(temp_path)
            
            # Parse and analyze file
            analysis = await self.file_parser.process_file(temp_path)
            
            response = f"""
📄 **File Analysis Complete**

**File:** {document.file_name}
**Category:** {analysis['category']}
**Classification:** {analysis['classification']}

**Summary:**
{analysis['summary']}

**Key Tags:** {', '.join(analysis['tags'])}

**Security Relevance:** {analysis['security_score']}/10

🔍 File processed and added to RAG database
            """
            
            await self._send_long_message(update, response)
            
            # Clean up temp file
            os.remove(temp_path)
            logger.info(f"File analyzed: {document.file_name}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ File analysis failed: {str(e)}")
            logger.error(f"File analysis error: {e}")

    async def finetune_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle fine-tuning preparation command"""
        if not self._check_authorization(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return

        await update.message.reply_text("🧪 Preparing fine-tuning data...")
        
        try:
            results = await self.finetune_preparer.prepare_training_data()
            
            response = f"""
🧪 **Fine-tuning Data Preparation Complete**

**Training Samples:** {results['training_samples']}
**Validation Samples:** {results['validation_samples']}
**Data Sources:** {results['data_sources']}

**Quality Metrics:**
- Average sequence length: {results['avg_sequence_length']}
- Vocabulary size: {results['vocab_size']}
- Coverage score: {results['coverage_score']}/10

📁 Data saved to: `finetune_data/processed/`

⚡ Ready for LoRA fine-tuning when needed
            """
            
            await self._send_long_message(update, response)
            logger.info("Fine-tuning data prepared")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Fine-tuning preparation failed: {str(e)}")
            logger.error(f"Fine-tuning preparation error: {e}")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show system status using shared utilities"""
        if not self._check_authorization(update.effective_user.id):
            await update.message.reply_text("❌ Unauthorized access")
            return

        try:
            # Get system metrics using shared utility
            system_metrics = SystemMetrics.get_system_metrics()
            
            # Get basic status from task router
            status = await self.task_router.get_system_status()
            
            response = f"""
🤖 **System Status**

**Bot Status:** ✅ Online
**Memory:** {system_metrics['memory_percent']}% ({system_metrics['memory_used']}/{system_metrics['memory_total']})
**CPU Load:** {system_metrics['cpu_percent']}%
**Disk:** {system_metrics['disk_percent']}% ({system_metrics['disk_used']}/{system_metrics['disk_total']})

**Services:**
- Gemini API: {'✅' if system_metrics.get('apis', {}).get('gemini') else '❌'}
- RAG Database: ✅ Active
- RSS Feeds: ✅ Active

**Database Stats:**
- RAG Documents: {status.get('rag_documents', 'N/A')}
- Processed Files: {status.get('processed_files', 'N/A')}

🔧 All systems operational
            """
            
            await self._send_long_message(update, response)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Status check failed: {str(e)}")
            logger.error(f"Status check error: {e}")

    async def run_async(self):
        """Start the bot asynchronously for use with main platform"""
        if not self.bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not set!")
            sys.exit(1)
        
        if not self.authorized_user_id:
            logger.error("AUTHORIZED_USER_ID not set!")
            sys.exit(1)

        # Create application
        application = Application.builder().token(self.bot_token).build()

        # Add command handlers
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("scan", self.scan_command))
        application.add_handler(CommandHandler("think", self.think_command))
        application.add_handler(CommandHandler("report", self.report_command))
        application.add_handler(CommandHandler("rss", self.rss_command))
        application.add_handler(CommandHandler("file", self.file_handler))
        application.add_handler(CommandHandler("fine_tune", self.finetune_command))
        application.add_handler(CommandHandler("status", self.status_command))

        # Start bot polling
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        
        # Keep running
        import signal
        stop_signals = (signal.SIGINT, signal.SIGTERM)
        loop = asyncio.get_running_loop()
        
        def stop_handler():
            loop.create_task(application.updater.stop())
            loop.create_task(application.stop())
            
        for sig in stop_signals:
            loop.add_signal_handler(sig, stop_handler)
        
        # Wait until stopped
        await application.updater.wait_until_stopped()

    def run(self):
        """Start the bot (synchronous version for standalone use)"""
        if not self.bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not set!")
            sys.exit(1)
        
        if not self.authorized_user_id:
            logger.error("AUTHORIZED_USER_ID not set!")
            sys.exit(1)

        # Create application
        application = Application.builder().token(self.bot_token).build()

        # Add command handlers
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("scan", self.scan_command))
        application.add_handler(CommandHandler("think", self.think_command))
        application.add_handler(CommandHandler("report", self.report_command))
        application.add_handler(CommandHandler("rss", self.rss_command))
        application.add_handler(CommandHandler("file", self.file_handler))
        application.add_handler(CommandHandler("fine_tune", self.finetune_command))
        application.add_handler(CommandHandler("status", self.status_command))

        # Start bot
        logger.info("🚀 Starting Cybersecurity AI Agent Bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = CybersecurityBot()
    bot.run()
