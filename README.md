# Vector Search Document Demo

A demonstration application for document indexing and semantic search using transformer-based embeddings.

## Overview

This project demonstrates how to build a simple yet powerful document search system using:
- FastAPI for the backend API
- Hugging Face's DistilBERT model for generating document embeddings
- ChromaDB as a vector store for similarity search
- A clean web interface for document upload and search

## Features

- Upload text and COBOL documents (.txt, .cbl, .cobol)
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
- `embeddings.py`: DistilBERT embedding generation logic
- `vector_store.py`: ChromaDB integration for vector storage and search
- `templates/`: HTML templates for the web interface
- `static/`: CSS, JavaScript, and other static assets
- `requirements.txt`: Project dependencies

## Technical Details

- Embeddings are generated using DistilBERT's [CLS] token representation
- ChromaDB is used for efficient similarity search with cosine distance
- The application uses asynchronous API endpoints for better performance

## License

This project is licensed under the MIT License - see the LICENSE file for details.
