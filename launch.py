#!/usr/bin/env python3
"""
Cybersecurity AI Agent Platform - Simple Launcher
Simplified entry point for production deployment
"""

import asyncio
import os
import sys
from pathlib import Path

# Ensure we're running from the project root
project_root = Path(__file__).parent
os.chdir(project_root)

# Add all necessary paths to Python path
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))
sys.path.insert(0, str(project_root / "agents"))
sys.path.insert(0, str(project_root / "integrations"))

# Set environment
os.environ['PYTHONPATH'] = ":".join([
    str(project_root),
    str(project_root / "core"),
    str(project_root / "agents"),
    str(project_root / "integrations")
])

if __name__ == "__main__":
    try:
        # Check for test flag
        if len(sys.argv) > 1 and sys.argv[1] == "--test":
            print("🧪 Running basic test...")
            # Basic import test
            try:
                import psutil
                import loguru
                import yaml
                print("✅ Core dependencies available")
                print("✅ Basic test passed")
                sys.exit(0)
            except ImportError as e:
                print(f"❌ Missing dependency: {e}")
                sys.exit(1)
        
        from core.main import CyberAgentPlatform
        
        print("🚀 Starting Cybersecurity AI Agent Platform...")
        platform = CyberAgentPlatform()
        asyncio.run(platform.run())
        
    except KeyboardInterrupt:
        print("\n🛑 Platform shutdown requested")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Platform startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
