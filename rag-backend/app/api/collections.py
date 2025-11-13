
# collection management endpoints.
# Handles CRUD operations for Weaviate collections.

from fastapi import APIRouter, HTTPException, status
import weaviate.classes as wvc
from weaviate.classes.config import Property, DataType
from app.db import get_weaviate_client
from app.core.config import settings

router = APIRouter(prefix="/api/v1/collections", tags=["Collections"])


@router.get("")
async def list_collections():
    """
    List all available collections in Weaviate vector database.
    
    Returns:
        Dict: List of all collection names with their counts
    
    Raises:
        HTTPException: If query fails
    """
    weaviate_client = get_weaviate_client()
    
    try:
        # Check if Weaviate client is initialized
        if weaviate_client is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Weaviate client not initialized. Check if Weaviate is running."
            )
        
        # Get all collections from Weaviate schema
        collections = weaviate_client.collections.list_all()
        
        # Create list to store collection information
        collection_list = []
        
        # Iterate through each collection and get its count
        for collection_name in collections:
            try:
                # Get collection reference
                collection = weaviate_client.collections.get(collection_name)
                
                # Get document count for this collection
                result = collection.aggregate.over_all(total_count=True)
                count = result.total_count
                
                # Add to list
                collection_list.append({
                    "name": collection_name,
                    "document_count": count
                })
            except Exception as e:
                # If count fails for a collection, add it with error
                collection_list.append({
                    "name": collection_name,
                    "document_count": 0,
                    "error": str(e)
                })
        
        # Return all collections with their counts
        return {
            "total_collections": len(collection_list),
            "collections": collection_list,
            "status": "success"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any errors during collection listing
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing collections: {str(e)}"
        )


@router.get("/{collection_name}/count")
async def get_document_count(collection_name: str):
    """
    Get the total number of documents in a specific Weaviate collection.
    
    Args:
        collection_name (str): Name of the collection to query
    
    Returns:
        Dict: Collection name and document count
    
    Raises:
        HTTPException: If collection doesn't exist or query fails
    """
    weaviate_client = get_weaviate_client()
    
    try:
        # Check if Weaviate client is initialized
        if weaviate_client is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Weaviate client not initialized. Check if Weaviate is running."
            )
        
        # Check if the collection exists in Weaviate schema
        if not weaviate_client.collections.exists(collection_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{collection_name}' does not exist in Weaviate"
            )
        
        # Get the collection reference
        collection = weaviate_client.collections.get(collection_name)
        
        # Perform aggregation query to count total objects in collection
        result = collection.aggregate.over_all(total_count=True)
        
        # Extract total count from result
        total_count = result.total_count
        
        # Return the count in JSON format
        return {
            "collection_name": collection_name,
            "document_count": total_count,
            "status": "success",
            "message": f"Successfully retrieved document count from collection '{collection_name}'"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404 for collection not found)
        raise
    except Exception as e:
        # Handle any other errors during query
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document count: {str(e)}"
        )


@router.post("")
async def create_collection(collection_name: str):
    """
    Create a new collection with default ticket schema by just providing a name.
    This is a simplified endpoint that creates a collection with predefined ticket properties.
    
    Args:
        collection_name: Name of the collection to create (query parameter)
        
    Returns:
        Dict: Success status and collection details
        
    Raises:
        HTTPException: If collection creation fails or already exists
    """
    weaviate_client = get_weaviate_client()
    
    try:
        # Check if Weaviate client is initialized
        if weaviate_client is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Weaviate client not initialized. Check if Weaviate is running."
            )
        
        # Check if collection already exists
        if weaviate_client.collections.exists(collection_name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Collection '{collection_name}' already exists"
            )
        
        # Create collection with default ticket schema
        weaviate_client.collections.create(
            name=collection_name,
            description=f"Support ticket collection: {collection_name}",
            vectorizer_config=wvc.config.Configure.Vectorizer.none(),  # Manual/local embeddings
            properties=[
                Property(name="ticket_id", data_type=DataType.TEXT, description="Unique ticket identifier"),
                Property(name="title", data_type=DataType.TEXT, description="Ticket title/summary"),
                Property(name="description", data_type=DataType.TEXT, description="Detailed problem description"),
                Property(name="category", data_type=DataType.TEXT, description="Issue category"),
                Property(name="status", data_type=DataType.TEXT, description="Ticket status (Open/Resolved)"),
                Property(name="severity", data_type=DataType.TEXT, description="Severity level"),
                Property(name="application", data_type=DataType.TEXT, description="Affected application/service"),
                Property(name="affected_users", data_type=DataType.TEXT, description="Impact scope"),
                Property(name="environment", data_type=DataType.TEXT, description="Environment (Production/Staging/etc)"),
                Property(name="solution", data_type=DataType.TEXT, description="Resolution steps"),
                Property(name="reasoning", data_type=DataType.TEXT, description="Root cause analysis"),
                Property(name="timestamp", data_type=DataType.TEXT, description="Ticket creation timestamp"),
            ]
        )
        
        return {
            "success": True,
            "message": f"Collection '{collection_name}' created successfully with default ticket schema",
            "collection": {
                "name": collection_name,
                "description": f"Support ticket collection: {collection_name}",
                "schema_type": "default_ticket_schema",
                "vectorizer": "manual/local (sentence-transformers)",
                "properties_count": 12,
                "properties": [
                    "ticket_id", "title", "description", "category", "status", 
                    "severity", "application", "affected_users", "environment", 
                    "solution", "reasoning", "timestamp"
                ]
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any other errors during collection creation
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating collection: {str(e)}"
        )


@router.delete("/{collection_name}")
async def delete_collection(collection_name: str):
    """
    Delete a collection from Weaviate.
    ⚠️ WARNING: This permanently deletes all data in the collection!
    
    Args:
        collection_name: Name of collection to delete
        
    Returns:
        Dict: Success status and deleted document count
        
    Raises:
        HTTPException: If collection doesn't exist or deletion fails
    """
    weaviate_client = get_weaviate_client()
    
    # Check if Weaviate client is connected
    if weaviate_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weaviate vector database is not connected. Please check connection."
        )
    
    try:
        # Check if collection exists
        if not weaviate_client.collections.exists(collection_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{collection_name}' does not exist"
            )
        
        # Get count before deletion (for reporting)
        try:
            collection = weaviate_client.collections.get(collection_name)
            count_result = collection.aggregate.over_all(total_count=True)
            deleted_count = count_result.total_count
        except Exception:
            deleted_count = 0  # If we can't get count, set to 0
        
        # Delete the collection
        weaviate_client.collections.delete(collection_name)
        
        return {
            "success": True,
            "message": f"Collection '{collection_name}' deleted successfully",
            "deleted_documents": deleted_count,
            "note": "Restart the application to recreate an empty collection"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting collection: {str(e)}"
        )


@router.get("/count")
async def get_default_collection_count():
    """
    Get document count from the default 'SupportTickets' collection.
    This is a convenience endpoint that doesn't require specifying collection name.
    
    Returns:
        Dict: Default collection name and document count
    
    Raises:
        HTTPException: If default collection doesn't exist or query fails
    """
    # Call the main count endpoint with SupportTickets collection
    return await get_document_count(settings.TICKETS_COLLECTION_NAME)
