from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from backend.models.database import create_db_and_tables
from backend.routers import auth, risk_profile, portfolio, scenario, export

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="AI-Powered Risk & Scenario Advisor API",
    description="Backend API for retail investment risk assessment and scenario analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(risk_profile.router)
app.include_router(portfolio.router)
app.include_router(scenario.router)
app.include_router(export.router)

@app.get("/")
async def root():
    return {"message": "AI-Powered Risk & Scenario Advisor API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )