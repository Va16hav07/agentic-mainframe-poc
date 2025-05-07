import os
import chromadb
from chromadb.utils import embedding_functions

class ChromaVectorStore:
    def __init__(self, embedding_function, collection_name="documents", persist_directory="./chroma_db"):
        # Ensure the persist directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Use custom embedding function
        self.embedding_function = embedding_function
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
        
        # Store document text for retrieval
        self.documents = {}
    
    def add_document(self, document_id, document_text, metadata=None):
        """Add a document to the vector store."""
        # Store the document text
        self.documents[document_id] = document_text
        
        # Add the document to the collection
        self.collection.add(
            ids=[document_id],
            documents=[document_text],
            metadatas=[metadata or {}]
        )
        
        return document_id
    
    def search(self, query_text, top_k=5):
        """Search for documents similar to the query text."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        
        # Process and return results
        processed_results = []
        if results and len(results['ids']) > 0:
            for i, doc_id in enumerate(results['ids'][0]):
                score = results['distances'][0][i] if 'distances' in results and results['distances'] else 0.0
                metadata = results['metadatas'][0][i] if 'metadatas' in results else {}
                doc_text = self.documents.get(doc_id, "Document text not found")
                
                processed_results.append((doc_id, score, metadata, doc_text))
        
        return processed_results
