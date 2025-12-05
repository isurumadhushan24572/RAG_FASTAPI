"""
Ticket management endpoints - similar to rag-backend.
Handles ticket CRUD operations and AI-powered ticket resolution with agentic RAG.
"""
from fastapi import APIRouter, HTTPException, status
from typing import Optional, List
from collections import Counter
import weaviate.classes as wvc
from datetime import datetime
from app.db import get_weaviate_client
from app.models.schemas import (
    TicketModel,
    TicketSubmissionModel,
    TicketResponse,
    AITicketResponse,
)
from app.services import embedding_service
from app.services.agents.agentic_rag_service import get_agentic_rag_service
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
    """
    weaviate_client = get_weaviate_client()
    
    if weaviate_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weaviate vector database is not connected. Please check connection."
        )
    
    target_collection = collection_name or settings.DOCUMENTS_COLLECTION_NAME
    
    try:
        if not weaviate_client.collections.exists(target_collection):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{target_collection}' does not exist"
            )
        
        tickets_collection = weaviate_client.collections.get(target_collection)
        
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
        text_to_embed = f"{ticket.title} {ticket.description} {ticket.solution} {ticket.reasoning}"
        embedding = embedding_service.generate_embedding(text_to_embed)
        
        # Insert ticket into Weaviate
        uuid = tickets_collection.data.insert(
            properties=ticket_data,
            vector=embedding
        )
        
        return TicketResponse(
            success=True,
            message=f"Ticket {ticket.ticket_id} uploaded successfully to collection '{target_collection}'",
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
    """
    weaviate_client = get_weaviate_client()
    
    if weaviate_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weaviate vector database is not connected."
        )
    
    target_collection = collection_name or settings.DOCUMENTS_COLLECTION_NAME
    
    try:
        if not weaviate_client.collections.exists(target_collection):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{target_collection}' does not exist"
            )
        
        tickets_collection = weaviate_client.collections.get(target_collection)
        
        uploaded_count = 0
        failed_tickets = []
        
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
                    
                    text_to_embed = f"{ticket.title} {ticket.description} {ticket.solution}"
                    embedding = embedding_service.generate_embedding(text_to_embed)
                    
                    batch.add_object(properties=ticket_data, vector=embedding)
                    uploaded_count += 1
                    
                except Exception as e:
                    failed_tickets.append({"ticket_id": ticket.ticket_id, "error": str(e)})
        
        return {
            "success": True,
            "message": f"Batch upload completed to collection '{target_collection}'",
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
async def submit_user_input(ticket: TicketSubmissionModel):
    """
    AGENTIC RAG endpoint - Uses AI agents with tool calling to generate solutions.
    
    Workflow:
    1. Search vector DB for similar past incidents (85% similarity threshold)
    2. Use agentic RAG system with web search and vector search tools
    3. Generate AI solution using Groq's Llama model with agent reasoning
    4. Return reasoning, solution, and similar tickets found (WITHOUT saving to DB)
    
    Args:
        ticket: TicketSubmissionModel with incident details
        
    Returns:
        AITicketResponse: Generated ticket ID, status, AI reasoning, solution, and similar tickets
    """
    weaviate_client = get_weaviate_client()
    
    if weaviate_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weaviate vector database is not connected."
        )
    
    try:
        target_collection = ticket.collection_name or settings.DOCUMENTS_COLLECTION_NAME
        
        if not weaviate_client.collections.exists(target_collection):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{target_collection}' does not exist."
            )
        
        # Get agentic RAG service
        agent_service = get_agentic_rag_service()
        
        # Prepare query for agent
        query = f"""Analyze this support ticket and provide a solution:

Title: {ticket.title}
Description: {ticket.description}
Category: {ticket.category}
Severity: {ticket.severity}
Application: {ticket.application}
Environment: {ticket.environment}
Affected Users: {ticket.affected_users}

INSTRUCTIONS:
1. FIRST, use the 'vector_search' tool ONCE to find similar past tickets.
2. SECOND, use the 'web_search' tool ONCE to find external documentation.
3. After using both tools, you MUST provide your Final Answer in this EXACT format:

ROOT CAUSE: [Your detailed root cause analysis, referencing similar past tickets if found]

RESOLUTION:

**Immediate Mitigation:**
[Quick actions to restore service]

**Diagnostic Steps:**
1. [Specific checks and queries]
2. [Log files and monitoring]
3. [Configuration verification]

**Fix Implementation:**
[Step-by-step resolution with specific commands/actions]

**Verification:**
[How to confirm the fix worked]

**Preventive Measures:**
[Actions to prevent recurrence]

IMPORTANT: After providing the ROOT CAUSE and RESOLUTION, you MUST end with "Final Answer: [repeat the ROOT CAUSE and RESOLUTION]" to complete your response."""
        
        # Execute agentic RAG query
        result = agent_service.query(
            query=query,
            collection_name=target_collection
        )
        
        # Extract reasoning and solution from agent response
        answer = result.get("answer", "")
        sources = result.get("sources", [])
        agent_steps = result.get("agent_steps", [])
        
        # The agent's full output is in intermediate steps, not just in "answer"
        # Try to reconstruct from agent steps if answer is incomplete
        full_output = answer
        
        # Check if we need to extract from intermediate steps
        if "ROOT CAUSE:" not in answer or "RESOLUTION:" not in answer:
            # Look through agent steps for the thought containing ROOT CAUSE
            for step in agent_steps:
                observation = step.get("observation", "")
                if "ROOT CAUSE:" in observation and "RESOLUTION:" in observation:
                    full_output = observation
                    break
        
        # Clean up agent artifacts
        # Remove "Final Answer:" prefix if present
        if "Final Answer:" in full_output:
            full_output = full_output.split("Final Answer:", 1)[-1].strip()
        
        # Remove trailing "Thought:" sections (agent reasoning artifacts)
        if "\nThought:" in full_output:
            full_output = full_output.split("\nThought:")[0].strip()
        
        # Also check for the case where ROOT CAUSE appears before "Observation:"
        if "Observation:" in full_output and "ROOT CAUSE:" in full_output:
            # The ROOT CAUSE might be in a Thought before Observation
            parts = full_output.split("Observation:")
            for part in parts:
                if "ROOT CAUSE:" in part and "RESOLUTION:" in part:
                    full_output = part.strip()
                    break
        
        # Parse agent output to extract reasoning and solution
        reasoning = ""
        solution = ""
        
        if "ROOT CAUSE:" in full_output and "RESOLUTION:" in full_output:
            # Split by RESOLUTION marker
            parts = full_output.split("RESOLUTION:", 1)
            
            # Extract ROOT CAUSE section (remove the marker itself)
            reasoning_section = parts[0].strip()
            if "ROOT CAUSE:" in reasoning_section:
                reasoning = reasoning_section.split("ROOT CAUSE:", 1)[1].strip()
            else:
                reasoning = reasoning_section
            
            # Extract RESOLUTION section (include the word RESOLUTION for display)
            solution = "RESOLUTION:\n\n" + parts[1].strip()
            
        elif "ROOT CAUSE:" in full_output:
            # Only ROOT CAUSE found
            reasoning = full_output.split("ROOT CAUSE:", 1)[1].strip()
            solution = "RESOLUTION:\n\nNo detailed resolution steps provided by the agent."
            
        elif "RESOLUTION:" in full_output:
            # Only RESOLUTION found
            reasoning = "The agent did not provide a structured root cause analysis."
            solution = "RESOLUTION:\n\n" + full_output.split("RESOLUTION:", 1)[1].strip()
            
        else:
            # Fallback: No structured format detected
            reasoning = "Agent analysis in progress. Full response below."
            solution = full_output if full_output else answer
        
        # Determine status based on similarity and agent confidence
        similar_tickets = [s for s in sources if s.get("type") == "vector_search"]
        has_similar = len(similar_tickets) > 0
        
        if has_similar:
            status_value = "Resolved"
            message = f"AI-generated solution based on {len(similar_tickets)} similar incident(s) using agentic RAG."
        else:
            status_value = "Open"
            message = "No similar incidents found (85% threshold). Agent used web search and reasoning."
        
        # Generate temporary ticket ID
        ticket_count = 0
        try:
            collection = weaviate_client.collections.get(target_collection)
            count_result = collection.aggregate.over_all(total_count=True)
            ticket_count = count_result.total_count
        except:
            pass
        
        ticket_id = f"TKT-PREVIEW-{ticket_count + 1:04d}"
        
        # Format similar tickets for response
        similar_tickets_response = [
            {
                "ticket_id": st.get("ticket_id", "N/A"),
                "title": st.get("title", "Untitled"),
                "similarity_score": st.get("similarity_score", 0),
                "similarity_percent": f"{st.get('similarity_score', 0) * 100:.1f}",
                "category": st.get("category", "N/A"),
                "severity": st.get("severity", "N/A")
            }
            for st in similar_tickets if st.get("type") == "vector_search"
        ]
        
        return AITicketResponse(
            success=True,
            ticket_id=ticket_id,
            status=status_value,
            reasoning=reasoning,
            solution=solution,
            similar_tickets=similar_tickets_response,
            llm_provider=result.get("llm_provider", "Unknown"),
            message=f"{message} Note: Ticket not saved to database."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing ticket submission: {str(e)}"
        )


@router.get("/stats")
async def get_ticket_stats(collection_name: Optional[str] = None):
    """
    Get statistics for tickets (severity, status, environment counts).
    """
    weaviate_client = get_weaviate_client()
    
    if weaviate_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weaviate vector database is not connected."
        )
    
    target_collection = collection_name or settings.DOCUMENTS_COLLECTION_NAME
    
    try:
        if not weaviate_client.collections.exists(target_collection):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{target_collection}' does not exist"
            )
        
        tickets_collection = weaviate_client.collections.get(target_collection)
        
        # Fetch all objects to aggregate in Python (simple approach for small datasets)
        # For large datasets, use Weaviate's aggregate.over_all(group_by=...) if available
        response = tickets_collection.query.fetch_objects(limit=10000)
        
        severity_counts = Counter()
        status_counts = Counter()
        environment_counts = Counter()
        
        for obj in response.objects:
            props = obj.properties
            if props.get("severity"):
                severity_counts[props.get("severity")] += 1
            if props.get("status"):
                status_counts[props.get("status")] += 1
            if props.get("environment"):
                environment_counts[props.get("environment")] += 1
                
        return {
            "success": True,
            "collection": target_collection,
            "total_tickets": len(response.objects),
            "stats": {
                "severity": dict(severity_counts),
                "status": dict(status_counts),
                "environment": dict(environment_counts)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating stats: {str(e)}"
        )


@router.get("")
async def get_all_tickets(limit: int = 100, offset: int = 0, collection_name: Optional[str] = None):
    """Retrieve all tickets from Weaviate collection."""
    weaviate_client = get_weaviate_client()
    
    if weaviate_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weaviate vector database is not connected."
        )
    
    target_collection = collection_name or settings.DOCUMENTS_COLLECTION_NAME
    
    try:
        if not weaviate_client.collections.exists(target_collection):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{target_collection}' does not exist"
            )
        
        tickets_collection = weaviate_client.collections.get(target_collection)
        
        response = tickets_collection.query.fetch_objects(limit=limit, offset=offset)
        
        total_result = tickets_collection.aggregate.over_all(total_count=True)
        total_count = total_result.total_count
        
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
    """Search for similar tickets using vector similarity search."""
    weaviate_client = get_weaviate_client()
    
    if weaviate_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weaviate vector database is not connected."
        )
    
    target_collection = collection_name or settings.DOCUMENTS_COLLECTION_NAME
    
    try:
        if not weaviate_client.collections.exists(target_collection):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{target_collection}' does not exist"
            )
        
        tickets_collection = weaviate_client.collections.get(target_collection)
        
        query_embedding = embedding_service.generate_embedding(query)
        
        response = tickets_collection.query.near_vector(
            near_vector=query_embedding,
            limit=limit,
            return_metadata=wvc.query.MetadataQuery(distance=True, certainty=True)
        )
        
        results = []
        for obj in response.objects:
            result_data = obj.properties
            result_data["uuid"] = str(obj.uuid)
            result_data["distance"] = obj.metadata.distance
            result_data["certainty"] = obj.metadata.certainty
            result_data["similarity_score"] = obj.metadata.certainty
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
    """Retrieve a specific ticket by its ticket_id."""
    weaviate_client = get_weaviate_client()
    
    if weaviate_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weaviate vector database is not connected."
        )
    
    target_collection = collection_name or settings.DOCUMENTS_COLLECTION_NAME
    
    try:
        if not weaviate_client.collections.exists(target_collection):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{target_collection}' does not exist"
            )
        
        tickets_collection = weaviate_client.collections.get(target_collection)
        
        response = tickets_collection.query.fetch_objects(
            filters=wvc.query.Filter.by_property("ticket_id").equal(ticket_id),
            limit=1
        )
        
        if len(response.objects) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket {ticket_id} not found"
            )
        
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
    """Delete a specific ticket from Weaviate by its ticket_id."""
    weaviate_client = get_weaviate_client()
    
    if weaviate_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weaviate vector database is not connected."
        )
    
    target_collection = collection_name or settings.DOCUMENTS_COLLECTION_NAME
    
    try:
        if not weaviate_client.collections.exists(target_collection):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{target_collection}' does not exist"
            )
        
        tickets_collection = weaviate_client.collections.get(target_collection)
        
        response = tickets_collection.query.fetch_objects(
            filters=wvc.query.Filter.by_property("ticket_id").equal(ticket_id),
            limit=1
        )
        
        if len(response.objects) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticket '{ticket_id}' not found"
            )
        
        ticket_uuid = response.objects[0].uuid
        ticket_data = response.objects[0].properties
        
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
