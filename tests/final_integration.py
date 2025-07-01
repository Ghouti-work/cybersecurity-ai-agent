#!/usr/bin/env python3
"""
Cybersecurity AI Agent Platform - Final System Integration
Complete platform validation and deployment preparation
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import yaml
from loguru import logger
from dotenv import load_dotenv

class PlatformIntegrator:
    """Final system integration and deployment preparation"""
    
    def __init__(self):
        self.config = self._load_config()
        self.integration_results = {}
        self.deployment_ready = False
        self._setup_logging()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration with validation"""
        load_dotenv()
        
        config_file = Path('config.yaml')
        if not config_file.exists():
            logger.error("❌ config.yaml not found!")
            sys.exit(1)
        
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            logger.info("✅ Configuration loaded successfully")
            return config
        except Exception as e:
            logger.error(f"❌ Failed to load config.yaml: {e}")
            sys.exit(1)
    
    def _setup_logging(self):
        """Setup integration logging"""
        log_dir = Path("logs/integration")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_dir / f"integration_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.log",
            rotation="1 day",
            retention="7 days",
            level="DEBUG"
        )
    
    async def validate_environment(self) -> Dict[str, Any]:
        """Comprehensive environment validation"""
        logger.info("🔍 Validating environment...")
        
        validation_results = {
            'status': 'pass',
            'checks': [],
            'warnings': [],
            'errors': []
        }
        
        # Check Python version
        import sys
        python_version = sys.version_info
        if python_version >= (3, 8):
            validation_results['checks'].append(f"✅ Python {python_version.major}.{python_version.minor} is compatible")
        else:
            validation_results['errors'].append(f"❌ Python {python_version.major}.{python_version.minor} is too old (3.8+ required)")
            validation_results['status'] = 'fail'
        
        # Check required environment variables
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'AUTHORIZED_USER_ID',
            'GEMINI_API_KEY'
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            if value and not value.startswith('your_'):
                validation_results['checks'].append(f"✅ {var} is configured")
            else:
                validation_results['warnings'].append(f"⚠️  {var} needs configuration")
        
        # Check system resources
        try:
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            disk_gb = psutil.disk_usage('.').free / (1024**3)
            
            if memory_gb >= 6:
                validation_results['checks'].append(f"✅ Memory: {memory_gb:.1f}GB available")
            else:
                validation_results['warnings'].append(f"⚠️  Low memory: {memory_gb:.1f}GB (6GB+ recommended)")
            
            if disk_gb >= 5:
                validation_results['checks'].append(f"✅ Disk space: {disk_gb:.1f}GB available")
            else:
                validation_results['warnings'].append(f"⚠️  Low disk space: {disk_gb:.1f}GB (5GB+ recommended)")
        except ImportError:
            validation_results['warnings'].append("⚠️  psutil not available for resource checking")
        
        # Check required files
        required_files = [
            'config.yaml',
            '.env',
            'requirements.txt',
            'main.py',
            'telegram_bot.py',
            'pentestgpt_gemini.py',
            'rag_embedder.py'
        ]
        
        for file in required_files:
            if Path(file).exists():
                validation_results['checks'].append(f"✅ {file} exists")
            else:
                validation_results['errors'].append(f"❌ {file} missing")
                validation_results['status'] = 'fail'
        
        # Check directory structure
        required_dirs = [
            'logs',
            'rag_data',
            'reports',
            'finetune_data',
            'models',
            'config',
            'temp'
        ]
        
        for dir in required_dirs:
            if Path(dir).exists():
                validation_results['checks'].append(f"✅ {dir}/ directory exists")
            else:
                validation_results['warnings'].append(f"⚠️  {dir}/ directory missing (will be created)")
                Path(dir).mkdir(parents=True, exist_ok=True)
        
        self.integration_results['environment'] = validation_results
        return validation_results
    
    async def validate_dependencies(self) -> Dict[str, Any]:
        """Validate Python dependencies"""
        logger.info("📚 Validating dependencies...")
        
        dependency_results = {
            'status': 'pass',
            'installed': [],
            'missing': [],
            'version_conflicts': []
        }
        
        # Core dependencies to check
        critical_deps = [
            'telegram',
            'yaml',
            'loguru',
            'transformers',
            'chromadb',
            'sentence_transformers',
            'google.generativeai'
        ]
        
        for dep in critical_deps:
            try:
                __import__(dep)
                dependency_results['installed'].append(f"✅ {dep}")
            except ImportError:
                dependency_results['missing'].append(f"❌ {dep}")
                dependency_results['status'] = 'fail'
        
        # Optional dependencies
        optional_deps = [
            'psutil',
            'aiohttp',
            'torch',
            'numpy'
        ]
        
        for dep in optional_deps:
            try:
                __import__(dep)
                dependency_results['installed'].append(f"✅ {dep} (optional)")
            except ImportError:
                dependency_results['missing'].append(f"⚠️  {dep} (optional)")
        
        self.integration_results['dependencies'] = dependency_results
        return dependency_results
    
    async def test_component_initialization(self) -> Dict[str, Any]:
        """Test initialization of all core components"""
        logger.info("🔧 Testing component initialization...")
        
        component_results = {
            'status': 'pass',
            'components': {},
            'errors': []
        }
        
        # Test each component
        components = [
            ('Task Router', 'task_router', 'TaskRouter'),
            ('RAG Embedder', 'rag_embedder', 'RAGEmbedder'),
            ('PentestGPT', 'pentestgpt_gemini', 'PentestGPT'),
            ('RSS Fetcher', 'rss_fetcher', 'RSSFetcher'),
            ('File Parser', 'file_parser', 'FileParser'),
            ('Report Generator', 'report_generator', 'ReportGenerator'),
            ('Fine-tune Preparer', 'finetune_preparer', 'FineTunePreparer')
        ]
        
        for name, module_name, class_name in components:
            try:
                # Import the module
                module = __import__(module_name)
                component_class = getattr(module, class_name)
                
                # Initialize the component
                component = component_class(self.config)
                
                # Test async initialization if available
                if hasattr(component, 'initialize'):
                    await component.initialize()
                
                component_results['components'][name] = {
                    'status': 'initialized',
                    'module': module_name,
                    'class': class_name
                }
                
                logger.info(f"✅ {name} initialized successfully")
                
            except Exception as e:
                error_msg = f"❌ {name} initialization failed: {str(e)}"
                component_results['errors'].append(error_msg)
                component_results['components'][name] = {
                    'status': 'failed',
                    'error': str(e)
                }
                component_results['status'] = 'fail'
                logger.error(error_msg)
        
        self.integration_results['components'] = component_results
        return component_results
    
    async def test_api_connectivity(self) -> Dict[str, Any]:
        """Test external API connectivity"""
        logger.info("🌐 Testing API connectivity...")
        
        api_results = {
            'status': 'pass',
            'apis': {},
            'warnings': []
        }
        
        # Test Telegram API
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if telegram_token and not telegram_token.startswith('your_'):
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    url = f"https://api.telegram.org/bot{telegram_token}/getMe"
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            api_results['apis']['telegram'] = {
                                'status': 'connected',
                                'bot_name': data.get('result', {}).get('first_name', 'Unknown')
                            }
                            logger.info("✅ Telegram API connected")
                        else:
                            api_results['apis']['telegram'] = {
                                'status': 'error',
                                'error': f"HTTP {response.status}"
                            }
                            api_results['warnings'].append("⚠️  Telegram API connection failed")
            except Exception as e:
                api_results['apis']['telegram'] = {
                    'status': 'error',
                    'error': str(e)
                }
                api_results['warnings'].append(f"⚠️  Telegram API error: {str(e)}")
        else:
            api_results['apis']['telegram'] = {'status': 'not_configured'}
            api_results['warnings'].append("⚠️  Telegram API not configured")
        
        # Test Gemini API
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key and not gemini_key.startswith('your_'):
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-pro')
                
                # Test with simple prompt
                response = await asyncio.to_thread(
                    model.generate_content, 
                    "Respond with 'API_TEST_OK' only."
                )
                
                if 'API_TEST_OK' in response.text:
                    api_results['apis']['gemini'] = {'status': 'connected'}
                    logger.info("✅ Gemini API connected")
                else:
                    api_results['apis']['gemini'] = {
                        'status': 'unexpected_response',
                        'response': response.text[:100]
                    }
                    api_results['warnings'].append("⚠️  Gemini API gave unexpected response")
                    
            except Exception as e:
                api_results['apis']['gemini'] = {
                    'status': 'error',
                    'error': str(e)
                }
                api_results['warnings'].append(f"⚠️  Gemini API error: {str(e)}")
        else:
            api_results['apis']['gemini'] = {'status': 'not_configured'}
            api_results['warnings'].append("⚠️  Gemini API not configured")
        
        self.integration_results['apis'] = api_results
        return api_results
    
    async def test_data_flow(self) -> Dict[str, Any]:
        """Test complete data flow through the system"""
        logger.info("🔄 Testing data flow...")
        
        dataflow_results = {
            'status': 'pass',
            'tests': [],
            'errors': []
        }
        
        try:
            # Test 1: RAG document storage and retrieval
            try:
                from rag_embedder import RAGEmbedder
                rag = RAGEmbedder(self.config)
                await rag.initialize()
                
                # Add test document
                test_content = "This is a cybersecurity test document about SQL injection vulnerabilities."
                doc_id = await rag.add_document(
                    content=test_content,
                    metadata={'category': 'test', 'source': 'integration_test'}
                )
                
                # Search for document
                search_results = await rag.search(
                    query="SQL injection",
                    collection="vulnerabilities",
                    top_k=1
                )
                
                if search_results:
                    dataflow_results['tests'].append("✅ RAG storage and retrieval")
                else:
                    dataflow_results['tests'].append("⚠️  RAG search returned no results")
                    
            except Exception as e:
                dataflow_results['errors'].append(f"❌ RAG data flow failed: {str(e)}")
                dataflow_results['status'] = 'fail'
            
            # Test 2: File parsing pipeline
            try:
                from file_parser import FileParser
                import tempfile
                
                parser = FileParser(self.config)
                
                # Create test file
                test_md_content = """# Security Test Document
                
This document contains information about:
- Web application vulnerabilities
- Network security issues
- Penetration testing methodologies
"""
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                    f.write(test_md_content)
                    temp_file = f.name
                
                try:
                    # Parse the file
                    result = await parser.parse_file(temp_file)
                    
                    if result and 'content' in result:
                        dataflow_results['tests'].append("✅ File parsing pipeline")
                    else:
                        dataflow_results['tests'].append("⚠️  File parsing returned incomplete results")
                finally:
                    os.unlink(temp_file)
                    
            except Exception as e:
                dataflow_results['errors'].append(f"❌ File parsing pipeline failed: {str(e)}")
                dataflow_results['status'] = 'fail'
            
            # Test 3: Task routing
            try:
                from task_router import TaskRouter
                router = TaskRouter(self.config)
                
                # Test command analysis
                test_command = "/scan 192.168.1.1"
                route = await router.analyze_command(test_command)
                
                if route and 'component' in route:
                    dataflow_results['tests'].append("✅ Task routing")
                else:
                    dataflow_results['tests'].append("⚠️  Task routing returned incomplete results")
                    
            except Exception as e:
                dataflow_results['errors'].append(f"❌ Task routing failed: {str(e)}")
                dataflow_results['status'] = 'fail'
            
        except Exception as e:
            dataflow_results['errors'].append(f"❌ Data flow testing failed: {str(e)}")
            dataflow_results['status'] = 'fail'
        
        self.integration_results['dataflow'] = dataflow_results
        return dataflow_results
    
    async def generate_deployment_checklist(self) -> Dict[str, Any]:
        """Generate deployment readiness checklist"""
        logger.info("📋 Generating deployment checklist...")
        
        checklist = {
            'ready_for_deployment': True,
            'critical_issues': [],
            'warnings': [],
            'deployment_steps': [],
            'post_deployment_tasks': []
        }
        
        # Analyze integration results
        for category, results in self.integration_results.items():
            if results.get('status') == 'fail':
                checklist['ready_for_deployment'] = False
                checklist['critical_issues'].extend(results.get('errors', []))
            
            checklist['warnings'].extend(results.get('warnings', []))
        
        # Deployment steps
        if checklist['ready_for_deployment']:
            checklist['deployment_steps'] = [
                "1. Upload code to Azure VM",
                "2. Run ./install_azure.sh",
                "3. Configure .env file with production keys",
                "4. Start service: ./manage_service.sh start",
                "5. Enable auto-start: ./manage_service.sh enable",
                "6. Test Telegram bot functionality",
                "7. Verify health monitoring",
                "8. Configure backup schedule"
            ]
            
            checklist['post_deployment_tasks'] = [
                "• Monitor system health for 24 hours",
                "• Test all Telegram commands",
                "• Verify RSS feed processing",
                "• Check log rotation",
                "• Configure alerting",
                "• Document recovery procedures"
            ]
        else:
            checklist['deployment_steps'] = [
                "❌ DEPLOYMENT BLOCKED - Fix critical issues first"
            ]
        
        self.integration_results['deployment'] = checklist
        return checklist
    
    def print_integration_summary(self):
        """Print comprehensive integration summary"""
        print("\n" + "="*80)
        print("🛡️  CYBERSECURITY AI AGENT PLATFORM - INTEGRATION SUMMARY")
        print("="*80)
        
        # Overall status
        deployment_ready = self.integration_results.get('deployment', {}).get('ready_for_deployment', False)
        status_emoji = "✅" if deployment_ready else "❌"
        status_text = "READY FOR DEPLOYMENT" if deployment_ready else "NOT READY - ISSUES DETECTED"
        
        print(f"\n🚀 Deployment Status: {status_emoji} {status_text}")
        print(f"📅 Integration Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Environment validation
        env_results = self.integration_results.get('environment', {})
        print(f"\n🔍 Environment Validation:")
        print(f"   Status: {env_results.get('status', 'unknown').upper()}")
        print(f"   Checks passed: {len(env_results.get('checks', []))}")
        print(f"   Warnings: {len(env_results.get('warnings', []))}")
        print(f"   Errors: {len(env_results.get('errors', []))}")
        
        # Dependencies
        dep_results = self.integration_results.get('dependencies', {})
        print(f"\n📚 Dependencies:")
        print(f"   Status: {dep_results.get('status', 'unknown').upper()}")
        print(f"   Installed: {len(dep_results.get('installed', []))}")
        print(f"   Missing: {len(dep_results.get('missing', []))}")
        
        # Components
        comp_results = self.integration_results.get('components', {})
        components = comp_results.get('components', {})
        successful_components = sum(1 for comp in components.values() if comp.get('status') == 'initialized')
        print(f"\n🔧 Component Initialization:")
        print(f"   Status: {comp_results.get('status', 'unknown').upper()}")
        print(f"   Successful: {successful_components}/{len(components)}")
        
        for name, status in components.items():
            emoji = "✅" if status.get('status') == 'initialized' else "❌"
            print(f"   {emoji} {name}")
        
        # API Connectivity
        api_results = self.integration_results.get('apis', {})
        apis = api_results.get('apis', {})
        print(f"\n🌐 API Connectivity:")
        for api_name, api_status in apis.items():
            status = api_status.get('status', 'unknown')
            emoji = {
                'connected': '✅',
                'not_configured': '⚠️',
                'error': '❌'
            }.get(status, '❓')
            print(f"   {emoji} {api_name.title()}: {status}")
        
        # Data Flow Tests
        dataflow_results = self.integration_results.get('dataflow', {})
        print(f"\n🔄 Data Flow Tests:")
        print(f"   Status: {dataflow_results.get('status', 'unknown').upper()}")
        for test in dataflow_results.get('tests', []):
            print(f"   {test}")
        
        # Critical Issues
        critical_issues = self.integration_results.get('deployment', {}).get('critical_issues', [])
        if critical_issues:
            print(f"\n❌ CRITICAL ISSUES TO FIX:")
            for issue in critical_issues:
                print(f"   • {issue}")
        
        # Warnings
        all_warnings = []
        for results in self.integration_results.values():
            all_warnings.extend(results.get('warnings', []))
        
        if all_warnings:
            print(f"\n⚠️  WARNINGS ({len(all_warnings)}):")
            for warning in all_warnings[:5]:  # Show first 5
                print(f"   • {warning}")
            if len(all_warnings) > 5:
                print(f"   ... and {len(all_warnings) - 5} more")
        
        # Deployment steps
        deployment_steps = self.integration_results.get('deployment', {}).get('deployment_steps', [])
        if deployment_steps:
            print(f"\n🚀 DEPLOYMENT STEPS:")
            for step in deployment_steps:
                print(f"   {step}")
        
        # Post-deployment tasks
        post_tasks = self.integration_results.get('deployment', {}).get('post_deployment_tasks', [])
        if post_tasks:
            print(f"\n📋 POST-DEPLOYMENT TASKS:")
            for task in post_tasks:
                print(f"   {task}")
        
        print("\n" + "="*80)
        
        if deployment_ready:
            print("🎉 PLATFORM READY FOR AZURE VM DEPLOYMENT!")
            print("Run ./install_azure.sh on your Azure VM to deploy.")
        else:
            print("🛠️  PLEASE FIX ISSUES BEFORE DEPLOYMENT")
            print("Re-run this script after addressing critical issues.")
        
        print("="*80)

async def main():
    """Run complete platform integration"""
    print("🛡️  Cybersecurity AI Agent Platform - Final Integration")
    print("="*70)
    
    integrator = PlatformIntegrator()
    
    try:
        # Run all integration tests
        await integrator.validate_environment()
        await integrator.validate_dependencies()
        await integrator.test_component_initialization()
        await integrator.test_api_connectivity()
        await integrator.test_data_flow()
        await integrator.generate_deployment_checklist()
        
        # Save results
        results_file = Path("logs/integration/final_integration_results.json")
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(integrator.integration_results, f, indent=2)
        
        # Print summary
        integrator.print_integration_summary()
        
        logger.info(f"✅ Integration complete. Results saved to: {results_file}")
        
    except Exception as e:
        logger.error(f"❌ Integration failed: {e}")
        print(f"\n❌ INTEGRATION FAILED: {e}")
        print("Check logs for detailed error information.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
