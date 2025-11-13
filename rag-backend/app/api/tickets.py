"""
Ticket management endpoints.
Handles ticket CRUD operations and AI-powered ticket resolution.
"""
from fastapi import APIRouter, HTTPException, status 
from typing import Optional, List
import weaviate.classes as wvc
from app.db import get_weaviate_client
from app.models import (
    TicketModel,
    TicketSubmissionModel,
    TicketResponse,
    AITicketResponse,
)
from app.services import embedding_service, ai_service, ticket_service
from app.core.config import settings

router = APIRouter(prefix="/api/v1/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponse)
async def upload_ticket(ticket: TicketModel, collection_name: Optional[str] = None):
    """
    Upload a single ticket to Weaviate collection with local embeddings.
    
    Args:
        ticket: TicketModel with all required fields
        collection_name: Name of the collection to upload to (default: SupportTickets)
        
    Returns:
        TicketResponse: Success status and ticket details
        
    Raises:
        HTTPException: If Weaviate is not connected or upload fails
    """
    weaviate_client = get_weaviate_client()
    
    # Check if Weaviate client is connected
    if weaviate_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weaviate vector database is not connected. Please check connection."
        )
    
    # Use default collection name if not provided
    target_collection = collection_name or settings.TICKETS_COLLECTION_NAME
    
    try:
        # Check if collection exists
        if not weaviate_client.collections.exists(target_collection):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{target_collection}' does not exist"
            )
        
        # Get the target collection
        tickets_collection = weaviate_client.collections.get(target_collection)
        
        # Prepare ticket data for Weaviate
        ticket_data = {
            "ticket_id": ticket.ticket_id,
            "title": ticket.title,
            "description": ticket.description,
            "category": ticket.category,
            "status": ticket.status,
            "severity": ticket.severity,
            "application": ticket.application,
            "affected_users": ticket.affected_users,
            "environment": ticket.environment,
            "solution": ticket.solution,
            "reasoning": ticket.reasoning,
            "timestamp": ticket.timestamp
        }
        
        # Generate embedding from ticket content (title + description + solution)
        text_to_embed = f"{ticket.title} {ticket.description} {ticket.solution}"
        embedding = embedding_service.generate_embedding(text_to_embed)
        
        # Insert ticket into Weaviate with local embedding
        uuid = tickets_collection.data.insert(
            properties=ticket_data,
            vector=embedding  # Provide embedding manually
        )
        
        return TicketResponse(
            success=True,
            message=f"Ticket {ticket.ticket_id} uploaded successfully to collection '{target_collection}' with embedding",
            ticket_id=ticket.ticket_id,
            data={"uuid": str(uuid), "ticket": ticket_data, "collection": target_collection}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading ticket: {str(e)}"
        )


@router.post("/batch")
async def upload_tickets_batch(tickets: List[TicketModel], collection_name: Optional[str] = None):
    """
    Upload multiple tickets to Weaviate collection in batch with local embeddings.
    
    Args:
        tickets: List of TicketModel objects
        collection_name: Name of the collection to upload to (default: SupportTickets)
        
    Returns:
        Dict: Success status, count, and details
        
    Raises:
        HTTPException: If Weaviate is not connected or batch upload fails
    """
    weaviate_client = get_weaviate_client()
    
    # Check if Weaviate client is connected
    if weaviate_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weaviate vector database is not connected. Please check connection."
        )
    
    # Use default collection name if not provided
    target_collection = collection_name or settings.TICKETS_COLLECTION_NAME
    
    try:
        # Check if collection exists
        if not weaviate_client.collections.exists(target_collection):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{target_collection}' does not exist"
            )
        
        # Get the target collection
        tickets_collection = weaviate_client.collections.get(target_collection)
        
        # Prepare batch data
        uploaded_count = 0
        failed_tickets = []
        
        # Use Weaviate batch insert for efficiency
        with tickets_collection.batch.dynamic() as batch:
            for ticket in tickets:
                try:
                    ticket_data = {
                        "ticket_id": ticket.ticket_id,
                        "title": ticket.title,
                        "description": ticket.description,
                        "category": ticket.category,
                        "status": ticket.status,
                        "severity": ticket.severity,
                        "application": ticket.application,
                        "affected_users": ticket.affected_users,
                        "environment": ticket.environment,
                        "solution": ticket.solution,
                        "reasoning": ticket.reasoning,
                        "timestamp": ticket.timestamp
                    }
                    
                    # Generate embedding from ticket content
                    text_to_embed = f"{ticket.title} {ticket.description} {ticket.solution}"
                    embedding = embedding_service.generate_embedding(text_to_embed)
                    
                    # Add to batch with embedding
                    batch.add_object(
                        properties=ticket_data,
                        vector=embedding
                    )
                    uploaded_count += 1
                    
                except Exception as e:
                    failed_tickets.append({
                        "ticket_id": ticket.ticket_id,
                        "error": str(e)
                    })
        
        return {
            "success": True,
            "message": f"Batch upload completed to collection '{target_collection}' with local embeddings",
            "collection": target_collection,
            "total_tickets": len(tickets),
            "uploaded": uploaded_count,
            "failed": len(failed_tickets),
            "failed_tickets": failed_tickets if failed_tickets else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in batch upload: {str(e)}"
        )


@router.post("/submit-user-input", response_model=AITicketResponse)
async def RAG_Response(ticket: TicketSubmissionModel):
    """
    This endpoint uses RAG (Retrieval-Augmented Generation) to find similar tickets and generate solutions.
    
    Workflow:
    1. Search vector DB for similar past incidents (85% similarity threshold)
    2. Generate AI solution using Groq's Llama model based on similar tickets
    3. Return reasoning, solution, and similar tickets found (WITHOUT saving to DB)
    
    Args:
        ticket: TicketSubmissionModel with incident details
        
    Returns:
        AITicketResponse: Generated ticket ID, status, AI reasoning, solution, and similar tickets
        
    Raises:
        HTTPException: If Weaviate is not connected or processing fails
    """
    weaviate_client = get_weaviate_client()
    
    # Check if Weaviate client is connected
    if weaviate_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weaviate vector database is not connected. Please check connection."
        )
    
    try:
        # Use default collection name if not provided
        target_collection = ticket.collection_name or settings.TICKETS_COLLECTION_NAME
        
        # Check if collection exists
        if not weaviate_client.collections.exists(target_collection):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{target_collection}' does not exist. Create it first."
            )
        
        # Step 1: Search for similar tickets in vector DB
        query_text = f"{ticket.title} {ticket.description} {ticket.application}"
        similar_tickets = ticket_service.find_similar_tickets(
            weaviate_client=weaviate_client,
            collection_name=target_collection,
            query_text=query_text,
            k=settings.DEFAULT_SEARCH_LIMIT,
            similarity_threshold=settings.SIMILARITY_THRESHOLD
        )
        
        # Step 2: Prepare ticket data for AI
        ticket_data = {
            "title": ticket.title,
            "description": ticket.description,
            "category": ticket.category,
            "severity": ticket.severity,
            "application": ticket.application,
            "affected_users": ticket.affected_users,
            "environment": ticket.environment
        }
        
        # Step 3: Generate AI solution using Groq's open-source LLM
        reasoning, solution = ai_service.generate_solution(ticket_data, similar_tickets)
        
        # Step 4: Determine ticket status
        has_error = reasoning.startswith("Unable to generate") or solution.startswith("Unable to generate")
        has_similar_tickets = len(similar_tickets) > 0
        
        if has_error:
            status_value = "Open"
            message = "AI generation failed. Manual review recommended."
        elif not has_similar_tickets:
            status_value = "Open"
            message = "No similar incidents found (85% threshold). Expert validation recommended."
        else:
            status_value = "Resolved"
            message = f"AI-generated solution based on {len(similar_tickets)} similar incident(s)."
        
        # Step 5: Generate temporary ticket ID (not saved to DB)
        ticket_id = ticket_service.generate_ticket_id(
            weaviate_client=weaviate_client,
            collection_name=target_collection,
            prefix="TKT-PREVIEW"
        )
        
        # Step 6: Format similar tickets for response
        similar_tickets_response = ticket_service.format_similar_tickets_for_response(similar_tickets)
        
        # Return response (ticket NOT saved to database)
        return AITicketResponse(
            success=True,
            ticket_id=ticket_id,
            status=status_value,
            reasoning=reasoning,
            solution=solution,
            similar_tickets=similar_tickets_response,
            message=f"{message} Note: Ticket not saved to database."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing ticket submission: {str(e)}"
        )


@router.get("")
async def get_all_tickets(limit: int = 100, offset: int = 0, collection_name: Optional[str] = None):
    """
    Retrieve all tickets from Weaviate collection.
    
    Args:
        limit: Maximum number of tickets to return (default 100)
        offset: Number of tickets to skip (default 0)
        collection_name: Name of the collection to query (default: SupportTickets)
        
    Returns:
        Dict: List of tickets and metadata
        
    Raises:
        HTTPException: If Weaviate is not connected or query fails
    """
    weaviate_client = get_weaviate_client()
    
    # Check if Weaviate client is connected
    if weaviate_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weaviate vector database is not connected. Please check connection."
        )
    
    # Use default collection name if not provided
    target_collection = collection_name or settings.TICKETS_COLLECTION_NAME
    
    try:
        # Check if collection exists
        if not weaviate_client.collections.exists(target_collection):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{target_collection}' does not exist"
            )
        
        # Get the target collection
        tickets_collection = weaviate_client.collections.get(target_collection)
        
        # Query all tickets with limit and offset
        response = tickets_collection.query.fetch_objects(
            limit=limit,
            offset=offset
        )
        
        # Get total count
        total_result = tickets_collection.aggregate.over_all(total_count=True)
        total_count = total_result.total_count
        
        # Extract ticket data
        tickets_list = []
        for obj in response.objects:
            ticket_data = obj.properties
            ticket_data["uuid"] = str(obj.uuid)
            tickets_list.append(ticket_data)
        
        return {
            "success": True,
            "collection": target_collection,
            "total_count": total_count,
            "returned_count": len(tickets_list),
            "limit": limit,
            "offset": offset,
            "tickets": tickets_list
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving tickets: {str(e)}"
        )


@router.get("/search")
async def search_tickets(query: str, limit: int = 3, collection_name: Optional[str] = None):
    """
    Search for similar tickets using vector similarity search with local embeddings.
    
    Args:
        query: Search query (natural language description)
        limit: Maximum number of results (default 3)
        collection_name: Name of the collection to search in (default: SupportTickets)
        
    Returns:
        Dict: List of similar tickets with similarity scores
        
    Raises:
        HTTPException: If search fails
    """
    weaviate_client = get_weaviate_client()
    
    # Check if Weaviate client is connected
    if weaviate_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weaviate vector database is not connected. Please check connection."
        )
    
    # Use default collection name if not provided
    target_collection = collection_name or settings.TICKETS_COLLECTION_NAME
    
    try:
        # Check if collection exists
        if not weaviate_client.collections.exists(target_collection):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{target_collection}' does not exist"
            )
        
        # Get the target collection
        tickets_collection = weaviate_client.collections.get(target_collection)
        
        # Generate embedding from search query using local model
        query_embedding = embedding_service.generate_embedding(query)
        
        # Perform vector similarity search using generated embedding
        response = tickets_collection.query.near_vector(
            near_vector=query_embedding,
            limit=limit,
            return_metadata=wvc.query.MetadataQuery(distance=True, certainty=True)
        )
        
        # Extract results
        results = []
        for obj in response.objects:
            result_data = obj.properties
            result_data["uuid"] = str(obj.uuid)
            result_data["distance"] = obj.metadata.distance
            result_data["certainty"] = obj.metadata.certainty
            result_data["similarity_score"] = obj.metadata.certainty  # 0-1 score
            results.append(result_data)
        
        return {
            "success": True,
            "collection": target_collection,
            "query": query,
            "results_count": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching tickets: {str(e)}"
        )


@router.get("/{ticket_id}")
async def get_ticket_by_id(ticket_id: str, collection_name: Optional[str] = None):
    """
    Retrieve a specific ticket by its ticket_id.
    
    Args:
        ticket_id: Unique ticket identifier (e.g., TKT-0001)
        collection_name: Name of the collection to search in (default: SupportTickets)
        
    Returns:
        Dict: Ticket data
        
    Raises:
        HTTPException: If ticket not found or query fails
    """
    weaviate_client = get_weaviate_client()
    
    # Check if Weaviate client is connected
    if weaviate_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weaviate vector database is not connected. Please check connection."
        )
    
    # Use default collection name if not provided
    target_collection = collection_name or settings.TICKETS_COLLECTION_NAME
    
    try:
        # Check if collection exists
        if not weaviate_client.collections.exists(target_collection):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{target_collection}' does not exist"
            )
        
        # Get the target collection
        tickets_collection = weaviate_client.collections.get(target_collection)
        
        # Query for specific ticket_id
        response = tickets_collection.query.fetch_objects(
            filters=wvc.query.Filter.by_property("ticket_id").equal(ticket_id),
            limit=1
        )
        
        if len(response.objects) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket {ticket_id} not found in collection '{target_collection}'"
            )
        
        # Extract ticket data
        obj = response.objects[0]
        ticket_data = obj.properties
        ticket_data["uuid"] = str(obj.uuid)
        
        return {
            "success": True,
            "collection": target_collection,
            "ticket": ticket_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving ticket: {str(e)}"
        )


@router.delete("/{ticket_id}")
async def delete_ticket_by_id(ticket_id: str, collection_name: Optional[str] = None):
    """
    Delete a specific ticket from Weaviate by its ticket_id.
    
    Args:
        ticket_id: Unique ticket identifier (e.g., TKT-0001)
        collection_name: Name of the collection to delete from (default: SupportTickets)
        
    Returns:
        Dict: Success status and deletion details
        
    Raises:
        HTTPException: If ticket not found or deletion fails
    """
    weaviate_client = get_weaviate_client()
    
    # Check if Weaviate client is connected
    if weaviate_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weaviate vector database is not connected. Please check connection."
        )
    
    # Use default collection name if not provided
    target_collection = collection_name or settings.TICKETS_COLLECTION_NAME
    
    try:
        # Check if collection exists
        if not weaviate_client.collections.exists(target_collection):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{target_collection}' does not exist"
            )
        
        # Get the target collection
        tickets_collection = weaviate_client.collections.get(target_collection)
        
        # First, find the ticket to get its UUID
        response = tickets_collection.query.fetch_objects(
            filters=wvc.query.Filter.by_property("ticket_id").equal(ticket_id),
            limit=1
        )
        
        # Check if ticket exists
        if len(response.objects) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket '{ticket_id}' not found in collection '{target_collection}'"
            )
        
        # Get the UUID of the ticket to delete
        ticket_uuid = response.objects[0].uuid
        ticket_data = response.objects[0].properties
        
        # Delete the ticket by UUID
        tickets_collection.data.delete_by_id(ticket_uuid)
        
        return {
            "success": True,
            "message": f"Ticket '{ticket_id}' deleted successfully from collection '{target_collection}'",
            "collection": target_collection,
            "deleted_ticket": {
                "ticket_id": ticket_id,
                "uuid": str(ticket_uuid),
                "title": ticket_data.get("title", "N/A")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting ticket: {str(e)}"
        )
