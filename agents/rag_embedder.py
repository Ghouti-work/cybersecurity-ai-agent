"""
RAG Embedder for Cybersecurity Knowledge Base
Handles vector embeddings and ChromaDB storage
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
from loguru import logger
import yaml

from shared_utils import ConfigManager, LoggerManager, DirectoryManager

class RAGEmbedder:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or ConfigManager.get_instance().config
        self.embedding_model_name = self.config['rag']['embedding_model']
        self.chunk_size = self.config['rag']['chunk_size']
        self.chunk_overlap = self.config['rag']['chunk_overlap']
        self.similarity_threshold = self.config['rag']['similarity_threshold']
        self.max_results = self.config['rag']['max_results']
        
        self.logger = LoggerManager.setup_logger('rag')
        
        # Initialize embedding model
        self.embedding_model = None
        self._initialize_embedding_model()
        
        # Initialize ChromaDB
        self.chroma_client = None
        self.collections = {}
        self._initialize_chromadb()
        
        # Setup RAG directories
        DirectoryManager.ensure_directory("rag_data")
        DirectoryManager.ensure_directory("rag_data/chroma_db")
        DirectoryManager.ensure_directory("rag_data/embeddings")
        
        self.logger.info("📚 RAG Embedder initialized")

    async def initialize(self):
        """Async initialization method for compatibility with main platform"""
        try:
            # Ensure embedding model is loaded
            if self.embedding_model is None:
                self._initialize_embedding_model()
            
            # Ensure ChromaDB is initialized
            if self.chroma_client is None:
                self._initialize_chromadb()
            
            self.logger.info("✅ RAG Embedder async initialization complete")
            return True
        except Exception as e:
            self.logger.error(f"❌ RAG Embedder initialization failed: {e}")
            return False

    def _initialize_embedding_model(self):
        """Initialize the sentence transformer model"""
        try:
            self.logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            self.logger.info("Embedding model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load embedding model: {e}")
            raise

    def _initialize_chromadb(self):
        """Initialize ChromaDB client and collections"""
        try:
            # Create ChromaDB directory
            chroma_db_path = Path(self.config.get('chroma_db_path', './rag_data/chroma_db'))
            chroma_db_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=str(chroma_db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Initialize collections for each category
            collection_configs = self.config['rag']['collections']
            for collection_name, description in collection_configs.items():
                try:
                    collection = self.chroma_client.get_or_create_collection(
                        name=collection_name,
                        metadata={"description": description}
                    )
                    self.collections[collection_name] = collection
                    self.logger.info(f"Initialized collection: {collection_name}")
                except Exception as e:
                    self.logger.error(f"Failed to initialize collection {collection_name}: {e}")
            
            self.logger.info("ChromaDB initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    async def add_document(self, content: str, metadata: Dict[str, Any], collection: str = "general") -> str:
        """Add a document to the RAG database"""
        try:
            # Generate document ID
            doc_id = self._generate_document_id(content, metadata)
            
            # Check if document already exists
            if await self._document_exists(doc_id, collection):
                self.logger.debug(f"Document already exists: {doc_id}")
                return doc_id
            
            # Generate embeddings
            embeddings = await self._generate_embeddings(content)
            
            # Prepare metadata
            processed_metadata = self._prepare_metadata(metadata)
            
            # Get or create collection
            if collection not in self.collections:
                collection_obj = self.chroma_client.get_or_create_collection(
                    name=collection,
                    metadata={"description": f"Auto-created collection for {collection}"}
                )
                self.collections[collection] = collection_obj
            else:
                collection_obj = self.collections[collection]
            
            # Add document to ChromaDB
            collection_obj.add(
                documents=[content],
                embeddings=[embeddings.tolist()],
                metadatas=[processed_metadata],
                ids=[doc_id]
            )
            
            self.logger.info(f"Added document to {collection}: {doc_id}")
            return doc_id
            
        except Exception as e:
            self.logger.error(f"Failed to add document: {e}")
            raise

    async def search_similar(self, query: str, collection: str = None, n_results: int = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            if n_results is None:
                n_results = self.max_results
            
            # Generate query embeddings
            query_embeddings = await self._generate_embeddings(query)
            
            results = []
            
            # Search in specific collection or all collections
            collections_to_search = [collection] if collection and collection in self.collections else self.collections.keys()
            
            for coll_name in collections_to_search:
                collection_obj = self.collections[coll_name]
                
                # Perform similarity search
                search_results = collection_obj.query(
                    query_embeddings=[query_embeddings.tolist()],
                    n_results=min(n_results, collection_obj.count()),
                    include=['documents', 'metadatas', 'distances']
                )
                
                # Process results
                for i in range(len(search_results['documents'][0])):
                    similarity_score = 1.0 - search_results['distances'][0][i]  # Convert distance to similarity
                    
                    if similarity_score >= self.similarity_threshold:
                        results.append({
                            'content': search_results['documents'][0][i],
                            'metadata': search_results['metadatas'][0][i],
                            'similarity_score': similarity_score,
                            'collection': coll_name
                        })
            
            # Sort by similarity score
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            self.logger.info(f"Found {len(results)} similar documents for query: {query[:50]}...")
            return results[:n_results]
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            raise

    async def search_by_category(self, category: str, query: str = None, n_results: int = None) -> List[Dict[str, Any]]:
        """Search documents by category"""
        try:
            if n_results is None:
                n_results = self.max_results
            
            if category not in self.collections:
                logger.warning(f"Category not found: {category}")
                return []
            
            collection_obj = self.collections[category]
            
            if query:
                # Search with query
                query_embeddings = await self._generate_embeddings(query)
                search_results = collection_obj.query(
                    query_embeddings=[query_embeddings.tolist()],
                    n_results=min(n_results, collection_obj.count()),
                    include=['documents', 'metadatas', 'distances']
                )
                
                results = []
                for i in range(len(search_results['documents'][0])):
                    similarity_score = 1.0 - search_results['distances'][0][i]
                    results.append({
                        'content': search_results['documents'][0][i],
                        'metadata': search_results['metadatas'][0][i],
                        'similarity_score': similarity_score,
                        'collection': category
                    })
                
                return results
            else:
                # Get all documents in category
                all_results = collection_obj.get(
                    limit=n_results,
                    include=['documents', 'metadatas']
                )
                
                results = []
                for i in range(len(all_results['documents'])):
                    results.append({
                        'content': all_results['documents'][i],
                        'metadata': all_results['metadatas'][i],
                        'similarity_score': 1.0,
                        'collection': category
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"Category search failed: {e}")
            raise

    async def search_by_tags(self, tags: List[str], collection: str = None) -> List[Dict[str, Any]]:
        """Search documents by tags"""
        try:
            results = []
            collections_to_search = [collection] if collection and collection in self.collections else self.collections.keys()
            
            for coll_name in collections_to_search:
                collection_obj = self.collections[coll_name]
                
                # Get all documents
                all_results = collection_obj.get(include=['documents', 'metadatas'])
                
                # Filter by tags
                for i, metadata in enumerate(all_results['metadatas']):
                    doc_tags = metadata.get('tags', [])
                    if isinstance(doc_tags, str):
                        doc_tags = [doc_tags]
                    
                    # Check if any of the search tags match document tags
                    if any(tag.lower() in [dt.lower() for dt in doc_tags] for tag in tags):
                        results.append({
                            'content': all_results['documents'][i],
                            'metadata': metadata,
                            'similarity_score': 1.0,
                            'collection': coll_name,
                            'matched_tags': [tag for tag in tags if tag.lower() in [dt.lower() for dt in doc_tags]]
                        })
            
            logger.info(f"Found {len(results)} documents matching tags: {tags}")
            return results
            
        except Exception as e:
            logger.error(f"Tag search failed: {e}")
            raise

    async def get_context_for_query(self, query: str, max_context_length: int = 2000) -> str:
        """Get relevant context for a query"""
        try:
            # Search for relevant documents
            relevant_docs = await self.search_similar(query, n_results=5)
            
            if not relevant_docs:
                return "No relevant context found."
            
            # Build context string
            context_parts = []
            current_length = 0
            
            for doc in relevant_docs:
                content = doc['content']
                metadata = doc['metadata']
                source_info = f"Source: {metadata.get('source', 'Unknown')} (Score: {doc['similarity_score']:.2f})"
                
                doc_text = f"{source_info}\n{content}\n---\n"
                
                if current_length + len(doc_text) <= max_context_length:
                    context_parts.append(doc_text)
                    current_length += len(doc_text)
                else:
                    # Add partial content if there's space
                    remaining_space = max_context_length - current_length - len(source_info) - 10
                    if remaining_space > 100:
                        partial_content = content[:remaining_space] + "..."
                        context_parts.append(f"{source_info}\n{partial_content}\n---\n")
                    break
            
            context = "\n".join(context_parts)
            logger.info(f"Generated context of {len(context)} characters for query")
            return context
            
        except Exception as e:
            logger.error(f"Context generation failed: {e}")
            return "Error generating context."

    async def _generate_embeddings(self, text: str) -> np.ndarray:
        """Generate embeddings for text"""
        try:
            # Run embedding generation in thread pool to avoid blocking
            embeddings = await asyncio.to_thread(self.embedding_model.encode, text)
            return embeddings
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise

    def _generate_document_id(self, content: str, metadata: Dict[str, Any]) -> str:
        """Generate unique document ID"""
        # Create ID based on content hash and key metadata
        id_string = content + str(metadata.get('filename', '')) + str(metadata.get('source', ''))
        return hashlib.md5(id_string.encode()).hexdigest()

    async def _document_exists(self, doc_id: str, collection: str) -> bool:
        """Check if document already exists in collection"""
        try:
            if collection not in self.collections:
                return False
            
            collection_obj = self.collections[collection]
            result = collection_obj.get(ids=[doc_id])
            return len(result['ids']) > 0
            
        except Exception as e:
            logger.debug(f"Document existence check failed: {e}")
            return False

    def _prepare_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare metadata for ChromaDB storage"""
        # ChromaDB requires string values for metadata
        processed_metadata = {}
        
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                processed_metadata[key] = str(value)
            elif isinstance(value, list):
                processed_metadata[key] = json.dumps(value)
            elif isinstance(value, dict):
                processed_metadata[key] = json.dumps(value)
            else:
                processed_metadata[key] = str(value)
        
        return processed_metadata

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about all collections"""
        stats = {
            'total_documents': 0,
            'collections': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            for coll_name, collection_obj in self.collections.items():
                count = collection_obj.count()
                stats['collections'][coll_name] = {
                    'document_count': count,
                    'description': collection_obj.metadata.get('description', 'No description')
                }
                stats['total_documents'] += count
            
            logger.info(f"RAG statistics: {stats['total_documents']} total documents")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return stats

    async def delete_document(self, doc_id: str, collection: str) -> bool:
        """Delete a document from collection"""
        try:
            if collection not in self.collections:
                logger.warning(f"Collection not found: {collection}")
                return False
            
            collection_obj = self.collections[collection]
            collection_obj.delete(ids=[doc_id])
            
            logger.info(f"Deleted document {doc_id} from {collection}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False

    async def update_document(self, doc_id: str, content: str, metadata: Dict[str, Any], collection: str) -> bool:
        """Update an existing document"""
        try:
            if collection not in self.collections:
                logger.warning(f"Collection not found: {collection}")
                return False
            
            # Delete old document
            await self.delete_document(doc_id, collection)
            
            # Add updated document
            await self.add_document(content, metadata, collection)
            
            logger.info(f"Updated document {doc_id} in {collection}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            return False

    async def clear_collection(self, collection: str) -> bool:
        """Clear all documents from a collection"""
        try:
            if collection not in self.collections:
                logger.warning(f"Collection not found: {collection}")
                return False
            
            # Delete and recreate collection
            self.chroma_client.delete_collection(collection)
            collection_obj = self.chroma_client.create_collection(collection)
            self.collections[collection] = collection_obj
            
            logger.info(f"Cleared collection: {collection}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False

    async def backup_collection(self, collection: str, backup_path: str) -> bool:
        """Backup a collection to JSON file"""
        try:
            if collection not in self.collections:
                logger.warning(f"Collection not found: {collection}")
                return False
            
            collection_obj = self.collections[collection]
            all_data = collection_obj.get(include=['documents', 'metadatas', 'embeddings'])
            
            backup_data = {
                'collection_name': collection,
                'timestamp': datetime.now().isoformat(),
                'document_count': len(all_data['documents']),
                'documents': all_data['documents'],
                'metadatas': all_data['metadatas'],
                'embeddings': all_data['embeddings']
            }
            
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            logger.info(f"Backed up collection {collection} to {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup collection: {e}")
            return False

if __name__ == "__main__":
    # Test the RAG embedder
    async def test_rag_embedder():
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        embedder = RAGEmbedder(config)
        
        # Test adding documents
        test_docs = [
            {
                'content': "SQL injection vulnerabilities allow attackers to manipulate database queries.",
                'metadata': {'source': 'test', 'category': 'web_security', 'tags': ['sql', 'injection', 'web']},
                'collection': 'vulnerabilities'
            },
            {
                'content': "Cross-site scripting (XSS) attacks inject malicious scripts into web pages.",
                'metadata': {'source': 'test', 'category': 'web_security', 'tags': ['xss', 'javascript', 'web']},
                'collection': 'vulnerabilities'
            }
        ]
        
        # Add test documents
        for doc in test_docs:
            doc_id = await embedder.add_document(
                doc['content'], 
                doc['metadata'], 
                doc['collection']
            )
            print(f"Added document: {doc_id}")
        
        # Test search
        results = await embedder.search_similar("web application security vulnerabilities")
        print(f"Found {len(results)} similar documents")
        for result in results:
            print(f"- {result['content'][:50]}... (Score: {result['similarity_score']:.2f})")
        
        # Get stats
        stats = await embedder.get_collection_stats()
        print(f"Total documents: {stats['total_documents']}")
    
    # Uncomment to test
    # asyncio.run(test_rag_embedder())
