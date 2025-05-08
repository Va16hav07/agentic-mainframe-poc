# Vector Search Document Demo

A demonstration application for document indexing and semantic search using transformer-based embeddings.

## Overview

This project demonstrates how to build a simple yet powerful document search system using:
- FastAPI for the backend API
- Hugging Face's DistilBERT model for generating document embeddings
- ChromaDB as a vector store for similarity search
- A clean web interface for document upload and search

## Features

- Upload text and COBOL documents (.txt, .cbl, .cobol, .cob)
- Generate embeddings from document content using DistilBERT
- Store and index document embeddings in a vector database
- Perform semantic search across indexed documents
- Retrieve the most relevant documents for any search query

## Installation

### Prerequisites

- Python 3.8 or higher
- Git

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/agentic-mainframe-poc.git
cd agentic-mainframe-poc
```

2. Make the setup script executable:
```bash
chmod +x setup.sh
```

3. Run the setup script to create a virtual environment and install dependencies:
```bash
./setup.sh
```

### Manual Setup (Alternative)

If you prefer to set up manually:

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Activate the virtual environment (if not already activated):
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Start the application:
```bash
python -m uvicorn main:app --reload
```

3. Open your web browser and navigate to http://localhost:8000

## Usage

### Document Upload
1. Select a document (.txt, .cbl, .cobol) using the file picker.
2. Click "Upload and Index" to process the document.
3. Wait for confirmation that the document has been indexed.

### Searching Documents
1. Enter your search query in the text area.
2. Specify the number of results you want to retrieve.
3. Click "Search" to find relevant documents.
4. View search results with relevance scores and content previews.

## Project Structure

- `main.py`: FastAPI application and API endpoints
- `embeddings.py`: Embedding generation logic
- `vector_store.py`: ChromaDB integration for vector storage and search
- `templates/`: HTML templates for the web interface
- `static/`: CSS, JavaScript, and other static assets
- `requirements.txt`: Project dependencies
- `uploads/`: Directory where uploaded documents are stored
- `chroma_db/`: Directory where ChromaDB stores the vector index and document embeddings

## Technical Details

- Embeddings are generated using a deterministic hashing approach for reliability
- ChromaDB is used for efficient similarity search with cosine distance
- The application uses asynchronous API endpoints for better performance
- Uploaded documents are stored in the `uploads/` directory with UUID-prefixed filenames
- The vector index and embeddings are stored in the `chroma_db/` directory

## Accessing Uploaded Documents

You can find your uploaded documents in two places:

1. **Original Files**: All uploaded files are stored in the `uploads/` directory with UUID-prefixed filenames for uniqueness.

2. **Vector Index**: The document embeddings and metadata are stored in the `chroma_db/` directory, managed by ChromaDB.

### Using the File Browser Utility

This project includes a file browser utility to help you explore uploaded documents:

```bash
# List all uploaded files
python file_browser.py

# View the content of a specific file (by index number)
python file_browser.py --view 1

# Explore the vector store contents
python file_browser.py --vector-store

# Test search functionality from the command line
python file_browser.py --search "your search query"

# Check if a specific file is properly indexed
python file_browser.py --test 1
```

### Troubleshooting "Document text not found" Messages

If search results display "Document text not found" instead of actual document content:

1. This happens because the document text wasn't properly cached in the vector store's memory.
2. Restart the application to reload the documents from disk.
3. For persistent document storage across restarts, you can use the file_browser.py tool to view the original documents:

```bash
# Find which file matches your search result
python file_browser.py

# View the full content of the document
python file_browser.py --view INDEX_NUMBER
```

The document content is always preserved in the `uploads/` directory, even if the in-memory cache doesn't contain it.

