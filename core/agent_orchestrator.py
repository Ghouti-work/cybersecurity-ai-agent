#!/usr/bin/env python3
"""
Unified Agent Orchestrator
Coordinates between custom agents, CAI, and PentestGPT
"""

import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

# Add integrations to path
sys.path.append(str(Path(__file__).parent.parent / "integrations"))
sys.path.append(str(Path(__file__).parent.parent / "agents"))

from shared_utils import ConfigManager, LoggerManager
from cai_integration import CAIIntegration
from pentestgpt_integration import PentestGPTIntegration

class AgentOrchestrator:
    """Orchestrates between all available AI frameworks and custom agents"""
    
    def __init__(self):
        self.config = ConfigManager.get_instance().config
        self.logger = LoggerManager.setup_logger('orchestrator')
        
        # Initialize framework integrations
        self.cai = CAIIntegration()
        self.pentestgpt = PentestGPTIntegration()
        
        # Initialize custom agents
        self.custom_agents = self._initialize_custom_agents()
        
        self.logger.info("🎭 Agent Orchestrator initialized")
    
    def _initialize_custom_agents(self) -> Dict[str, Any]:
        """Initialize custom agent instances"""
        agents = {}
        
        try:
            # Import custom agents
            from rag_embedder import RAGEmbedder
            from rss_fetcher import RSSFetcher
            from file_parser import FileParser
            from report_generator import ReportGenerator
            from pentestgpt_gemini import PentestGPT
            
            agents['rag'] = RAGEmbedder(self.config)
            agents['rss'] = RSSFetcher(self.config)
            agents['file_parser'] = FileParser(self.config)
            agents['report_generator'] = ReportGenerator(self.config)
            agents['pentestgpt_gemini'] = PentestGPT(self.config)
            
            self.logger.info("✅ Custom agents initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize custom agents: {e}")
            
        return agents
    
    async def route_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Intelligently route tasks to the best-suited agent framework"""
        task_lower = task.lower()
        context = context or {}
        
        # Determine task type and route accordingly
        if self._is_penetration_testing_task(task_lower):
            return await self._route_pentest_task(task, context)
        elif self._is_intelligence_gathering_task(task_lower):
            return await self._route_intelligence_task(task, context)
        elif self._is_analysis_task(task_lower):
            return await self._route_analysis_task(task, context)
        else:
            return await self._route_general_task(task, context)
    
    def _is_penetration_testing_task(self, task: str) -> bool:
        """Check if task is penetration testing related"""
        pentest_keywords = ['scan', 'exploit', 'vulnerability', 'pentest', 'hack', 'attack', 'payload']
        return any(keyword in task for keyword in pentest_keywords)
    
    def _is_intelligence_gathering_task(self, task: str) -> bool:
        """Check if task is intelligence gathering related"""
        intel_keywords = ['rss', 'news', 'feed', 'cve', 'threat', 'intelligence', 'osint']
        return any(keyword in task for keyword in intel_keywords)
    
    def _is_analysis_task(self, task: str) -> bool:
        """Check if task is analysis related"""
        analysis_keywords = ['analyze', 'file', 'document', 'report', 'parse', 'extract']
        return any(keyword in task for keyword in analysis_keywords)
    
    async def _route_pentest_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Route penetration testing tasks"""
        results = {}
        
        # Try CAI first for tool execution
        if 'target' in context:
            self.logger.info("Routing to CAI for tool execution...")
            cai_result = await self.cai.run_cai_agent("reconnaissance", task, context)
            results['cai_execution'] = cai_result
        
        # Use PentestGPT for strategic reasoning
        if 'target' in context:
            self.logger.info("Routing to PentestGPT for strategic analysis...")
            pentestgpt_result = await self.pentestgpt.run_pentestgpt_session(context['target'])
            results['pentestgpt_analysis'] = pentestgpt_result
        
        # Use custom PentestGPT Gemini for additional insights
        if 'pentestgpt_gemini' in self.custom_agents:
            self.logger.info("Adding Gemini-based analysis...")
            gemini_result = await self.custom_agents['pentestgpt_gemini'].analyze_security_scenario(task)
            results['gemini_insights'] = gemini_result
        
        return self._combine_results(results, 'penetration_testing')
    
    async def _route_intelligence_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Route intelligence gathering tasks"""
        results = {}
        
        # Use RSS fetcher for threat intelligence
        if 'rss' in self.custom_agents:
            self.logger.info("Gathering RSS intelligence...")
            rss_result = await self.custom_agents['rss'].fetch_and_process_feeds()
            results['rss_intelligence'] = rss_result
        
        # Use RAG for knowledge base queries
        if 'rag' in self.custom_agents and 'query' in context:
            self.logger.info("Querying knowledge base...")
            rag_result = await self.custom_agents['rag'].search_knowledge_base(context['query'])
            results['knowledge_base'] = rag_result
        
        return self._combine_results(results, 'intelligence_gathering')
    
    async def _route_analysis_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Route analysis tasks"""
        results = {}
        
        # Use file parser for document analysis
        if 'file_parser' in self.custom_agents and 'file_path' in context:
            self.logger.info("Analyzing file...")
            file_result = await self.custom_agents['file_parser'].parse_file(context['file_path'])
            results['file_analysis'] = file_result
        
        # Use report generator for report creation
        if 'report' in task.lower() and 'report_generator' in self.custom_agents:
            self.logger.info("Generating report...")
            report_result = await self.custom_agents['report_generator'].generate_report()
            results['report'] = report_result
        
        return self._combine_results(results, 'analysis')
    
    async def _route_general_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Route general tasks"""
        # Default to Gemini-based analysis
        if 'pentestgpt_gemini' in self.custom_agents:
            self.logger.info("Using Gemini for general analysis...")
            result = await self.custom_agents['pentestgpt_gemini'].analyze_security_scenario(task)
            return {'general_analysis': result, 'task_type': 'general'}
        
        return {'error': 'No suitable agent available for general task'}
    
    def _combine_results(self, results: Dict[str, Any], task_type: str) -> Dict[str, Any]:
        """Combine results from multiple agents"""
        return {
            'task_type': task_type,
            'timestamp': asyncio.get_event_loop().time(),
            'results': results,
            'summary': f"Combined results from {len(results)} agents"
        }

# Example usage
async def main():
    orchestrator = AgentOrchestrator()
    
    # Example penetration testing task
    pentest_result = await orchestrator.route_task(
        "scan target for vulnerabilities", 
        {'target': 'example.com'}
    )
    print("Pentest Result:", pentest_result)
    
    # Example intelligence gathering task
    intel_result = await orchestrator.route_task(
        "gather threat intelligence from RSS feeds",
        {}
    )
    print("Intel Result:", intel_result)

if __name__ == "__main__":
    asyncio.run(main())
