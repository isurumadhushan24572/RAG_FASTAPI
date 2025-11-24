"""
Embedding service for generating document embeddings.
Uses sentence-transformers for local embeddings.
"""
from sentence_transformers import SentenceTransformer
from typing import Optional, List
import numpy as np
from app.core.config import settings


class EmbeddingService:
    """Service for generating embeddings using sentence-transformers."""
    
    def __init__(self):
        """Initialize embedding service."""
        self.model: Optional[SentenceTransformer] = None
        self.model_name = settings.EMBEDDING_MODEL
    
    def load_model(self):
        """Load the sentence-transformers model."""
        if self.model is None:
            try:
                print(f"📦 Loading embedding model: {self.model_name}...")
                self.model = SentenceTransformer(self.model_name)
                print(f"✅ Embedding model loaded successfully")
                print(f"ℹ️  Model dimension: {self.model.get_sentence_embedding_dimension()}")
            except Exception as e:
                print(f"❌ Failed to load embedding model: {str(e)}")
                raise
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if self.model is None:
            raise RuntimeError("Embedding model not loaded. Call load_model() first.")
        
        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # Convert to list and return
            return embedding.tolist()
        
        except Exception as e:
            print(f"❌ Error generating embedding: {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing).
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embedding vectors
        """
        if self.model is None:
            raise RuntimeError("Embedding model not loaded. Call load_model() first.")
        
        try:
            # Generate embeddings in batch
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            
            # Convert to list of lists
            return embeddings.tolist()
        
        except Exception as e:
            print(f"❌ Error generating embeddings: {str(e)}")
            raise
    
    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        if self.model is None:
            raise RuntimeError("Embedding model not loaded.")
        return self.model.get_sentence_embedding_dimension()


# Global instance
embedding_service = EmbeddingService()


def get_embedding_service() -> EmbeddingService:
    """Dependency to get embedding service."""
    return embedding_service
