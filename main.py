import os
import shutil
import tempfile
import uuid
import traceback
import logging
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules
from embeddings import EmbeddingGenerator
from vector_store import ChromaVectorStore, CustomEmbeddingFunction

# Create directories if they don't exist
os.makedirs("./uploads", exist_ok=True)
os.makedirs("./static", exist_ok=True)

app = FastAPI(title="Document Search API")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize embedding generator and vector store
try:
    # Create a simple embedding generator
    embedding_generator = EmbeddingGenerator()
    
    # Initialize vector store with our custom wrapper
    vector_store = ChromaVectorStore(
        embedding_function=embedding_generator,
        collection_name="documents",
        persist_directory="./chroma_db"
    )
    logger.info("Successfully initialized components")
except Exception as e:
    logger.error(f"Error initializing components: {str(e)}")
    logger.error(traceback.format_exc())
    raise

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    document_id: str
    document_name: str
    score: float
    preview: str

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."}
    )

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Check file type - add .cob extension to supported formats
    if not file.filename.lower().endswith(('.txt', '.cbl', '.cobol', '.cob')):
        raise HTTPException(status_code=400, detail="Only text and COBOL files (.txt, .cbl, .cobol, .cob) are supported")
    
    logger.info(f"Processing upload for {file.filename}")
    
    try:
        # Save file to disk
        file_path = os.path.join("uploads", f"{uuid.uuid4()}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Add to vector store
        vector_store.add_document(
            document_id=doc_id,
            document_text=content[:50000], # Limit size
            metadata={"filename": file.filename}
        )
        
        return {"message": "Document uploaded and indexed successfully", "document_id": doc_id}
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()

@app.post("/search", response_model=List[SearchResult])
async def search_documents(search_query: SearchQuery):
    try:
        results = vector_store.search(search_query.query, top_k=search_query.top_k)
        
        formatted_results = []
        for doc_id, score, metadata, doc_text in results:
            # Create preview
            preview = doc_text[:200] + "..." if len(doc_text) > 200 else doc_text
            
            formatted_results.append(
                SearchResult(
                    document_id=doc_id,
                    document_name=metadata.get("filename", "Unknown"),
                    score=float(score),
                    preview=preview
                )
            )
        
        return formatted_results
    
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/document/{doc_id}")
async def get_document(doc_id: str):
    """Retrieve full document content by ID."""
    try:
        # Try to get the document from the vector store
        doc_info = vector_store.collection.get(ids=[doc_id])
        
        if doc_info and 'documents' in doc_info and doc_info['documents']:
            content = doc_info['documents'][0]
            return {"content": content}
        
        # If not found in vector store, check if there's a file path in metadata
        metadata = {}
        try:
            meta_info = vector_store.collection.get(ids=[doc_id], include=["metadatas"])
            if meta_info and 'metadatas' in meta_info and meta_info['metadatas']:
                metadata = meta_info['metadatas'][0] or {}
        except:
            pass
            
        # Try to load from file if we have a path
        if 'file_path' in metadata and os.path.exists(metadata['file_path']):
            with open(metadata['file_path'], 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return {"content": content}
            
        # If we still don't have the document, return an error
        raise HTTPException(status_code=404, detail="Document not found")
    
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error retrieving document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving document: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
