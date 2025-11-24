"""
Document service for managing documents in vector database.
Documents are stored as whole units (no chunking).
Supports both ticket and document schemas using Weaviate v4 API.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json
import logging
import weaviate.classes as wvc
from app.db.weaviate_client import get_weaviate_client
from app.services.embedding_service import get_embedding_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document management with vector database using Weaviate v4 API."""
    
    def __init__(self):
        """Initialize document service."""
        self.collection_name = settings.DOCUMENTS_COLLECTION_NAME
    
    def collection_exists(self, client, collection_name: str) -> bool:
        """Check if a collection exists in Weaviate."""
        try:
            if client is None:
                return False
            return client.collections.exists(collection_name)
        except Exception as e:
            logger.error(f"Error checking collection existence: {str(e)}")
            return False
    
    def add_document(
        self,
        title: str,
        content: str,
        document_type: str = "text",
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a document to the vector database (stored as whole, not chunked).
        
        Args:
            title: Document title
            content: Full document content
            document_type: Type of document (pdf, txt, docx, etc.)
            source: Document source or origin
            metadata: Additional metadata
            
        Returns:
            Dictionary with document information
        """
        try:
            client = get_weaviate_client()
            if client is None:
                raise RuntimeError("Weaviate client not connected")
            
            embedding_service = get_embedding_service()
            
            # Generate document ID
            document_id = str(uuid.uuid4())
            
            # Generate embedding for the full document content
            print(f"📝 Generating embedding for document: {title}")
            embedding = embedding_service.generate_embedding(content)
            
            # Calculate word count
            word_count = len(content.split())
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            # Prepare document data
            document_data = {
                "document_id": document_id,
                "title": title,
                "content": content,  # Full content, not chunked
                "document_type": document_type,
                "source": source or "unknown",
                "metadata": json.dumps(metadata),
                "created_at": datetime.now().isoformat(),
                "word_count": word_count,
            }
            
            # Get collection
            collection = client.collections.get(self.collection_name)
            
            # Insert document with embedding
            uuid_result = collection.data.insert(
                properties=document_data,
                vector=embedding
            )
            
            print(f"✅ Document added successfully: {title} ({word_count} words)")
            
            return {
                "document_id": document_id,
                "uuid": str(uuid_result),
                "title": title,
                "word_count": word_count,
                "status": "success"
            }
        
        except Exception as e:
            print(f"❌ Error adding document: {str(e)}")
            raise
    
    def search_documents(
        self,
        query: str,
        limit: int = 5,
        threshold: Optional[float] = None,
        collection_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using semantic search (Weaviate v4 API).
        
        Args:
            query: Search query
            limit: Maximum number of results
            threshold: Minimum similarity threshold
            collection_name: Optional collection name (uses default if not provided)
            
        Returns:
            List of matching documents with similarity scores
        """
        try:
            client = get_weaviate_client()
            if client is None:
                logger.error("Weaviate client not connected")
                return []
            
            embedding_service = get_embedding_service()
            
            # Use provided collection_name or fall back to default
            target_collection = collection_name or self.collection_name
            
            logger.info(f"🔍 Searching '{target_collection}' for: {query[:100]}...")
            
            # Check if collection exists
            if not self.collection_exists(client, target_collection):
                logger.warning(f"Collection '{target_collection}' does not exist")
                return []
            
            # Get collection
            collection = client.collections.get(target_collection)
            
            # Generate embedding for query
            query_embedding = embedding_service.generate_embedding(query)
            
            # Perform vector search (v4 API)
            response = collection.query.near_vector(
                near_vector=query_embedding,
                limit=limit,
                return_metadata=wvc.query.MetadataQuery(distance=True)
            )
            
            # Check if we have results
            if not response.objects:
                logger.info(f"No documents found in collection '{target_collection}'")
                return []
            
            # Process results
            results = []
            for obj in response.objects:
                try:
                    # Get properties
                    props = obj.properties
                    
                    # Calculate similarity score from distance
                    # Weaviate v4 returns distance (0=identical, 2=opposite for cosine)
                    # Convert to similarity score (1=identical, 0=opposite)
                    distance = obj.metadata.distance if obj.metadata and obj.metadata.distance is not None else 1.0
                    similarity = 1 - (distance / 2)
                    
                    # Apply threshold if specified
                    if threshold is not None and similarity < threshold:
                        continue
                    
                    # Parse metadata
                    metadata_str = props.get("metadata", "{}")
                    try:
                        metadata = json.loads(metadata_str) if metadata_str else {}
                    except:
                        metadata = {}
                    
                    # Handle both ticket and document schemas
                    result_doc = {
                        "document_id": props.get("document_id") or props.get("ticket_id", "N/A"),
                        "ticket_id": props.get("ticket_id", props.get("document_id", "N/A")),
                        "title": props.get("title", "Untitled"),
                        "content": props.get("content") or props.get("description", ""),
                        "description": props.get("description") or props.get("content", ""),
                        "category": props.get("category", "N/A"),
                        "severity": props.get("severity", "N/A"),
                        "application": props.get("application", "N/A"),
                        "environment": props.get("environment", "N/A"),
                        "affected_users": props.get("affected_users", "N/A"),
                        "solution": props.get("solution", ""),
                        "reasoning": props.get("reasoning", ""),
                        "status": props.get("status", "Unknown"),
                        "document_type": props.get("document_type", "ticket"),
                        "source": props.get("source", "unknown"),
                        "metadata": metadata,
                        "word_count": props.get("word_count", 0),
                        "created_at": props.get("created_at", ""),
                        "similarity_score": round(similarity, 4),
                        "uuid": str(obj.uuid)
                    }
                    
                    results.append(result_doc)
                    
                except Exception as e:
                    logger.error(f"Error formatting document: {str(e)}")
                    continue
            
            logger.info(f"✅ Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error searching documents: {str(e)}")
            logger.exception(e)
            return []
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID (Weaviate v4 API).
        
        Args:
            document_id: Document ID or ticket ID
            
        Returns:
            Document data or None if not found
        """
        try:
            client = get_weaviate_client()
            if client is None:
                return None
            
            if not self.collection_exists(client, self.collection_name):
                return None
            
            collection = client.collections.get(self.collection_name)
            
            # Query by document_id or ticket_id property (v4 API)
            response = collection.query.fetch_objects(
                filters=wvc.query.Filter.by_property("document_id").equal(document_id) |
                        wvc.query.Filter.by_property("ticket_id").equal(document_id),
                limit=1
            )
            
            if response.objects:
                obj = response.objects[0]
                
                # Parse metadata
                try:
                    metadata = json.loads(obj.properties.get("metadata", "{}"))
                except:
                    metadata = {}
                
                return {
                    "document_id": obj.properties.get("document_id") or obj.properties.get("ticket_id"),
                    "ticket_id": obj.properties.get("ticket_id") or obj.properties.get("document_id"),
                    "title": obj.properties.get("title"),
                    "content": obj.properties.get("content") or obj.properties.get("description"),
                    "description": obj.properties.get("description") or obj.properties.get("content"),
                    "document_type": obj.properties.get("document_type"),
                    "source": obj.properties.get("source"),
                    "metadata": metadata,
                    "word_count": obj.properties.get("word_count"),
                    "created_at": obj.properties.get("created_at"),
                    "uuid": str(obj.uuid)
                }
            
            return None
        
        except Exception as e:
            logger.error(f"❌ Error getting document: {str(e)}")
            return None
    
    def list_documents(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all documents.
        
        Args:
            limit: Maximum number of documents to return
            
        Returns:
            List of documents
        """
        try:
            client = get_weaviate_client()
            if client is None:
                raise RuntimeError("Weaviate client not connected")
            
            collection = client.collections.get(self.collection_name)
            
            # Fetch all documents
            response = collection.query.fetch_objects(limit=limit)
            
            # Process results
            documents = []
            for obj in response.objects:
                # Parse metadata
                try:
                    metadata = json.loads(obj.properties.get("metadata", "{}"))
                except:
                    metadata = {}
                
                documents.append({
                    "document_id": obj.properties.get("document_id"),
                    "title": obj.properties.get("title"),
                    "content": obj.properties.get("content"),
                    "document_type": obj.properties.get("document_type"),
                    "source": obj.properties.get("source"),
                    "metadata": metadata,
                    "word_count": obj.properties.get("word_count"),
                    "created_at": obj.properties.get("created_at"),
                })
            
            print(f"📚 Retrieved {len(documents)} documents")
            return documents
        
        except Exception as e:
            print(f"❌ Error listing documents: {str(e)}")
            raise
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document by ID (Weaviate v4 API).
        
        Args:
            document_id: Document ID or ticket ID
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            client = get_weaviate_client()
            if client is None:
                return False
            
            if not self.collection_exists(client, self.collection_name):
                return False
            
            collection = client.collections.get(self.collection_name)
            
            # Find and delete document (v4 API)
            response = collection.query.fetch_objects(
                filters=wvc.query.Filter.by_property("document_id").equal(document_id) |
                        wvc.query.Filter.by_property("ticket_id").equal(document_id),
                limit=1
            )
            
            if response.objects:
                uuid_to_delete = response.objects[0].uuid
                collection.data.delete_by_id(uuid_to_delete)
                logger.info(f"🗑️ Document deleted: {document_id}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"❌ Error deleting document: {str(e)}")
            return False


# Global instance
document_service = DocumentService()


def get_document_service() -> DocumentService:
    """Dependency to get document service."""
    return document_service
