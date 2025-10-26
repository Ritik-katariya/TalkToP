# Simple in-memory storage for documents
from typing import Dict, List
import uuid
from datetime import datetime

class DocumentStore:
    def __init__(self):
        self.documents: Dict[str, dict] = {}

    def add_document(self, filename: str, text_content: str) -> str:
        doc_id = str(uuid.uuid4())
        self.documents[doc_id] = {
            "id": doc_id,
            "filename": filename,
            "upload_date": datetime.now(),
            "text_content": text_content
        }
        return doc_id

    def get_document(self, doc_id: str) -> dict:
        return self.documents.get(doc_id)

    def get_all_documents(self) -> List[dict]:
        return list(self.documents.values())

# Global document store instance
document_store = DocumentStore()

def get_document_store():
    return document_store
