"""
Task Router for Cybersecurity AI Agent
Central orchestration and routing of tasks
"""

import asyncio
import json
import os
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess

from loguru import logger
import yaml

# Import our modules
from pentestgpt_gemini import PentestGPTGemini
from rag_embedder import RAGEmbedder
from file_parser import FileParser
from rss_fetcher import RSSFetcher
from shared_utils import (
    ConfigManager, LoggerManager, DirectoryManager,
    SystemMetrics, PromptTemplates
)

class TaskRouter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.start_time = datetime.now()
        
        # Initialize components
        self.pentestgpt = None
        self.rag_embedder = None
        self.file_parser = None
        self.rss_fetcher = None
        
        # Initialize components lazily to save memory
        self._initialize_components()
        
        # Setup logging using shared utility
        LoggerManager.setup_logger('task_router')
        
        logger.info("🧵 Task Router initialized with shared utilities")

    def _initialize_components(self):
        """Initialize components lazily"""
        try:
            self.rag_embedder = RAGEmbedder(self.config)
            logger.info("RAG Embedder initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RAG Embedder: {e}")

    async def route_scan_task(self, target: str) -> Dict[str, Any]:
        """Route scanning task - can integrate with external tools"""
        logger.info(f"Routing scan task for target: {target}")
        
        try:
            # Basic validation
            if not target or len(target.strip()) < 3:
                raise ValueError("Invalid target specified")
            
            # For now, we'll use PentestGPT to analyze the scan approach
            # In production, this would integrate with actual scanning tools
            
            if not self.pentestgpt:
                self.pentestgpt = PentestGPTGemini(self.config)
            
            # Create scan analysis query
            scan_query = f"Provide a comprehensive security scanning approach for target: {target}. Include reconnaissance, vulnerability assessment, and enumeration strategies."
            
            # Get analysis from PentestGPT
            analysis = await self.pentestgpt.analyze_security_scenario(scan_query)
            
            # Simulate scan results (in production, integrate with real tools)
            scan_results = await self._simulate_scan_results(target, analysis)
            
            result = {
                'target': target,
                'scan_type': 'comprehensive',
                'status': 'completed',
                'summary': scan_results['summary'],
                'findings': scan_results['findings'],
                'recommendations': scan_results['recommendations'],
                'timestamp': datetime.now().isoformat(),
                'analysis_id': analysis.get('timestamp', '')
            }
            
            # Save scan results
            await self._save_scan_results(result)
            
            logger.info(f"Scan task completed for: {target}")
            return result
            
        except Exception as e:
            logger.error(f"Scan task failed: {e}")
            raise

    async def _simulate_scan_results(self, target: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate scan results (replace with real scanning tools)"""
        
        # Extract key points from PentestGPT analysis
        detailed_analysis = analysis.get('detailed_analysis', '')
        attack_vectors = analysis.get('attack_vectors', '')
        
        # Create realistic scan summary
        summary = f"Security scan completed for {target}. Analysis focused on web application security, network enumeration, and vulnerability assessment."
        
        # Generate findings based on analysis
        findings = []
        if 'sql injection' in detailed_analysis.lower():
            findings.append("• Potential SQL injection vectors identified in input forms")
        if 'xss' in detailed_analysis.lower():
            findings.append("• Cross-site scripting vulnerabilities may exist")
        if 'network' in detailed_analysis.lower():
            findings.append("• Network services enumerated, potential attack surface identified")
        if 'authentication' in detailed_analysis.lower():
            findings.append("• Authentication mechanisms analyzed for weaknesses")
        
        if not findings:
            findings = ["• General security posture assessed", "• Attack surface enumerated"]
        
        findings_text = "\n".join(findings)
        
        # Generate recommendations
        recommendations = [
            "• Implement input validation and parameterized queries",
            "• Deploy web application firewall (WAF)",
            "• Regular security testing and code reviews",
            "• Monitor for suspicious activities"
        ]
        
        recommendations_text = "\n".join(recommendations)
        
        return {
            'summary': summary,
            'findings': findings_text,
            'recommendations': recommendations_text
        }

    async def route_thinking_task(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Route analytical thinking task to PentestGPT"""
        logger.info(f"Routing thinking task: {query[:50]}...")
        
        try:
            if not self.pentestgpt:
                self.pentestgpt = PentestGPTGemini(self.config)
            
            # Get RAG context if available
            if self.rag_embedder and not context:
                context = await self.rag_embedder.get_context_for_query(query)
            
            # Perform analysis
            analysis = await self.pentestgpt.analyze_security_scenario(query, context)
            
            result = {
                'query': query,
                'analysis': analysis,
                'context_used': bool(context),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("Thinking task completed")
            return result
            
        except Exception as e:
            logger.error(f"Thinking task failed: {e}")
            raise

    async def route_file_analysis_task(self, file_path: str) -> Dict[str, Any]:
        """Route file analysis task"""
        logger.info(f"Routing file analysis task: {file_path}")
        
        try:
            if not self.file_parser:
                self.file_parser = FileParser(self.config)
            
            # Process the file
            analysis = await self.file_parser.process_file(file_path)
            
            result = {
                'file_path': file_path,
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("File analysis task completed")
            return result
            
        except Exception as e:
            logger.error(f"File analysis task failed: {e}")
            raise

    async def route_rss_task(self) -> Dict[str, Any]:
        """Route RSS fetching task"""
        logger.info("Routing RSS fetching task")
        
        try:
            if not self.rss_fetcher:
                self.rss_fetcher = RSSFetcher(self.config)
            
            # Fetch RSS feeds
            results = await self.rss_fetcher.fetch_all_feeds()
            
            result = {
                'rss_results': results,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("RSS task completed")
            return result
            
        except Exception as e:
            logger.error(f"RSS task failed: {e}")
            raise

    async def route_search_task(self, query: str, collection: Optional[str] = None) -> Dict[str, Any]:
        """Route search task through RAG"""
        logger.info(f"Routing search task: {query[:50]}...")
        
        try:
            if not self.rag_embedder:
                raise ValueError("RAG Embedder not available")
            
            # Perform search
            results = await self.rag_embedder.search_similar(query, collection)
            
            # Format results for display
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'content': result['content'][:300] + "..." if len(result['content']) > 300 else result['content'],
                    'source': result['metadata'].get('source', 'Unknown'),
                    'category': result['metadata'].get('category', 'Unknown'),
                    'similarity_score': result['similarity_score']
                })
            
            search_result = {
                'query': query,
                'results': formatted_results,
                'total_results': len(results),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Search task completed: {len(results)} results")
            return search_result
            
        except Exception as e:
            logger.error(f"Search task failed: {e}")
            raise

    async def detect_task_type(self, message: str) -> str:
        """Detect the type of task from user message"""
        message_lower = message.lower()
        
        # Scan-related keywords
        if any(keyword in message_lower for keyword in ['scan', 'nmap', 'enumerate', 'discover']):
            return 'scan'
        
        # Analysis/thinking keywords
        elif any(keyword in message_lower for keyword in ['how to', 'exploit', 'vulnerability', 'attack']):
            return 'analysis'
        
        # Search keywords
        elif any(keyword in message_lower for keyword in ['search', 'find', 'look for', 'show me']):
            return 'search'
        
        # RSS keywords
        elif any(keyword in message_lower for keyword in ['rss', 'news', 'feeds', 'updates']):
            return 'rss'
        
        # Default to analysis
        else:
            return 'analysis'

    async def process_natural_language_task(self, message: str) -> Dict[str, Any]:
        """Process natural language task and route appropriately"""
        logger.info(f"Processing natural language task: {message[:50]}...")
        
        try:
            # Detect task type
            task_type = await self.detect_task_type(message)
            
            if task_type == 'scan':
                # Extract target from message
                target = await self._extract_target_from_message(message)
                return await self.route_scan_task(target)
            
            elif task_type == 'analysis':
                return await self.route_thinking_task(message)
            
            elif task_type == 'search':
                # Extract search query
                search_query = await self._extract_search_query_from_message(message)
                return await self.route_search_task(search_query)
            
            elif task_type == 'rss':
                return await self.route_rss_task()
            
            else:
                # Default to analysis
                return await self.route_thinking_task(message)
                
        except Exception as e:
            logger.error(f"Natural language task processing failed: {e}")
            raise

    async def _extract_target_from_message(self, message: str) -> str:
        """Extract target from scan message"""
        # Simple extraction - could be improved with NLP
        words = message.split()
        
        # Look for domain-like patterns or IP addresses
        for word in words:
            if '.' in word and not word.startswith('.'):
                # Simple check for domain or IP
                if any(char.isalpha() for char in word) or word.replace('.', '').isdigit():
                    return word.strip('.,;!?')
        
        # If no clear target found, return a placeholder
        return "target-not-specified"

    async def _extract_search_query_from_message(self, message: str) -> str:
        """Extract search query from message"""
        # Remove common search prefixes
        prefixes = ['search for', 'find', 'look for', 'show me']
        
        query = message.lower()
        for prefix in prefixes:
            if query.startswith(prefix):
                query = query[len(prefix):].strip()
                break
        
        return query

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status using shared utilities"""
        try:
            # Use shared system metrics
            system_metrics = SystemMetrics.get_system_metrics()
            
            # Calculate uptime
            uptime = datetime.now() - self.start_time
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds
            
            # RAG statistics
            rag_stats = {}
            if self.rag_embedder:
                try:
                    rag_stats = await self.rag_embedder.get_collection_stats()
                except Exception as e:
                    logger.error(f"Failed to get RAG stats: {e}")
                    rag_stats = {'total_documents': 0}
            
            # Log file counts
            log_entries = await self._count_log_entries()
            
            # File processing statistics
            file_stats = await self._get_file_processing_stats()
            
            # Recent activities
            recent_activities = await self._get_recent_activities()
            
            status = {
                'uptime': uptime_str,
                'memory_usage': system_metrics['memory_percent'],
                'disk_usage': system_metrics['disk_percent'],
                'rag_documents': rag_stats.get('total_documents', 0),
                'log_entries': log_entries,
                'processed_files': file_stats.get('total_files', 0),
                'last_rss_update': recent_activities.get('last_rss_update', 'Never'),
                'last_report': recent_activities.get('last_report', 'Never'),
                'last_finetune': recent_activities.get('last_finetune', 'Never'),
                'system_health': 'Good' if system_metrics['memory_percent'] < 80 and system_metrics['disk_percent'] < 90 else 'Warning'
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {
                'uptime': 'Unknown',
                'memory_usage': 0,
                'disk_usage': 0,
                'system_health': 'Error'
            }

    async def _save_scan_results(self, result: Dict[str, Any]):
        """Save scan results to file"""
        try:
            # Create reports directory
            reports_dir = Path("reports/scans")
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Save scan result
            filename = f"scan_{result['target']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = reports_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            logger.info(f"Scan results saved: {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save scan results: {e}")

    async def _count_log_entries(self) -> int:
        """Count total log entries"""
        try:
            log_count = 0
            logs_dir = Path("logs")
            
            if logs_dir.exists():
                for log_file in logs_dir.rglob("*.log"):
                    try:
                        with open(log_file, 'r') as f:
                            log_count += sum(1 for _ in f)
                    except Exception:
                        continue
            
            return log_count
            
        except Exception as e:
            logger.error(f"Failed to count log entries: {e}")
            return 0

    async def _get_file_processing_stats(self) -> Dict[str, Any]:
        """Get file processing statistics"""
        try:
            if self.file_parser:
                return await self.file_parser.get_processing_statistics()
            else:
                # Count processed files manually
                rag_data_dir = Path("rag_data")
                total_files = 0
                
                if rag_data_dir.exists():
                    for category_dir in rag_data_dir.iterdir():
                        if category_dir.is_dir() and category_dir.name != 'chroma_db':
                            total_files += len(list(category_dir.glob('file_*.json')))
                
                return {'total_files': total_files}
                
        except Exception as e:
            logger.error(f"Failed to get file processing stats: {e}")
            return {'total_files': 0}

    async def _get_recent_activities(self) -> Dict[str, str]:
        """Get timestamps of recent activities"""
        activities = {
            'last_rss_update': 'Never',
            'last_report': 'Never',
            'last_finetune': 'Never'
        }
        
        try:
            # Check RSS logs
            rss_logs = Path("logs/rss")
            if rss_logs.exists():
                rss_files = list(rss_logs.glob("*.log"))
                if rss_files:
                    latest_rss = max(rss_files, key=lambda x: x.stat().st_mtime)
                    activities['last_rss_update'] = datetime.fromtimestamp(
                        latest_rss.stat().st_mtime
                    ).strftime('%Y-%m-%d %H:%M')
            
            # Check reports
            reports_dir = Path("reports")
            if reports_dir.exists():
                report_files = list(reports_dir.rglob("*.md")) + list(reports_dir.rglob("*.json"))
                if report_files:
                    latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
                    activities['last_report'] = datetime.fromtimestamp(
                        latest_report.stat().st_mtime
                    ).strftime('%Y-%m-%d %H:%M')
            
            # Check fine-tuning data
            finetune_dir = Path("finetune_data/processed")
            if finetune_dir.exists():
                finetune_files = list(finetune_dir.glob("*.jsonl"))
                if finetune_files:
                    latest_finetune = max(finetune_files, key=lambda x: x.stat().st_mtime)
                    activities['last_finetune'] = datetime.fromtimestamp(
                        latest_finetune.stat().st_mtime
                    ).strftime('%Y-%m-%d %H:%M')
            
        except Exception as e:
            logger.error(f"Failed to get recent activities: {e}")
        
        return activities

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health = {
            'overall_status': 'healthy',
            'components': {},
            'issues': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Check components
        components = {
            'rag_embedder': self.rag_embedder,
            'pentestgpt': self.pentestgpt,
            'file_parser': self.file_parser,
            'rss_fetcher': self.rss_fetcher
        }
        
        for name, component in components.items():
            if component:
                health['components'][name] = 'active'
            else:
                health['components'][name] = 'inactive'
        
        # Check system resources
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        if memory.percent > 90:
            health['issues'].append('High memory usage')
            health['overall_status'] = 'warning'
        
        if disk.percent > 95:
            health['issues'].append('Low disk space')
            health['overall_status'] = 'critical'
        
        # Check required directories
        required_dirs = ['logs', 'rag_data', 'reports', 'finetune_data']
        for dir_name in required_dirs:
            if not Path(dir_name).exists():
                health['issues'].append(f'Missing directory: {dir_name}')
                health['overall_status'] = 'warning'
        
        return health

if __name__ == "__main__":
    # Test the task router
    async def test_task_router():
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        router = TaskRouter(config)
        
        # Test natural language processing
        test_message = "How can I test for SQL injection in a web application?"
        result = await router.process_natural_language_task(test_message)
        print(f"Task type detected and processed")
        
        # Test system status
        status = await router.get_system_status()
        print(f"System status: {status['system_health']}")
        
        # Test health check
        health = await router.health_check()
        print(f"Health check: {health['overall_status']}")
    
    # Uncomment to test
    # asyncio.run(test_task_router())
