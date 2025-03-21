from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import shutil
from typing import List
from ..database import get_db
from ..models import Document
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import google.generativeai as genai
import os

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

router = APIRouter()

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Save the file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text from the PDF
        raw_text = get_pdf_text(file_path)

        # Process text into chunks
        chunks = get_text_chunks(raw_text)

        # Generate vector store
        vector_store = get_vector_store(chunks)

        # Save to database
        document = Document(filename=file.filename, text_content=raw_text)
        db.add(document)
        db.commit()
        db.refresh(document)

        # Clean up temporary file
        os.remove(file_path)

        return {
            "message": "Successfully processed document",
            "document": {
                "document_id": document.id,
                "filename": document.filename
            }
        }

    except Exception as e:
        # Clean up temporary file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

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
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    return vector_store
