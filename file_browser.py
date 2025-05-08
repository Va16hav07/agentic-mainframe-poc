#!/usr/bin/env python3

import os
import sys
import json
import argparse
from datetime import datetime
import chromadb
import numpy as np

def list_uploads():
    """List all uploaded files."""
    upload_dir = "./uploads"
    
    if not os.path.exists(upload_dir):
        print(f"Upload directory '{upload_dir}' does not exist.")
        return
    
    files = os.listdir(upload_dir)
    
    if not files:
        print("No uploaded files found.")
        return
    
    print(f"Found {len(files)} uploaded files:")
    print("-" * 80)
    
    for i, filename in enumerate(files, 1):
        file_path = os.path.join(upload_dir, filename)
        size = os.path.getsize(file_path)
        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        # Try to get the original filename (after the UUID)
        parts = filename.split("_", 1)
        original_name = parts[1] if len(parts) > 1 else filename
        
        print(f"{i}. {original_name}")
        print(f"   UUID: {parts[0] if len(parts) > 1 else 'N/A'}")
        print(f"   Path: {file_path}")
        print(f"   Size: {size} bytes")
        print(f"   Modified: {mod_time}")
        print("-" * 80)
        
def view_file(file_index):
    """View contents of a specific file."""
    upload_dir = "./uploads"
    
    if not os.path.exists(upload_dir):
        print(f"Upload directory '{upload_dir}' does not exist.")
        return
    
    files = os.listdir(upload_dir)
    
    if not files:
        print("No uploaded files found.")
        return
    
    try:
        index = int(file_index) - 1
        if index < 0 or index >= len(files):
            print(f"Invalid file index. Choose between 1 and {len(files)}")
            return
        
        filename = files[index]
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        print(f"Contents of {filename}:")
        print("=" * 80)
        print(content[:1000] + "..." if len(content) > 1000 else content)
        print("=" * 80)
        
    except ValueError:
        print("Please provide a valid file index number.")
    except Exception as e:
        print(f"Error reading file: {str(e)}")

def explore_vector_store():
    """Explore the vector store contents."""
    db_dir = "./chroma_db"
    
    if not os.path.exists(db_dir):
        print(f"Vector store directory '{db_dir}' does not exist.")
        return
        
    try:
        # Connect to ChromaDB
        client = chromadb.PersistentClient(path=db_dir)
        
        # Get available collections
        collections = client.list_collections()
        
        if not collections:
            print("No collections found in the vector store.")
            return
            
        print(f"Found {len(collections)} collections in the vector store:")
        print("-" * 80)
        
        for i, collection in enumerate(collections, 1):
            collection_name = collection.name
            
            # Get the collection
            col = client.get_collection(name=collection_name)
            
            # Count items in collection
            count = col.count()
            
            print(f"{i}. Collection: {collection_name}")
            print(f"   Item count: {count}")
            
            # Get a sample of items
            if count > 0:
                try:
                    sample = col.peek(limit=5)
                    print(f"   Sample IDs: {', '.join(sample['ids'][:3])}...")
                    print(f"   Sample has {len(sample['documents'])} documents")
                except Exception as e:
                    print(f"   Error getting sample: {str(e)}")
                    
            print("-" * 80)
    
    except Exception as e:
        print(f"Error exploring vector store: {str(e)}")

def test_search(query, limit=5):
    """Test search functionality with a query."""
    from vector_store import ChromaVectorStore
    from embeddings import EmbeddingGenerator
    
    try:
        print(f"Searching for: '{query}' (limit: {limit})")
        print("-" * 80)
        
        # Initialize components
        embedding_generator = EmbeddingGenerator()
        vector_store = ChromaVectorStore(
            embedding_function=embedding_generator,
            collection_name="documents",
            persist_directory="./chroma_db"
        )
        
        # Perform search
        results = vector_store.search(query, top_k=limit)
        
        if not results:
            print("No matching documents found.")
            return
            
        print(f"Found {len(results)} results:")
        print("-" * 80)
        
        for i, (doc_id, score, metadata, doc_text) in enumerate(results, 1):
            filename = metadata.get("filename", "Unknown")
            preview = doc_text[:200] + "..." if len(doc_text) > 200 else doc_text
            
            print(f"Result {i}: {filename} (ID: {doc_id})")
            print(f"Score: {score:.4f}")
            print(f"Preview: {preview}")
            print("-" * 80)
            
    except Exception as e:
        print(f"Error testing search: {str(e)}")
        import traceback
        traceback.print_exc()

def get_test_status(file_path):
    """Check if a file is properly indexed and searchable."""
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Get some words to use as search terms
        words = [word for word in content.split() if len(word) > 5]
        if not words:
            return "UNKNOWN", "No suitable search terms found in the file"
        
        # Pick a random word to use as a search term
        import random
        search_term = random.choice(words[:20])
        
        # Try to search for this term
        from vector_store import ChromaVectorStore
        from embeddings import EmbeddingGenerator
        
        # Initialize components
        embedding_generator = EmbeddingGenerator()
        vector_store = ChromaVectorStore(
            embedding_function=embedding_generator,
            collection_name="documents",
            persist_directory="./chroma_db"
        )
        
        # Perform search
        results = vector_store.search(search_term, top_k=5)
        
        # Check if the file is in the results
        filename = os.path.basename(file_path)
        found = False
        for _, _, metadata, _ in results:
            if metadata.get("filename", "") == filename or metadata.get("file_path", "").endswith(filename):
                found = True
                break
        
        if found:
            return "OK", f"File is indexed and searchable. Search term '{search_term}' returned this document."
        else:
            return "NOT FOUND", f"File appears to be indexed but search for '{search_term}' did not return this document."
            
    except Exception as e:
        return "ERROR", f"Error testing file: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Browse uploaded files and vector index")
    parser.add_argument("--view", "-v", type=str, help="View contents of a file by index")
    parser.add_argument("--vector-store", "-vs", action="store_true", help="Explore vector store contents")
    parser.add_argument("--search", "-s", type=str, help="Test search with a query")
    parser.add_argument("--limit", "-l", type=int, default=5, help="Number of search results to return")
    parser.add_argument("--test", "-t", type=str, help="Test if a specific file is properly indexed")
    
    args = parser.parse_args()
    
    if args.view:
        view_file(args.view)
    elif args.vector_store:
        explore_vector_store()
    elif args.search:
        test_search(args.search, args.limit)
    elif args.test:
        try:
            index = int(args.test)
            files = os.listdir("./uploads")
            if index < 1 or index > len(files):
                print(f"Invalid file index. Choose between 1 and {len(files)}")
                return
                
            file_path = os.path.join("./uploads", files[index-1])
        except ValueError:
            # Assume it's a file path
            file_path = args.test
            
        status, message = get_test_status(file_path)
        print(f"Status: {status}")
        print(f"Message: {message}")
    else:
        list_uploads()

if __name__ == "__main__":
    main()
