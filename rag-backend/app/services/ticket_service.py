"""
Ticket service for business logic related to ticket operations.
Handles ticket search, retrieval, and similarity matching.
"""
from typing import List, Dict, Optional
import weaviate.classes as wvc
from app.core.config import settings
from app.services.embedding_service import embedding_service


class TicketService:
    """Service for ticket-related operations."""
    
    def find_similar_tickets(
        self,
        weaviate_client,
        collection_name: str,
        query_text: str,
        k: int = 5,
        similarity_threshold: float = 0.85
    ) -> List[Dict]:
        """
        Find similar tickets in Weaviate using vector similarity search.
        
        Args:
            weaviate_client: Weaviate client instance
            collection_name: Name of the collection to search
            query_text: Query text to search for
            k: Number of results to return
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of similar tickets with metadata and similarity scores
        """
        if weaviate_client is None:
            return []
        
        try:
            # Check if collection exists
            if not weaviate_client.collections.exists(collection_name):
                return []
            
            # Get collection
            collection = weaviate_client.collections.get(collection_name)
            
            # Generate embedding for query
            query_embedding = embedding_service.generate_embedding(query_text)
            
            # Perform vector search
            response = collection.query.near_vector(
                near_vector=query_embedding,
                limit=k,
                return_metadata=wvc.query.MetadataQuery(distance=True, certainty=True)
            )
            
            # Extract results with similarity filtering
            similar_tickets = []
            for obj in response.objects:
                # Weaviate certainty is already 0-1 (cosine similarity)
                similarity_score = obj.metadata.certainty
                
                # Only include tickets above threshold
                if similarity_score >= similarity_threshold:
                    ticket_data = {
                        "ticket_id": obj.properties.get("ticket_id", "N/A"),
                        "title": obj.properties.get("title", ""),
                        "description": obj.properties.get("description", ""),
                        "solution": obj.properties.get("solution", ""),
                        "reasoning": obj.properties.get("reasoning", ""),
                        "category": obj.properties.get("category", ""),
                        "severity": obj.properties.get("severity", ""),
                        "similarity_score": float(similarity_score)
                    }
                    similar_tickets.append(ticket_data)
            
            return similar_tickets
            
        except Exception as e:
            print(f"Error finding similar tickets: {e}")
            return []
    
    def format_similar_tickets_for_response(self, similar_tickets: List[Dict]) -> List[Dict]:
        """Format similar tickets for API response."""
        return [
            {
                "ticket_id": st["ticket_id"],
                "title": st["title"],
                "similarity_score": st["similarity_score"],
                "similarity_percent": f"{st['similarity_score'] * 100:.1f}%",
                "category": st["category"],
                "severity": st["severity"]
            }
            for st in similar_tickets
        ]
    
    def generate_ticket_id(self, weaviate_client, collection_name: str, prefix: str = "TKT") -> str:
        """
        Generate a new ticket ID based on current collection count.
        
        Args:
            weaviate_client: Weaviate client instance
            collection_name: Name of the collection
            prefix: Prefix for the ticket ID
            
        Returns:
            Generated ticket ID (e.g., "TKT-0001")
        """
        try:
            collection = weaviate_client.collections.get(collection_name)
            count_result = collection.aggregate.over_all(total_count=True)
            ticket_count = count_result.total_count
            return f"{prefix}-{ticket_count + 1:04d}"
        except Exception:
            return f"{prefix}-0001"


# Global instance
ticket_service = TicketService()


def get_ticket_service() -> TicketService:
    """
    Dependency function to get ticket service.
    Used by FastAPI endpoints.
    """
    return ticket_service
