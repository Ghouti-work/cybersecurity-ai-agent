#!/usr/bin/env python3
"""
Shared Utilities for Cybersecurity AI Agent Platform
Common functions and classes used across multiple modules
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import yaml
from loguru import logger
from dotenv import load_dotenv

class ConfigManager:
    """Centralized configuration management"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from files"""
        load_dotenv()
        
        try:
            config_path = Path(__file__).parent / 'config.yaml'
            with open(config_path, 'r') as f:
                self._config = yaml.safe_load(f)
            logger.info("✅ Configuration loaded successfully")
        except FileNotFoundError:
            logger.error("❌ config.yaml not found!")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to load config.yaml: {e}")
            raise
        
        return self._config
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get configuration dictionary"""
        return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a service"""
        key_map = {
            'telegram': 'TELEGRAM_BOT_TOKEN',
            'gemini': 'GEMINI_API_KEY',
            'azure_openai': 'AZURE_OPENAI_API_KEY'
        }
        
        env_var = key_map.get(service)
        if not env_var:
            return None
        
        key = os.getenv(env_var)
        return key if key and not key.startswith('your_') else None

class LoggerManager:
    """Centralized logging setup and management"""
    
    _initialized_loggers = set()
    
    @classmethod
    def setup_logger(cls, component: str, level: str = "INFO") -> None:
        """Setup logger for a component"""
        if component in cls._initialized_loggers:
            return
        
        log_dir = Path(f"logs/{component}")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_dir / f"{component}_{datetime.now().strftime('%Y-%m-%d')}.log",
            rotation="1 day",
            retention="30 days",
            level=level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
        )
        
        cls._initialized_loggers.add(component)
        logger.info(f"📝 Logger initialized for {component}")

class GeminiClient:
    """Shared Gemini API client with connection management"""
    
    _instance = None
    _model = None
    _api_key = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self._initialize()
    
    def _initialize(self):
        """Initialize Gemini client"""
        self._api_key = os.getenv('GEMINI_API_KEY')
        
        if not self._api_key or self._api_key.startswith('your_'):
            logger.warning("⚠️ Gemini API key not configured")
            return
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            self._model = genai.GenerativeModel('gemini-pro')
            logger.info("✅ Gemini client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini client: {e}")
            raise
    
    @property
    def is_available(self) -> bool:
        """Check if Gemini API is available"""
        return self._model is not None
    
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using Gemini API"""
        if not self.is_available:
            raise ValueError("Gemini API not available")
        
        try:
            # Get configuration
            config_manager = ConfigManager()
            model_config = config_manager.get('models.gemini', {})
            
            generation_config = {
                'temperature': kwargs.get('temperature', model_config.get('temperature', 0.7)),
                'max_output_tokens': kwargs.get('max_tokens', model_config.get('max_tokens', 4096)),
                'top_p': kwargs.get('top_p', model_config.get('top_p', 0.9))
            }
            
            # Import here to avoid circular imports
            import google.generativeai as genai
            
            response = await asyncio.to_thread(
                self._model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(**generation_config)
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"❌ Gemini API call failed: {e}")
            raise
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Gemini API connection"""
        if not self.is_available:
            return {'status': 'not_configured'}
        
        try:
            start_time = time.time()
            response = await self.generate_content("Respond with 'API_TEST_OK' only.")
            response_time = (time.time() - start_time) * 1000
            
            if 'API_TEST_OK' in response:
                return {
                    'status': 'connected',
                    'response_time_ms': round(response_time, 2)
                }
            else:
                return {
                    'status': 'unexpected_response',
                    'response': response[:100]
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

class DirectoryManager:
    """Shared directory creation and management"""
    
    REQUIRED_DIRS = [
        'logs',
        'rag_data',
        'reports',
        'finetune_data',
        'models',
        'config',
        'temp',
        'monitoring',
        'backup'
    ]
    
    SUBDIRS = {
        'logs': ['main', 'pentestgpt', 'telegram', 'rss', 'finetune', 'file_parser', 'rag', 'reports', 'local_llm', 'testing', 'health', 'integration'],
        'rag_data': ['recon', 'web', 'network', 'exploit', 'reports', 'raw', 'processed', 'chroma_db'],
        'reports': ['daily', 'weekly', 'custom', 'automated'],
        'finetune_data': ['raw', 'processed', 'checkpoints'],
        'models': ['embeddings', 'lora', 'local'],
        'config': ['prompts', 'feeds', 'templates'],
        'temp': ['uploads', 'processing'],
        'monitoring': ['health', 'performance'],
        'backup': ['daily', 'weekly']
    }
    
    @classmethod
    def create_all_directories(cls) -> None:
        """Create all required directories"""
        for main_dir in cls.REQUIRED_DIRS:
            Path(main_dir).mkdir(exist_ok=True)
            
            # Create subdirectories
            if main_dir in cls.SUBDIRS:
                for subdir in cls.SUBDIRS[main_dir]:
                    Path(main_dir, subdir).mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ All directories created")
    
    @classmethod
    def ensure_directory(cls, path: Union[str, Path]) -> Path:
        """Ensure a directory exists"""
        dir_path = Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

class EnvironmentValidator:
    """Environment validation utilities"""
    
    REQUIRED_VARS = [
        'TELEGRAM_BOT_TOKEN',
        'AUTHORIZED_USER_ID',
        'GEMINI_API_KEY'
    ]
    
    OPTIONAL_VARS = [
        'AZURE_OPENAI_API_KEY',
        'AZURE_OPENAI_ENDPOINT',
        'WEBHOOK_URL',
        'WEBHOOK_SECRET'
    ]
    
    @classmethod
    def validate_environment(cls) -> Dict[str, Any]:
        """Validate environment configuration"""
        results = {
            'status': 'pass',
            'configured': [],
            'missing': [],
            'warnings': []
        }
        
        # Check required variables
        for var in cls.REQUIRED_VARS:
            value = os.getenv(var)
            if value and not value.startswith('your_'):
                results['configured'].append(var)
            else:
                results['missing'].append(var)
                if var in ['TELEGRAM_BOT_TOKEN', 'GEMINI_API_KEY']:
                    results['status'] = 'fail'
        
        # Check optional variables
        for var in cls.OPTIONAL_VARS:
            value = os.getenv(var)
            if value and not value.startswith('your_'):
                results['configured'].append(var)
            else:
                results['warnings'].append(f"{var} not configured (optional)")
        
        return results
    
    @classmethod
    def check_api_keys(cls) -> Dict[str, bool]:
        """Check which API keys are configured"""
        config_manager = ConfigManager()
        
        return {
            'telegram': bool(config_manager.get_api_key('telegram')),
            'gemini': bool(config_manager.get_api_key('gemini')),
            'azure_openai': bool(config_manager.get_api_key('azure_openai'))
        }

class FileHandler:
    """Shared file handling utilities"""
    
    SUPPORTED_FORMATS = ['.pdf', '.txt', '.md', '.html', '.json', '.xml', '.csv']
    
    @classmethod
    def is_supported_format(cls, file_path: Union[str, Path]) -> bool:
        """Check if file format is supported"""
        return Path(file_path).suffix.lower() in cls.SUPPORTED_FORMATS
    
    @classmethod
    def get_file_info(cls, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Get file information"""
        path = Path(file_path)
        
        if not path.exists():
            return {'error': 'File not found'}
        
        stat = path.stat()
        
        return {
            'name': path.name,
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'extension': path.suffix.lower(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'supported': cls.is_supported_format(path)
        }
    
    @classmethod
    def validate_upload(cls, file_path: Union[str, Path], max_size_mb: int = 50) -> Dict[str, Any]:
        """Validate uploaded file"""
        info = cls.get_file_info(file_path)
        
        if 'error' in info:
            return info
        
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check file size
        if info['size_mb'] > max_size_mb:
            validation['valid'] = False
            validation['errors'].append(f"File too large: {info['size_mb']}MB (max: {max_size_mb}MB)")
        
        # Check file format
        if not info['supported']:
            validation['warnings'].append(f"File format {info['extension']} may not be fully supported")
        
        return {**info, **validation}

class SystemMetrics:
    """System monitoring and metrics utilities"""
    
    @classmethod
    def get_system_metrics(cls) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        try:
            import psutil
            
            # Memory information
            memory = psutil.virtual_memory()
            
            # Disk information
            disk = psutil.disk_usage('/')
            
            # CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Process information
            process_count = len(psutil.pids())
            
            return {
                'memory': {
                    'total_gb': round(memory.total / (1024**3), 2),
                    'available_gb': round(memory.available / (1024**3), 2),
                    'used_gb': round(memory.used / (1024**3), 2),
                    'percent': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / (1024**3), 2),
                    'free_gb': round(disk.free / (1024**3), 2),
                    'used_gb': round(disk.used / (1024**3), 2),
                    'percent': round((disk.used / disk.total) * 100, 1)
                },
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'count_logical': psutil.cpu_count(logical=True)
                },
                'system': {
                    'process_count': process_count,
                    'boot_time': psutil.boot_time()
                },
                'timestamp': datetime.now().isoformat()
            }
        except ImportError:
            logger.warning("psutil not available, using fallback metrics")
            return cls._get_fallback_metrics()
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return cls._get_fallback_metrics()
    
    @classmethod
    def _get_fallback_metrics(cls) -> Dict[str, Any]:
        """Fallback metrics when psutil is not available"""
        return {
            'memory': {'total_gb': 8, 'available_gb': 4, 'used_gb': 4, 'percent': 50},
            'disk': {'total_gb': 100, 'free_gb': 50, 'used_gb': 50, 'percent': 50},
            'cpu': {'percent': 25, 'count': 2, 'count_logical': 2},
            'system': {'process_count': 100, 'boot_time': time.time() - 3600},
            'timestamp': datetime.now().isoformat(),
            'fallback': True
        }
    
    @classmethod
    def check_system_health(cls) -> Dict[str, Any]:
        """Check overall system health"""
        metrics = cls.get_system_metrics()
        
        health = {
            'status': 'healthy',
            'warnings': [],
            'errors': []
        }
        
        # Memory checks
        if metrics['memory']['percent'] > 90:
            health['status'] = 'critical'
            health['errors'].append(f"Critical memory usage: {metrics['memory']['percent']}%")
        elif metrics['memory']['percent'] > 80:
            health['status'] = 'warning'
            health['warnings'].append(f"High memory usage: {metrics['memory']['percent']}%")
        
        # Disk checks
        if metrics['disk']['percent'] > 95:
            health['status'] = 'critical'
            health['errors'].append(f"Critical disk usage: {metrics['disk']['percent']}%")
        elif metrics['disk']['percent'] > 85:
            if health['status'] != 'critical':
                health['status'] = 'warning'
            health['warnings'].append(f"High disk usage: {metrics['disk']['percent']}%")
        
        # CPU checks
        if metrics['cpu']['percent'] > 95:
            health['status'] = 'critical'
            health['errors'].append(f"Critical CPU usage: {metrics['cpu']['percent']}%")
        elif metrics['cpu']['percent'] > 80:
            if health['status'] != 'critical':
                health['status'] = 'warning'
            health['warnings'].append(f"High CPU usage: {metrics['cpu']['percent']}%")
        
        return {**health, 'metrics': metrics}

class PromptTemplates:
    """Shared prompt templates for AI interactions"""
    
    SYSTEM_PROMPTS = {
        'security_analyst': """You are an expert cybersecurity analyst with deep knowledge of:
- Vulnerability assessment and penetration testing
- Threat intelligence and malware analysis
- Network security and incident response
- Security frameworks (NIST, OWASP, MITRE ATT&CK)
- Risk assessment and mitigation strategies

Provide accurate, actionable security insights while maintaining ethical standards.""",
        
        'pentesting_expert': """You are a professional penetration tester with expertise in:
- Web application security testing
- Network reconnaissance and scanning
- Exploit development and payload creation
- Post-exploitation techniques
- Security reporting and risk assessment

Always provide educational content for authorized testing only.""",
        
        'intelligence_analyst': """You are a threat intelligence analyst specializing in:
- CVE analysis and vulnerability research
- Threat actor profiling and campaign tracking
- IOC extraction and threat hunting
- Security news analysis and trend identification
- Risk prioritization and impact assessment

Focus on actionable intelligence and defensive recommendations."""
    }
    
    TASK_PROMPTS = {
        'vulnerability_analysis': """Analyze the following for security vulnerabilities:

Target: {target}
Context: {context}

Provide:
1. Potential vulnerability categories
2. Risk assessment (Low/Medium/High/Critical)
3. Exploitation likelihood
4. Recommended mitigation strategies
5. Additional investigation steps

Format your response as structured analysis.""",
        
        'threat_intelligence': """Analyze the following threat intelligence:

Source: {source}
Data: {data}

Provide:
1. Threat classification and severity
2. Associated threat actors or campaigns
3. Indicators of Compromise (IOCs)
4. Potential impact and targets
5. Defensive recommendations

Focus on actionable intelligence.""",
        
        'incident_response': """Provide incident response guidance for:

Incident Type: {incident_type}
Details: {details}

Provide:
1. Immediate containment steps
2. Investigation procedures
3. Evidence collection guidelines
4. Communication protocols
5. Recovery recommendations

Prioritize containment and evidence preservation."""
    }
    
    @classmethod
    def get_system_prompt(cls, agent_type: str) -> str:
        """Get system prompt for agent type"""
        return cls.SYSTEM_PROMPTS.get(agent_type, cls.SYSTEM_PROMPTS['security_analyst'])
    
    @classmethod
    def get_task_prompt(cls, task_type: str, **kwargs) -> str:
        """Get formatted task prompt"""
        template = cls.TASK_PROMPTS.get(task_type, "Analyze the following: {context}")
        return template.format(**kwargs)
    
    @classmethod
    def format_security_prompt(cls, task: str, context: Dict[str, Any] = None) -> str:
        """Format a general security analysis prompt"""
        context = context or {}
        
        prompt = f"""Security Analysis Request:
Task: {task}

Context:
"""
        for key, value in context.items():
            prompt += f"- {key}: {value}\n"
        
        prompt += """
Please provide a comprehensive security analysis including:
1. Risk assessment
2. Potential vulnerabilities or threats
3. Mitigation recommendations
4. Additional considerations

Maintain ethical guidelines and focus on defensive security."""
        
        return prompt

def initialize_shared_components() -> Dict[str, Any]:
    """Initialize all shared components"""
    logger.info("🚀 Initializing shared components...")
    
    results = {}
    
    try:
        # Initialize configuration
        config_manager = ConfigManager()
        results['config'] = 'initialized'
        
        # Create directories
        DirectoryManager.create_all_directories()
        results['directories'] = 'created'
        
        # Validate environment
        env_validation = EnvironmentValidator.validate_environment()
        results['environment'] = env_validation
        
        # Initialize Gemini client
        gemini_client = GeminiClient()
        results['gemini'] = 'available' if gemini_client.is_available else 'not_configured'
        
        # Check system health
        system_health = SystemMetrics.check_system_health()
        results['system_health'] = system_health['status']
        
        logger.info("✅ Shared components initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize shared components: {e}")
        results['error'] = str(e)
    
    return results

# Compatibility functions for backward compatibility
def setup_logging(component: str) -> None:
    """Backward compatibility function"""
    return LoggerManager.setup_logger(component)

def get_config() -> Dict[str, Any]:
    """Backward compatibility function"""
    return ConfigManager.get_instance().config

def ensure_dir(path: Union[str, Path]) -> Path:
    """Backward compatibility function"""
    return DirectoryManager.ensure_directory(path)
