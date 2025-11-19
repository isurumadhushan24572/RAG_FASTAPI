"""
Health check endpoints.
Provides API and database health status.
"""
from fastapi import APIRouter, HTTPException, status # FastAPI router and exceptions
from fastapi.responses import JSONResponse # JSON response handling
from app.db import get_weaviate_client

router = APIRouter(tags=["Health Check"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify Weaviate connection status.
    
    Returns:
        Dict: Health status of API and Weaviate database
    
    Raises:
        HTTPException: If Weaviate connection fails
    """
    weaviate_client = get_weaviate_client()
    
    try:
        # Check if Weaviate client exists
        if weaviate_client is None:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unhealthy",
                    "weaviate_status": "not_connected",
                    "weaviate_ready": False,
                    "message": "Weaviate client not initialized"
                }
            )
        
        # Check if Weaviate is ready
        is_ready = weaviate_client.is_ready()
        
        if is_ready:
            return {
                "status": "healthy",
                "weaviate_status": "connected",
                "weaviate_ready": True,
                "message": "API and Weaviate are running successfully"
            }
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unhealthy",
                    "weaviate_status": "not_ready",
                    "weaviate_ready": False,
                    "message": "Weaviate is not ready"
                }
            )
    except Exception as e:
        # Return error if connection fails
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Weaviate connection failed: {str(e)}"
        )
