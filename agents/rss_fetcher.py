"""
RSS Feed Fetcher for Cybersecurity Intelligence
Fetches and processes security-related RSS feeds
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import re
import os

import feedparser
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from loguru import logger
import yaml

from rag_embedder import RAGEmbedder
from shared_utils import (
    ConfigManager, LoggerManager, GeminiClient,
    DirectoryManager, PromptTemplates
)

class RSSFetcher:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rss_feeds = config['rss_feeds']
        
        # Setup logging using shared utility
        LoggerManager.setup_logger('rss')
        
        # Initialize shared Gemini client
        self.gemini_client = GeminiClient()
        
        # Initialize RAG embedder
        self.rag_embedder = RAGEmbedder(config)
        
        # Ensure data directories exist using shared utility
        DirectoryManager.ensure_directory("rag_data")
        self.data_dir = Path("rag_data")
        
        logger.info("📡 RSS Fetcher initialized with shared utilities")

    async def fetch_all_feeds(self) -> Dict[str, Any]:
        """Fetch and process all configured RSS feeds"""
        logger.info("Starting RSS feed collection...")
        
        total_articles = 0
        new_cves = 0
        security_news = 0
        research_items = 0
        highlights = []
        
        try:
            # Process each feed category
            for category, feeds in self.rss_feeds.items():
                logger.info(f"Processing {category} feeds...")
                
                for feed_config in feeds:
                    try:
                        articles = await self._fetch_and_process_feed(feed_config)
                        
                        # Update counters
                        total_articles += len(articles)
                        
                        for article in articles:
                            if article['category'] == 'vulnerabilities':
                                new_cves += 1
                            elif article['category'] == 'news':
                                security_news += 1
                            elif article['category'] == 'research':
                                research_items += 1
                            
                            # Add interesting articles to highlights
                            if article.get('security_score', 0) >= 7:
                                highlights.append({
                                    'title': article['title'],
                                    'source': article['source'],
                                    'score': article['security_score']
                                })
                    
                    except Exception as e:
                        logger.error(f"Failed to process feed {feed_config['name']}: {e}")
                        continue
            
            # Sort highlights by score
            highlights.sort(key=lambda x: x['score'], reverse=True)
            highlights = highlights[:5]  # Top 5 highlights
            
            result = {
                'total_articles': total_articles,
                'new_cves': new_cves,
                'security_news': security_news,
                'research_items': research_items,
                'highlights': self._format_highlights(highlights),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"RSS collection complete: {total_articles} articles processed")
            return result
            
        except Exception as e:
            logger.error(f"RSS feed collection failed: {e}")
            raise

    async def _fetch_and_process_feed(self, feed_config: Dict[str, str]) -> List[Dict[str, Any]]:
        """Fetch and process a single RSS feed"""
        feed_name = feed_config['name']
        feed_url = feed_config['url']
        category = feed_config['category']
        
        logger.info(f"Fetching feed: {feed_name}")
        
        try:
            # Fetch RSS feed
            response = requests.get(feed_url, timeout=30)
            response.raise_for_status()
            
            # Parse RSS feed
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                logger.warning(f"No entries found in feed: {feed_name}")
                return []
            
            articles = []
            max_articles = self.config.get('rss_fetch_max_articles', 50)
            
            for entry in feed.entries[:max_articles]:
                try:
                    article = await self._process_feed_entry(entry, feed_name, category)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.error(f"Failed to process entry from {feed_name}: {e}")
                    continue
            
            logger.info(f"Processed {len(articles)} articles from {feed_name}")
            return articles
            
        except Exception as e:
            logger.error(f"Failed to fetch feed {feed_name}: {e}")
            raise

    async def _process_feed_entry(self, entry: Any, source: str, category: str) -> Optional[Dict[str, Any]]:
        """Process a single RSS feed entry"""
        try:
            # Extract basic information
            title = entry.get('title', 'No title')
            link = entry.get('link', '')
            published = entry.get('published', '')
            summary = entry.get('summary', entry.get('description', ''))
            
            # Create unique ID for deduplication
            content_hash = hashlib.md5(f"{title}{link}".encode()).hexdigest()
            
            # Check if we've already processed this article
            if await self._is_duplicate_article(content_hash):
                return None
            
            # Extract full content if possible
            full_content = await self._extract_full_content(link, summary)
            
            # Classify and analyze content using AI
            if self.gemini_client.is_available:
                analysis = await self._analyze_content_with_ai(title, full_content, category)
            else:
                analysis = self._basic_content_analysis(title, full_content, category)
            
            # Extract CVE numbers and other security identifiers
            security_identifiers = self._extract_security_identifiers(title + " " + full_content)
            
            article = {
                'id': content_hash,
                'title': title,
                'url': link,
                'source': source,
                'category': category,
                'published': published,
                'summary': analysis['summary'],
                'classification': analysis['classification'],
                'tags': analysis['tags'],
                'security_score': analysis['security_score'],
                'security_identifiers': security_identifiers,
                'content': full_content[:2000],  # Limit content size
                'processed_at': datetime.now().isoformat()
            }
            
            # Save to RAG database
            await self._save_to_rag(article)
            
            # Save to JSON file
            await self._save_article_json(article)
            
            return article
            
        except Exception as e:
            logger.error(f"Failed to process entry: {e}")
            return None

    async def _extract_full_content(self, url: str, fallback_summary: str) -> str:
        """Extract full article content from URL"""
        if not url:
            return fallback_summary
        
        try:
            response = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to find main content
            content_selectors = [
                'article', '.article-content', '.post-content', 
                '.entry-content', '.content', 'main', '.main'
            ]
            
            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text()
                    break
            
            if not content:
                content = soup.get_text()
            
            # Clean up content
            content = re.sub(r'\s+', ' ', content).strip()
            
            return content[:5000] if content else fallback_summary  # Limit content length
            
        except Exception as e:
            logger.debug(f"Failed to extract content from {url}: {e}")
            return fallback_summary

    async def _analyze_content_with_ai(self, title: str, content: str, category: str) -> Dict[str, Any]:
        """Analyze content using shared Gemini client"""
        try:
            analysis_prompt = f"""
Analyze this cybersecurity article and provide structured information:

Title: {title}
Category: {category}
Content: {content[:2000]}

Please provide analysis in this JSON format:
{{
  "summary": "2-3 sentence summary highlighting key security insights",
  "classification": "specific subcategory (e.g., 'sql_injection', 'ransomware', 'zero_day')",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "security_score": 8,
  "threat_level": "HIGH/MEDIUM/LOW",
  "affected_systems": ["system1", "system2"],
  "indicators": ["ioc1", "ioc2"]
}}

Security score (1-10): Rate the importance/severity for cybersecurity professionals.
Tags should include: vulnerability types, affected technologies, attack methods, etc.
            """
            
            if self.gemini_client.is_available:
                response = await self.gemini_client.generate_content(
                    analysis_prompt,
                    temperature=0.3,
                    max_tokens=1000
                )
            else:
                return self._basic_content_analysis(title, content, category)
            
            # Parse JSON response
            try:
                analysis = json.loads(response)
                return analysis
            except json.JSONDecodeError:
                return self._basic_content_analysis(title, content, category)
                
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._basic_content_analysis(title, content, category)

    def _basic_content_analysis(self, title: str, content: str, category: str) -> Dict[str, Any]:
        """Basic content analysis without AI"""
        # Extract keywords
        security_keywords = [
            'vulnerability', 'exploit', 'malware', 'ransomware', 'phishing',
            'zero-day', 'CVE', 'patch', 'security', 'attack', 'breach',
            'trojan', 'backdoor', 'SQL injection', 'XSS', 'CSRF'
        ]
        
        text_lower = (title + " " + content).lower()
        found_keywords = [kw for kw in security_keywords if kw.lower() in text_lower]
        
        # Calculate basic security score
        security_score = min(len(found_keywords) + 3, 10)
        
        return {
            'summary': title + ". " + content[:200] + "...",
            'classification': category,
            'tags': found_keywords[:5],
            'security_score': security_score,
            'threat_level': 'MEDIUM' if security_score >= 6 else 'LOW',
            'affected_systems': [],
            'indicators': []
        }

    def _extract_security_identifiers(self, text: str) -> List[str]:
        """Extract CVE numbers and other security identifiers"""
        identifiers = []
        
        # CVE pattern
        cve_pattern = r'CVE-\d{4}-\d{4,7}'
        cves = re.findall(cve_pattern, text, re.IGNORECASE)
        identifiers.extend(cves)
        
        # CWE pattern
        cwe_pattern = r'CWE-\d{1,4}'
        cwes = re.findall(cwe_pattern, text, re.IGNORECASE)
        identifiers.extend(cwes)
        
        # CAPEC pattern
        capec_pattern = r'CAPEC-\d{1,4}'
        capecs = re.findall(capec_pattern, text, re.IGNORECASE)
        identifiers.extend(capecs)
        
        return list(set(identifiers))  # Remove duplicates

    async def _is_duplicate_article(self, content_hash: str) -> bool:
        """Check if article has already been processed"""
        duplicate_file = self.data_dir / "processed_hashes.txt"
        
        if not duplicate_file.exists():
            return False
        
        with open(duplicate_file, 'r') as f:
            processed_hashes = f.read().splitlines()
        
        return content_hash in processed_hashes

    async def _save_to_rag(self, article: Dict[str, Any]):
        """Save article to RAG database"""
        try:
            await self.rag_embedder.add_document(
                content=article['content'],
                metadata={
                    'title': article['title'],
                    'source': article['source'],
                    'category': article['category'],
                    'tags': article['tags'],
                    'security_score': article['security_score'],
                    'url': article['url']
                },
                collection=article['category']
            )
        except Exception as e:
            logger.error(f"Failed to save to RAG: {e}")

    async def _save_article_json(self, article: Dict[str, Any]):
        """Save article to JSON file"""
        try:
            # Create category directory
            category_dir = self.data_dir / article['category']
            category_dir.mkdir(exist_ok=True)
            
            # Save article
            filename = f"{article['id']}_{datetime.now().strftime('%Y%m%d')}.json"
            filepath = category_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(article, f, indent=2, default=str)
            
            # Update processed hashes
            duplicate_file = self.data_dir / "processed_hashes.txt"
            with open(duplicate_file, 'a') as f:
                f.write(f"{article['id']}\n")
                
        except Exception as e:
            logger.error(f"Failed to save article JSON: {e}")

    def _format_highlights(self, highlights: List[Dict[str, Any]]) -> str:
        """Format highlights for display"""
        if not highlights:
            return "No significant highlights found."
        
        formatted = []
        for i, highlight in enumerate(highlights, 1):
            formatted.append(
                f"{i}. **{highlight['title']}** "
                f"(Score: {highlight['score']}/10) - {highlight['source']}"
            )
        
        return "\n".join(formatted)

    async def fetch_specific_feed(self, feed_name: str) -> Dict[str, Any]:
        """Fetch a specific RSS feed by name"""
        for category, feeds in self.rss_feeds.items():
            for feed_config in feeds:
                if feed_config['name'] == feed_name:
                    articles = await self._fetch_and_process_feed(feed_config)
                    return {
                        'feed_name': feed_name,
                        'articles': articles,
                        'count': len(articles),
                        'timestamp': datetime.now().isoformat()
                    }
        
        raise ValueError(f"Feed '{feed_name}' not found in configuration")

    async def get_feed_statistics(self) -> Dict[str, Any]:
        """Get statistics about processed feeds"""
        stats = {
            'total_articles': 0,
            'articles_by_category': {},
            'articles_by_source': {},
            'processing_dates': [],
            'security_score_distribution': {
                'high': 0,   # 8-10
                'medium': 0, # 5-7
                'low': 0     # 1-4
            }
        }
        
        # Count articles in each category
        for category_dir in self.data_dir.iterdir():
            if category_dir.is_dir() and category_dir.name != 'chroma_db':
                category_articles = list(category_dir.glob('*.json'))
                stats['articles_by_category'][category_dir.name] = len(category_articles)
                stats['total_articles'] += len(category_articles)
                
                # Analyze security scores
                for article_file in category_articles:
                    try:
                        with open(article_file, 'r') as f:
                            article = json.load(f)
                            score = article.get('security_score', 0)
                            source = article.get('source', 'unknown')
                            
                            # Update source count
                            stats['articles_by_source'][source] = stats['articles_by_source'].get(source, 0) + 1
                            
                            # Update score distribution
                            if score >= 8:
                                stats['security_score_distribution']['high'] += 1
                            elif score >= 5:
                                stats['security_score_distribution']['medium'] += 1
                            else:
                                stats['security_score_distribution']['low'] += 1
                                
                    except Exception as e:
                        logger.error(f"Failed to analyze article {article_file}: {e}")
        
        return stats

if __name__ == "__main__":
    # Test the RSS fetcher
    async def test_rss_fetcher():
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        fetcher = RSSFetcher(config)
        
        # Test fetching all feeds
        results = await fetcher.fetch_all_feeds()
        print(f"Fetched {results['total_articles']} articles")
        
        # Get statistics
        stats = await fetcher.get_feed_statistics()
        print(f"Total articles in database: {stats['total_articles']}")
    
    # Uncomment to test
    # asyncio.run(test_rss_fetcher())
