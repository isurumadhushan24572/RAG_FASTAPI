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
    
    # PostgreSQL Configuration
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct PostgreSQL connection URL with psycopg2 dialect."""
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Collection Configuration
    DOCUMENTS_COLLECTION_NAME: str = os.getenv("DOCUMENTS_COLLECTION_NAME")
    
    # Embedding Model Configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL")
    
    # LLM Configuration
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL")
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE"))

    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.3"))   
    
    # Agent Configuration
    AGENT_MAX_ITERATIONS: int = int(os.getenv("AGENT_MAX_ITERATIONS"))
    AGENT_MAX_EXECUTION_TIME: int = int(os.getenv("AGENT_MAX_EXECUTION_TIME"))
    
    # Web Search Configuration
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
    
    # JWT Authentication Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_HOURS: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_HOURS", "24"))
    
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
