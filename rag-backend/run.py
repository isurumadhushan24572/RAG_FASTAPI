"""
Application entry point.
Run this file to start the FastAPI server.
"""

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    # Run the FastAPI application with Uvicorn server
    uvicorn.run(
        "app.main:app",           # Import string format (required for reload)
        host="0.0.0.0",           # Listen on all interfaces
        port=settings.API_PORT,   # Application port from config
        log_level="info",         # Set logging level
        reload=True               # Enable auto-reload for development
    )
