from sqlalchemy import Column, Integer, String, DateTime, UUID
from sqlalchemy.sql import func
from .database import Base
from uuid import uuid4

class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    filename = Column(String, index=True)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    text_content = Column(String)
