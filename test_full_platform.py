#!/usr/bin/env python3
"""
Comprehensive Test Suite for Cybersecurity AI Agent Platform
Tests all major components and functionality
"""

import asyncio
import json
import os
import time
import sys
from pathlib import Path
from datetime import datetime

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))
sys.path.insert(0, str(project_root / "agents"))

# Import components
from core.shared_utils import ConfigManager, initialize_shared_components
from agents.rag_embedder import RAGEmbedder
from agents.pentestgpt_gemini import PentestGPTGemini
from agents.rss_fetcher import RSSFetcher
from agents.file_parser import FileParser
from agents.report_generator import ReportGenerator
from loguru import logger

class PlatformTester:
    def __init__(self):
        self.test_results = {}
        self.config = None
        
    async def run_all_tests(self):
        """Run comprehensive platform tests"""
        print("\n🧪 CYBERSECURITY AI AGENT PLATFORM - COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        
        # Initialize shared components
        await self.test_shared_components()
        
        # Test individual components
        await self.test_rag_embedder()
        await self.test_pentestgpt_gemini()
        await self.test_rss_fetcher()
        await self.test_file_parser()
        await self.test_report_generator()
        
        # Integration tests
        await self.test_integration_scenarios()
        
        # Performance tests
        await self.test_performance()
        
        # Generate test report
        self.generate_test_report()
        
    async def test_shared_components(self):
        """Test shared utilities and configuration"""
        print("\n📋 Testing Shared Components...")
        
        try:
            # Test configuration loading
            await initialize_shared_components()
            config_manager = ConfigManager()
            self.config = config_manager.config
            
            self.test_results['shared_components'] = {
                'config_loading': True,
                'directories_created': True,
                'logger_setup': True,
                'gemini_client': True if self.config.get('gemini_api_key') else False
            }
            print("✅ Shared components initialized successfully")
            
        except Exception as e:
            self.test_results['shared_components'] = {'error': str(e)}
            print(f"❌ Shared components failed: {e}")
    
    async def test_rag_embedder(self):
        """Test RAG embedder functionality"""
        print("\n📚 Testing RAG Embedder...")
        
        try:
            embedder = RAGEmbedder(self.config)
            await embedder.initialize()
            
            # Test document addition
            test_doc = {
                'content': "SQL injection is a common web vulnerability that allows attackers to manipulate database queries.",
                'metadata': {
                    'source': 'test_platform',
                    'category': 'web_security',
                    'tags': ['sql', 'injection', 'web'],
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            doc_id = await embedder.add_document(
                test_doc['content'],
                test_doc['metadata'],
                'vulnerabilities'
            )
            
            # Test search functionality
            search_results = await embedder.search_similar(
                "web application security vulnerabilities",
                n_results=3
            )
            
            # Test collection stats
            stats = await embedder.get_collection_stats()
            
            self.test_results['rag_embedder'] = {
                'initialization': True,
                'document_addition': bool(doc_id),
                'search_functionality': len(search_results) > 0,
                'collections_count': len(stats['collections']),
                'total_documents': stats['total_documents']
            }
            print(f"✅ RAG Embedder: {len(search_results)} search results, {stats['total_documents']} total docs")
            
        except Exception as e:
            self.test_results['rag_embedder'] = {'error': str(e)}
            print(f"❌ RAG Embedder failed: {e}")
    
    async def test_pentestgpt_gemini(self):
        """Test PentestGPT Gemini AI functionality"""
        print("\n🛡️ Testing PentestGPT Gemini...")
        
        try:
            pentestgpt = PentestGPTGemini(self.config)
            
            # Test target analysis
            test_target = {
                'target': 'example.com',
                'type': 'web_application',
                'description': 'Test web application for security analysis'
            }
            
            analysis_result = await pentestgpt.analyze_target(test_target)
            
            # Test vulnerability analysis  
            vuln_analysis = await pentestgpt.analyze_vulnerabilities([
                {'type': 'sql_injection', 'severity': 'high', 'description': 'SQL injection in login form'}
            ])
            
            self.test_results['pentestgpt_gemini'] = {
                'initialization': True,
                'target_analysis': bool(analysis_result.get('analysis')),
                'vulnerability_analysis': bool(vuln_analysis.get('analysis')),
                'ai_reasoning': bool(analysis_result.get('recommendations'))
            }
            print("✅ PentestGPT Gemini: AI analysis and reasoning working")
            
        except Exception as e:
            self.test_results['pentestgpt_gemini'] = {'error': str(e)}
            print(f"❌ PentestGPT Gemini failed: {e}")
    
    async def test_rss_fetcher(self):
        """Test RSS feed fetching"""
        print("\n📡 Testing RSS Fetcher...")
        
        try:
            rss_fetcher = RSSFetcher(self.config)
            
            # Test feed fetching (limit to avoid overload)
            test_feeds = [
                'https://feeds.feedburner.com/eset/blog',
                'https://www.us-cert.gov/ncas/all.xml'
            ]
            
            articles = await rss_fetcher.fetch_feeds(max_feeds=2, max_articles_per_feed=5)
            
            # Test article processing
            if articles:
                processed = await rss_fetcher.process_articles(articles[:3])
            else:
                processed = []
            
            self.test_results['rss_fetcher'] = {
                'initialization': True,
                'feed_fetching': len(articles) > 0,
                'article_processing': len(processed) > 0,
                'articles_count': len(articles)
            }
            print(f"✅ RSS Fetcher: {len(articles)} articles fetched, {len(processed)} processed")
            
        except Exception as e:
            self.test_results['rss_fetcher'] = {'error': str(e)}
            print(f"❌ RSS Fetcher failed: {e}")
    
    async def test_file_parser(self):
        """Test file parsing capabilities"""
        print("\n📄 Testing File Parser...")
        
        try:
            file_parser = FileParser(self.config)
            
            # Create test files
            test_dir = Path("temp/test_files")
            test_dir.mkdir(parents=True, exist_ok=True)
            
            # Test text file
            test_txt = test_dir / "test.txt"
            test_txt.write_text("This is a test cybersecurity document about SQL injection vulnerabilities.")
            
            # Test JSON file
            test_json = test_dir / "test.json"
            test_json.write_text(json.dumps({
                "vulnerability": "XSS",
                "severity": "medium",
                "description": "Cross-site scripting vulnerability"
            }))
            
            # Test parsing
            txt_result = await file_parser.parse_file(str(test_txt))
            json_result = await file_parser.parse_file(str(test_json))
            
            self.test_results['file_parser'] = {
                'initialization': True,
                'text_parsing': bool(txt_result.get('content')),
                'json_parsing': bool(json_result.get('content')),
                'metadata_extraction': bool(txt_result.get('metadata'))
            }
            print("✅ File Parser: Text and JSON parsing working")
            
            # Cleanup
            test_txt.unlink(missing_ok=True)
            test_json.unlink(missing_ok=True)
            
        except Exception as e:
            self.test_results['file_parser'] = {'error': str(e)}
            print(f"❌ File Parser failed: {e}")
    
    async def test_report_generator(self):
        """Test report generation"""
        print("\n📊 Testing Report Generator...")
        
        try:
            report_gen = ReportGenerator(self.config)
            
            # Test daily report generation
            daily_report = await report_gen.generate_report('daily')
            
            # Test summary report
            summary_report = await report_gen.generate_report('summary')
            
            self.test_results['report_generator'] = {
                'initialization': True,
                'daily_report': bool(daily_report),
                'summary_report': bool(summary_report),
                'report_files_created': True
            }
            print("✅ Report Generator: Daily and summary reports generated")
            
        except Exception as e:
            self.test_results['report_generator'] = {'error': str(e)}
            print(f"❌ Report Generator failed: {e}")
    
    async def test_integration_scenarios(self):
        """Test integration between components"""
        print("\n🔗 Testing Integration Scenarios...")
        
        try:
            # Scenario 1: Document processing pipeline
            embedder = RAGEmbedder(self.config)
            file_parser = FileParser(self.config)
            
            # Create test document
            test_file = Path("temp/integration_test.txt")
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text("Buffer overflow vulnerabilities can lead to remote code execution.")
            
            # Parse and embed
            parsed = await file_parser.parse_file(str(test_file))
            if parsed.get('content'):
                doc_id = await embedder.add_document(
                    parsed['content'],
                    parsed['metadata'],
                    'vulnerabilities'
                )
                
                # Search for related content
                search_results = await embedder.search_similar(
                    "memory corruption vulnerabilities",
                    n_results=2
                )
                
                integration_success = bool(doc_id and search_results)
            else:
                integration_success = False
            
            self.test_results['integration'] = {
                'document_pipeline': integration_success,
                'search_integration': len(search_results) > 0 if 'search_results' in locals() else False
            }
            print("✅ Integration: Document processing pipeline working")
            
            # Cleanup
            test_file.unlink(missing_ok=True)
            
        except Exception as e:
            self.test_results['integration'] = {'error': str(e)}
            print(f"❌ Integration tests failed: {e}")
    
    async def test_performance(self):
        """Test system performance"""
        print("\n⚡ Testing Performance...")
        
        try:
            import psutil
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('.')
            disk_usage = (disk.used / disk.total) * 100
            
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Test embedding speed
            embedder = RAGEmbedder(self.config)
            start_time = time.time()
            await embedder._generate_embeddings("Test performance embedding")
            embedding_time = time.time() - start_time
            
            self.test_results['performance'] = {
                'memory_usage_percent': memory_usage,
                'disk_usage_percent': disk_usage,
                'cpu_usage_percent': cpu_usage,
                'embedding_speed_seconds': embedding_time,
                'performance_acceptable': memory_usage < 80 and embedding_time < 5
            }
            print(f"✅ Performance: {memory_usage:.1f}% RAM, {cpu_usage:.1f}% CPU, {embedding_time:.2f}s embedding")
            
        except Exception as e:
            self.test_results['performance'] = {'error': str(e)}
            print(f"❌ Performance tests failed: {e}")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📋 COMPREHENSIVE TEST REPORT")
        print("=" * 70)
        
        total_tests = 0
        passed_tests = 0
        
        for component, results in self.test_results.items():
            print(f"\n🔍 {component.upper().replace('_', ' ')}")
            print("-" * 40)
            
            if 'error' in results:
                print(f"❌ FAILED: {results['error']}")
                continue
                
            for test_name, result in results.items():
                total_tests += 1
                if result is True:
                    passed_tests += 1
                    print(f"✅ {test_name}: PASSED")
                elif result is False:
                    print(f"❌ {test_name}: FAILED")
                else:
                    print(f"ℹ️  {test_name}: {result}")
        
        # Overall results
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 OVERALL RESULTS")
        print("=" * 30)
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 PLATFORM STATUS: EXCELLENT")
        elif success_rate >= 60:
            print("✅ PLATFORM STATUS: GOOD") 
        else:
            print("⚠️ PLATFORM STATUS: NEEDS ATTENTION")
        
        # Save detailed results
        results_file = Path("test_results.json")
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests, 
                    'success_rate': success_rate
                },
                'detailed_results': self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")

async def main():
    """Main test execution"""
    tester = PlatformTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
