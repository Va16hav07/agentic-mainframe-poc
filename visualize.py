#!/usr/bin/env python3

import os
import sys
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def check_requirements():
    """Check if required packages are installed"""
    try:
        import matplotlib
        import sklearn
        print("✓ Required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        return False

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib", "scikit-learn"])
        print("✓ Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install packages: {e}")
        return False

def create_static_directory():
    """Create static directory if not exists"""
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        print(f"Created static directory: {static_dir}")
    else:
        print(f"Static directory exists: {static_dir}")
    return static_dir

def create_placeholder_image():
    """Create a simple placeholder image for when visualizations aren't available."""
    static_dir = create_static_directory()
    placeholder_path = os.path.join(static_dir, "placeholder.png")
    
    try:
        # Create a basic matplotlib figure
        plt.figure(figsize=(8, 6))
        plt.text(0.5, 0.5, 'Visualization not available\nRun "python visualize.py" to generate',
                 horizontalalignment='center', verticalalignment='center', fontsize=14)
        plt.axis('off')
        plt.savefig(placeholder_path)
        plt.close()
        print(f"Created placeholder image at {placeholder_path}")
    except Exception as e:
        print(f"Error creating placeholder with matplotlib: {e}")
        # Create a simple text file as fallback
        with open(placeholder_path, "wb") as f:
            # Simple minimal valid PNG
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDAT\x08\x99c\xf8\x0f\x04\x00\x09\xfb\x03\xfd\x08\xbf\xef\xd6\x00\x00\x00\x00IEND\xaeB`\x82')

def create_sample_visualization():
    """Create a sample visualization using random data."""
    static_dir = create_static_directory()
    
    # Create random data points
    np.random.seed(42)  # For reproducibility
    num_points = 20
    x = np.random.rand(num_points)
    y = np.random.rand(num_points)
    
    # Create random labels
    labels = [f"Doc {i+1}" for i in range(num_points)]
    
    # Create a simple PCA plot
    plt.figure(figsize=(10, 8))
    plt.scatter(x, y, s=50, alpha=0.7)
    
    # Add labels to some points
    for i in range(num_points):
        if i % 3 == 0:  # Label every 3rd point
            plt.annotate(labels[i], (x[i], y[i]), fontsize=9)
    
    plt.title('Sample PCA Visualization')
    plt.xlabel('Dimension 1')
    plt.ylabel('Dimension 2')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    # Save to static directory
    pca_path = os.path.join(static_dir, "vector_visualization_pca.png")
    plt.savefig(pca_path)
    plt.close()
    print(f"Created sample PCA visualization at {pca_path}")
    
    # Create a simple t-SNE plot (slightly different arrangement)
    plt.figure(figsize=(10, 8))
    # Add some slight non-linearity to make it look different from PCA
    x2 = x + 0.1 * np.sin(5 * x)
    y2 = y + 0.1 * np.cos(5 * y)
    plt.scatter(x2, y2, s=50, alpha=0.7, c=x+y, cmap='viridis')
    
    # Add labels to some points
    for i in range(num_points):
        if i % 4 == 0:  # Label every 4th point
            plt.annotate(labels[i], (x2[i], y2[i]), fontsize=9)
    
    plt.title('Sample t-SNE Visualization')
    plt.xlabel('Dimension 1')
    plt.ylabel('Dimension 2')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    
    # Save to static directory
    tsne_path = os.path.join(static_dir, "vector_visualization_tsne.png")
    plt.savefig(tsne_path)
    plt.close()
    print(f"Created sample t-SNE visualization at {tsne_path}")

def run_vector_explorer():
    """Try running the vector_explorer.py script."""
    try:
        print("Attempting to run vector_explorer.py...")
        
        # First try PCA
        subprocess.run(
            [sys.executable, "vector_explorer.py", "--visualize", "documents", "--method", "pca"],
            check=True,
            timeout=60  # Set a timeout in case it hangs
        )
        
        # Then try t-SNE
        subprocess.run(
            [sys.executable, "vector_explorer.py", "--visualize", "documents", "--method", "tsne"],
            check=True,
            timeout=120  # t-SNE may take longer
        )
        
        print("Successfully ran vector_explorer.py")
        return True
    except Exception as e:
        print(f"Error running vector_explorer.py: {e}")
        return False

def main():
    print("=" * 60)
    print("Vector Visualization Setup")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        print("\nMissing required packages. Attempting to install...")
        if not install_requirements():
            print("\nUnable to install required packages. Please install manually with:")
            print("pip install matplotlib scikit-learn")
            return
    
    # Create static directory
    static_dir = create_static_directory()
    
    # Create placeholder image
    create_placeholder_image()
    
    # Try to run vector_explorer.py first
    if run_vector_explorer():
        print("\nVisualization completed using vector_explorer.py")
    else:
        # If that fails, create sample visualizations
        print("\nFalling back to sample visualizations...")
        create_sample_visualization()
    
    # Check if files exist
    pca_path = os.path.join(static_dir, "vector_visualization_pca.png")
    tsne_path = os.path.join(static_dir, "vector_visualization_tsne.png")
    
    print("\n=== Visualization Status ===")
    print(f"PCA visualization: {'EXISTS' if os.path.exists(pca_path) else 'MISSING'}")
    print(f"t-SNE visualization: {'EXISTS' if os.path.exists(tsne_path) else 'MISSING'}")
    
    print(f"\nView visualizations at: http://localhost:8000/static/visualize.html")
    print("\n============================\n")

if __name__ == "__main__":
    main()
