import os
import matplotlib.pyplot as plt

def visualize_vectors(collection_name, method='pca'):
    """Visualize vector embeddings in 2D."""
    if not os.path.exists("./chroma_db"):
        print("ChromaDB directory not found.")
        return
    
    try:
        # Check if matplotlib and sklearn are available
        try:
            import matplotlib.pyplot as plt
            from sklearn.decomposition import PCA
            from sklearn.manifold import TSNE
        except ImportError:
            print("Visualization requires additional packages. Install them with:")
            print("pip install matplotlib scikit-learn")
            return
        
        # Make sure static directory exists
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
        os.makedirs(static_dir, exist_ok=True)
        
        client = chromadb.PersistentClient(path="./chroma_db")
        
        try:
            # Get the collection
            collection = client.get_collection(name=collection_name)
        except:
            print(f"Collection '{collection_name}' not found.")
            collections = client.list_collections()
            if collections:
                print("Available collections:")
                for col in collections:
                    print(f" - {col.name}")
            return
        
        # Get all items
        items = collection.get()
        
        if not items or 'embeddings' not in items or not items['embeddings']:
            print("No embeddings found in the collection.")
            return
        
        # Convert embeddings to numpy array
        embeddings = np.array(items['embeddings'])
        
        # Reduce dimensions
        if method.lower() == 'tsne':
            print("Reducing dimensions using t-SNE (this may take a while)...")
            reduced_data = TSNE(n_components=2, random_state=42).fit_transform(embeddings)
        else:  # default to PCA
            print("Reducing dimensions using PCA...")
            reduced_data = PCA(n_components=2, random_state=42).fit_transform(embeddings)
        
        # Create plot
        plt.figure(figsize=(10, 8))
        plt.scatter(reduced_data[:, 0], reduced_data[:, 1], alpha=0.6)
        
        # Add labels for some points
        for i, doc_id in enumerate(items['ids']):
            if i % max(1, len(items['ids']) // 10) == 0:  # Label ~10 points
                filename = ""
                if 'metadatas' in items and items['metadatas'] and i < len(items['metadatas']):
                    metadata = items['metadatas'][i] or {}
                    filename = metadata.get('filename', '')
                plt.annotate(
                    filename or f'doc_{i}',
                    (reduced_data[i, 0], reduced_data[i, 1]),
                    fontsize=9
                )
        
        plt.title(f'Document Embeddings Visualization ({method.upper()})')
        plt.xlabel('Dimension 1')
        plt.ylabel('Dimension 2')
        plt.tight_layout()
        
        # Save to both locations - static directory for web and current for CLI
        static_output_file = os.path.join(static_dir, f"vector_visualization_{method}.png")
        plt.savefig(static_output_file)
        plt.savefig(f"vector_visualization_{method}.png")
        
        print(f"Visualization saved to static directory: {static_output_file}")
        print(f"Visualization also saved to current directory: vector_visualization_{method}.png")
        
        # Check if we're in an interactive environment that can show plots
        import sys
        if not (hasattr(sys, 'ps1') or not sys.stderr.isatty()):
            print("Running in non-interactive mode; skipping plot display")
        else:
            plt.show()
    
    except Exception as e:
        print(f"Error visualizing vectors: {str(e)}")
        import traceback
        traceback.print_exc()