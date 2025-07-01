#!/usr/bin/env python3
"""
Cybersecurity AI Agent Platform - System Health Monitor
Real-time monitoring and alerts for the platform
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import psutil
import yaml
from loguru import logger
from dotenv import load_dotenv

from shared_utils import ConfigManager, LoggerManager, DirectoryManager, SystemMetrics

class SystemHealthMonitor:
    """Comprehensive system health monitoring"""
    
    def __init__(self):
        self.config = ConfigManager.get_instance().config
        self.logger = LoggerManager.setup_logger('health_monitor')
        self.start_time = datetime.now()
        self.health_data = {}
        self.alert_thresholds = {
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'cpu_percent': 90.0,
            'response_time': 30.0,  # seconds
            'error_rate': 10.0      # errors per hour
        }
        
        # Setup monitoring directories
        DirectoryManager.ensure_directory("monitoring/health")
        
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics using shared utilities"""
        try:
            # Use shared SystemMetrics instead of direct psutil calls
            return SystemMetrics.get_system_metrics()
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            return {}
        
    async def check_component_health(self) -> Dict[str, Any]:
        """Check health of individual components"""
        components = {}
        
        try:
            # Check Telegram Bot
            components['telegram_bot'] = await self._check_telegram_health()
            
            # Check Gemini API
            components['gemini_api'] = await self._check_gemini_health()
            
            # Check RAG Database
            components['rag_database'] = await self._check_rag_health()
            
            # Check File System
            components['file_system'] = await self._check_filesystem_health()
            
            # Check Network Connectivity
            components['network'] = await self._check_network_health()
            
        except Exception as e:
            self.logger.error(f"Component health check failed: {e}")
            
        return components

    async def _check_telegram_health(self) -> Dict[str, Any]:
        """Check Telegram bot health"""
        try:
            # Check if bot token is configured
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            if not bot_token or bot_token.startswith('your_'):
                return {'status': 'error', 'message': 'Bot token not configured'}
            
            # Check bot process (simplified check)
            return {'status': 'healthy', 'message': 'Bot token configured'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def _check_gemini_health(self) -> Dict[str, Any]:
        """Check Gemini API health"""
        try:
            from shared_utils import GeminiClient
            gemini = GeminiClient()
            
            if not gemini.is_available:
                return {'status': 'error', 'message': 'Gemini API not configured'}
            
            # Test API connection
            test_result = await gemini.test_connection()
            return {
                'status': test_result.get('status', 'unknown'),
                'message': test_result.get('error', 'API accessible'),
                'response_time': test_result.get('response_time_ms', 0)
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def _check_rag_health(self) -> Dict[str, Any]:
        """Check RAG database health"""
        try:
            # Check if RAG data directory exists
            rag_dir = Path("rag_data")
            if not rag_dir.exists():
                return {'status': 'warning', 'message': 'RAG data directory missing'}
            
            # Check ChromaDB files
            chroma_dir = rag_dir / "chroma_db"
            if chroma_dir.exists():
                return {'status': 'healthy', 'message': 'RAG database accessible'}
            else:
                return {'status': 'warning', 'message': 'ChromaDB not initialized'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def _check_filesystem_health(self) -> Dict[str, Any]:
        """Check file system health"""
        try:
            # Check required directories
            required_dirs = ['logs', 'rag_data', 'reports', 'temp']
            missing_dirs = []
            
            for dir_name in required_dirs:
                if not Path(dir_name).exists():
                    missing_dirs.append(dir_name)
            
            if missing_dirs:
                return {
                    'status': 'warning',
                    'message': f'Missing directories: {", ".join(missing_dirs)}'
                }
            
            return {'status': 'healthy', 'message': 'All directories present'}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def _check_network_health(self) -> Dict[str, Any]:
        """Check network connectivity"""
        try:
            import socket
            
            # Test DNS resolution
            socket.gethostbyname('google.com')
            
            # Test HTTPS connectivity
            import urllib.request
            with urllib.request.urlopen('https://www.google.com', timeout=5) as response:
                if response.status == 200:
                    return {'status': 'healthy', 'message': 'Network connectivity OK'}
                    
        except Exception as e:
            return {'status': 'error', 'message': f'Network issue: {str(e)}'}

    async def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        self.logger.info("Generating health report...")
        
        try:
            # Collect all metrics
            system_metrics = await self.get_system_metrics()
            component_health = await self.check_component_health()
            
            # Calculate uptime
            uptime = datetime.now() - self.start_time
            
            # Generate alerts
            alerts = self._generate_alerts(system_metrics, component_health)
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': int(uptime.total_seconds()),
                'system_metrics': system_metrics,
                'component_health': component_health,
                'alerts': alerts,
                'overall_status': self._calculate_overall_status(component_health, alerts)
            }
            
            # Save report
            await self._save_health_report(report)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate health report: {e}")
            return {'error': str(e)}

    def _generate_alerts(self, system_metrics: Dict, component_health: Dict) -> List[Dict]:
        """Generate alerts based on thresholds"""
        alerts = []
        
        try:
            # Memory usage alert
            memory_percent = system_metrics.get('memory', {}).get('percent', 0)
            if memory_percent > self.alert_thresholds['memory_percent']:
                alerts.append({
                    'type': 'memory',
                    'severity': 'warning',
                    'message': f'High memory usage: {memory_percent:.1f}%',
                    'threshold': self.alert_thresholds['memory_percent']
                })
            
            # Disk usage alert
            disk_percent = system_metrics.get('disk', {}).get('percent', 0)
            if disk_percent > self.alert_thresholds['disk_percent']:
                alerts.append({
                    'type': 'disk',
                    'severity': 'warning',
                    'message': f'High disk usage: {disk_percent:.1f}%',
                    'threshold': self.alert_thresholds['disk_percent']
                })
            
            # CPU usage alert
            cpu_percent = system_metrics.get('cpu', {}).get('percent', 0)
            if cpu_percent > self.alert_thresholds['cpu_percent']:
                alerts.append({
                    'type': 'cpu',
                    'severity': 'warning',
                    'message': f'High CPU usage: {cpu_percent:.1f}%',
                    'threshold': self.alert_thresholds['cpu_percent']
                })
            
            # Component health alerts
            for component, health in component_health.items():
                if health.get('status') == 'error':
                    alerts.append({
                        'type': 'component',
                        'severity': 'error',
                        'message': f'{component}: {health.get("message", "Unknown error")}',
                        'component': component
                    })
                elif health.get('status') == 'warning':
                    alerts.append({
                        'type': 'component',
                        'severity': 'warning',
                        'message': f'{component}: {health.get("message", "Warning")}',
                        'component': component
                    })
                    
        except Exception as e:
            self.logger.error(f"Failed to generate alerts: {e}")
            
        return alerts

    def _calculate_overall_status(self, component_health: Dict, alerts: List) -> str:
        """Calculate overall system status"""
        try:
            # Check for critical errors
            error_alerts = [a for a in alerts if a.get('severity') == 'error']
            if error_alerts:
                return 'critical'
            
            # Check for warnings
            warning_alerts = [a for a in alerts if a.get('severity') == 'warning']
            if warning_alerts:
                return 'warning'
            
            # Check component health
            error_components = [c for c, h in component_health.items() if h.get('status') == 'error']
            if error_components:
                return 'degraded'
            
            return 'healthy'
            
        except Exception as e:
            self.logger.error(f"Failed to calculate overall status: {e}")
            return 'unknown'

    async def _save_health_report(self, report: Dict[str, Any]):
        """Save health report to file"""
        try:
            health_dir = Path("monitoring/health")
            health_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = health_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"Health report saved: {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to save health report: {e}")

    async def start_monitoring(self, interval: int = 300):
        """Start continuous health monitoring"""
        self.logger.info(f"Starting health monitoring (interval: {interval}s)")
        
        while True:
            try:
                await self.generate_health_report()
                await asyncio.sleep(interval)
            except KeyboardInterrupt:
                self.logger.info("Health monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

async def main():
    """Main function for standalone health monitoring"""
    monitor = SystemHealthMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        await monitor.start_monitoring()
    else:
        # Generate single report
        report = await monitor.generate_health_report()
        print(json.dumps(report, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())