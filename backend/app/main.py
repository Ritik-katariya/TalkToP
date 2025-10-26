from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from app.database import get_db, init_db
from app.routers import question, upload  # Import routers

# Define lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # Ensure tables are created
    yield  # Continue app execution

# Initialize FastAPI with lifespan
app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")  # Test query to check DB connection
        return {"status": "Database Connected ✅"}
    except Exception as e:
        return {"status": "Database Connection Failed ❌", "error": str(e)}

@app.get("/hello")
def root():
    return {"message": "Hello, world!"}

# Include API routes
app.include_router(question.router, prefix="/api")
app.include_router(upload.router, prefix="/api")

# Allow CORS for frontend
origins = ["*"]  # Allow all origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
