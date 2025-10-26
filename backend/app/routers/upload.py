from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import shutil
from typing import List
from ..database import get_document_store, DocumentStore
from ..models import Document
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
import uuid

# Load environment variables (expect OPENAI_API_KEY in .env)
load_dotenv()

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), doc_store: DocumentStore = Depends(get_document_store)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_path = None
    try:
        # Check if OpenAI API key is configured
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            raise HTTPException(status_code=500, detail="OpenAI API key not configured. Please set OPENAI_API_KEY in .env file")
        
        # Save the file temporarily
        file_path = f"uploads/temp_{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text from the PDF
        raw_text = get_pdf_text(file_path)
        
        if not raw_text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")

        # Process text into chunks
        chunks = get_text_chunks(raw_text)

        # Generate vector store
        vector_store = get_vector_store(chunks)

        # Save to document store
        doc_id = doc_store.add_document(filename=file.filename, text_content=raw_text)

        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "message": "Successfully processed document",
            "document": {
                "document_id": doc_id,
                "filename": file.filename
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        # Clean up temporary file if it exists
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        print(f"Upload error: {str(e)}")  # Debug logging
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

def get_pdf_text(pdf_path):
    """Extracts text from a given PDF file path."""
    text = ""
    with open(pdf_path, "rb") as f:
        pdf_reader = PdfReader(f)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""  # Handle None cases
    return text

def get_text_chunks(text):
    """Splits the text into manageable chunks."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return text_splitter.split_text(text)

def get_vector_store(text_chunks):
    """Generates embeddings and stores them in FAISS."""
    # Use OpenAI embeddings (text-embedding-3-small is a reasonable default)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=os.getenv("OPENAI_API_KEY"))
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    return vector_store
