"""
Health check endpoint.
"""
from fastapi import APIRouter
from datetime import datetime
from app.models.schemas import HealthCheck
from app.db import weaviate_manager
from app.services import embedding_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Check the health status of the application and its dependencies."""
    return HealthCheck(
        status="healthy",
        weaviate_connected=weaviate_manager.is_connected(),
        embedding_model_loaded=embedding_service.is_loaded(),
        timestamp=datetime.now().isoformat()
    )
