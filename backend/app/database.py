from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# DATABASE_URL = "postgresql+psycopg2://postgres:Ritik%402808@localhost:5432/pdfreader"
DATABASE_URL = "postgresql://avnadmin:AVNS__SuNXcSzr5N-BDh1zXj@talktopdf-ritikkumar790667-ba29.l.aivencloud.com:22331/defaultdb?sslmode=require"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Automatically create tables on startup
def init_db():
    from app.models import Document  # Import all models
    Base.metadata.create_all(bind=engine)  # Create tables if they don't exist

def get_db():
    db = SessionLocal()
    try:
        # Enable UUID extension
        db.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
        yield db
    finally:
        db.close()
