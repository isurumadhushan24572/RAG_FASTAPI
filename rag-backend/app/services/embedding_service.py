"""
Embedding service for text vectorization.
Handles loading and using the sentence transformer model.
"""
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from fastapi import HTTPException, status
from app.core.config import settings


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
    
    def load_model(self):
        """Load the embedding model."""
        try:
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            print("✅ Embedding model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load embedding model: {str(e)}")
            self.model = None
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            HTTPException: If model is not initialized
        """
        if self.model is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Embedding model not initialized"
            )
        
        try:
            embedding = self.model.encode(text).tolist()
            return embedding
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating embedding: {str(e)}"
            )


# Global instance
embedding_service = EmbeddingService()


def get_embedding_service() -> EmbeddingService:
    """
    Dependency function to get embedding service.
    Used by FastAPI endpoints.
    """
    return embedding_service
