"""
Main application module.
FastAPI application setup and lifecycle management.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db import weaviate_manager
from app.services import embedding_service
from app.api import health, collections, tickets


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events using modern async context manager.
    """
    # STARTUP: Initialize services
    print("🚀 Starting application...")
    
    # Load embedding model
    embedding_service.load_model()
    
    # Connect to Weaviate
    connected = weaviate_manager.connect()
    
    if connected:
        # Initialize default collections
        weaviate_manager.initialize_collections()
    
    # Yield control to the application
    yield
    
    # SHUTDOWN: Cleanup
    print("🛑 Shutting down application...")
    weaviate_manager.disconnect()


# Create FastAPI application instance with lifespan handler
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan
)

# Configure CORS - Allow frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default port
        "http://localhost:5174",  # Alternative Vite port
        "http://localhost:3000",  # Alternative frontend port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(health.router)
app.include_router(collections.router)
app.include_router(tickets.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "docs_url": "/docs",
        "health_check": "/health"
    }
