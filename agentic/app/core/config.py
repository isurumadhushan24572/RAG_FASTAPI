"""
Configuration module for application settings.
Handles environment variables and application constants.
"""
import os
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings and configuration."""
    
    # API Configuration
    API_TITLE: str = "Agentic RAG API"
    API_DESCRIPTION: str = "Advanced Agentic RAG system with web search and vector database"
    API_VERSION: str = "1.0.0"
    API_HOST: str = os.getenv("API_HOST")
    API_PORT: int = int(os.getenv("API_PORT"))
    
    # Weaviate Configuration
    WEAVIATE_HOST: str = os.getenv("WEAVIATE_HOST")
    WEAVIATE_PORT: int = int(os.getenv("WEAVIATE_PORT"))
    WEAVIATE_GRPC_PORT: int = int(os.getenv("WEAVIATE_GRPC_PORT"))
    
    # Collection Configuration
    DOCUMENTS_COLLECTION_NAME: str = os.getenv("DOCUMENTS_COLLECTION_NAME")
    
    # Embedding Model Configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL")
    
    # LLM Configuration
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL")
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE"))
    
    # Agent Configuration
    AGENT_MAX_ITERATIONS: int = int(os.getenv("AGENT_MAX_ITERATIONS"))
    AGENT_MAX_EXECUTION_TIME: int = int(os.getenv("AGENT_MAX_EXECUTION_TIME"))
    
    # Web Search Configuration
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GOOGLE_CSE_ID: Optional[str] = os.getenv("GOOGLE_CSE_ID")
    
    # Search Configuration
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD"))
    DEFAULT_SEARCH_LIMIT: int = int(os.getenv("MAX_RETRIEVAL_DOCUMENTS"))
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS"
    ).split(",")
    
    # LangSmith Configuration (Optional)
    LANGSMITH_TRACING: bool = os.getenv("LANGSMITH_TRACING").lower() == "true"
    LANGSMITH_ENDPOINT: Optional[str] = os.getenv("LANGSMITH_ENDPOINT")
    LANGSMITH_API_KEY: Optional[str] = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT: str = os.getenv("LANGSMITH_PROJECT")
    
    # Application Settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT")
    DEBUG: bool = os.getenv("DEBUG").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL")


# Create a singleton instance
settings = Settings()
