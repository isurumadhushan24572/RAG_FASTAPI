"""
Configuration module for application settings.
Handles environment variables and application constants.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings and configuration."""
    
    # API Configuration
    API_TITLE: str = "Weaviate Vector DB API"
    API_DESCRIPTION: str = "REST API for Weaviate Vector Database Operations"
    API_VERSION: str = "1.0.0"
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Weaviate Configuration
    WEAVIATE_HOST: str = os.getenv("WEAVIATE_HOST", "localhost")
    WEAVIATE_PORT: int = int(os.getenv("WEAVIATE_PORT", "8080"))
    WEAVIATE_GRPC_PORT: int = int(os.getenv("WEAVIATE_GRPC_PORT", "50051"))
    
    # Collection Configuration
    TICKETS_COLLECTION_NAME: str = "SupportTickets"
    
    # Embedding Model Configuration
    EMBEDDING_MODEL: str = "all-mpnet-base-v2"
    
    # AI Model Configuration
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_TEMPERATURE: float = 0.1
    
    # Search Configuration
    SIMILARITY_THRESHOLD: float = 0.85
    DEFAULT_SEARCH_LIMIT: int = 3


# Create a singleton instance
settings = Settings()
