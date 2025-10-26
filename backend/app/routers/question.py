from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import Document
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import google.generativeai as genai
from uuid import UUID

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
router = APIRouter()

class AskQuestionRequest(BaseModel):
    document_id: UUID
    question: str

@router.post("/ask")
async def ask_question(request: AskQuestionRequest, db: Session = Depends(get_db)):
    # Fetch the document
    # document = db.query(Document).filter(Document.id == request.document_id).first()
    # if not document:
    #     return {"error": "Document not found"}
    
    answer = process_question(request.question)
    return {"answer": answer}

def process_question(user_question):
    # Load embeddings
    if not os.path.exists("faiss_index"):
        return "Vector database not found. Please upload a document first."

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)

    # Initialize LLM Model
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3)

    
    # Create QA Prompt
    prompt_template = """
    Answer the question as accurately as possible based on the provided context. If the answer is not found, say "Answer not available."
    Context: {context}
    Question: {question}
    Answer:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    # Get the response
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
    return response
