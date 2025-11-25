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
    """Agentic RAG query endpoint.

    Workflow:
    1. Search vector DB for similar past incidents
    2. Use agentic RAG with web search and vector search tools
    3. Generate AI solution with agent reasoning and tool usage
    4. Return reasoning, and solution
    
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
        
        # Extract information from agent response
        answer = result.get("answer", "")
        sources = result.get("sources", [])
        agent_steps = result.get("agent_steps", [])
        
        # Parse agent output to extract reasoning (ROOT CAUSE) and solution (RESOLUTION)
        reasoning = ""
        solution = ""
        
        # Store original for fallback
        original_answer = answer
        
        # Step 1: Remove "Final Answer:" and everything after "Thought:" that follows it
        if "Final Answer:" in answer:
            final_answer_pos = answer.find("Final Answer:")
            # Check if there's useful content before "Final Answer:"
            before_final = answer[:final_answer_pos].strip()
            if "ROOT CAUSE:" in before_final and "RESOLUTION:" in before_final:
                # Use content before Final Answer
                answer = before_final
            else:
                # Final Answer might contain a summary, ignore it and use what's before
                answer = before_final if before_final else answer
        
        # Step 2: Handle multiple "Thought:" occurrences
        # The structured content usually appears after a "Thought:" that analyzes the results
        if "Thought:" in answer:
            parts = answer.split("Thought:")
            # Find the part that has both ROOT CAUSE and RESOLUTION
            found_structured = False
            for i, part in enumerate(parts):
                if "ROOT CAUSE:" in part and "RESOLUTION:" in part:
                    answer = part.strip()
                    found_structured = True
                    break
            
            # If no part has both, check if ROOT CAUSE and RESOLUTION are in different parts
            if not found_structured:
                combined = ""
                for i, part in enumerate(parts):
                    if "ROOT CAUSE:" in part or "RESOLUTION:" in part:
                        combined += part + " "
                if combined and ("ROOT CAUSE:" in combined and "RESOLUTION:" in combined):
                    answer = combined.strip()
                elif len(parts) > 1:
                    # Use the last meaningful part
                    answer = parts[-1].strip()
        
        # Step 3: Remove the <reasoning> block as it's separate from ROOT CAUSE
        if "<reasoning>" in answer and "</reasoning>" in answer:
            reasoning_block_start = answer.find("<reasoning>")
            reasoning_block_end = answer.find("</reasoning>") + len("</reasoning>")
            answer = answer[:reasoning_block_start] + answer[reasoning_block_end:]
            answer = answer.strip()
        
        # Step 4: Extract ROOT CAUSE and RESOLUTION
        if "ROOT CAUSE:" in answer and "RESOLUTION:" in answer:
            root_cause_pos = answer.find("ROOT CAUSE:")
            resolution_pos = answer.find("RESOLUTION:")
            
            # reasoning = ROOT CAUSE content (between ROOT CAUSE: and RESOLUTION:)
            reasoning = answer[root_cause_pos:resolution_pos].strip()
            
            # solution = RESOLUTION content (everything after RESOLUTION:)
            solution = answer[resolution_pos:].strip()
            
            # Clean up any trailing "Thought:" or "Final Answer:" in solution
            if "Thought:" in solution:
                solution = solution[:solution.find("Thought:")].strip()
            if "Final Answer:" in solution:
                solution = solution[:solution.find("Final Answer:")].strip()
            
        elif "ROOT CAUSE:" in answer:
            root_cause_pos = answer.find("ROOT CAUSE:")
            reasoning = answer[root_cause_pos:].strip()
            if "Thought:" in reasoning:
                reasoning = reasoning[:reasoning.find("Thought:")].strip()
            solution = "RESOLUTION:\n\nNo detailed resolution steps provided by the agent."
            
        elif "RESOLUTION:" in answer:
            resolution_pos = answer.find("RESOLUTION:")
            reasoning = "ROOT CAUSE:\n\nThe agent did not provide a structured root cause analysis."
            solution = answer[resolution_pos:].strip()
            if "Thought:" in solution:
                solution = solution[:solution.find("Thought:")].strip()
            
        else:
            # Fallback: Check if original_answer has the structured format
            if "ROOT CAUSE:" in original_answer and "RESOLUTION:" in original_answer:
                # Try parsing the original answer
                root_cause_pos = original_answer.find("ROOT CAUSE:")
                resolution_pos = original_answer.find("RESOLUTION:")
                
                reasoning = original_answer[root_cause_pos:resolution_pos].strip()
                solution = original_answer[resolution_pos:].strip()
                
                # Clean up
                if "Thought:" in reasoning:
                    reasoning = reasoning[:reasoning.find("Thought:")].strip()
                if "Thought:" in solution:
                    solution = solution[:solution.find("Thought:")].strip()
                if "Final Answer:" in solution:
                    solution = solution[:solution.find("Final Answer:")].strip()
            else:
                # True fallback - create generic response
                reasoning = f"ROOT CAUSE:\n\nBased on analysis using {len(agent_steps)} steps and {len(sources)} sources, the agent identified potential causes but did not provide structured root cause analysis."
                solution = f"RESOLUTION:\n\nThe agent provided analysis but did not format the resolution in the expected structure. Please review the agent's findings and formulate appropriate resolution steps."
        
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
            status_value = "Open"
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
        "response_format": "AITicketResponse"
    }
