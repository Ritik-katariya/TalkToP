from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class Document(BaseModel):
    id: UUID
    filename: str
    upload_date: datetime
    text_content: str
