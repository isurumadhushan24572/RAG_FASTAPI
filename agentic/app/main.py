"""
Main FastAPI application.
Handles application lifecycle and routes.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db import weaviate_manager
from app.db.postgres_client import postgres_manager
from app.services import embedding_service

# Import routers directly to avoid circular imports
from app.api import health, documents, agent, tickets, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # STARTUP
    print("🚀 Starting Agentic RAG Application...")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    
    # Load embedding model
    print("\n📦 Loading embedding model...")
    embedding_service.load_model()
    
    # Connect to PostgreSQL
    print("\n🔌 Connecting to PostgreSQL...")
    postgres_connected = postgres_manager.connect()
    
    if postgres_connected:
        # Create database tables
        postgres_manager.create_tables()
        print("✅ PostgreSQL ready (User data & Chat messages)")
    else:
        print("⚠️ Warning: PostgreSQL not connected")
        print("💡 Start PostgreSQL: docker-compose up -d postgres")
    
    # Connect to Weaviate
    print("\n🔌 Connecting to Weaviate...")
    weaviate_connected = weaviate_manager.connect()
    
    if weaviate_connected:
        # Initialize collections
        weaviate_manager.initialize_collections()
        print("✅ Weaviate ready (Knowledge Base with embeddings)")
    else:
        print("⚠️ Warning: Weaviate not connected")
        print("💡 Start Weaviate: docker-compose up -d weaviate")
    
    print("\n✅ Application startup complete!")
    print(f"📖 API Documentation: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(f"🔍 Health Check: http://{settings.API_HOST}:{settings.API_PORT}/health")
    
    # Yield control to the application
    yield
    
    # SHUTDOWN
    print("\n🛑 Shutting down Agentic RAG Application...")
    postgres_manager.disconnect()
    weaviate_manager.disconnect()
    print("✅ Shutdown complete!")


# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(health.router)
app.include_router(tickets.router)
app.include_router(documents.router)
app.include_router(agent.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "features": [
            "Agentic RAG with tool calling",
            "Web search integration (Tavily/DuckDuckGo)",
            "Vector database search",
            "Ticket-based input format (compatible with rag-backend)",
            "LangChain prompt templates"
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "tickets": "/api/v1/tickets",
            "documents": "/documents",
            "agent": "/agent/query"
        }
    }


@app.get("/status")
async def status():
    """Get application status."""
    return {
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "databases": {
            "postgres": {
                "connected": postgres_manager.is_connected(),
                "purpose": "User authentication & Chat messages"
            },
            "weaviate": {
                "connected": weaviate_manager.is_connected(),
                "purpose": "Knowledge Base (Support tickets with embeddings)"
            }
        },
        "embedding_model_loaded": embedding_service.is_loaded(),
        "llm_model": settings.GROQ_MODEL,
        "agent_config": {
            "max_iterations": settings.AGENT_MAX_ITERATIONS,
            "max_execution_time": settings.AGENT_MAX_EXECUTION_TIME,
        }
    }
