#!/usr/bin/env python3
"""
CAI Framework Integration Wrapper with Local RAG LLM Support
Provides unified interface to CAI framework components with local model integration
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add CAI to Python path
cai_path = Path(__file__).parent.parent / "CAI" / "src"
if cai_path.exists():
    sys.path.insert(0, str(cai_path))

from shared_utils import ConfigManager, LoggerManager
from local_llm_server import LocalLLMAPI

class CAIIntegration:
    """Integration wrapper for CAI framework with local RAG LLM"""
    
    def __init__(self):
        self.config = ConfigManager.get_instance().config
        self.logger = LoggerManager.setup_logger('cai_integration')
        self.cai_available = self._check_cai_availability()
        
        # Initialize local LLM for RAG
        self.local_llm = LocalLLMAPI(self.config)
        self.use_local_llm = self.config.get('cai', {}).get('use_local_llm', True)
        self.rag_enabled = self.config.get('cai', {}).get('rag_enabled', True)
        
        # RAG knowledge base
        self.knowledge_base = {}
        if self.rag_enabled:
            asyncio.create_task(self._initialize_rag_knowledge())
        
        self.logger.info("🤖 CAI Integration with Local RAG LLM initialized")
    
    def _check_cai_availability(self) -> bool:
        """Check if CAI framework is available"""
        try:
            import cai
            self.logger.info("✅ CAI framework available")
            return True
        except ImportError:
            self.logger.warning("⚠️ CAI framework not available")
            return False
    
    async def run_cai_agent(self, agent_type: str, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run CAI agent with RAG-enhanced local LLM support"""
        self.logger.info(f"🤖 Running CAI agent: {agent_type} for task: {task[:50]}...")
        
        try:
            # First, query RAG knowledge base for relevant information
            rag_response = await self.query_rag_knowledge(task, str(context) if context else "")
            
            # Enhance task with RAG knowledge
            enhanced_context = {
                **(context or {}),
                "rag_knowledge": rag_response.get("answer", ""),
                "knowledge_sources": rag_response.get("sources", []),
                "rag_confidence": rag_response.get("confidence", 0.0)
            }
            
            # Run appropriate agent based on type
            if agent_type == "reconnaissance":
                return await self._run_rag_enhanced_recon(task, enhanced_context)
            elif agent_type == "ctf":
                return await self._run_rag_enhanced_ctf(task, enhanced_context)
            elif agent_type == "vulnerability_assessment":
                return await self._run_rag_enhanced_vuln(task, enhanced_context)
            elif agent_type == "code_analysis":
                return await self._run_rag_enhanced_code_analysis(task, enhanced_context)
            elif agent_type == "threat_intelligence":
                return await self._run_rag_enhanced_threat_intel(task, enhanced_context)
            else:
                return await self._run_generic_rag_agent(agent_type, task, enhanced_context)
                
        except Exception as e:
            self.logger.error(f"❌ CAI agent execution failed: {e}")
            return {"error": str(e), "status": "failed"}

    async def _run_rag_enhanced_recon(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run reconnaissance agent with RAG enhancement"""
        try:
            # Prepare reconnaissance prompt with RAG knowledge
            prompt = f"""Cybersecurity Reconnaissance Task: {task}

Knowledge Base Context:
{context.get('rag_knowledge', 'No relevant knowledge found')}

Please provide a comprehensive reconnaissance approach including:
1. Information gathering techniques
2. Tools and commands to use
3. Potential attack vectors to explore
4. Risk assessment considerations
5. Next steps based on findings

Provide practical, actionable reconnaissance guidance."""
            
            # Use local LLM for analysis
            if self.use_local_llm and hasattr(self, 'local_llm'):
                messages = [{"role": "user", "content": prompt}]
                response = await self.local_llm.chat_completion(messages)
                
                if 'error' not in response:
                    return {
                        "status": "completed",
                        "type": "reconnaissance",
                        "analysis": response['choices'][0]['message']['content'],
                        "rag_enhanced": True,
                        "knowledge_sources": context.get('knowledge_sources', []),
                        "confidence": context.get('rag_confidence', 0.0),
                        "timestamp": context.get('timestamp', 'unknown')
                    }
            
            # Fallback analysis
            return await self._fallback_recon_analysis(task, context)
            
        except Exception as e:
            self.logger.error(f"RAG-enhanced reconnaissance failed: {e}")
            return {"error": str(e), "type": "reconnaissance", "status": "failed"}

    async def _run_rag_enhanced_ctf(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run CTF solving agent with RAG enhancement"""
        try:
            prompt = f"""CTF Challenge Analysis: {task}

Knowledge Base Context:
{context.get('rag_knowledge', 'No relevant knowledge found')}

Please analyze this CTF challenge and provide:
1. Challenge type identification
2. Likely solution approaches
3. Tools and techniques to use
4. Step-by-step solving strategy
5. Common pitfalls to avoid

Provide detailed CTF solving guidance."""
            
            if self.use_local_llm and hasattr(self, 'local_llm'):
                messages = [{"role": "user", "content": prompt}]
                response = await self.local_llm.chat_completion(messages)
                
                if 'error' not in response:
                    return {
                        "status": "completed",
                        "type": "ctf",
                        "solution_strategy": response['choices'][0]['message']['content'],
                        "rag_enhanced": True,
                        "knowledge_sources": context.get('knowledge_sources', []),
                        "confidence": context.get('rag_confidence', 0.0)
                    }
            
            return await self._fallback_ctf_analysis(task, context)
            
        except Exception as e:
            return {"error": str(e), "type": "ctf", "status": "failed"}

    async def _run_rag_enhanced_vuln(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run vulnerability assessment with RAG enhancement"""
        try:
            prompt = f"""Vulnerability Assessment Task: {task}

Knowledge Base Context:
{context.get('rag_knowledge', 'No relevant knowledge found')}

Please provide comprehensive vulnerability assessment including:
1. Vulnerability identification methods
2. Exploitation techniques and proof-of-concept
3. Impact assessment and CVSS scoring
4. Remediation recommendations
5. Testing verification methods

Provide detailed vulnerability analysis."""
            
            if self.use_local_llm and hasattr(self, 'local_llm'):
                messages = [{"role": "user", "content": prompt}]
                response = await self.local_llm.chat_completion(messages)
                
                if 'error' not in response:
                    return {
                        "status": "completed",
                        "type": "vulnerability_assessment",
                        "assessment": response['choices'][0]['message']['content'],
                        "rag_enhanced": True,
                        "knowledge_sources": context.get('knowledge_sources', []),
                        "confidence": context.get('rag_confidence', 0.0)
                    }
            
            return await self._fallback_vuln_analysis(task, context)
            
        except Exception as e:
            return {"error": str(e), "type": "vulnerability_assessment", "status": "failed"}

    async def _run_rag_enhanced_code_analysis(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run code analysis with RAG enhancement"""
        try:
            prompt = f"""Security Code Analysis Task: {task}

Knowledge Base Context:
{context.get('rag_knowledge', 'No relevant knowledge found')}

Please analyze the code for security issues including:
1. Vulnerability identification (SQL injection, XSS, buffer overflows, etc.)
2. Code quality and security best practices
3. Potential attack vectors
4. Remediation suggestions
5. Secure coding recommendations

Provide detailed security code analysis."""
            
            if self.use_local_llm and hasattr(self, 'local_llm'):
                messages = [{"role": "user", "content": prompt}]
                response = await self.local_llm.chat_completion(messages)
                
                if 'error' not in response:
                    return {
                        "status": "completed",
                        "type": "code_analysis",
                        "analysis": response['choices'][0]['message']['content'],
                        "rag_enhanced": True,
                        "knowledge_sources": context.get('knowledge_sources', []),
                        "confidence": context.get('rag_confidence', 0.0)
                    }
            
            return {"status": "completed", "type": "code_analysis", "analysis": "Local LLM not available for code analysis"}
            
        except Exception as e:
            return {"error": str(e), "type": "code_analysis", "status": "failed"}

    async def _run_rag_enhanced_threat_intel(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run threat intelligence analysis with RAG enhancement"""
        try:
            prompt = f"""Threat Intelligence Analysis Task: {task}

Knowledge Base Context:
{context.get('rag_knowledge', 'No relevant knowledge found')}

Please provide threat intelligence analysis including:
1. Threat actor identification and attribution
2. Tactics, techniques, and procedures (TTPs)
3. Indicators of compromise (IOCs)
4. Attack timeline and methodology
5. Defensive recommendations and countermeasures

Provide comprehensive threat intelligence analysis."""
            
            if self.use_local_llm and hasattr(self, 'local_llm'):
                messages = [{"role": "user", "content": prompt}]
                response = await self.local_llm.chat_completion(messages)
                
                if 'error' not in response:
                    return {
                        "status": "completed",
                        "type": "threat_intelligence",
                        "intelligence": response['choices'][0]['message']['content'],
                        "rag_enhanced": True,
                        "knowledge_sources": context.get('knowledge_sources', []),
                        "confidence": context.get('rag_confidence', 0.0)
                    }
            
            return {"status": "completed", "type": "threat_intelligence", "intelligence": "Local LLM not available for threat intel"}
            
        except Exception as e:
            return {"error": str(e), "type": "threat_intelligence", "status": "failed"}

    async def _run_generic_rag_agent(self, agent_type: str, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run generic RAG-enhanced agent for unknown types"""
        try:
            prompt = f"""Cybersecurity Analysis Task ({agent_type}): {task}

Knowledge Base Context:
{context.get('rag_knowledge', 'No relevant knowledge found')}

Please provide comprehensive cybersecurity analysis for this {agent_type} task including:
1. Problem analysis and approach
2. Relevant tools and techniques
3. Step-by-step methodology
4. Risk considerations
5. Recommendations and next steps

Provide detailed cybersecurity guidance."""
            
            if self.use_local_llm and hasattr(self, 'local_llm'):
                messages = [{"role": "user", "content": prompt}]
                response = await self.local_llm.chat_completion(messages)
                
                if 'error' not in response:
                    return {
                        "status": "completed",
                        "type": agent_type,
                        "analysis": response['choices'][0]['message']['content'],
                        "rag_enhanced": True,
                        "knowledge_sources": context.get('knowledge_sources', []),
                        "confidence": context.get('rag_confidence', 0.0)
                    }
            
            return {"status": "completed", "type": agent_type, "analysis": "Local LLM not available for analysis"}
            
        except Exception as e:
            return {"error": str(e), "type": agent_type, "status": "failed"}
    
    async def _run_recon_agent(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run reconnaissance agent"""
        # Implement CAI reconnaissance pattern
        return {"status": "completed", "type": "reconnaissance", "result": "simulated_recon_data"}
    
    async def _run_ctf_agent(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run CTF solving agent"""
        # Implement CAI CTF pattern
        return {"status": "completed", "type": "ctf", "result": "simulated_ctf_solution"}
    
    async def _run_vuln_agent(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run vulnerability assessment agent"""
        # Implement CAI vulnerability assessment
        return {"status": "completed", "type": "vulnerability_assessment", "result": "simulated_vuln_results"}
    
    async def _initialize_rag_knowledge(self):
        """Initialize RAG knowledge base from processed documents"""
        try:
            # Load processed cybersecurity knowledge
            rag_data_dir = Path("data/rag_data")
            if rag_data_dir.exists():
                for json_file in rag_data_dir.glob("*.json"):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            self.knowledge_base[json_file.stem] = data
                    except Exception as e:
                        self.logger.warning(f"Failed to load RAG data from {json_file}: {e}")
            
            # Load processed reports and documents
            processed_dir = Path("data/processed")
            if processed_dir.exists():
                for json_file in processed_dir.glob("*.json"):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            self.knowledge_base[f"processed_{json_file.stem}"] = data
                    except Exception as e:
                        self.logger.warning(f"Failed to load processed data from {json_file}: {e}")
            
            self.logger.info(f"📚 RAG knowledge base initialized with {len(self.knowledge_base)} documents")
            
        except Exception as e:
            self.logger.error(f"❌ RAG knowledge base initialization failed: {e}")
    
    async def query_rag_knowledge(self, query: str, context: str = "") -> Dict[str, Any]:
        """Query RAG knowledge base with local LLM"""
        try:
            # Search relevant documents
            relevant_docs = await self._search_relevant_documents(query)
            
            # Prepare RAG prompt
            rag_context = self._prepare_rag_context(relevant_docs, query, context)
            
            # Query local LLM if available
            if self.use_local_llm and hasattr(self, 'local_llm'):
                if not self.local_llm.is_running:
                    await self.local_llm.start()
                
                messages = [
                    {
                        "role": "system", 
                        "content": "You are a cybersecurity expert AI assistant with access to a comprehensive knowledge base. Use the provided context to answer questions accurately."
                    },
                    {
                        "role": "user", 
                        "content": rag_context
                    }
                ]
                
                response = await self.local_llm.chat_completion(messages)
                
                if 'error' not in response:
                    return {
                        "answer": response['choices'][0]['message']['content'],
                        "sources": [doc['source'] for doc in relevant_docs],
                        "confidence": 0.8,
                        "method": "local_rag"
                    }
            
            # Fallback to simple document search
            return await self._fallback_document_search(query, relevant_docs)
            
        except Exception as e:
            self.logger.error(f"❌ RAG query failed: {e}")
            return {"error": str(e), "answer": "RAG query failed"}
    
    async def _search_relevant_documents(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents in knowledge base"""
        try:
            query_lower = query.lower()
            relevant_docs = []
            
            for doc_id, doc_data in self.knowledge_base.items():
                relevance_score = await self._calculate_relevance_score(query_lower, doc_data)
                
                if relevance_score > 0.1:  # Threshold for relevance
                    relevant_docs.append({
                        "doc_id": doc_id,
                        "relevance_score": relevance_score,
                        "content": doc_data,
                        "source": doc_data.get('source', doc_id)
                    })
            
            # Sort by relevance and return top results
            relevant_docs.sort(key=lambda x: x['relevance_score'], reverse=True)
            return relevant_docs[:max_results]
            
        except Exception as e:
            self.logger.error(f"Document search failed: {e}")
            return []
    
    async def _calculate_relevance_score(self, query: str, doc_data: Dict[str, Any]) -> float:
        """Calculate relevance score between query and document"""
        try:
            # Simple keyword-based scoring
            score = 0.0
            query_words = set(query.split())
            
            # Check different fields in the document
            text_fields = ['content', 'analysis', 'summary', 'techniques', 'tools', 'key_topics']
            
            for field in text_fields:
                if field in doc_data:
                    field_content = str(doc_data[field]).lower()
                    field_words = set(field_content.split())
                    
                    # Calculate word overlap
                    overlap = len(query_words.intersection(field_words))
                    field_score = overlap / max(len(query_words), 1)
                    
                    # Weight different fields
                    weights = {
                        'content': 1.0,
                        'analysis': 1.2,
                        'summary': 0.8,
                        'techniques': 1.5,
                        'tools': 1.3,
                        'key_topics': 1.4
                    }
                    
                    score += field_score * weights.get(field, 1.0)
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception:
            return 0.0
    
    def _prepare_rag_context(self, relevant_docs: List[Dict[str, Any]], query: str, context: str) -> str:
        """Prepare RAG context for LLM"""
        try:
            context_parts = [
                f"Query: {query}",
                f"Additional Context: {context}" if context else "",
                "Relevant Knowledge Base Information:"
            ]
            
            for i, doc in enumerate(relevant_docs[:3]):  # Limit to top 3 docs
                doc_content = doc['content']
                
                # Extract key information from document
                if isinstance(doc_content, dict):
                    summary = ""
                    if 'summary' in doc_content:
                        summary = doc_content['summary']
                    elif 'analysis' in doc_content:
                        summary = str(doc_content['analysis'])[:500] + "..."
                    elif 'content' in doc_content:
                        summary = str(doc_content['content'])[:500] + "..."
                    
                    context_parts.append(f"\nDocument {i+1} (Source: {doc['source']}):\n{summary}")
                
            context_parts.append(f"\nBased on the above knowledge base information, please provide a comprehensive answer to the query: {query}")
            
            return "\n".join(filter(None, context_parts))
            
        except Exception as e:
            return f"Query: {query}\nContext preparation failed: {str(e)}"
    
    async def _fallback_document_search(self, query: str, relevant_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback document search when LLM is not available"""
        try:
            if not relevant_docs:
                return {
                    "answer": "No relevant information found in knowledge base.",
                    "sources": [],
                    "confidence": 0.0,
                    "method": "fallback_search"
                }
            
            # Combine relevant document summaries
            combined_info = []
            sources = []
            
            for doc in relevant_docs[:3]:
                doc_content = doc['content']
                sources.append(doc['source'])
                
                if isinstance(doc_content, dict):
                    if 'summary' in doc_content:
                        combined_info.append(doc_content['summary'])
                    elif 'key_points' in doc_content:
                        combined_info.append(str(doc_content['key_points']))
                    elif 'analysis' in doc_content:
                        combined_info.append(str(doc_content['analysis'])[:300] + "...")
            
            answer = "\n\n".join(combined_info) if combined_info else "Relevant documents found but no clear summary available."
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": 0.6,
                "method": "fallback_search"
            }
            
        except Exception as e:
            return {
                "answer": f"Fallback search failed: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "method": "error"
            }
```
