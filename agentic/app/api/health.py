"""
Health check endpoints for monitoring system status.
"""
from fastapi import APIRouter
from app.core.config import settings
from app.db import weaviate_manager
from app.db.postgres_client import postgres_manager
from app.services import embedding_service
from datetime import datetime

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check():
    """Get overall system health status."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "postgres": postgres_manager.is_connected(),
            "weaviate": weaviate_manager.is_connected(),
            "embedding_model": embedding_service.is_loaded()
        }
    }


@router.get("/postgres")
async def postgres_health():
    """Check PostgreSQL connection status."""
    is_connected = postgres_manager.is_connected()
    return {
        "service": "PostgreSQL",
        "status": "healthy" if is_connected else "unhealthy",
        "connected": is_connected,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/weaviate")
async def weaviate_health():
    """Check Weaviate connection status."""
    is_connected = weaviate_manager.is_connected()
    return {
        "service": "Weaviate",
        "status": "healthy" if is_connected else "unhealthy",
        "connected": is_connected,
        "timestamp": datetime.utcnow().isoformat()
    }
