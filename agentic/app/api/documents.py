"""
Document management endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict
from app.models.schemas import (
    DocumentUpload,
    DocumentResponse,
    DocumentListResponse,
    DocumentSearchQuery,
    DocumentSearchResponse,
    DocumentSearchResult,
)
from app.services import get_document_service

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=Dict, status_code=status.HTTP_201_CREATED)
async def upload_document(document: DocumentUpload):
    """
    Upload a document to the vector database.
    Documents are stored as complete units (not chunked).
    """
    try:
        document_service = get_document_service()
        
        result = document_service.add_document(
            title=document.title,
            content=document.content,
            document_type=document.document_type,
            source=document.source,
            metadata=document.metadata
        )
        
        return {
            "message": "Document uploaded successfully",
            "document_id": result["document_id"],
            "word_count": result["word_count"]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.get("/list", response_model=DocumentListResponse)
async def list_documents(limit: int = 100):
    """List all documents in the vector database."""
    try:
        document_service = get_document_service()
        documents = document_service.list_documents(limit=limit)
        
        # Convert to response models
        document_responses = [
            DocumentResponse(
                document_id=doc["document_id"],
                title=doc["title"],
                content=doc["content"],
                document_type=doc["document_type"],
                source=doc["source"],
                metadata=doc["metadata"],
                created_at=doc["created_at"],
                word_count=doc["word_count"]
            )
            for doc in documents
        ]
        
        return DocumentListResponse(
            documents=document_responses,
            total=len(document_responses)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(search_query: DocumentSearchQuery):
    """Search for similar documents using semantic search."""
    try:
        document_service = get_document_service()
        
        results = document_service.search_documents(
            query=search_query.query,
            limit=search_query.limit,
            threshold=search_query.threshold
        )
        
        # Convert to response models
        search_results = [
            DocumentSearchResult(
                document_id=doc["document_id"],
                title=doc["title"],
                content=doc["content"],
                similarity_score=doc["similarity_score"],
                metadata=doc["metadata"]
            )
            for doc in results
        ]
        
        return DocumentSearchResponse(
            query=search_query.query,
            results=search_results,
            total_results=len(search_results)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search documents: {str(e)}"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Get a specific document by ID."""
    try:
        document_service = get_document_service()
        document = document_service.get_document(document_id)
        
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}"
            )
        
        return DocumentResponse(
            document_id=document["document_id"],
            title=document["title"],
            content=document["content"],
            document_type=document["document_type"],
            source=document["source"],
            metadata=document["metadata"],
            created_at=document["created_at"],
            word_count=document["word_count"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document: {str(e)}"
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str):
    """Delete a document by ID."""
    try:
        document_service = get_document_service()
        deleted = document_service.delete_document(document_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found: {document_id}"
            )
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


