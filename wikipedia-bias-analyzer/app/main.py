from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import wikipedia

app = FastAPI(
    title="Wikipedia Bias Analyzer",
    description="API for analyzing bias in Wikipedia articles",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(wikipedia.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the Wikipedia Bias Analyzer API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
