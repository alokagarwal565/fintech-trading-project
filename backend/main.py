from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from backend.models.database import create_db_and_tables
from backend.routers import auth, risk_profile, portfolio, scenario, export
from backend.middleware.rate_limiter import rate_limit_middleware
from backend.middleware.security import security_middleware_func
from backend.utils.logger import app_logger, log_api_request

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app_logger.info("Starting AI-Powered Risk & Scenario Advisor API")
    create_db_and_tables()
    app_logger.info("Database initialized successfully")
    yield
    # Shutdown
    app_logger.info("Shutting down AI-Powered Risk & Scenario Advisor API")

app = FastAPI(
    title="AI-Powered Risk & Scenario Advisor API",
    description="Backend API for retail investment risk assessment and scenario analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Get CORS origins from environment
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:8501,http://localhost:3000").split(",")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.middleware("http")(security_middleware_func)

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
    return {"status": "healthy", "timestamp": time.time()}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all API requests"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log request
    log_api_request(
        app_logger,
        request.method,
        request.url.path,
        response.status_code,
        duration=duration
    )
    
    return response

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )