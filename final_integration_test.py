#!/usr/bin/env python3
"""
Final Integration Test for Live Platform
Tests components while platform is running
"""

import requests
import json
import os
from datetime import datetime
from pathlib import Path

def test_telegram_bot():
    """Test Telegram bot accessibility"""
    try:
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token or token == 'test_token_placeholder':
            return False, "No valid token"
        
        response = requests.get(f'https://api.telegram.org/bot{token}/getMe', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                return True, f"Bot: @{data['result']['username']}"
        return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def test_gemini_api():
    """Test Gemini API connection"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'test_key_placeholder':
            return False, "No valid API key"
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content('Test: respond with "OK" only')
        
        if response and response.text:
            return True, f"Response: {response.text.strip()}"
        return False, "No response"
    except Exception as e:
        return False, str(e)

def test_database():
    """Test database and storage"""
    try:
        chroma_path = Path('rag_data/chroma_db')
        if not chroma_path.exists():
            return False, "ChromaDB not found"
        
        # Check for collection files
        collection_files = list(chroma_path.rglob('*.sqlite3'))
        return True, f"{len(collection_files)} collections active"
    except Exception as e:
        return False, str(e)

def test_logs():
    """Test logging system"""
    try:
        log_path = Path('logs')
        if not log_path.exists():
            return False, "Log directory missing"
        
        log_files = list(log_path.rglob('*.log'))
        if not log_files:
            return False, "No log files found"
        
        # Check latest log for recent activity
        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
        size_kb = latest_log.stat().st_size / 1024
        
        return True, f"{len(log_files)} logs, latest: {size_kb:.1f}KB"
    except Exception as e:
        return False, str(e)

def test_file_structure():
    """Test critical file structure"""
    required_files = [
        'core/config.yaml',
        'core/main.py', 
        'agents/rag_embedder.py',
        'agents/pentestgpt_gemini.py',
        '.env'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        return False, f"Missing: {missing_files}"
    return True, f"{len(required_files)} files present"

def main():
    """Run final integration tests"""
    print("🧪 FINAL INTEGRATION TEST - LIVE PLATFORM")
    print("=" * 50)
    
    tests = [
        ("🤖 Telegram Bot", test_telegram_bot),
        ("🧠 Gemini AI", test_gemini_api),
        ("💾 Database", test_database),
        ("📝 Logging", test_logs),
        ("📁 File Structure", test_file_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success, message = test_func()
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{test_name}: {status} - {message}")
            results.append((test_name, success, message))
        except Exception as e:
            print(f"{test_name}: ❌ ERROR - {e}")
            results.append((test_name, False, str(e)))
    
    # Summary
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"├── Tests Passed: {passed}/{total}")
    print(f"├── Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("└── Status: 🎉 ALL SYSTEMS OPERATIONAL")
    elif passed >= total * 0.8:
        print("└── Status: ✅ MOSTLY FUNCTIONAL")
    else:
        print("└── Status: ⚠️ NEEDS ATTENTION")
    
    # Save results
    with open('final_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'tests': [{'name': name, 'passed': success, 'message': msg} for name, success, msg in results],
            'summary': {'passed': passed, 'total': total, 'success_rate': passed/total*100}
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: final_test_results.json")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
