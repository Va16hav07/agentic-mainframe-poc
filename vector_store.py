import os
import logging
import numpy as np
import chromadb
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

class CustomEmbeddingFunction:
    """A wrapper to ensure embeddings meet ChromaDB's requirements"""
    def __init__(self, embedding_function):
        self.embedding_function = embedding_function
    
    def __call__(self, texts: List[str]) -> List[List[float]]:
        try:
            # Generate embeddings
            embeddings = self.embedding_function(texts)
            
            # Convert each numpy array to a simple Python list
            python_lists = []
            for emb in embeddings:
                # Ensure it's a numpy array first
                if not isinstance(emb, np.ndarray):
                    emb = np.array(emb, dtype=np.float32)
                
                # Convert to Python list
                python_list = emb.tolist()
                python_lists.append(python_list)
                
            return python_lists
        except Exception as e:
            logger.error(f"Error in custom embedding function: {str(e)}")
            # Return default embedding lists as fallback
            dim = getattr(self.embedding_function, "embedding_dim", 768)
            return [[0.0] * dim for _ in texts]

class ChromaVectorStore:
    def __init__(self, embedding_function, collection_name="documents", persist_directory="./chroma_db"):
        # Ensure the persist directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
            logger.info(f"ChromaDB initialized with persist directory: {persist_directory}")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {str(e)}")
            raise
        
        # Wrap the embedding function to ensure compatibility
        self.embedding_function = CustomEmbeddingFunction(embedding_function)
        
        # Create or get collection
        try:
            try:
                self.collection = self.client.get_collection(name=collection_name)
                logger.info(f"Retrieved existing collection: {collection_name}")
            except Exception:
                self.collection = self.client.create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function
                )
                logger.info(f"Created new collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error creating/getting collection: {str(e)}")
            raise
        
        # Store document text for retrieval
        self.documents = {}
        
        # Try to load existing documents
        self._load_documents_from_collection()
    
    def _load_documents_from_collection(self):
        """Load existing documents from collection to the cache."""
        try:
            # Get all documents from the collection
            all_docs = self.collection.get()
            
            if all_docs and 'ids' in all_docs and all_docs['ids']:
                for i, doc_id in enumerate(all_docs['ids']):
                    # Get document text from the collection
                    if 'documents' in all_docs and i < len(all_docs['documents']):
                        doc_text = all_docs['documents'][i]
                        # Store in our cache
                        self.documents[doc_id] = doc_text
                        
                logger.info(f"Loaded {len(self.documents)} documents from collection")
        except Exception as e:
            logger.error(f"Error loading documents from collection: {str(e)}")
    
    def add_document(self, document_id: str, document_text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a document to the vector store."""
        if metadata is None:
            metadata = {}
            
        logger.info(f"Adding document to vector store: {document_id}")
        
        try:
            # Ensure document_text is a string
            if not isinstance(document_text, str):
                document_text = str(document_text)
            
            # Limit document size
            if len(document_text) > 50000:
                document_text = document_text[:50000]
                
            # Store the document text
            self.documents[document_id] = document_text
            
            # Add the document to the collection - use explicit embedding
            embeddings = self.embedding_function([document_text])
            
            self.collection.add(
                ids=[document_id],
                documents=[document_text],
                metadatas=[metadata],
                embeddings=embeddings
            )
            
            logger.info(f"Document added successfully: {document_id}")
            return document_id
        except Exception as e:
            logger.error(f"Error adding document to vector store: {str(e)}")
            raise
    
    def search(self, query_text: str, top_k: int = 5) -> List[Tuple[str, float, Dict[str, Any], str]]:
        """Search for documents similar to the query text."""
        logger.info(f"Searching for: '{query_text}' with top_k={top_k}")
        
        try:
            # Ensure the query is valid
            if not query_text or not isinstance(query_text, str):
                query_text = str(query_text) if query_text else "empty query"
            
            # Generate query embedding
            query_embeddings = self.embedding_function([query_text])
            
            # Execute search with explicit embedding
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=min(top_k, 20)
            )
            
            # Process and return results
            processed_results = []
            if results and 'ids' in results and results['ids'] and len(results['ids']) > 0:
                for i, doc_id in enumerate(results['ids'][0]):
                    # Get score
                    score = 0.0
                    if 'distances' in results and results['distances'] and i < len(results['distances'][0]):
                        score = float(results['distances'][0][i])
                    
                    # Get metadata
                    metadata = {}
                    if 'metadatas' in results and results['metadatas'] and i < len(results['metadatas'][0]):
                        metadata = results['metadatas'][0][i] or {}
                    
                    # Try to get document text from cache first
                    doc_text = self.documents.get(doc_id)
                    
                    # If not in cache, try to get from the collection directly
                    if doc_text is None or doc_text == "Document text not found":
                        try:
                            # Try to fetch the document from the collection by ID
                            doc_info = self.collection.get(ids=[doc_id])
                            if doc_info and 'documents' in doc_info and doc_info['documents']:
                                doc_text = doc_info['documents'][0]
                                # Update our cache
                                self.documents[doc_id] = doc_text
                            else:
                                # If still not found, check if there's a file path in metadata
                                if metadata and 'file_path' in metadata and os.path.exists(metadata['file_path']):
                                    with open(metadata['file_path'], 'r', encoding='utf-8', errors='ignore') as f:
                                        doc_text = f.read()
                                        # Update our cache
                                        self.documents[doc_id] = doc_text
                                else:
                                    doc_text = "Document text not found"
                        except:
                            doc_text = "Document text not found"
                    
                    processed_results.append((doc_id, score, metadata, doc_text))
                    
                logger.info(f"Search complete, found {len(processed_results)} results")
            else:
                logger.info("Search complete, no results found")
                
            return processed_results
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            raise
