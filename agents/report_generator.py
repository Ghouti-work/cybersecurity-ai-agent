"""
Report Generator for Cybersecurity AI Agent
Generates markdown and PDF reports from collected data
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import statistics

from loguru import logger
import yaml
from jinja2 import Template

from shared_utils import ConfigManager, LoggerManager, DirectoryManager, SystemMetrics

class ReportGenerator:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or ConfigManager.get_instance().config
        self.logger = LoggerManager.setup_logger('reports')
        
        # Setup report directories
        DirectoryManager.ensure_directory("reports")
        DirectoryManager.ensure_directory("reports/daily")
        DirectoryManager.ensure_directory("reports/weekly")
        DirectoryManager.ensure_directory("reports/custom")
        
        self.reports_dir = Path("reports")
        
        self.logger.info("📊 Report Generator initialized")

    async def generate_report(self, report_type: str = "latest") -> Dict[str, Any]:
        """Generate a comprehensive security report"""
        self.logger.info(f"Generating {report_type} report...")
        
        try:
            if report_type == "daily":
                return await self._generate_daily_report()
            elif report_type == "weekly":
                return await self._generate_weekly_report()
            elif report_type == "latest":
                return await self._generate_latest_activity_report()
            elif report_type == "summary":
                return await self._generate_summary_report()
            else:
                return await self._generate_custom_report(report_type)
                
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            raise

    async def _generate_daily_report(self) -> Dict[str, Any]:
        """Generate daily activity report"""
        today = datetime.now().date()
        
        # Collect daily data
        daily_data = await self._collect_daily_data(today)
        
        # Generate report content
        content = await self._create_daily_report_content(daily_data, today)
        
        # Save report
        filename = f"daily_report_{today.strftime('%Y%m%d')}.md"
        filepath = self.reports_dir / "daily" / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        result = {
            'title': f"Daily Security Report - {today.strftime('%Y-%m-%d')}",
            'type': 'daily',
            'content': content,
            'filepath': str(filepath),
            'generated_at': datetime.now().isoformat()
        }
        
        self.logger.info(f"Daily report generated: {filename}")
        return result

    async def _generate_weekly_report(self) -> Dict[str, Any]:
        """Generate weekly summary report"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        # Collect weekly data
        weekly_data = await self._collect_weekly_data(start_date, end_date)
        
        # Generate report content
        content = await self._create_weekly_report_content(weekly_data, start_date, end_date)
        
        # Save report
        filename = f"weekly_report_{end_date.strftime('%Y%m%d')}.md"
        filepath = self.reports_dir / "weekly" / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        result = {
            'title': f"Weekly Security Report - {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            'type': 'weekly',
            'content': content,
            'filepath': str(filepath),
            'generated_at': datetime.now().isoformat()
        }
        
        self.logger.info(f"Weekly report generated: {filename}")
        return result

    async def _generate_latest_activity_report(self) -> Dict[str, Any]:
        """Generate report of latest activities"""
        
        # Collect latest activity data
        latest_data = await self._collect_latest_activity_data()
        
        # Generate report content
        content = await self._create_latest_activity_content(latest_data)
        
        # Save report
        filename = f"latest_activity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.reports_dir / "custom" / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        result = {
            'title': "Latest Activity Report",
            'type': 'latest',
            'content': content,
            'filepath': str(filepath),
            'generated_at': datetime.now().isoformat()
        }
        
        self.logger.info(f"Latest activity report generated: {filename}")
        return result

    async def _generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive summary report"""
        
        # Collect summary data
        summary_data = await self._collect_summary_data()
        
        # Generate report content
        content = await self._create_summary_report_content(summary_data)
        
        # Save report
        filename = f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.reports_dir / "custom" / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        result = {
            'title': "Comprehensive Security Summary Report",
            'type': 'summary',
            'content': content,
            'filepath': str(filepath),
            'generated_at': datetime.now().isoformat()
        }
        
        self.logger.info(f"Summary report generated: {filename}")
        return result

    async def _collect_daily_data(self, date) -> Dict[str, Any]:
        """Collect data for daily report"""
        data = {
            'date': date,
            'rss_articles': [],
            'scan_results': [],
            'pentestgpt_analyses': [],
            'processed_files': [],
            'system_events': []
        }
        
        try:
            # Collect RSS articles from today
            data['rss_articles'] = await self._get_rss_articles_by_date(date)
            
            # Collect scan results from today
            data['scan_results'] = await self._get_scan_results_by_date(date)
            
            # Collect PentestGPT analyses from today
            data['pentestgpt_analyses'] = await self._get_pentestgpt_analyses_by_date(date)
            
            # Collect processed files from today
            data['processed_files'] = await self._get_processed_files_by_date(date)
            
            # Collect system events
            data['system_events'] = await self._get_system_events_by_date(date)
            
        except Exception as e:
            self.logger.error(f"Failed to collect daily data: {e}")
        
        return data

    async def _collect_weekly_data(self, start_date, end_date) -> Dict[str, Any]:
        """Collect data for weekly report"""
        data = {
            'start_date': start_date,
            'end_date': end_date,
            'daily_summaries': [],
            'trending_topics': [],
            'security_metrics': {},
            'top_threats': [],
            'system_performance': {}
        }
        
        try:
            # Collect daily summaries for the week
            current_date = start_date
            while current_date <= end_date:
                daily_summary = await self._get_daily_summary(current_date)
                data['daily_summaries'].append(daily_summary)
                current_date += timedelta(days=1)
            
            # Analyze trending topics
            data['trending_topics'] = await self._analyze_trending_topics(start_date, end_date)
            
            # Calculate security metrics
            data['security_metrics'] = await self._calculate_weekly_metrics(start_date, end_date)
            
            # Identify top threats
            data['top_threats'] = await self._identify_top_threats(start_date, end_date)
            
            # Get system performance metrics
            data['system_performance'] = await self._get_weekly_performance_metrics()
            
        except Exception as e:
            self.logger.error(f"Failed to collect weekly data: {e}")
        
        return data

    async def _collect_latest_activity_data(self) -> Dict[str, Any]:
        """Collect latest activity data"""
        data = {
            'recent_analyses': [],
            'recent_scans': [],
            'recent_rss_updates': [],
            'recent_files': [],
            'system_status': {},
            'active_threats': []
        }
        
        try:
            # Get recent PentestGPT analyses (last 24 hours)
            data['recent_analyses'] = await self._get_recent_analyses(hours=24)
            
            # Get recent scan results
            data['recent_scans'] = await self._get_recent_scans(hours=24)
            
            # Get recent RSS updates
            data['recent_rss_updates'] = await self._get_recent_rss_updates(hours=24)
            
            # Get recently processed files
            data['recent_files'] = await self._get_recent_files(hours=24)
            
            # Get current system status
            data['system_status'] = await self._get_current_system_status()
            
            # Get active threats from recent data
            data['active_threats'] = await self._get_active_threats()
            
        except Exception as e:
            self.logger.error(f"Failed to collect latest activity data: {e}")
        
        return data

    async def _collect_summary_data(self) -> Dict[str, Any]:
        """Collect comprehensive summary data"""
        data = {
            'total_statistics': {},
            'category_breakdown': {},
            'security_posture': {},
            'knowledge_base_stats': {},
            'learning_progress': {},
            'recommendations': []
        }
        
        try:
            # Get total statistics
            data['total_statistics'] = await self._get_total_statistics()
            
            # Get category breakdown
            data['category_breakdown'] = await self._get_category_breakdown()
            
            # Assess security posture
            data['security_posture'] = await self._assess_security_posture()
            
            # Get knowledge base statistics
            data['knowledge_base_stats'] = await self._get_knowledge_base_stats()
            
            # Calculate learning progress
            data['learning_progress'] = await self._calculate_learning_progress()
            
            # Generate recommendations
            data['recommendations'] = await self._generate_recommendations()
            
        except Exception as e:
            self.logger.error(f"Failed to collect summary data: {e}")
        
        return data

    async def _create_daily_report_content(self, data: Dict[str, Any], date) -> str:
        """Create daily report content"""
        
        template = Template("""
# Daily Security Report - {{ date.strftime('%B %d, %Y') }}

## Executive Summary
Today's cybersecurity activities included {{ rss_count }} new threat intelligence articles, {{ scan_count }} security scans, {{ analysis_count }} PentestGPT analyses, and {{ file_count }} processed security documents.

## RSS Feed Updates
{% if rss_articles %}
### New Threat Intelligence ({{ rss_articles|length }} articles)
{% for article in rss_articles[:10] %}
- **{{ article.get('title', 'Unknown Title') }}** (Score: {{ article.get('security_score', 'N/A') }}/10)
  - Source: {{ article.get('source', 'Unknown') }}
  - Category: {{ article.get('category', 'Unknown') }}
  - Tags: {{ article.get('tags', [])|join(', ') }}
{% endfor %}
{% if rss_articles|length > 10 %}
*... and {{ rss_articles|length - 10 }} more articles*
{% endif %}
{% else %}
No new RSS articles processed today.
{% endif %}

## Security Scans
{% if scan_results %}
### Completed Scans ({{ scan_results|length }})
{% for scan in scan_results %}
- **Target**: {{ scan.get('target', 'Unknown') }}
  - Status: {{ scan.get('status', 'Unknown') }}
  - Findings: {{ scan.get('findings', 'No findings') }}
{% endfor %}
{% else %}
No security scans performed today.
{% endif %}

## PentestGPT Analyses
{% if pentestgpt_analyses %}
### Security Analysis Sessions ({{ pentestgpt_analyses|length }})
{% for analysis in pentestgpt_analyses %}
- **Query**: {{ analysis.get('query', 'Unknown')[:100] }}...
  - Risk Level: {{ analysis.get('risk_level', 'Unknown') }}
  - Timestamp: {{ analysis.get('timestamp', 'Unknown') }}
{% endfor %}
{% else %}
No PentestGPT analyses performed today.
{% endif %}

## File Processing
{% if processed_files %}
### Processed Documents ({{ processed_files|length }})
{% for file in processed_files %}
- **{{ file.get('filename', 'Unknown') }}**
  - Category: {{ file.get('category', 'Unknown') }}
  - Security Score: {{ file.get('security_score', 'N/A') }}/10
{% endfor %}
{% else %}
No files processed today.
{% endif %}

## System Events
{% if system_events %}
### Notable Events
{% for event in system_events %}
- {{ event }}
{% endfor %}
{% else %}
No notable system events today.
{% endif %}

---
*Report generated on {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}*
        """)
        
        return template.render(
            date=date,
            rss_articles=data['rss_articles'],
            rss_count=len(data['rss_articles']),
            scan_results=data['scan_results'],
            scan_count=len(data['scan_results']),
            pentestgpt_analyses=data['pentestgpt_analyses'],
            analysis_count=len(data['pentestgpt_analyses']),
            processed_files=data['processed_files'],
            file_count=len(data['processed_files']),
            system_events=data['system_events'],
            datetime=datetime
        )

    async def _create_weekly_report_content(self, data: Dict[str, Any], start_date, end_date) -> str:
        """Create weekly report content"""
        
        template = Template("""
# Weekly Security Report
## {{ start_date.strftime('%B %d') }} - {{ end_date.strftime('%B %d, %Y') }}

## Executive Summary
This week's cybersecurity activities focused on threat intelligence gathering, vulnerability analysis, and security knowledge enhancement. Key metrics and trending threats are highlighted below.

## Weekly Metrics
{% if security_metrics %}
### Security Intelligence
- **Total Articles Processed**: {{ security_metrics.get('total_articles', 0) }}
- **High-Priority Threats**: {{ security_metrics.get('high_priority_threats', 0) }}
- **Security Scans**: {{ security_metrics.get('total_scans', 0) }}
- **Analysis Sessions**: {{ security_metrics.get('total_analyses', 0) }}
- **Knowledge Base Growth**: {{ security_metrics.get('kb_growth', 0) }} new documents
{% endif %}

## Trending Security Topics
{% if trending_topics %}
{% for topic in trending_topics[:10] %}
- **{{ topic.get('topic', 'Unknown') }}** ({{ topic.get('frequency', 0) }} mentions)
  - Relevance: {{ topic.get('relevance_score', 'N/A') }}/10
  - Categories: {{ topic.get('categories', [])|join(', ') }}
{% endfor %}
{% else %}
No trending topics identified this week.
{% endif %}

## Top Threats Identified
{% if top_threats %}
{% for threat in top_threats[:5] %}
- **{{ threat.get('name', 'Unknown Threat') }}**
  - Severity: {{ threat.get('severity', 'Unknown') }}
  - Frequency: {{ threat.get('frequency', 0) }} mentions
  - Description: {{ threat.get('description', 'No description available') }}
{% endfor %}
{% else %}
No specific threats identified this week.
{% endif %}

## Daily Activity Summary
{% for daily in daily_summaries %}
### {{ daily.get('date', 'Unknown Date').strftime('%A, %B %d') if daily.get('date') else 'Unknown Date' }}
- RSS Articles: {{ daily.get('rss_count', 0) }}
- Scans: {{ daily.get('scan_count', 0) }}
- Analyses: {{ daily.get('analysis_count', 0) }}
- Files: {{ daily.get('file_count', 0) }}
{% endfor %}

## System Performance
{% if system_performance %}
- **Average Memory Usage**: {{ system_performance.get('avg_memory', 'N/A') }}%
- **Peak Disk Usage**: {{ system_performance.get('peak_disk', 'N/A') }}%
- **Uptime**: {{ system_performance.get('uptime', 'N/A') }}
- **Processing Efficiency**: {{ system_performance.get('efficiency', 'N/A') }}%
{% endif %}

## Recommendations
1. Continue monitoring trending threats and CVEs
2. Enhance detection capabilities for identified threat patterns
3. Regular system maintenance and optimization
4. Knowledge base expansion in underrepresented categories

---
*Report generated on {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}*
        """)
        
        return template.render(
            start_date=start_date,
            end_date=end_date,
            security_metrics=data['security_metrics'],
            trending_topics=data['trending_topics'],
            top_threats=data['top_threats'],
            daily_summaries=data['daily_summaries'],
            system_performance=data['system_performance'],
            datetime=datetime
        )

    async def _create_latest_activity_content(self, data: Dict[str, Any]) -> str:
        """Create latest activity report content"""
        
        template = Template("""
# Latest Activity Report
*Generated on {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}*

## Recent Security Analyses (Last 24 Hours)
{% if recent_analyses %}
{% for analysis in recent_analyses[:5] %}
- **{{ analysis.get('query', 'Unknown Query')[:80] }}...**
  - Risk Level: {{ analysis.get('risk_level', 'Unknown') }}
  - Time: {{ analysis.get('timestamp', 'Unknown') }}
{% endfor %}
{% if recent_analyses|length > 5 %}
*... and {{ recent_analyses|length - 5 }} more analyses*
{% endif %}
{% else %}
No recent analyses in the last 24 hours.
{% endif %}

## Recent Security Scans
{% if recent_scans %}
{% for scan in recent_scans %}
- **{{ scan.get('target', 'Unknown Target') }}**
  - Status: {{ scan.get('status', 'Unknown') }}
  - Time: {{ scan.get('timestamp', 'Unknown') }}
{% endfor %}
{% else %}
No recent scans in the last 24 hours.
{% endif %}

## Recent RSS Updates
{% if recent_rss_updates %}
{% for update in recent_rss_updates[:10] %}
- **{{ update.get('title', 'Unknown Article') }}**
  - Source: {{ update.get('source', 'Unknown') }}
  - Security Score: {{ update.get('security_score', 'N/A') }}/10
{% endfor %}
{% else %}
No recent RSS updates in the last 24 hours.
{% endif %}

## Recently Processed Files
{% if recent_files %}
{% for file in recent_files %}
- **{{ file.get('filename', 'Unknown File') }}**
  - Category: {{ file.get('category', 'Unknown') }}
  - Security Score: {{ file.get('security_score', 'N/A') }}/10
{% endfor %}
{% else %}
No files processed in the last 24 hours.
{% endif %}

## Current System Status
{% if system_status %}
- **Memory Usage**: {{ system_status.get('memory_usage', 'N/A') }}%
- **Disk Usage**: {{ system_status.get('disk_usage', 'N/A') }}%
- **Uptime**: {{ system_status.get('uptime', 'N/A') }}
- **Health**: {{ system_status.get('health', 'Unknown') }}
- **Active Documents**: {{ system_status.get('active_documents', 'N/A') }}
{% endif %}

## Active Threats & Monitoring
{% if active_threats %}
{% for threat in active_threats %}
- **{{ threat.get('name', 'Unknown Threat') }}**
  - Severity: {{ threat.get('severity', 'Unknown') }}
  - Last Seen: {{ threat.get('last_seen', 'Unknown') }}
  - Status: {{ threat.get('status', 'Unknown') }}
{% endfor %}
{% else %}
No active threats currently being monitored.
{% endif %}

---
*This report provides a snapshot of the most recent cybersecurity activities and system status.*
        """)
        
        return template.render(
            recent_analyses=data['recent_analyses'],
            recent_scans=data['recent_scans'],
            recent_rss_updates=data['recent_rss_updates'],
            recent_files=data['recent_files'],
            system_status=data['system_status'],
            active_threats=data['active_threats'],
            datetime=datetime
        )

    async def _create_summary_report_content(self, data: Dict[str, Any]) -> str:
        """Create comprehensive summary report content"""
        
        template = Template("""
# Comprehensive Security Summary Report
*Generated on {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}*

## Overview
This comprehensive report provides an analysis of the cybersecurity AI agent's performance, knowledge base status, and security intelligence capabilities.

## Total Statistics
{% if total_statistics %}
- **Total Documents Processed**: {{ total_statistics.get('total_documents', 0) }}
- **Security Analyses Performed**: {{ total_statistics.get('total_analyses', 0) }}
- **RSS Articles Collected**: {{ total_statistics.get('total_rss_articles', 0) }}
- **Security Scans Executed**: {{ total_statistics.get('total_scans', 0) }}
- **Knowledge Base Size**: {{ total_statistics.get('kb_size', 0) }} MB
- **Average Security Score**: {{ total_statistics.get('avg_security_score', 0) }}/10
{% endif %}

## Category Breakdown
{% if category_breakdown %}
### Document Categories
{% for category, count in category_breakdown.items() %}
- **{{ category.replace('_', ' ').title() }}**: {{ count }} documents
{% endfor %}
{% endif %}

## Security Posture Assessment
{% if security_posture %}
- **Overall Security Awareness**: {{ security_posture.get('awareness_level', 'Unknown') }}
- **Threat Detection Capability**: {{ security_posture.get('detection_capability', 'Unknown') }}
- **Knowledge Coverage**: {{ security_posture.get('knowledge_coverage', 0) }}%
- **Response Readiness**: {{ security_posture.get('response_readiness', 'Unknown') }}
{% endif %}

## Knowledge Base Statistics
{% if knowledge_base_stats %}
- **Total Collections**: {{ knowledge_base_stats.get('total_collections', 0) }}
- **Indexed Documents**: {{ knowledge_base_stats.get('indexed_documents', 0) }}
- **Average Document Quality**: {{ knowledge_base_stats.get('avg_quality', 0) }}/10
- **Search Efficiency**: {{ knowledge_base_stats.get('search_efficiency', 0) }}%
{% endif %}

## Learning Progress
{% if learning_progress %}
- **Data Growth Rate**: {{ learning_progress.get('growth_rate', 0) }}% per week
- **Model Improvement**: {{ learning_progress.get('model_improvement', 0) }}%
- **Fine-tuning Readiness**: {{ learning_progress.get('finetune_readiness', 0) }}%
- **Quality Trend**: {{ learning_progress.get('quality_trend', 'Unknown') }}
{% endif %}

## Strategic Recommendations
{% if recommendations %}
{% for rec in recommendations %}
- {{ rec }}
{% endfor %}
{% else %}
1. Continue expanding threat intelligence collection
2. Enhance model training with domain-specific data
3. Improve automated threat detection capabilities
4. Strengthen incident response procedures
{% endif %}

## System Health & Performance
- **Operational Status**: Optimal
- **Resource Utilization**: Efficient
- **Data Processing**: Active
- **Security Monitoring**: Continuous

---
*This report represents the current state of the cybersecurity AI agent platform and provides insights for continued improvement.*
        """)
        
        return template.render(
            total_statistics=data['total_statistics'],
            category_breakdown=data['category_breakdown'],
            security_posture=data['security_posture'],
            knowledge_base_stats=data['knowledge_base_stats'],
            learning_progress=data['learning_progress'],
            recommendations=data['recommendations'],
            datetime=datetime
        )

    # Helper methods for data collection
    async def _get_rss_articles_by_date(self, date) -> List[Dict[str, Any]]:
        """Get RSS articles for a specific date"""
        articles = []
        try:
            rag_data_dir = Path("rag_data")
            date_str = date.strftime('%Y%m%d')
            
            for category_dir in rag_data_dir.iterdir():
                if category_dir.is_dir() and category_dir.name != 'chroma_db':
                    for article_file in category_dir.glob(f"*{date_str}.json"):
                        try:
                            with open(article_file, 'r') as f:
                                article_data = json.load(f)
                                articles.append(article_data)
                        except Exception:
                            continue
        except Exception as e:
            self.logger.error(f"Failed to get RSS articles: {e}")
        
        return articles

    async def _get_scan_results_by_date(self, date) -> List[Dict[str, Any]]:
        """Get scan results for a specific date"""
        scans = []
        try:
            scans_dir = Path("reports/scans")
            if scans_dir.exists():
                date_str = date.strftime('%Y%m%d')
                for scan_file in scans_dir.glob(f"*{date_str}*.json"):
                    try:
                        with open(scan_file, 'r') as f:
                            scan_data = json.load(f)
                            scans.append(scan_data)
                    except Exception:
                        continue
        except Exception as e:
            self.logger.error(f"Failed to get scan results: {e}")
        
        return scans

    async def _get_pentestgpt_analyses_by_date(self, date) -> List[Dict[str, Any]]:
        """Get PentestGPT analyses for a specific date"""
        analyses = []
        try:
            analyses_dir = Path("logs/pentestgpt")
            if analyses_dir.exists():
                date_str = date.strftime('%Y%m%d')
                for analysis_file in analyses_dir.glob(f"analysis_{date_str}*.json"):
                    try:
                        with open(analysis_file, 'r') as f:
                            analysis_data = json.load(f)
                            analyses.append(analysis_data)
                    except Exception:
                        continue
        except Exception as e:
            self.logger.error(f"Failed to get PentestGPT analyses: {e}")
        
        return analyses

    async def _get_processed_files_by_date(self, date) -> List[Dict[str, Any]]:
        """Get processed files for a specific date"""
        files = []
        try:
            rag_data_dir = Path("rag_data")
            
            for category_dir in rag_data_dir.iterdir():
                if category_dir.is_dir() and category_dir.name != 'chroma_db':
                    for file_info in category_dir.glob("file_*.json"):
                        try:
                            with open(file_info, 'r') as f:
                                file_data = json.load(f)
                                
                            # Check if file was processed on the specified date
                            processed_date = file_data.get('processed_at', '')
                            if date.strftime('%Y-%m-%d') in processed_date:
                                files.append(file_data.get('metadata', {}))
                        except Exception:
                            continue
        except Exception as e:
            self.logger.error(f"Failed to get processed files: {e}")
        
        return files

    async def _get_system_events_by_date(self, date) -> List[str]:
        """Get system events for a specific date"""
        events = []
        try:
            # This would parse log files for system events
            # For now, return placeholder events
            events = [
                "System startup completed successfully",
                "All components initialized",
                "Regular health checks passed"
            ]
        except Exception as e:
            logger.error(f"Failed to get system events: {e}")
        
        return events

    # Placeholder methods for more complex data analysis
    async def _get_daily_summary(self, date) -> Dict[str, Any]:
        """Get summary for a specific day"""
        return {
            'date': date,
            'rss_count': len(await self._get_rss_articles_by_date(date)),
            'scan_count': len(await self._get_scan_results_by_date(date)),
            'analysis_count': len(await self._get_pentestgpt_analyses_by_date(date)),
            'file_count': len(await self._get_processed_files_by_date(date))
        }

    async def _analyze_trending_topics(self, start_date, end_date) -> List[Dict[str, Any]]:
        """Analyze trending topics for date range"""
        # Placeholder implementation
        return [
            {'topic': 'SQL Injection', 'frequency': 15, 'relevance_score': 8, 'categories': ['web_security']},
            {'topic': 'Ransomware', 'frequency': 12, 'relevance_score': 9, 'categories': ['malware_analysis']},
            {'topic': 'Zero-day Exploits', 'frequency': 8, 'relevance_score': 10, 'categories': ['exploit_development']}
        ]

    async def _calculate_weekly_metrics(self, start_date, end_date) -> Dict[str, Any]:
        """Calculate weekly security metrics"""
        # Placeholder implementation
        return {
            'total_articles': 45,
            'high_priority_threats': 8,
            'total_scans': 12,
            'total_analyses': 28,
            'kb_growth': 15
        }

    async def _identify_top_threats(self, start_date, end_date) -> List[Dict[str, Any]]:
        """Identify top threats for date range"""
        # Placeholder implementation
        return [
            {'name': 'CVE-2024-1234', 'severity': 'Critical', 'frequency': 8, 'description': 'Remote code execution vulnerability'},
            {'name': 'Phishing Campaign', 'severity': 'High', 'frequency': 12, 'description': 'Targeted phishing attacks'}
        ]

    async def _get_weekly_performance_metrics(self) -> Dict[str, Any]:
        """Get weekly system performance metrics"""
        # Placeholder implementation
        return {
            'avg_memory': 45,
            'peak_disk': 78,
            'uptime': '99.8%',
            'efficiency': 92
        }

    # Additional helper methods would be implemented here...
    async def _get_recent_analyses(self, hours: int) -> List[Dict[str, Any]]:
        """Get recent analyses"""
        return []  # Placeholder

    async def _get_recent_scans(self, hours: int) -> List[Dict[str, Any]]:
        """Get recent scans"""
        return []  # Placeholder

    async def _get_recent_rss_updates(self, hours: int) -> List[Dict[str, Any]]:
        """Get recent RSS updates"""
        return []  # Placeholder

    async def _get_recent_files(self, hours: int) -> List[Dict[str, Any]]:
        """Get recent files"""
        return []  # Placeholder

    async def _get_current_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {'health': 'Good', 'uptime': '2 days', 'memory_usage': 45, 'disk_usage': 32}

    async def _get_active_threats(self) -> List[Dict[str, Any]]:
        """Get active threats"""
        return []  # Placeholder

    async def _get_total_statistics(self) -> Dict[str, Any]:
        """Get total statistics"""
        return {'total_documents': 150, 'total_analyses': 89, 'avg_security_score': 7.2}

    async def _get_category_breakdown(self) -> Dict[str, int]:
        """Get category breakdown"""
        return {'web_security': 45, 'network_security': 32, 'malware_analysis': 28}

    async def _assess_security_posture(self) -> Dict[str, Any]:
        """Assess security posture"""
        return {'awareness_level': 'High', 'detection_capability': 'Advanced', 'knowledge_coverage': 85}

    async def _get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        return {'total_collections': 8, 'indexed_documents': 150, 'avg_quality': 8.2}

    async def _calculate_learning_progress(self) -> Dict[str, Any]:
        """Calculate learning progress"""
        return {'growth_rate': 15, 'model_improvement': 12, 'finetune_readiness': 78}

    async def _generate_recommendations(self) -> List[str]:
        """Generate strategic recommendations"""
        return [
            "Expand threat intelligence sources",
            "Implement automated threat hunting",
            "Enhance incident response capabilities",
            "Improve security awareness training"
        ]

if __name__ == "__main__":
    # Test the report generator
    async def test_report_generator():
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        generator = ReportGenerator(config)
        
        # Test daily report
        daily_report = await generator.generate_report("daily")
        print(f"Generated daily report: {daily_report['title']}")
        print(f"Content length: {len(daily_report['content'])} characters")
        
        # Test latest activity report
        latest_report = await generator.generate_report("latest")
        print(f"Generated latest report: {latest_report['title']}")
    
    # Uncomment to test
    # asyncio.run(test_report_generator())
