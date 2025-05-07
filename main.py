import os
import shutil
import tempfile
import uuid
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from embeddings import EmbeddingGenerator
from vector_store import ChromaVectorStore

# Create directories if they don't exist
os.makedirs("./uploads", exist_ok=True)
os.makedirs("./static", exist_ok=True)
os.makedirs("./templates", exist_ok=True)

app = FastAPI(title="Document Search API")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize embedding generator and vector store
embedding_generator = EmbeddingGenerator()
vector_store = ChromaVectorStore(embedding_function=embedding_generator)

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

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # Check if file type is supported
    if not file.filename.lower().endswith(('.txt', '.cbl', '.cobol')):
        raise HTTPException(status_code=400, detail="Only text files (.txt) and COBOL files (.cbl, .cobol) are supported")
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Copy uploaded file content to temporary file
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        # Process the file and generate embeddings
        with open(temp_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Generate a unique ID for this document
        doc_id = str(uuid.uuid4())
        
        # Generate embedding and add to vector store
        vector_store.add_document(
            document_id=doc_id,
            document_text=content,
            metadata={"filename": file.filename}
        )
        
        # Remove temporary file
        os.unlink(temp_file_path)
        
        return {"message": "Document uploaded and indexed successfully", "document_id": doc_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    finally:
        file.file.close()

@app.post("/search", response_model=List[SearchResult])
async def search_documents(search_query: SearchQuery):
    try:
        # Perform the search
        results = vector_store.search(search_query.query, top_k=search_query.top_k)
        
        # Format the results
        formatted_results = []
        for doc_id, score, metadata, doc_text in results:
            # Create a short preview of the document
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
        raise HTTPException(status_code=500, detail=f"Error during search: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
