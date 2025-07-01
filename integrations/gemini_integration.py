#!/usr/bin/env python3
"""
Gemini Integration for Books and File Extraction
Specialized for document processing and PentestGPT enhancement
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import base64
import mimetypes
from datetime import datetime

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import PyPDF2
import docx
from PIL import Image
import pandas as pd
from loguru import logger
import yaml

from shared_utils import ConfigManager, LoggerManager, DirectoryManager

class GeminiDocumentProcessor:
    """Gemini-powered document and file extraction processor"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or ConfigManager.get_instance().config
        self.logger = LoggerManager.setup_logger('gemini_processor')
        
        # Gemini configuration
        self.api_key = os.getenv('GEMINI_API_KEY') or self.config.get('gemini', {}).get('api_key')
        self.model_name = "gemini-1.5-pro-latest"  # Best for document processing
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment or config")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model with safety settings for cybersecurity content
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            safety_settings=self.safety_settings
        )
        
        # Setup directories
        DirectoryManager.ensure_directory("data/documents")
        DirectoryManager.ensure_directory("data/extracted")
        DirectoryManager.ensure_directory("data/processed")
        
        self.doc_dir = Path("data/documents")
        self.extracted_dir = Path("data/extracted")
        self.processed_dir = Path("data/processed")
        
        self.logger.info("🔮 Gemini Document Processor initialized")

    async def process_cybersecurity_book(self, file_path: str) -> Dict[str, Any]:
        """Process cybersecurity books and extract key information"""
        self.logger.info(f"📚 Processing cybersecurity book: {file_path}")
        
        try:
            file_path = Path(file_path)
            
            # Extract text content
            content = await self._extract_document_content(file_path)
            
            if not content:
                return {"error": "Failed to extract content from document"}
            
            # Analyze with Gemini
            analysis = await self._analyze_cybersecurity_content(content, file_path.name)
            
            # Extract specific cybersecurity knowledge
            extracted_data = await self._extract_cybersecurity_knowledge(content, analysis)
            
            # Save processed data
            output_file = await self._save_processed_book(file_path.name, extracted_data)
            
            result = {
                "status": "success",
                "file": str(file_path),
                "output_file": str(output_file),
                "content_length": len(content),
                "extracted_sections": len(extracted_data.get('sections', [])),
                "key_topics": extracted_data.get('key_topics', []),
                "vulnerability_techniques": extracted_data.get('techniques', []),
                "tools_mentioned": extracted_data.get('tools', []),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Book processing complete: {len(extracted_data.get('sections', []))} sections extracted")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Book processing failed: {e}")
            return {"error": str(e), "status": "failed"}

    async def _extract_document_content(self, file_path: Path) -> str:
        """Extract text content from various document formats"""
        try:
            file_extension = file_path.suffix.lower()
            
            if file_extension == '.pdf':
                return await self._extract_pdf_content(file_path)
            elif file_extension == '.docx':
                return await self._extract_docx_content(file_path)
            elif file_extension == '.txt':
                return await self._extract_txt_content(file_path)
            elif file_extension in ['.md', '.markdown']:
                return await self._extract_markdown_content(file_path)
            else:
                self.logger.warning(f"Unsupported file format: {file_extension}")
                return ""
                
        except Exception as e:
            self.logger.error(f"Content extraction failed: {e}")
            return ""

    async def _extract_pdf_content(self, file_path: Path) -> str:
        """Extract text from PDF files"""
        try:
            content = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\\n"
            return content
        except Exception as e:
            self.logger.error(f"PDF extraction failed: {e}")
            return ""

    async def _extract_docx_content(self, file_path: Path) -> str:
        """Extract text from DOCX files"""
        try:
            doc = docx.Document(file_path)
            content = ""
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\\n"
            return content
        except Exception as e:
            self.logger.error(f"DOCX extraction failed: {e}")
            return ""

    async def _extract_txt_content(self, file_path: Path) -> str:
        """Extract text from TXT files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            self.logger.error(f"TXT extraction failed: {e}")
            return ""

    async def _extract_markdown_content(self, file_path: Path) -> str:
        """Extract text from Markdown files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            self.logger.error(f"Markdown extraction failed: {e}")
            return ""

    async def _analyze_cybersecurity_content(self, content: str, filename: str) -> Dict[str, Any]:
        """Analyze content using Gemini for cybersecurity insights"""
        try:
            prompt = f"""Analyze this cybersecurity document and extract key information:

Document: {filename}

Please provide a comprehensive analysis including:
1. Main cybersecurity topics covered
2. Vulnerability types discussed
3. Attack techniques and methodologies
4. Security tools and technologies mentioned
5. Defensive strategies and mitigations
6. Key learning objectives
7. Practical examples and case studies
8. Industry standards and frameworks referenced

Content:
{content[:50000]}  # Limit content for API

Provide the analysis in JSON format with clear categories."""
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            # Parse JSON response
            try:
                analysis = json.loads(response.text)
                return analysis
            except json.JSONDecodeError:
                # If not valid JSON, create structured response
                return {
                    "analysis": response.text,
                    "topics": [],
                    "techniques": [],
                    "tools": [],
                    "mitigations": []
                }
                
        except Exception as e:
            self.logger.error(f"Gemini analysis failed: {e}")
            return {"error": str(e)}

    async def _extract_cybersecurity_knowledge(self, content: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract specific cybersecurity knowledge from content"""
        try:
            # Split content into manageable chunks
            content_chunks = self._split_content(content, 10000)
            
            extracted_sections = []
            all_techniques = []
            all_tools = []
            key_topics = []
            
            for i, chunk in enumerate(content_chunks):
                section_analysis = await self._analyze_content_section(chunk, i + 1)
                
                if section_analysis and section_analysis.get('relevant', False):
                    extracted_sections.append(section_analysis)
                    
                    # Collect techniques and tools
                    all_techniques.extend(section_analysis.get('techniques', []))
                    all_tools.extend(section_analysis.get('tools', []))
                    key_topics.extend(section_analysis.get('topics', []))
            
            # Remove duplicates
            unique_techniques = list(set(all_techniques))
            unique_tools = list(set(all_tools))
            unique_topics = list(set(key_topics))
            
            return {
                "sections": extracted_sections,
                "techniques": unique_techniques,
                "tools": unique_tools,
                "key_topics": unique_topics,
                "analysis_summary": analysis,
                "total_sections": len(extracted_sections),
                "processing_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Knowledge extraction failed: {e}")
            return {"error": str(e)}

    def _split_content(self, content: str, chunk_size: int) -> List[str]:
        """Split content into manageable chunks"""
        words = content.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks

    async def _analyze_content_section(self, content_chunk: str, section_num: int) -> Dict[str, Any]:
        """Analyze a specific content section for cybersecurity relevance"""
        try:
            prompt = f"""Analyze this cybersecurity content section and extract:

Section {section_num}:

1. Is this section relevant to cybersecurity/pentesting? (true/false)
2. What specific techniques are discussed?
3. What tools or technologies are mentioned?
4. What topics are covered?
5. Any practical examples or commands?
6. Key learning points

Content:
{content_chunk}

Respond in JSON format:
{{
    "relevant": true/false,
    "techniques": ["technique1", "technique2"],
    "tools": ["tool1", "tool2"],
    "topics": ["topic1", "topic2"],
    "examples": ["example1", "example2"],
    "key_points": ["point1", "point2"],
    "section_summary": "brief summary"
}}"""
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                # Fallback parsing
                return {
                    "relevant": "security" in content_chunk.lower() or "vulnerability" in content_chunk.lower(),
                    "techniques": [],
                    "tools": [],
                    "topics": [],
                    "examples": [],
                    "key_points": [],
                    "section_summary": response.text[:200] + "..."
                }
                
        except Exception as e:
            self.logger.error(f"Section analysis failed: {e}")
            return {"relevant": False, "error": str(e)}

    async def _save_processed_book(self, filename: str, extracted_data: Dict[str, Any]) -> Path:
        """Save processed book data"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"processed_{filename}_{timestamp}.json"
            output_path = self.processed_dir / output_filename
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Processed book data saved to: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to save processed book: {e}")
            raise

    async def extract_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata and content summary from any file"""
        self.logger.info(f"📄 Extracting metadata from: {file_path}")
        
        try:
            file_path = Path(file_path)
            
            # Basic file info
            stat = file_path.stat()
            file_info = {
                "filename": file_path.name,
                "extension": file_path.suffix,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "mime_type": mimetypes.guess_type(str(file_path))[0]
            }
            
            # Content analysis
            if file_path.suffix.lower() in ['.pdf', '.docx', '.txt', '.md']:
                content = await self._extract_document_content(file_path)
                
                if content:
                    # Analyze content with Gemini
                    content_analysis = await self._analyze_file_content(content, file_path.name)
                    file_info.update(content_analysis)
            
            elif file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                # Image analysis
                image_analysis = await self._analyze_image_file(file_path)
                file_info.update(image_analysis)
            
            return {
                "status": "success",
                "metadata": file_info,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Metadata extraction failed: {e}")
            return {"error": str(e), "status": "failed"}

    async def _analyze_file_content(self, content: str, filename: str) -> Dict[str, Any]:
        """Analyze file content for security relevance"""
        try:
            prompt = f"""Analyze this file for cybersecurity and pentesting relevance:

Filename: {filename}

Please provide:
1. Content type classification
2. Security relevance score (1-10)
3. Key cybersecurity topics identified
4. Potential use in penetration testing
5. Sensitive information indicators
6. Brief content summary

Content sample:
{content[:5000]}

Respond in JSON format."""
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            try:
                analysis = json.loads(response.text)
                return {
                    "content_analysis": analysis,
                    "content_length": len(content),
                    "word_count": len(content.split())
                }
            except json.JSONDecodeError:
                return {
                    "content_analysis": {"summary": response.text},
                    "content_length": len(content),
                    "word_count": len(content.split())
                }
                
        except Exception as e:
            return {"content_analysis_error": str(e)}

    async def _analyze_image_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze image files for cybersecurity content"""
        try:
            # Load and analyze image with Gemini Vision
            with open(file_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # Create image object for Gemini
            image = Image.open(file_path)
            
            prompt = """Analyze this image for cybersecurity and penetration testing content:

1. Does it contain:
   - Network diagrams
   - Screenshots of security tools
   - Vulnerability reports
   - Code snippets
   - System architecture
   - Security configurations

2. Extract any visible text
3. Identify security-relevant elements
4. Assess potential use in pentesting

Respond in JSON format."""
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                [prompt, image]
            )
            
            try:
                analysis = json.loads(response.text)
                return {"image_analysis": analysis}
            except json.JSONDecodeError:
                return {"image_analysis": {"summary": response.text}}
                
        except Exception as e:
            return {"image_analysis_error": str(e)}

    async def enhance_pentestgpt_query(self, query: str, context: str = "") -> str:
        """Enhance PentestGPT queries using Gemini's advanced reasoning"""
        self.logger.info(f"🔮 Enhancing PentestGPT query: {query[:50]}...")
        
        try:
            prompt = f"""You are an expert cybersecurity consultant enhancing penetration testing queries.

Original Query: {query}
Additional Context: {context}

Please enhance this query for better PentestGPT analysis by:

1. Adding specific technical details
2. Suggesting relevant attack vectors
3. Including appropriate tools and techniques
4. Providing structured analysis approach
5. Adding context for better understanding

Return an enhanced, more comprehensive penetration testing query that will yield better results from automated analysis tools.

Enhanced Query:"""
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            enhanced_query = response.text.strip()
            
            self.logger.info(f"✅ Query enhanced: {len(enhanced_query)} characters")
            return enhanced_query
            
        except Exception as e:
            self.logger.error(f"❌ Query enhancement failed: {e}")
            return query  # Return original query if enhancement fails

    async def process_vulnerability_report(self, file_path: str) -> Dict[str, Any]:
        """Process vulnerability reports and extract actionable intelligence"""
        self.logger.info(f"🛡️ Processing vulnerability report: {file_path}")
        
        try:
            content = await self._extract_document_content(Path(file_path))
            
            if not content:
                return {"error": "Failed to extract content from report"}
            
            # Analyze vulnerabilities
            vuln_analysis = await self._extract_vulnerability_data(content)
            
            # Generate remediation recommendations
            remediation = await self._generate_remediation_plan(vuln_analysis)
            
            result = {
                "status": "success",
                "file": file_path,
                "vulnerabilities": vuln_analysis.get('vulnerabilities', []),
                "severity_breakdown": vuln_analysis.get('severity_breakdown', {}),
                "affected_systems": vuln_analysis.get('affected_systems', []),
                "remediation_plan": remediation,
                "risk_score": vuln_analysis.get('risk_score', 0),
                "timestamp": datetime.now().isoformat()
            }
            
            # Save processed report
            output_file = self.processed_dir / f"vuln_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Vulnerability report processed: {len(vuln_analysis.get('vulnerabilities', []))} vulnerabilities found")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Vulnerability report processing failed: {e}")
            return {"error": str(e), "status": "failed"}

    async def _extract_vulnerability_data(self, content: str) -> Dict[str, Any]:
        """Extract structured vulnerability data from report content"""
        try:
            prompt = f"""Extract structured vulnerability data from this security report:

{content[:20000]}

Please extract and structure:
1. List of vulnerabilities with:
   - CVE IDs (if any)
   - Severity levels
   - Affected components
   - CVSS scores
   - Descriptions

2. Severity breakdown (Critical, High, Medium, Low counts)
3. Affected systems/services
4. Overall risk assessment
5. Timeline information

Return in JSON format with clear structure."""
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                # Fallback structure
                return {
                    "vulnerabilities": [],
                    "severity_breakdown": {},
                    "affected_systems": [],
                    "risk_score": 0,
                    "raw_analysis": response.text
                }
                
        except Exception as e:
            self.logger.error(f"Vulnerability extraction failed: {e}")
            return {"error": str(e)}

    async def _generate_remediation_plan(self, vuln_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate remediation plan based on vulnerability data"""
        try:
            prompt = f"""Generate a comprehensive remediation plan for these vulnerabilities:

Vulnerability Data:
{json.dumps(vuln_data, indent=2)}

Create a structured remediation plan including:
1. Priority order (based on risk)
2. Specific remediation steps for each vulnerability
3. Timeline estimates
4. Resource requirements
5. Verification methods
6. Preventive measures

Return in JSON format with actionable recommendations."""
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                return {
                    "remediation_summary": response.text,
                    "priority_actions": [],
                    "timeline": "Not specified"
                }
                
        except Exception as e:
            self.logger.error(f"Remediation plan generation failed: {e}")
            return {"error": str(e)}

async def main():
    """Test Gemini document processor"""
    print("🔮 Testing Gemini Document Processor...")
    
    # Load config
    with open('core/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    try:
        processor = GeminiDocumentProcessor(config)
        
        # Test query enhancement
        test_query = "How do I test for SQL injection in a web application?"
        enhanced = await processor.enhance_pentestgpt_query(test_query)
        print(f"Original: {test_query}")
        print(f"Enhanced: {enhanced}")
        
        print("✅ Gemini Document Processor test complete")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
