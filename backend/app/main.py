from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import question, upload  # Import routers

# Initialize FastAPI
app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "Service is healthy ✅"}

@app.get("/hello")
def root():
    return {"message": "Hello, world!"}

# Include API routes
app.include_router(question.router, prefix="/api")
app.include_router(upload.router, prefix="/api")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust for frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
