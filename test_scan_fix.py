#!/usr/bin/env python3
"""
Test the scan functionality after fixing import issues
"""

import asyncio
import os
import sys
sys.path.append('/home/h7ck3r/Notes/code/cybersecurity-ai-agent')

from core.task_router import TaskRouter
from core.shared_utils import ConfigManager
from loguru import logger

async def test_scan_functionality():
    """Test the scan command functionality"""
    logger.info("🧪 Testing scan functionality after import fixes...")
    
    try:
        # Load configuration
        config = ConfigManager().get_config()
        
        # Initialize task router
        task_router = TaskRouter(config)
        
        # Test scan command
        test_target = "https://xss-game.appspot.com/"
        logger.info(f"🎯 Testing scan for target: {test_target}")
        
        result = await task_router.route_scan_task(test_target)
        
        logger.info("✅ Scan completed successfully!")
        logger.info(f"📋 Result summary: {result.get('summary', 'No summary available')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Scan test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_scan_functionality())
    if success:
        print("✅ SCAN FUNCTIONALITY TEST PASSED")
    else:
        print("❌ SCAN FUNCTIONALITY TEST FAILED")
