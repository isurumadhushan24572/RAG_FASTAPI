"""
Document management endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Optional
import weaviate.classes as wvc
from weaviate.classes.config import Property, DataType
from app.models.schemas import (
    DocumentResponse,
    DocumentSearchQuery,
    DocumentSearchResponse,
    DocumentSearchResult,
)
from app.services import get_document_service
from app.db.weaviate_client import get_weaviate_client

router = APIRouter(prefix="", tags=["Collections"])


@router.get("/collections")
async def list_collections(collection_name: Optional[str] = None):
    """
    List all available collections in Weaviate vector database.
    
    Args:
        collection_name: Optional filter - if provided, returns info for only that collection
    
    Returns:
        Dict: List of all collection names with their counts (or single collection if filtered)
    
    Raises:
        HTTPException: If query fails or collection not found
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
        all_collections = weaviate_client.collections.list_all()
        
        # Filter to specific collection if requested
        if collection_name:
            if collection_name not in all_collections:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Collection '{collection_name}' does not exist"
                )
            collections_to_process = [collection_name]
        else:
            collections_to_process = all_collections
        
        # Create list to store collection information
        collection_list = []
        
        # Iterate through each collection and get its count
        for coll_name in collections_to_process:
            try:
                # Get collection reference
                collection = weaviate_client.collections.get(coll_name)
                
                # Get document count for this collection
                result = collection.aggregate.over_all(total_count=True)
                count = result.total_count
                
                # Add to list
                collection_list.append({
                    "name": coll_name,
                    "document_count": count
                })
            except Exception as e:
                # If count fails for a collection, add it with error
                collection_list.append({
                    "name": coll_name,
                    "document_count": 0,
                    "error": str(e)
                })
        
        # Return all collections with their counts
        return {
            "total_collections": len(collection_list),
            "collections": collection_list,
            "filtered": collection_name is not None,
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


@router.post("/collections")
async def create_collection(collection_name: str, schema_type: str = "ticket"):
    """
    Create a new collection in Weaviate with specified schema.
    
    Args:
        collection_name: Name of the collection to create (query parameter)
        schema_type: Type of schema - "ticket" (default) or "document"
        
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
        
        # Define properties based on schema type
        if schema_type == "document":
            properties = [
                Property(name="document_id", data_type=DataType.TEXT, description="Unique document identifier"),
                Property(name="title", data_type=DataType.TEXT, description="Document title"),
                Property(name="content", data_type=DataType.TEXT, description="Full document content"),
                Property(name="document_type", data_type=DataType.TEXT, description="Type of document (pdf, txt, etc.)"),
                Property(name="source", data_type=DataType.TEXT, description="Document source/origin"),
                Property(name="metadata", data_type=DataType.TEXT, description="Additional metadata (JSON string)"),
                Property(name="created_at", data_type=DataType.TEXT, description="Creation timestamp"),
                Property(name="word_count", data_type=DataType.INT, description="Number of words in document"),
            ]
            description = f"Document collection: {collection_name}"
        else:  # ticket schema (default)
            properties = [
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
            description = f"Support ticket collection: {collection_name}"
        
        # Create collection
        weaviate_client.collections.create(
            name=collection_name,
            description=description,
            vectorizer_config=wvc.config.Configure.Vectorizer.none(),  # Manual/local embeddings
            properties=properties
        )
        
        return {
            "success": True,
            "message": f"Collection '{collection_name}' created successfully with {schema_type} schema",
            "collection": {
                "name": collection_name,
                "description": description,
                "schema_type": schema_type,
                "vectorizer": "manual/local (sentence-transformers)",
                "properties_count": len(properties),
                "properties": [prop.name for prop in properties]
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


@router.delete("/collections/{collection_name}")
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
    
    try:
        # Check if Weaviate client is initialized
        if weaviate_client is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Weaviate client not initialized. Check if Weaviate is running."
            )
        
        # Check if collection exists
        if not weaviate_client.collections.exists(collection_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{collection_name}' does not exist"
            )
        
        # Get count before deletion (for reporting)
        deleted_count = 0
        try:
            collection = weaviate_client.collections.get(collection_name)
            count_result = collection.aggregate.over_all(total_count=True)
            deleted_count = count_result.total_count
        except Exception:
            pass  # If we can't get count, continue with deletion
        
        # Delete the collection
        weaviate_client.collections.delete(collection_name)
        
        return {
            "success": True,
            "message": f"Collection '{collection_name}' deleted successfully",
            "deleted_documents": deleted_count,
            "warning": "This action is permanent and cannot be undone"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting collection: {str(e)}"
        )
