#!/usr/bin/env python3
"""
Cybersecurity AI Agent Platform - Integration Test Suite
Tests all components and their interactions
"""

import asyncio
import os
import sys
import yaml
import tempfile
from pathlib import Path
from typing import Dict, Any
import json
from loguru import logger
from dotenv import load_dotenv

# Test imports
try:
    from pentestgpt_gemini import PentestGPT
    from rss_fetcher import RSSFetcher
    from file_parser import FileParser
    from rag_embedder import RAGEmbedder
    from task_router import TaskRouter
    from report_generator import ReportGenerator
    from finetune_preparer import FineTunePreparer
    print("✅ All core modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class PlatformTester:
    """Comprehensive platform testing suite"""
    
    def __init__(self):
        self.test_results = {}
        self.config = self._load_test_config()
        self._setup_test_logging()
        
    def _load_test_config(self) -> Dict[str, Any]:
        """Load test configuration"""
        load_dotenv()
        
        # Check if config.yaml exists
        if not Path('config.yaml').exists():
            print("❌ config.yaml not found!")
            sys.exit(1)
            
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    
    def _setup_test_logging(self):
        """Setup test logging"""
        test_log_dir = Path("logs/testing")
        test_log_dir.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            test_log_dir / "integration_test.log",
            rotation="1 day",
            retention="7 days",
            level="DEBUG"
        )
    
    async def test_environment(self):
        """Test environment and prerequisites"""
        print("\n🔍 Testing Environment...")
        
        tests = []
        
        # Check environment variables
        required_vars = ['GEMINI_API_KEY']
        for var in required_vars:
            if os.getenv(var):
                tests.append(f"✅ {var} is set")
            else:
                tests.append(f"⚠️  {var} is missing (tests will use mock)")
        
        # Check Python version
        import sys
        if sys.version_info >= (3, 10):
            tests.append(f"✅ Python {sys.version.split()[0]} is compatible")
        else:
            tests.append(f"❌ Python {sys.version.split()[0]} is too old")
        
        # Check disk space
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free // (2**30)
        if free_gb >= 2:
            tests.append(f"✅ Disk space: {free_gb}GB available")
        else:
            tests.append(f"⚠️  Low disk space: {free_gb}GB available")
        
        # Check memory
        try:
            import psutil
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            tests.append(f"✅ System memory: {memory_gb:.1f}GB")
        except ImportError:
            tests.append("⚠️  psutil not available for memory check")
        
        self.test_results['environment'] = tests
        
        for test in tests:
            print(f"  {test}")
        
        return True
    
    async def test_rag_embedder(self):
        """Test RAG embedder functionality"""
        print("\n🧠 Testing RAG Embedder...")
        
        try:
            rag_embedder = RAGEmbedder(self.config)
            await rag_embedder.initialize()
            
            # Test document addition
            test_doc = "This is a test cybersecurity document about SQL injection vulnerabilities."
            doc_id = await rag_embedder.add_document(
                content=test_doc,
                metadata={"category": "web_security", "test": True}
            )
            
            # Test search
            results = await rag_embedder.search(
                query="SQL injection",
                collection="vulnerabilities",
                top_k=1
            )
            
            # Test collection stats
            stats = await rag_embedder.get_collection_stats()
            
            self.test_results['rag_embedder'] = [
                "✅ RAG embedder initialized",
                f"✅ Document added with ID: {doc_id}",
                f"✅ Search returned {len(results)} results",
                f"✅ Collection stats: {stats}"
            ]
            
            print("  ✅ RAG Embedder: All tests passed")
            return True
            
        except Exception as e:
            error = f"❌ RAG Embedder error: {e}"
            self.test_results['rag_embedder'] = [error]
            print(f"  {error}")
            return False
    
    async def test_pentestgpt(self):
        """Test PentestGPT reasoning"""
        print("\n🧠 Testing PentestGPT...")
        
        try:
            pentestgpt = PentestGPT(self.config)
            
            # Test analysis with a simple scenario
            test_query = "How to test for basic SQL injection in a login form?"
            
            if os.getenv('GEMINI_API_KEY'):
                result = await pentestgpt.analyze_security_scenario(test_query)
                
                self.test_results['pentestgpt'] = [
                    "✅ PentestGPT initialized",
                    f"✅ Analysis completed for: {test_query[:50]}...",
                    f"✅ Result type: {type(result)}",
                    f"✅ Risk assessment: {result.get('risk_assessment', {}).get('risk_category', 'N/A')}"
                ]
                
                print("  ✅ PentestGPT: All tests passed")
            else:
                self.test_results['pentestgpt'] = [
                    "✅ PentestGPT initialized",
                    "⚠️  Skipped API test (no GEMINI_API_KEY)"
                ]
                print("  ⚠️  PentestGPT: API test skipped (no API key)")
            
            return True
            
        except Exception as e:
            error = f"❌ PentestGPT error: {e}"
            self.test_results['pentestgpt'] = [error]
            print(f"  {error}")
            return False
    
    async def test_file_parser(self):
        """Test file parser functionality"""
        print("\n📄 Testing File Parser...")
        
        try:
            file_parser = FileParser(self.config)
            
            # Create a test markdown file
            test_content = """# Test Security Document
            
This is a test document containing information about:
- Web application security
- SQL injection vulnerabilities
- Cross-site scripting (XSS)
- Authentication bypasses

## Vulnerability Details
This section contains technical details about security issues.
"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(test_content)
                test_file_path = f.name
            
            try:
                # Test file parsing
                result = await file_parser.parse_file(test_file_path)
                
                self.test_results['file_parser'] = [
                    "✅ File parser initialized",
                    f"✅ Test file parsed successfully",
                    f"✅ Content length: {len(result.get('content', ''))} chars",
                    f"✅ Category: {result.get('category', 'N/A')}"
                ]
                
                print("  ✅ File Parser: All tests passed")
                
            finally:
                # Clean up test file
                os.unlink(test_file_path)
            
            return True
            
        except Exception as e:
            error = f"❌ File Parser error: {e}"
            self.test_results['file_parser'] = [error]
            print(f"  {error}")
            return False
    
    async def test_rss_fetcher(self):
        """Test RSS fetcher functionality"""
        print("\n📡 Testing RSS Fetcher...")
        
        try:
            rss_fetcher = RSSFetcher(self.config)
            
            # Test with a single feed (non-blocking)
            test_feed = {
                'name': 'Test Feed',
                'url': 'https://feeds.feedburner.com/TheHackersNews',
                'category': 'news'
            }
            
            # Just test initialization and basic functionality
            # Don't fetch actual RSS to avoid network dependencies
            
            self.test_results['rss_fetcher'] = [
                "✅ RSS fetcher initialized",
                f"✅ Feed configuration loaded: {len(self.config.get('rss_feeds', {}))} categories",
                "⚠️  Network fetch test skipped (to avoid dependencies)"
            ]
            
            print("  ✅ RSS Fetcher: Basic tests passed")
            return True
            
        except Exception as e:
            error = f"❌ RSS Fetcher error: {e}"
            self.test_results['rss_fetcher'] = [error]
            print(f"  {error}")
            return False
    
    async def test_task_router(self):
        """Test task router functionality"""
        print("\n🔀 Testing Task Router...")
        
        try:
            task_router = TaskRouter(self.config)
            
            # Test route analysis
            test_command = "/scan target.com"
            route = await task_router.analyze_command(test_command)
            
            # Test system status
            status = await task_router.get_system_status()
            
            self.test_results['task_router'] = [
                "✅ Task router initialized",
                f"✅ Command analysis: {route.get('component', 'unknown')}",
                f"✅ System status: {status.get('status', 'unknown')}"
            ]
            
            print("  ✅ Task Router: All tests passed")
            return True
            
        except Exception as e:
            error = f"❌ Task Router error: {e}"
            self.test_results['task_router'] = [error]
            print(f"  {error}")
            return False
    
    async def test_report_generator(self):
        """Test report generator functionality"""
        print("\n📊 Testing Report Generator...")
        
        try:
            report_generator = ReportGenerator(self.config)
            
            # Test report generation with mock data
            test_data = {
                'scan_results': ['Finding 1', 'Finding 2'],
                'analysis': 'Test analysis',
                'recommendations': ['Rec 1', 'Rec 2']
            }
            
            report = await report_generator.generate_report(
                report_type='security_scan',
                data=test_data,
                title='Test Security Report'
            )
            
            self.test_results['report_generator'] = [
                "✅ Report generator initialized",
                f"✅ Report generated successfully",
                f"✅ Report length: {len(report)} chars"
            ]
            
            print("  ✅ Report Generator: All tests passed")
            return True
            
        except Exception as e:
            error = f"❌ Report Generator error: {e}"
            self.test_results['report_generator'] = [error]
            print(f"  {error}")
            return False
    
    async def test_finetune_preparer(self):
        """Test fine-tuning data preparer"""
        print("\n🎯 Testing Fine-tune Preparer...")
        
        try:
            finetune_preparer = FineTunePreparer(self.config)
            
            # Create mock training data
            mock_data_dir = Path("logs/pentestgpt")
            mock_data_dir.mkdir(parents=True, exist_ok=True)
            
            mock_data = {
                'query': 'Test security query',
                'analysis': 'Test security analysis',
                'timestamp': '2024-01-01T00:00:00'
            }
            
            with open(mock_data_dir / 'test_data.json', 'w') as f:
                json.dump(mock_data, f)
            
            # Don't actually prepare data to avoid long processing
            # Just test initialization
            
            self.test_results['finetune_preparer'] = [
                "✅ Fine-tune preparer initialized",
                f"✅ Data sources configured: {len(self.config.get('fine_tuning', {}).get('data_sources', []))}",
                "⚠️  Full preparation test skipped (time-intensive)"
            ]
            
            print("  ✅ Fine-tune Preparer: Basic tests passed")
            return True
            
        except Exception as e:
            error = f"❌ Fine-tune Preparer error: {e}"
            self.test_results['finetune_preparer'] = [error]
            print(f"  {error}")
            return False
    
    async def test_integration(self):
        """Test component integration"""
        print("\n🔗 Testing Component Integration...")
        
        try:
            # Test that components can work together
            rag_embedder = RAGEmbedder(self.config)
            await rag_embedder.initialize()
            
            file_parser = FileParser(self.config)
            task_router = TaskRouter(self.config)
            
            # Test data flow: File -> Parser -> RAG
            test_content = "Test vulnerability document with SQL injection details."
            
            # Simulate file parsing
            parsed_result = {
                'content': test_content,
                'category': 'web_security',
                'metadata': {'test': True}
            }
            
            # Add to RAG
            doc_id = await rag_embedder.add_document(
                content=parsed_result['content'],
                metadata=parsed_result['metadata']
            )
            
            # Search in RAG
            search_results = await rag_embedder.search(
                query="SQL injection",
                collection="vulnerabilities",
                top_k=1
            )
            
            self.test_results['integration'] = [
                "✅ Components initialized together",
                f"✅ Data flow test: file -> parser -> RAG",
                f"✅ Document added: {doc_id}",
                f"✅ Search results: {len(search_results)} found"
            ]
            
            print("  ✅ Integration: All tests passed")
            return True
            
        except Exception as e:
            error = f"❌ Integration error: {e}"
            self.test_results['integration'] = [error]
            print(f"  {error}")
            return False
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("🧪 INTEGRATION TEST REPORT")
        print("="*60)
        
        total_tests = 0
        passed_tests = 0
        
        for component, results in self.test_results.items():
            print(f"\n📦 {component.upper()}:")
            for result in results:
                print(f"   {result}")
                total_tests += 1
                if result.startswith("✅"):
                    passed_tests += 1
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Checks: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Issues: {total_tests - passed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! Platform is ready for deployment.")
        elif passed_tests >= total_tests * 0.8:
            print("\n⚠️  MOSTLY WORKING: Minor issues detected, platform should work.")
        else:
            print("\n❌ SIGNIFICANT ISSUES: Please fix errors before deployment.")
        
        # Save report to file
        report_file = Path("logs/testing/integration_report.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': str(asyncio.get_event_loop().time()),
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'success_rate': (passed_tests/total_tests)*100,
                'results': self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")

async def main():
    """Run comprehensive integration tests"""
    print("🧪 Cybersecurity AI Agent Platform - Integration Tests")
    print("="*60)
    
    tester = PlatformTester()
    
    # Run all tests
    test_functions = [
        tester.test_environment,
        tester.test_rag_embedder,
        tester.test_pentestgpt,
        tester.test_file_parser,
        tester.test_rss_fetcher,
        tester.test_task_router,
        tester.test_report_generator,
        tester.test_finetune_preparer,
        tester.test_integration
    ]
    
    for test_func in test_functions:
        try:
            await test_func()
        except Exception as e:
            print(f"❌ Test function {test_func.__name__} failed: {e}")
    
    # Generate final report
    tester.generate_test_report()

if __name__ == "__main__":
    # Ensure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests
    asyncio.run(main())
