#!/usr/bin/env python3
"""
Cybersecurity AI Agent Platform - Main Launcher
Orchestrates all components for the intelligent pentesting assistant
"""

import asyncio
import signal
import sys
import os
import time
import psutil
from pathlib import Path
from typing import Dict, Any
import yaml
from loguru import logger
from dotenv import load_dotenv

# Import all components
from telegram_bot import CybersecurityBot
from task_router import TaskRouter
from rss_fetcher import RSSFetcher
from pentestgpt_gemini import PentestGPT
from rag_embedder import RAGEmbedder
from shared_utils import (
    ConfigManager, LoggerManager, DirectoryManager,
    EnvironmentValidator, initialize_shared_components
)

class CyberAgentPlatform:
    """Main platform orchestrator"""
    
    def __init__(self):
        self.is_running = False
        self.components = {}
        
        # Initialize shared components first
        if not initialize_shared_components():
            logger.error("❌ Failed to initialize shared components!")
            sys.exit(1)
        
        # Use shared configuration manager
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        
        # Setup logging using shared utility
        LoggerManager.setup_logger('main')
        
        # Environment validation
        env_validation = EnvironmentValidator.validate_environment()
        if env_validation['status'] == 'fail':
            logger.error(f"❌ Critical environment variables missing: {env_validation['missing']}")
            sys.exit(1)
        
        logger.info("🚀 Cybersecurity AI Agent Platform initialized with shared utilities")
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        load_dotenv()
        try:
            with open('config.yaml', 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error("❌ config.yaml not found!")
            sys.exit(1)
    
    def _setup_logging(self):
        """Setup comprehensive logging"""
        log_dir = Path("logs/main")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_dir / f"platform_{time.strftime('%Y-%m-%d')}.log",
            rotation="1 day",
            retention="30 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
        )
        
        logger.info("🚀 Cybersecurity AI Agent Platform Starting...")
    
    def _check_environment(self):
        """Check system requirements and environment"""
        logger.info("🔍 Checking system environment...")
        
        # Check memory
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        logger.info(f"💾 System Memory: {memory_gb:.1f}GB")
        
        if memory_gb < 7:
            logger.warning("⚠️  Low memory detected! Consider reducing batch sizes.")
        
        # Check disk space
        disk = psutil.disk_usage('.')
        disk_gb = disk.free / (1024**3)
        logger.info(f"💽 Available Disk: {disk_gb:.1f}GB")
        
        if disk_gb < 5:
            logger.warning("⚠️  Low disk space! Enable log cleanup.")
        
        # Check required environment variables
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'AUTHORIZED_USER_ID',
            'GEMINI_API_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"❌ Missing environment variables: {missing_vars}")
            logger.error("Please check your .env file")
            sys.exit(1)
        
        logger.info("✅ Environment check passed")
    
    async def initialize_components(self):
        """Initialize all system components"""
        logger.info("🔧 Initializing components...")
        
        try:
            # Initialize core components
            self.components['rag_embedder'] = RAGEmbedder(self.config)
            await self.components['rag_embedder'].initialize()
            logger.info("✅ RAG Embedder initialized")
            
            self.components['pentestgpt'] = PentestGPT(self.config)
            logger.info("✅ PentestGPT initialized")
            
            self.components['task_router'] = TaskRouter(self.config)
            logger.info("✅ Task Router initialized")
            
            self.components['rss_fetcher'] = RSSFetcher(self.config)
            logger.info("✅ RSS Fetcher initialized")
            
            # Initialize Telegram bot (main interface)
            self.components['telegram_bot'] = CybersecurityBot()
            logger.info("✅ Telegram Bot initialized")
            
            logger.info("🎉 All components initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Component initialization failed: {e}")
            raise
    
    async def start_background_tasks(self):
        """Start background automation tasks"""
        logger.info("🔄 Starting background tasks...")
        
        tasks = []
        
        # RSS Feed Monitoring
        if self.config.get('automation', {}).get('rss_enabled', True):
            tasks.append(asyncio.create_task(self._rss_monitor()))
            logger.info("📡 RSS monitoring started")
        
        # System Health Monitoring
        tasks.append(asyncio.create_task(self._health_monitor()))
        logger.info("🏥 Health monitoring started")
        
        # Memory cleanup task
        tasks.append(asyncio.create_task(self._memory_cleanup()))
        logger.info("🧹 Memory cleanup task started")
        
        return tasks
    
    async def _rss_monitor(self):
        """Background RSS feed monitoring"""
        rss_interval = int(os.getenv('RSS_FETCH_INTERVAL', 21600))  # 6 hours
        
        while self.is_running:
            try:
                logger.info("📡 Starting RSS feed fetch...")
                await self.components['rss_fetcher'].fetch_all_feeds()
                logger.info("✅ RSS feeds processed successfully")
            except Exception as e:
                logger.error(f"❌ RSS fetch error: {e}")
            
            await asyncio.sleep(rss_interval)
    
    async def _health_monitor(self):
        """Monitor system health using shared utilities"""
        while self.is_running:
            try:
                # Use shared system metrics
                from shared_utils import SystemMetrics
                metrics = SystemMetrics.get_system_metrics()
                
                memory_percent = metrics['memory_percent']
                disk_percent = metrics['disk_percent']
                
                if memory_percent > 85:
                    logger.warning(f"⚠️  High memory usage: {memory_percent}%")
                
                if disk_percent > 90:
                    logger.warning(f"⚠️  High disk usage: {disk_percent}%")
                
                # Log health status every hour
                logger.info(f"💊 System Health - Memory: {memory_percent}%, Disk: {disk_percent}%")
                
            except Exception as e:
                logger.error(f"❌ Health monitor error: {e}")
            
            await asyncio.sleep(3600)  # Check every hour
    
    async def _memory_cleanup(self):
        """Periodic memory cleanup"""
        while self.is_running:
            try:
                import gc
                gc.collect()
                logger.debug("🧹 Memory cleanup performed")
            except Exception as e:
                logger.error(f"❌ Memory cleanup error: {e}")
            
            await asyncio.sleep(1800)  # Every 30 minutes
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers"""
        def signal_handler(signum, frame):
            logger.info(f"📡 Received signal {signum}, shutting down gracefully...")
            self.is_running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self):
        """Main run loop"""
        self.is_running = True
        self.setup_signal_handlers()
        
        try:
            # Initialize all components
            await self.initialize_components()
            
            # Start background tasks
            background_tasks = await self.start_background_tasks()
            
            # Start the main Telegram bot
            logger.info("🤖 Starting Telegram bot...")
            bot_task = asyncio.create_task(
                self.components['telegram_bot'].run_async()
            )
            
            # Wait for all tasks
            all_tasks = background_tasks + [bot_task]
            
            logger.info("✨ Cybersecurity AI Agent Platform is running!")
            logger.info("🔗 Connect via Telegram to start using the system")
            
            await asyncio.gather(*all_tasks, return_exceptions=True)
            
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested by user")
        except Exception as e:
            logger.error(f"❌ Platform error: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down platform...")
        self.is_running = False
        
        # Close components
        for name, component in self.components.items():
            try:
                if hasattr(component, 'close'):
                    await component.close()
                logger.info(f"✅ {name} closed")
            except Exception as e:
                logger.error(f"❌ Error closing {name}: {e}")
        
        logger.info("👋 Platform shutdown complete")

async def main():
    """Entry point"""
    try:
        platform = CyberAgentPlatform()
        await platform.run()
    except Exception as e:
        logger.error(f"❌ Platform failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure we're using the right Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # For Azure VM: Set optimal memory settings
    os.environ.setdefault('PYTORCH_CUDA_ALLOC_CONF', 'max_split_size_mb:512')
    os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
    
    print("""
🛡️  Cybersecurity AI Agent Platform
🤖 Intelligent Pentesting Assistant
📡 24/7 Telegram Bot Access
🧠 Powered by Gemini API
    """)
    
    asyncio.run(main())
