"""
File Parser for Cybersecurity Documents
Handles PDFs, markdown, text, HTML, JSON and other file formats
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import mimetypes

import PyPDF2
import markdown
from bs4 import BeautifulSoup
import google.generativeai as genai
from loguru import logger
import yaml

from rag_embedder import RAGEmbedder
from core.shared_utils import (
    ConfigManager, LoggerManager, GeminiClient,
    DirectoryManager, PromptTemplates, FileHandler
)

class FileParser:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.supported_formats = config['file_processing']['supported_formats']
        self.categories = config['file_processing']['classification_categories']
        
        # Setup logging using shared utility
        LoggerManager.setup_logger('file_parser')
        
        # Initialize shared Gemini client
        self.gemini_client = GeminiClient()
        
        # Initialize RAG embedder
        self.rag_embedder = RAGEmbedder(config)
        
        # Ensure data directories exist using shared utility
        DirectoryManager.ensure_directory("rag_data")
        self.data_dir = Path("rag_data")
        
        logger.info("📄 File Parser initialized with shared utilities")

    async def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a file and extract relevant cybersecurity information"""
        logger.info(f"Processing file: {file_path}")
        
        try:
            # Validate file
            if not await self._validate_file(file_path):
                raise ValueError("File validation failed")
            
            # Extract text content
            text_content = await self._extract_text(file_path)
            
            if not text_content or len(text_content.strip()) < 10:
                raise ValueError("No meaningful content extracted from file")
            
            # Analyze content with AI
            analysis = await self._analyze_content(text_content, file_path)
            
            # Create file metadata
            file_metadata = await self._create_file_metadata(file_path, analysis)
            
            # Save to RAG database
            await self._save_to_rag(text_content, file_metadata, analysis)
            
            # Save processed file info
            await self._save_file_info(file_metadata, analysis, text_content)
            
            result = {
                'filename': os.path.basename(file_path),
                'file_type': file_metadata['file_type'],
                'category': analysis['category'],
                'classification': analysis['classification'],
                'summary': analysis['summary'],
                'tags': analysis['tags'],
                'security_score': analysis['security_score'],
                'key_findings': analysis.get('key_findings', []),
                'threats_identified': analysis.get('threats_identified', []),
                'recommendations': analysis.get('recommendations', []),
                'processed_at': datetime.now().isoformat()
            }
            
            logger.info(f"File processing completed: {os.path.basename(file_path)}")
            return result
            
        except Exception as e:
            logger.error(f"File processing failed for {file_path}: {e}")
            raise

    async def _validate_file(self, file_path: str) -> bool:
        """Validate file format and size"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False
            
            # Check file size
            file_size = os.path.getsize(file_path)
            max_size = self.config['security']['file_upload']['max_size_mb'] * 1024 * 1024
            
            if file_size > max_size:
                logger.error(f"File too large: {file_size} bytes")
                return False
            
            # Check file extension
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in self.supported_formats:
                logger.error(f"Unsupported file format: {ext}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"File validation error: {e}")
            return False

    async def _extract_text(self, file_path: str) -> str:
        """Extract text content from various file formats"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        try:
            if ext == '.pdf':
                return await self._extract_from_pdf(file_path)
            elif ext == '.md':
                return await self._extract_from_markdown(file_path)
            elif ext == '.html':
                return await self._extract_from_html(file_path)
            elif ext == '.json':
                return await self._extract_from_json(file_path)
            elif ext in ['.txt', '.csv']:
                return await self._extract_from_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {ext}")
                
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise

    async def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                return text.strip()
                
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise

    async def _extract_from_markdown(self, file_path: str) -> str:
        """Extract text from Markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # Convert markdown to HTML, then extract text
                html = markdown.markdown(content)
                soup = BeautifulSoup(html, 'html.parser')
                text = soup.get_text()
                
                return text.strip()
                
        except Exception as e:
            logger.error(f"Markdown extraction failed: {e}")
            raise

    async def _extract_from_html(self, file_path: str) -> str:
        """Extract text from HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text = soup.get_text()
                
                # Clean up text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                return text
                
        except Exception as e:
            logger.error(f"HTML extraction failed: {e}")
            raise

    async def _extract_from_json(self, file_path: str) -> str:
        """Extract text from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # Convert JSON to readable text
                if isinstance(data, dict):
                    text_parts = []
                    for key, value in data.items():
                        if isinstance(value, (str, int, float)):
                            text_parts.append(f"{key}: {value}")
                        elif isinstance(value, list):
                            text_parts.append(f"{key}: {', '.join(map(str, value))}")
                    text = "\n".join(text_parts)
                else:
                    text = json.dumps(data, indent=2)
                
                return text
                
        except Exception as e:
            logger.error(f"JSON extraction failed: {e}")
            raise

    async def _extract_from_text(self, file_path: str) -> str:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
                
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise

    async def _analyze_content(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze content using AI for cybersecurity relevance"""
        if self.gemini_client.is_available:
            return await self._analyze_with_ai(content, file_path)
        else:
            return self._basic_analysis(content, file_path)

    async def _analyze_with_ai(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze content using shared Gemini client"""
        try:
            analysis_prompt = f"""
Analyze this cybersecurity document and provide detailed classification:

Filename: {os.path.basename(file_path)}
Content Length: {len(content)} characters
Content Preview: {content[:3000]}...

Provide analysis in JSON format:
{{
  "category": "select from: {', '.join(self.categories)}",
  "classification": "specific subcategory or attack type",
  "summary": "2-3 sentence summary highlighting key security insights",
  "tags": ["security_tag1", "security_tag2", "security_tag3", "security_tag4", "security_tag5"],
  "security_score": 8,
  "threat_level": "CRITICAL/HIGH/MEDIUM/LOW",
  "key_findings": ["finding1", "finding2", "finding3"],
  "threats_identified": ["threat1", "threat2"],
  "recommendations": ["recommendation1", "recommendation2"],
  "affected_systems": ["system1", "system2"],
  "technical_details": {{
    "vulnerabilities": ["vuln1", "vuln2"],
    "attack_vectors": ["vector1", "vector2"],
    "indicators": ["ioc1", "ioc2"]
  }}
}}

Security Score (1-10): Rate importance for cybersecurity professionals
Focus on practical security insights, vulnerabilities, attack methods, and defensive measures.
            """
            
            response = await self.gemini_client.generate_content(
                analysis_prompt,
                temperature=0.3,
                max_tokens=2000
            )
            
            try:
                analysis = json.loads(response)
                
                # Validate and clean the response
                analysis['category'] = analysis.get('category', 'general')
                analysis['security_score'] = min(max(analysis.get('security_score', 5), 1), 10)
                analysis['tags'] = analysis.get('tags', [])[:10]  # Limit tags
                
                return analysis
                
            except json.JSONDecodeError:
                logger.warning("AI returned invalid JSON, using basic analysis")
                return self._basic_analysis(content, file_path)
                
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._basic_analysis(content, file_path)

    def _basic_analysis(self, content: str, file_path: str) -> Dict[str, Any]:
        """Basic content analysis without AI"""
        # Security-related keywords
        security_keywords = {
            'vulnerability': ['vulnerability', 'CVE', 'exploit', 'flaw', 'weakness'],
            'malware': ['malware', 'virus', 'trojan', 'ransomware', 'backdoor'],
            'network': ['firewall', 'IDS', 'IPS', 'network', 'traffic'],
            'web': ['XSS', 'SQL injection', 'CSRF', 'OWASP', 'web application'],
            'incident': ['incident', 'breach', 'attack', 'compromise', 'forensics'],
            'compliance': ['compliance', 'audit', 'policy', 'framework', 'standard']
        }
        
        content_lower = content.lower()
        found_keywords = []
        category_scores = {}
        
        # Analyze content for keywords
        for category, keywords in security_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            category_scores[category] = score
            found_keywords.extend([kw for kw in keywords if kw in content_lower])
        
        # Determine primary category
        primary_category = max(category_scores, key=category_scores.get) if category_scores else 'general'
        
        # Map to our classification categories
        category_mapping = {
            'vulnerability': 'exploit_development',
            'malware': 'malware_analysis',
            'network': 'network_security',
            'web': 'web_security',
            'incident': 'incident_response',
            'compliance': 'compliance'
        }
        
        category = category_mapping.get(primary_category, 'tools_techniques')
        
        # Calculate security score
        security_score = min(sum(category_scores.values()) + 3, 10)
        
        return {
            'category': category,
            'classification': primary_category,
            'summary': f"Security document containing {len(found_keywords)} relevant keywords. " + content[:200] + "...",
            'tags': list(set(found_keywords))[:5],
            'security_score': security_score,
            'threat_level': 'HIGH' if security_score >= 8 else 'MEDIUM' if security_score >= 5 else 'LOW',
            'key_findings': [],
            'threats_identified': [],
            'recommendations': [],
            'affected_systems': [],
            'technical_details': {
                'vulnerabilities': [],
                'attack_vectors': [],
                'indicators': []
            }
        }

    async def _create_file_metadata(self, file_path: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive file metadata"""
        file_stats = os.stat(file_path)
        
        # Generate content hash for deduplication
        with open(file_path, 'rb') as f:
            content_hash = hashlib.md5(f.read()).hexdigest()
        
        metadata = {
            'filename': os.path.basename(file_path),
            'file_path': file_path,
            'file_size': file_stats.st_size,
            'file_type': mimetypes.guess_type(file_path)[0] or 'unknown',
            'content_hash': content_hash,
            'created_date': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
            'modified_date': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
            'processed_date': datetime.now().isoformat(),
            'category': analysis['category'],
            'security_score': analysis['security_score']
        }
        
        return metadata

    async def _save_to_rag(self, content: str, metadata: Dict[str, Any], analysis: Dict[str, Any]):
        """Save processed file to RAG database"""
        try:
            # Chunk content if it's too long
            max_chunk_size = self.config['rag'].get('chunk_size', 512)
            chunks = self._chunk_text(content, max_chunk_size)
            
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    **metadata,
                    'chunk_id': i,
                    'total_chunks': len(chunks),
                    'tags': analysis['tags'],
                    'classification': analysis['classification']
                }
                
                await self.rag_embedder.add_document(
                    content=chunk,
                    metadata=chunk_metadata,
                    collection=analysis['category']
                )
                
        except Exception as e:
            logger.error(f"Failed to save to RAG: {e}")

    def _chunk_text(self, text: str, max_size: int) -> List[str]:
        """Split text into chunks for RAG processing"""
        if len(text) <= max_size:
            return [text]
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= max_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    async def _save_file_info(self, metadata: Dict[str, Any], analysis: Dict[str, Any], content: str):
        """Save file processing information to JSON"""
        try:
            # Create category directory
            category_dir = self.data_dir / analysis['category']
            category_dir.mkdir(exist_ok=True)
            
            # Create file info
            file_info = {
                'metadata': metadata,
                'analysis': analysis,
                'content_preview': content[:1000],  # Store preview only
                'processed_at': datetime.now().isoformat()
            }
            
            # Save to file
            filename = f"file_{metadata['content_hash']}.json"
            filepath = category_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(file_info, f, indent=2, default=str)
                
            logger.info(f"File info saved: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save file info: {e}")

    async def batch_process_directory(self, directory_path: str) -> Dict[str, Any]:
        """Process all supported files in a directory"""
        logger.info(f"Batch processing directory: {directory_path}")
        
        if not os.path.exists(directory_path):
            raise ValueError(f"Directory not found: {directory_path}")
        
        results = {
            'processed_files': [],
            'failed_files': [],
            'total_files': 0,
            'success_count': 0,
            'failure_count': 0
        }
        
        # Find all supported files
        supported_files = []
        for ext in self.supported_formats:
            pattern = f"**/*{ext}"
            supported_files.extend(Path(directory_path).glob(pattern))
        
        results['total_files'] = len(supported_files)
        
        # Process each file
        for file_path in supported_files:
            try:
                result = await self.process_file(str(file_path))
                results['processed_files'].append({
                    'filename': result['filename'],
                    'category': result['category'],
                    'security_score': result['security_score']
                })
                results['success_count'] += 1
                
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                results['failed_files'].append({
                    'filename': os.path.basename(str(file_path)),
                    'error': str(e)
                })
                results['failure_count'] += 1
        
        logger.info(f"Batch processing complete: {results['success_count']}/{results['total_files']} files processed")
        return results

    async def get_processing_statistics(self) -> Dict[str, Any]:
        """Get statistics about processed files"""
        stats = {
            'total_files': 0,
            'files_by_category': {},
            'files_by_type': {},
            'security_score_distribution': {
                'critical': 0,  # 9-10
                'high': 0,      # 7-8
                'medium': 0,    # 5-6
                'low': 0        # 1-4
            },
            'average_security_score': 0
        }
        
        total_score = 0
        
        # Analyze processed files
        for category_dir in self.data_dir.iterdir():
            if category_dir.is_dir() and category_dir.name != 'chroma_db':
                category_files = list(category_dir.glob('file_*.json'))
                stats['files_by_category'][category_dir.name] = len(category_files)
                stats['total_files'] += len(category_files)
                
                for file_path in category_files:
                    try:
                        with open(file_path, 'r') as f:
                            file_info = json.load(f)
                            
                        # Update file type stats
                        file_type = file_info['metadata'].get('file_type', 'unknown')
                        stats['files_by_type'][file_type] = stats['files_by_type'].get(file_type, 0) + 1
                        
                        # Update security score distribution
                        score = file_info['analysis'].get('security_score', 0)
                        total_score += score
                        
                        if score >= 9:
                            stats['security_score_distribution']['critical'] += 1
                        elif score >= 7:
                            stats['security_score_distribution']['high'] += 1
                        elif score >= 5:
                            stats['security_score_distribution']['medium'] += 1
                        else:
                            stats['security_score_distribution']['low'] += 1
                            
                    except Exception as e:
                        logger.error(f"Failed to analyze file {file_path}: {e}")
        
        # Calculate average security score
        if stats['total_files'] > 0:
            stats['average_security_score'] = round(total_score / stats['total_files'], 2)
        
        return stats

if __name__ == "__main__":
    # Test the file parser
    async def test_file_parser():
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        parser = FileParser(config)
        
        # Test with a sample file (create one for testing)
        test_content = """
        # Cybersecurity Vulnerability Report
        
        This document describes a critical SQL injection vulnerability (CVE-2023-12345) 
        found in the login system. The vulnerability allows attackers to bypass 
        authentication and gain unauthorized access to the database.
        
        ## Attack Vector
        The attack exploits improper input validation in the login form.
        """
        
        # Create a test file
        test_file = "temp_test.md"
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        try:
            result = await parser.process_file(test_file)
            print(f"Processed file: {result['filename']}")
            print(f"Category: {result['category']}")
            print(f"Security Score: {result['security_score']}")
            print(f"Tags: {result['tags']}")
        finally:
            # Clean up test file
            if os.path.exists(test_file):
                os.remove(test_file)
    
    # Uncomment to test
    # asyncio.run(test_file_parser())
