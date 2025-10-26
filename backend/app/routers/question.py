from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..database import get_document_store, DocumentStore
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()
os.getenv("OPENAI_API_KEY")
router = APIRouter()

class AskQuestionRequest(BaseModel):
    document_id: str
    question: str

@router.post("/ask")
async def ask_question(request: AskQuestionRequest, doc_store: DocumentStore = Depends(get_document_store)):
    try:
        # Check if OpenAI API key is configured
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            raise HTTPException(status_code=500, detail="OpenAI API key not configured. Please set OPENAI_API_KEY in .env file")
        
        # Fetch the document
        document = doc_store.get_document(request.document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        answer = process_question(request.question)
        return {"answer": {"output_text": answer}}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Question error: {str(e)}")  # Debug logging
        raise HTTPException(status_code=500, detail=f"Question processing failed: {str(e)}")

def process_question(user_question):
    # Load embeddings
    if not os.path.exists("faiss_index"):
        return "Vector database not found. Please upload a document first."

    # Use OpenAI embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=os.getenv("OPENAI_API_KEY"))
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

    # Create a retriever from the vector store
    retriever = new_db.as_retriever()

    # Initialize LLM Model (from langchain_openai)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, openai_api_key=os.getenv("OPENAI_API_KEY"))

    # Create QA Prompt
    prompt_template = """
    Answer the question as accurately as possible based on the provided context. If the answer is not found, say "Answer not available."
    Context: {context}
    Question: {question}
    Answer:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    # Build a RetrievalQA chain (inject prompt via chain_type_kwargs)
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
    )

    # Run the chain with the user question
    response = chain.run(user_question)
    return response
