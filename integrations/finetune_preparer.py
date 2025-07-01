"""
Fine-tuning Data Preparer
Converts logs and RAG data to fine-tuning ready format
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import random
import re

from loguru import logger
import yaml

from shared_utils import ConfigManager, LoggerManager, DirectoryManager

class FineTunePreparer:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or ConfigManager.get_instance().config
        self.finetune_config = self.config.get('fine_tuning', {})
        self.data_sources = self.finetune_config.get('data_sources', [])
        self.prompt_templates = self.finetune_config.get('prompt_templates', {})
        self.validation_split = self.finetune_config.get('validation_split', 0.1)
        self.max_sequence_length = self.finetune_config.get('max_sequence_length', 2048)
        
        self.logger = LoggerManager.setup_logger('finetune')
        
        # Setup output directories
        DirectoryManager.ensure_directory("finetune_data")
        DirectoryManager.ensure_directory("finetune_data/raw")
        DirectoryManager.ensure_directory("finetune_data/processed")
        
        self.output_dir = Path("finetune_data")
        
        self.logger.info("🧪 Fine-tune Preparer initialized")

    async def prepare_training_data(self) -> Dict[str, Any]:
        """Prepare comprehensive training data from all sources"""
        self.logger.info("Starting fine-tuning data preparation...")
        
        try:
            # Collect data from all sources
            raw_data = await self._collect_raw_data()
            
            # Process and convert to training format
            training_samples = await self._process_to_training_format(raw_data)
            
            # Split into training and validation sets
            train_data, val_data = await self._split_data(training_samples)
            
            # Save processed data
            train_file, val_file = await self._save_processed_data(train_data, val_data)
            
            # Generate quality metrics
            quality_metrics = await self._calculate_quality_metrics(training_samples)
            
            result = {
                'training_samples': len(train_data),
                'validation_samples': len(val_data),
                'data_sources': len(self.data_sources),
                'avg_sequence_length': quality_metrics['avg_sequence_length'],
                'vocab_size': quality_metrics['vocab_size'],
                'coverage_score': quality_metrics['coverage_score'],
                'train_file': str(train_file),
                'validation_file': str(val_file),
                'quality_metrics': quality_metrics,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Fine-tuning preparation complete: {len(training_samples)} total samples")
            return result
            
        except Exception as e:
            self.logger.error(f"Fine-tuning preparation failed: {e}")
            raise

    async def _collect_raw_data(self) -> List[Dict[str, Any]]:
        """Collect raw data from all configured sources"""
        self.logger.info("Collecting raw data from sources...")
        
        raw_data = []
        
        for source_pattern in self.data_sources:
            try:
                # Expand glob patterns
                source_files = list(Path(".").glob(source_pattern))
                self.logger.info(f"Found {len(source_files)} files matching pattern: {source_pattern}")
                
                for file_path in source_files:
                    if file_path.is_file():
                        file_data = await self._load_source_file(file_path)
                        raw_data.extend(file_data)
                        
            except Exception as e:
                self.logger.error(f"Failed to process source {source_pattern}: {e}")
                continue
        
        self.logger.info(f"Collected {len(raw_data)} raw data samples")
        return raw_data

    async def _load_source_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load data from a source file"""
        try:
            if file_path.suffix == '.json':
                return await self._load_json_file(file_path)
            elif file_path.suffix == '.md':
                return await self._load_markdown_file(file_path)
            elif file_path.suffix == '.log':
                return await self._load_log_file(file_path)
            else:
                self.logger.warning(f"Unsupported file type: {file_path}")
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to load file {file_path}: {e}")
            return []

    async def _load_json_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load data from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to load JSON file {file_path}: {e}")
            return []

    async def _load_markdown_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract training data from markdown reports"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract sections that could be useful for training
            samples = []
            
            # Look for Q&A patterns
            qa_patterns = [
                r'(?:Question|Q):\s*(.*?)\n.*?(?:Answer|A):\s*(.*?)(?=\n\n|\n(?:Question|Q):|$)',
                r'##\s*(.*?)\n(.*?)(?=\n##|\n\n|$)'
            ]
            
            for pattern in qa_patterns:
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                for question, answer in matches:
                    if len(question.strip()) > 10 and len(answer.strip()) > 20:
                        samples.append({
                            'type': 'qa_pair',
                            'question': question.strip(),
                            'answer': answer.strip(),
                            'source': str(file_path),
                            'category': 'report'
                        })
            
            return samples
            
        except Exception as e:
            self.logger.error(f"Failed to load markdown file {file_path}: {e}")
            return []

    async def _load_log_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract training data from log files"""
        try:
            samples = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for PentestGPT analysis patterns
            if 'pentestgpt' in str(file_path).lower():
                samples.extend(await self._extract_pentestgpt_data(content, file_path))
            
            # Look for RSS processing patterns
            elif 'rss' in str(file_path).lower():
                samples.extend(await self._extract_rss_data(content, file_path))
            
            return samples
            
        except Exception as e:
            self.logger.error(f"Failed to load log file {file_path}: {e}")
            return []

    async def _extract_pentestgpt_data(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract training data from PentestGPT logs"""
        samples = []
        
        try:
            # Look for JSON analysis entries
            json_pattern = r'\{[^{}]*"query"[^{}]*\}'
            matches = re.findall(json_pattern, content, re.DOTALL)
            
            for match in matches:
                try:
                    analysis_data = json.loads(match)
                    if 'query' in analysis_data and 'detailed_analysis' in analysis_data:
                        samples.append({
                            'type': 'security_analysis',
                            'query': analysis_data['query'],
                            'analysis': analysis_data['detailed_analysis'],
                            'source': str(file_path),
                            'category': 'pentesting'
                        })
                except json.JSONDecodeError:
                    continue
            
            return samples
            
        except Exception as e:
            self.logger.error(f"Failed to extract PentestGPT data: {e}")
            return []

    async def _extract_rss_data(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract training data from RSS processing logs"""
        samples = []
        
        try:
            # Look for article processing entries
            # This would extract security news summaries and classifications
            lines = content.split('\n')
            
            for line in lines:
                if 'processed article' in line.lower() and 'security' in line.lower():
                    # Extract useful information for training
                    # This is a simplified extraction - would need more sophisticated parsing
                    samples.append({
                        'type': 'security_news',
                        'content': line.strip(),
                        'source': str(file_path),
                        'category': 'intelligence'
                    })
            
            return samples
            
        except Exception as e:
            self.logger.error(f"Failed to extract RSS data: {e}")
            return []

    async def _process_to_training_format(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Convert raw data to training format with prompt/completion pairs"""
        logger.info("Converting raw data to training format...")
        
        training_samples = []
        
        for item in raw_data:
            try:
                samples = await self._convert_item_to_training(item)
                training_samples.extend(samples)
            except Exception as e:
                logger.error(f"Failed to convert item to training format: {e}")
                continue
        
        # Remove duplicates
        training_samples = await self._remove_duplicates(training_samples)
        
        # Filter by quality
        training_samples = await self._filter_by_quality(training_samples)
        
        logger.info(f"Generated {len(training_samples)} training samples")
        return training_samples

    async def _convert_item_to_training(self, item: Dict[str, Any]) -> List[Dict[str, str]]:
        """Convert a single item to training samples"""
        samples = []
        item_type = item.get('type', 'unknown')
        
        if item_type == 'security_analysis':
            samples.append(await self._create_analysis_sample(item))
        elif item_type == 'qa_pair':
            samples.append(await self._create_qa_sample(item))
        elif item_type == 'security_news':
            samples.append(await self._create_news_sample(item))
        
        return [s for s in samples if s]  # Filter out None values

    async def _create_analysis_sample(self, item: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Create training sample from security analysis"""
        try:
            query = item.get('query', '')
            analysis = item.get('analysis', '')
            
            if len(query) < 10 or len(analysis) < 50:
                return None
            
            template = self.prompt_templates.get('analysis', '### Security Analysis Request:\n{query}\n\n### Expert Analysis:\n{analysis}')
            
            formatted_sample = template.format(
                query=query,
                analysis=analysis
            )
            
            # Split into prompt and completion
            parts = formatted_sample.split('### Expert Analysis:\n')
            if len(parts) == 2:
                return {
                    'prompt': parts[0].strip(),
                    'completion': parts[1].strip()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to create analysis sample: {e}")
            return None

    async def _create_qa_sample(self, item: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Create training sample from Q&A pair"""
        try:
            question = item.get('question', '')
            answer = item.get('answer', '')
            
            if len(question) < 10 or len(answer) < 20:
                return None
            
            template = self.prompt_templates.get('instruction', '### Instruction:\n{instruction}\n\n### Response:\n{response}')
            
            formatted_sample = template.format(
                instruction=question,
                response=answer
            )
            
            # Split into prompt and completion
            parts = formatted_sample.split('### Response:\n')
            if len(parts) == 2:
                return {
                    'prompt': parts[0].strip(),
                    'completion': parts[1].strip()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to create Q&A sample: {e}")
            return None

    async def _create_news_sample(self, item: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Create training sample from security news"""
        try:
            content = item.get('content', '')
            
            if len(content) < 50:
                return None
            
            # Create a generic cybersecurity knowledge sample
            return {
                'prompt': '### Cybersecurity Information:\nProvide relevant cybersecurity insights based on current threat intelligence.',
                'completion': content
            }
            
        except Exception as e:
            logger.error(f"Failed to create news sample: {e}")
            return None

    async def _remove_duplicates(self, samples: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Remove duplicate training samples"""
        seen_prompts = set()
        unique_samples = []
        
        for sample in samples:
            prompt = sample.get('prompt', '')
            if prompt not in seen_prompts:
                seen_prompts.add(prompt)
                unique_samples.append(sample)
        
        logger.info(f"Removed {len(samples) - len(unique_samples)} duplicate samples")
        return unique_samples

    async def _filter_by_quality(self, samples: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Filter samples by quality criteria"""
        quality_samples = []
        
        for sample in samples:
            if await self._is_quality_sample(sample):
                quality_samples.append(sample)
        
        logger.info(f"Filtered to {len(quality_samples)} quality samples")
        return quality_samples

    async def _is_quality_sample(self, sample: Dict[str, str]) -> bool:
        """Check if a sample meets quality criteria"""
        prompt = sample.get('prompt', '')
        completion = sample.get('completion', '')
        
        # Basic quality checks
        if len(prompt) < 20 or len(completion) < 30:
            return False
        
        # Check for minimum cybersecurity relevance
        security_keywords = [
            'security', 'vulnerability', 'exploit', 'attack', 'malware',
            'penetration', 'hacking', 'cyber', 'threat', 'risk'
        ]
        
        text = (prompt + ' ' + completion).lower()
        security_score = sum(1 for keyword in security_keywords if keyword in text)
        
        if security_score < 2:
            return False
        
        # Check sequence length
        total_length = len(prompt) + len(completion)
        if total_length > self.max_sequence_length:
            return False
        
        return True

    async def _split_data(self, samples: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
        """Split data into training and validation sets"""
        random.shuffle(samples)
        
        split_idx = int(len(samples) * (1 - self.validation_split))
        train_data = samples[:split_idx]
        val_data = samples[split_idx:]
        
        logger.info(f"Split data: {len(train_data)} training, {len(val_data)} validation")
        return train_data, val_data

    async def _save_processed_data(self, train_data: List[Dict[str, str]], val_data: List[Dict[str, str]]) -> Tuple[Path, Path]:
        """Save processed training data to JSONL files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        train_file = self.output_dir / "processed" / f"train_{timestamp}.jsonl"
        val_file = self.output_dir / "processed" / f"validation_{timestamp}.jsonl"
        
        # Save training data
        with open(train_file, 'w', encoding='utf-8') as f:
            for sample in train_data:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        
        # Save validation data
        with open(val_file, 'w', encoding='utf-8') as f:
            for sample in val_data:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved training data to: {train_file}")
        logger.info(f"Saved validation data to: {val_file}")
        
        return train_file, val_file

    async def _calculate_quality_metrics(self, samples: List[Dict[str, str]]) -> Dict[str, Any]:
        """Calculate quality metrics for the training data"""
        if not samples:
            return {
                'avg_sequence_length': 0,
                'vocab_size': 0,
                'coverage_score': 0
            }
        
        # Calculate average sequence length
        total_length = sum(len(s.get('prompt', '') + s.get('completion', '')) for s in samples)
        avg_length = total_length / len(samples)
        
        # Calculate vocabulary size
        all_text = ' '.join([s.get('prompt', '') + ' ' + s.get('completion', '') for s in samples])
        vocab = set(all_text.lower().split())
        vocab_size = len(vocab)
        
        # Calculate coverage score (based on security topic diversity)
        security_topics = [
            'vulnerability', 'exploitation', 'reconnaissance', 'networking', 
            'web_security', 'malware', 'forensics', 'compliance'
        ]
        
        covered_topics = 0
        for topic in security_topics:
            if any(topic in (s.get('prompt', '') + s.get('completion', '')).lower() for s in samples):
                covered_topics += 1
        
        coverage_score = (covered_topics / len(security_topics)) * 10
        
        return {
            'avg_sequence_length': round(avg_length, 2),
            'vocab_size': vocab_size,
            'coverage_score': round(coverage_score, 2),
            'total_samples': len(samples),
            'security_topic_coverage': covered_topics,
            'data_quality_score': min(10, (coverage_score + min(vocab_size/1000, 5)) / 2)
        }

    async def create_lora_config(self) -> Dict[str, Any]:
        """Create LoRA adapter configuration"""
        config = {
            'task_type': 'CAUSAL_LM',
            'inference_mode': False,
            'r': 16,
            'lora_alpha': 32,
            'lora_dropout': 0.1,
            'target_modules': ['q_proj', 'v_proj', 'k_proj', 'o_proj'],
            'bias': 'none'
        }
        
        # Save LoRA config
        config_file = self.output_dir / "processed" / "lora_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"LoRA configuration saved to: {config_file}")
        return config

    async def validate_training_data(self, file_path: str) -> Dict[str, Any]:
        """Validate training data file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                samples = [json.loads(line) for line in f]
            
            validation_results = {
                'total_samples': len(samples),
                'valid_samples': 0,
                'invalid_samples': 0,
                'errors': []
            }
            
            for i, sample in enumerate(samples):
                try:
                    # Check required fields
                    if 'prompt' not in sample or 'completion' not in sample:
                        validation_results['errors'].append(f"Line {i+1}: Missing required fields")
                        validation_results['invalid_samples'] += 1
                        continue
                    
                    # Check content quality
                    if await self._is_quality_sample(sample):
                        validation_results['valid_samples'] += 1
                    else:
                        validation_results['invalid_samples'] += 1
                        validation_results['errors'].append(f"Line {i+1}: Quality check failed")
                        
                except Exception as e:
                    validation_results['errors'].append(f"Line {i+1}: {str(e)}")
                    validation_results['invalid_samples'] += 1
            
            validation_results['success_rate'] = validation_results['valid_samples'] / len(samples) if samples else 0
            
            logger.info(f"Validation complete: {validation_results['success_rate']:.2%} success rate")
            return validation_results
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise

if __name__ == "__main__":
    # Test the fine-tune preparer
    async def test_finetune_preparer():
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        preparer = FineTunePreparer(config)
        
        # Test data preparation
        results = await preparer.prepare_training_data()
        print(f"Prepared {results['training_samples']} training samples")
        print(f"Quality score: {results['coverage_score']}/10")
        
        # Create LoRA config
        lora_config = await preparer.create_lora_config()
        print("LoRA configuration created")
    
    # Uncomment to test
    # asyncio.run(test_finetune_preparer())
