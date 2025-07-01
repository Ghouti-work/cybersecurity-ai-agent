#!/usr/bin/env python3
"""
Local LLM Server for Cybersecurity AI Agent Platform
Provides fallback processing using DeepSeek/Phi-2 models
Memory-optimized for 8GB RAM systems
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    pipeline,
    BitsAndBytesConfig
)
from loguru import logger
import yaml
from datetime import datetime
import psutil

from shared_utils import ConfigManager, LoggerManager, DirectoryManager, SystemMetrics

class LocalLLMServer:
    """Local LLM server with memory optimization"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or ConfigManager.get_instance().config
        self.logger = LoggerManager.setup_logger('local_llm')
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.is_initialized = False
        self.model_name = self._select_optimal_model()
        
        # Memory management
        self.max_memory_mb = int(os.getenv('MAX_MEMORY_MB', 4096))  # 4GB for model
        self.device = 'cpu'  # Force CPU for 8GB systems
        
        # Setup directories
        DirectoryManager.ensure_directory("models/local")
        DirectoryManager.ensure_directory("temp/llm_cache")
        
        self.logger.info("🤖 Local LLM Server initialized")
        
    def _select_optimal_model(self) -> str:
        """Select optimal model based on system resources"""
        memory_info = SystemMetrics.get_system_metrics().get('memory', {})
        memory_gb = memory_info.get('total_gb', 8)
        
        if memory_gb >= 16:
            # High memory: Use larger model
            return "deepseek-ai/deepseek-coder-1.3b-instruct"
        elif memory_gb >= 8:
            # Medium memory: Use optimized model
            return "microsoft/DialoGPT-small"
        else:
            # Low memory: Use tiny model
            return "distilgpt2"
    
    async def initialize(self):
        """Initialize the local LLM with memory optimization"""
        self.logger.info(f"🔧 Initializing local LLM: {self.model_name}")
        
        try:
            # Check available memory
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            
            if available_gb < 2:
                self.logger.warning(f"⚠️  Low available memory: {available_gb:.1f}GB")
                return False
            
            # Configure quantization for memory efficiency
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_enable_fp32_cpu_offload=True
            ) if torch.cuda.is_available() else None
            
            # Load tokenizer
            logger.info("📚 Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                cache_dir="models/local"
            )
            
            # Add pad token if missing
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with memory optimization
            logger.info("🧠 Loading model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=quantization_config,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                low_cpu_mem_usage=True,
                cache_dir="models/local",
                trust_remote_code=True
            )
            
            # Move to CPU if needed
            if self.device == 'cpu':
                self.model = self.model.to('cpu')
            
            # Create pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1,
                max_length=512,  # Limit for memory
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            self.is_initialized = True
            logger.info("✅ Local LLM initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize local LLM: {e}")
            return False
    
    async def generate_response(self, prompt: str, max_tokens: int = 256) -> str:
        """Generate response using local LLM"""
        if not self.is_initialized:
            await self.initialize()
            if not self.is_initialized:
                return "❌ Local LLM not available"
        
        try:
            # Limit prompt length for memory efficiency
            max_prompt_length = 300
            if len(prompt) > max_prompt_length:
                prompt = prompt[:max_prompt_length] + "..."
            
            # Format prompt for cybersecurity context
            formatted_prompt = self._format_cybersecurity_prompt(prompt)
            
            # Generate response
            logger.info(f"🔄 Generating response for: {prompt[:50]}...")
            
            # Use pipeline with memory limits
            outputs = await asyncio.to_thread(
                self.pipeline,
                formatted_prompt,
                max_new_tokens=min(max_tokens, 256),  # Strict limit
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                return_full_text=False
            )
            
            response = outputs[0]['generated_text'].strip()
            
            # Clean up response
            response = self._clean_response(response)
            
            logger.info(f"✅ Response generated: {len(response)} chars")
            return response
            
        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            return f"❌ Local LLM error: {str(e)}"
    
    def _format_cybersecurity_prompt(self, prompt: str) -> str:
        """Format prompt for cybersecurity context"""
        system_prompt = """You are a cybersecurity expert assistant. Provide concise, accurate information about:
- Vulnerability assessment
- Penetration testing
- Security analysis
- Threat intelligence

Keep responses focused and practical."""
        
        return f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
    
    def _clean_response(self, response: str) -> str:
        """Clean and format the response"""
        # Remove common artifacts
        response = response.replace("<|endoftext|>", "")
        response = response.replace("[PAD]", "")
        
        # Limit response length
        max_length = 500
        if len(response) > max_length:
            response = response[:max_length] + "..."
        
        return response.strip()
    
    async def analyze_security_query(self, query: str) -> Dict[str, Any]:
        """Analyze security query using local LLM"""
        if not self.is_initialized:
            return {
                'analysis': '❌ Local LLM not available',
                'confidence': 0.0,
                'recommendations': []
            }
        
        try:
            # Generate analysis
            analysis_prompt = f"""Analyze this cybersecurity query and provide:
1. Brief technical analysis
2. Key security considerations
3. Recommended actions

Query: {query}"""
            
            analysis = await self.generate_response(analysis_prompt, max_tokens=200)
            
            # Generate recommendations
            rec_prompt = f"List 3 key security recommendations for: {query}"
            recommendations = await self.generate_response(rec_prompt, max_tokens=150)
            
            return {
                'analysis': analysis,
                'recommendations': recommendations.split('\n')[:3],
                'confidence': 0.7,  # Local model confidence
                'source': 'local_llm'
            }
            
        except Exception as e:
            logger.error(f"❌ Security analysis error: {e}")
            return {
                'analysis': f"❌ Analysis error: {str(e)}",
                'confidence': 0.0,
                'recommendations': []
            }
    
    async def classify_content(self, content: str, categories: List[str]) -> str:
        """Classify content into security categories"""
        if not self.is_initialized:
            return "unknown"
        
        try:
            prompt = f"""Classify this cybersecurity content into one category:
Categories: {', '.join(categories)}

Content: {content[:200]}...

Category:"""
            
            response = await self.generate_response(prompt, max_tokens=50)
            
            # Extract category from response
            for category in categories:
                if category.lower() in response.lower():
                    return category
            
            return "unknown"
            
        except Exception as e:
            logger.error(f"❌ Classification error: {e}")
            return "unknown"
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.is_initialized:
            return {'status': 'not_initialized'}
        
        try:
            # Get memory usage
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            return {
                'status': 'ready',
                'model_name': self.model_name,
                'device': self.device,
                'memory_usage_mb': round(memory_mb, 1),
                'max_tokens': 512,
                'supports_streaming': False
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    async def shutdown(self):
        """Shutdown and cleanup"""
        logger.info("🛑 Shutting down local LLM server...")
        
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer
        if self.pipeline:
            del self.pipeline
        
        # Force garbage collection
        import gc
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.is_initialized = False
        logger.info("✅ Local LLM server shutdown complete")

# API-like interface for the local server
class LocalLLMAPI:
    """API wrapper for local LLM server"""
    
    def __init__(self, config: Dict[str, Any]):
        self.server = LocalLLMServer(config)
        self.is_running = False
    
    async def start(self):
        """Start the local LLM API"""
        logger.info("🚀 Starting Local LLM API...")
        success = await self.server.initialize()
        self.is_running = success
        return success
    
    async def chat_completion(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """OpenAI-like chat completion interface"""
        if not self.is_running:
            return {
                'error': 'Local LLM not available',
                'choices': []
            }
        
        # Extract user message
        user_message = ""
        for msg in messages:
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break
        
        if not user_message:
            return {
                'error': 'No user message found',
                'choices': []
            }
        
        # Generate response
        response = await self.server.generate_response(user_message)
        
        return {
            'choices': [{
                'message': {
                    'role': 'assistant',
                    'content': response
                }
            }],
            'model': self.server.model_name,
            'usage': {
                'prompt_tokens': len(user_message.split()),
                'completion_tokens': len(response.split()),
                'total_tokens': len(user_message.split()) + len(response.split())
            }
        }
    
    async def stop(self):
        """Stop the local LLM API"""
        await self.server.shutdown()
        self.is_running = False

async def main():
    """Test the local LLM server"""
    print("🧠 Testing Local LLM Server...")
    
    # Load config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize server
    api = LocalLLMAPI(config)
    
    if await api.start():
        print("✅ Local LLM server started")
        
        # Test queries
        test_queries = [
            "What is SQL injection?",
            "How to test for XSS vulnerabilities?",
            "Explain buffer overflow attacks"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            
            # Test chat completion
            messages = [{'role': 'user', 'content': query}]
            response = await api.chat_completion(messages)
            
            if 'error' not in response:
                content = response['choices'][0]['message']['content']
                print(f"💬 Response: {content[:100]}...")
            else:
                print(f"❌ Error: {response['error']}")
        
        # Get model info
        info = await api.server.get_model_info()
        print(f"\n📊 Model Info: {info}")
        
        await api.stop()
    else:
        print("❌ Failed to start local LLM server")

if __name__ == "__main__":
    asyncio.run(main())
