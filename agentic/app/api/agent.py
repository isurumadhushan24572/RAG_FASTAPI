"""
Agent endpoints for agentic RAG queries.
"""
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import TicketSubmissionModel, AITicketResponse
from app.services import get_agentic_rag_service, embedding_service
from app.db import get_weaviate_client
from app.core.config import settings
import weaviate.classes as wvc

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/query", response_model=AITicketResponse)
async def query_agent(ticket: TicketSubmissionModel):
    """
    Agentic RAG endpoint - Query the agent with ticket submission format.
    
    This endpoint uses the same input format as rag-backend's submit-user-input,
    but leverages the agentic RAG system with multi-tool reasoning.
    
    Workflow:
    1. Search vector DB for similar past incidents
    2. Use agentic RAG with web search and vector search tools
    3. Generate AI solution with agent reasoning and tool usage
    4. Return reasoning, solution, and similar tickets found
    
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
        
        # Construct detailed query for the agent using structured format
        query = f"""Analyze this support ticket and provide a structured response with root cause analysis and resolution steps.

### Current Incident:
Title: {ticket.title}
Description: {ticket.description}
Category: {ticket.category}
Severity: {ticket.severity}
Application: {ticket.application}
Environment: {ticket.environment}
Affected Users: {ticket.affected_users}

INSTRUCTIONS:
1. First, use the vector_search tool to find similar past tickets in the knowledge base
2. If needed, use web_search tool to find additional context about error codes or Azure services
3. Then provide your analysis in this EXACT format:

<reasoning>
1. Deconstruct Current Incident:
   * Key symptoms, error codes, and affected components
   
2. Correlate with Past Incidents:
   * Similar tickets found in knowledge base
   * Their root causes and resolutions
   
3. Formulate Hypothesis:
   * Most likely root cause
   * Critical diagnostic steps
</reasoning>

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

Be specific to Azure, cloud applications, microservices, APIs, and DevOps practices."""
        
        # Execute agentic RAG query
        result = agent_service.query(
            query=query,
            collection_name=target_collection
        )
        
        # Extract information from agent response
        answer = result.get("answer", "")
        sources = result.get("sources", [])
        agent_steps = result.get("agent_steps", [])
        
        # Parse agent output to extract reasoning and solution
        reasoning = ""
        solution = ""
        
        # Try to extract structured format
        if "<reasoning>" in answer and "</reasoning>" in answer:
            # Extract reasoning block
            reasoning_start = answer.find("<reasoning>")
            reasoning_end = answer.find("</reasoning>")
            reasoning = answer[reasoning_start:reasoning_end + 12].strip()
            
            # Extract everything after reasoning as the solution
            solution_start = answer.find("ROOT CAUSE:")
            if solution_start > 0:
                solution = answer[solution_start:].strip()
            else:
                solution = answer[reasoning_end + 12:].strip()
        elif "ROOT CAUSE:" in answer:
            # If no reasoning block but has ROOT CAUSE format
            parts = answer.split("ROOT CAUSE:", 1)
            reasoning = "Agent performed multi-step analysis using vector search and web search tools."
            solution = "ROOT CAUSE:" + parts[1] if len(parts) > 1 else answer
        elif "RESOLUTION:" in answer:
            # If has RESOLUTION but no ROOT CAUSE
            parts = answer.split("RESOLUTION:", 1)
            reasoning = parts[0].strip() if parts[0] else "Agent analysis completed"
            solution = "RESOLUTION:" + parts[1] if len(parts) > 1 else answer
        else:
            # Fallback: use full answer
            reasoning = f"Agent analyzed the ticket using {len(agent_steps)} steps and {len(sources)} sources."
            solution = answer
        
        # Extract similar tickets from vector search sources
        similar_tickets = []
        for source in sources:
            if source.get("type") == "vector_search":
                similar_tickets.append(source)
        
        # Determine status based on findings
        has_similar = len(similar_tickets) > 0
        has_web_sources = any(s.get("type") == "web_search" for s in sources)
        
        if has_similar:
            status_value = "Resolved"
            message = f"AI-generated solution using agentic RAG. Found {len(similar_tickets)} similar ticket(s)."
        elif has_web_sources:
            status_value = "Resolved"
            message = "AI-generated solution using web search and agent reasoning."
        else:
            status_value = "Open"
            message = "Agent provided solution but no similar tickets found. Manual review recommended."
        
        # Generate temporary ticket ID
        ticket_count = 0
        try:
            collection = weaviate_client.collections.get(target_collection)
            count_result = collection.aggregate.over_all(total_count=True)
            ticket_count = count_result.total_count
        except:
            pass
        
        ticket_id = f"TKT-AGENT-{ticket_count + 1:04d}"
        
        return AITicketResponse(
            success=True,
            ticket_id=ticket_id,
            status=status_value,
            reasoning=reasoning if reasoning else "Agent analysis completed with multi-tool reasoning",
            solution=solution if solution else answer,
            message=f"{message} Agent used {len(agent_steps)} steps. Ticket not saved to database."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing agent query: {str(e)}"
        )


@router.get("/info")
async def get_agent_info():
    """Get information about the agent's capabilities."""
    return {
        "agent_type": "Tool-Calling Agentic RAG",
        "llm_model": "llama-3.3-70b-versatile (Groq)",
        "input_format": "TicketSubmissionModel (same as rag-backend)",
        "available_tools": [
            {
                "name": "vector_search",
                "description": "Search tickets/documents in the knowledge base using semantic similarity"
            },
            {
                "name": "web_search",
                "description": "Search the web for current information using Tavily/DuckDuckGo"
            }
        ],
        "features": [
            "Multi-tool reasoning and orchestration",
            "Iterative problem solving",
            "Source attribution and tracking",
            "Context-aware responses",
            "Web search for up-to-date information",
            "Vector search for similar historical tickets"
        ],
        "endpoint": "/agent/query",
        "response_format": "AITicketResponse (same as rag-backend)"
    }
