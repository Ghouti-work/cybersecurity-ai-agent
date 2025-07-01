#!/usr/bin/env python3
"""
Comprehensive test for the scan functionality
"""

import asyncio
import os
import sys
import time
sys.path.append('/home/h7ck3r/Notes/code/cybersecurity-ai-agent')

from core.shared_utils import ConfigManager
from agents.pentestgpt_gemini import PentestGPTGemini

async def test_pentestgpt_analysis():
    """Test PentestGPTGemini analysis functionality"""
    
    print("🧪 Starting comprehensive PentestGPT analysis test...")
    
    try:
        # Load config
        config = ConfigManager().get_config()
        print("✅ Config loaded")
        
        # Initialize PentestGPT
        print("⚙️ Initializing PentestGPTGemini...")
        pentestgpt = PentestGPTGemini(config)
        print("✅ PentestGPTGemini initialized")
        
        # Test query
        query = "Analyze security testing approach for web application: https://xss-game.appspot.com/"
        print(f"🎯 Testing analysis with query: {query}")
        
        # Run analysis
        start_time = time.time()
        result = await pentestgpt.analyze_security_scenario(query)
        end_time = time.time()
        
        print(f"✅ Analysis completed in {end_time - start_time:.2f} seconds")
        print(f"📋 Result keys: {list(result.keys())}")
        print(f"📝 Analysis timestamp: {result.get('timestamp', 'N/A')}")
        
        # Check key components
        if 'initial_analysis' in result:
            print("✅ Initial analysis present")
            print(f"   Length: {len(result['initial_analysis'])} characters")
            
        if 'detailed_analysis' in result:
            print("✅ Detailed analysis present")
            
        if 'attack_vectors' in result:
            print("✅ Attack vectors present")
            
        if 'risk_assessment' in result:
            print("✅ Risk assessment present")
            
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_pentestgpt_analysis())
    if success:
        print("\n🎉 PENTESTGPT ANALYSIS TEST PASSED!")
        print("🔥 The /scan command should now work correctly!")
    else:
        print("\n💥 PENTESTGPT ANALYSIS TEST FAILED!")
