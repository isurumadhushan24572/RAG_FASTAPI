"""
Chat API endpoints.
Handles chat session creation, message sending, and conversation history.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from app.models.schemas import (
    ChatSessionCreate,
    ChatSessionResponse,
    ChatMessageResponse,
    SendMessageRequest,
    SendMessageResponse,
    ChatSessionListResponse,
    ChatMessagesResponse
)
from app.services.chat_service import chat_service
from app.services.agents.agentic_rag_service import agentic_rag_service
from app.core.security import decode_access_token
from app.core.config import settings


router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


# Dependency to get current user from JWT token
async def get_current_user(authorization: str = Depends(lambda: None)):
    """Extract user from JWT token."""
    # This will be updated to use proper FastAPI security dependency
    # For now, expecting Authorization header manually
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # Remove "Bearer " prefix
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return payload.get("user_id")


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    session_data: ChatSessionCreate,
    user_id: str = Depends(get_current_user)
):
    """
    Create a new chat session.
    
    Returns a session_id that should be used for all subsequent messages.
    """
    success, message, session = chat_service.create_session(
        user_id=user_id,
        title=session_data.title
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "success": True,
        "message": message,
        "session": session
    }


@router.get("/sessions", response_model=ChatSessionListResponse)
async def get_user_sessions(
    user_id: str = Depends(get_current_user)
):
    """
    Get all active chat sessions for the current user.
    
    Sessions are ordered by most recently updated first.
    """
    success, message, sessions = chat_service.get_user_sessions(
        user_id=user_id,
        include_inactive=False
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return {
        "sessions": sessions,
        "total": len(sessions)
    }


@router.get("/sessions/{session_id}/messages", response_model=ChatMessagesResponse)
async def get_session_messages(
    session_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get all messages for a specific chat session.
    
    Messages are ordered chronologically (oldest first).
    """
    success, message, messages = chat_service.get_session_messages(
        session_id=session_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message
        )
    
    return {
        "session_id": session_id,
        "messages": messages,
        "total": len(messages)
    }


@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: str,
    message_data: SendMessageRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Send a message in a chat session and get AI response.
    
    - First message in session: Agent uses tools (vector search, web search) to find ROOT CAUSE and RESOLUTION
    - Follow-up messages: Conversational responses with memory (window size 5 + first message)
    """
    # Get conversation context
    _, _, context = chat_service.get_conversation_context(
        session_id=session_id,
        user_id=user_id
    )
    
    is_first_message = len(context) == 0
    
    # Add user message to database
    user_msg_success, user_msg_message, user_message = chat_service.add_message(
        session_id=session_id,
        user_id=user_id,
        role="user",
        content=message_data.message
    )
    
    if not user_msg_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=user_msg_message
        )
    
    # Generate AI response using agentic RAG service
    try:
        if is_first_message:
            # First message: Use tools for ROOT CAUSE and RESOLUTION
            print(f"🔍 First message - using tools for analysis")
            agent_result = agentic_rag_service.query(
                query=message_data.message,
                use_web_search=True,
                use_vector_search=True,
                collection_name=settings.DOCUMENTS_COLLECTION_NAME,
                chat_history=None  # No history for first message
            )
            
            ai_response_content = agent_result.get("answer", "Unable to generate response")
            metadata = {
                "is_first_message": True,
                "sources": agent_result.get("sources", []),
                "agent_steps": agent_result.get("agent_steps", []),
                "execution_time": agent_result.get("execution_time", 0),
                "llm_provider": agent_result.get("llm_provider", "unknown")
            }
        else:
            # Follow-up message: Use conversation history for context
            print(f"💬 Follow-up message - using conversation history")
            
            # Format context for agent (exclude current user message, it's already added)
            chat_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in context
            ]
            
            agent_result = agentic_rag_service.query(
                query=message_data.message,
                use_web_search=False,  # Disable web search for follow-ups
                use_vector_search=True,  # Keep vector search for relevant info
                collection_name=settings.DOCUMENTS_COLLECTION_NAME,
                chat_history=chat_history
            )
            
            ai_response_content = agent_result.get("answer", "Unable to generate response")
            metadata = {
                "is_first_message": False,
                "context_window_size": len(chat_history),
                "execution_time": agent_result.get("execution_time", 0),
                "llm_provider": agent_result.get("llm_provider", "unknown")
            }
    
    except Exception as e:
        print(f"❌ Error generating AI response: {str(e)}")
        ai_response_content = f"I apologize, but I encountered an error processing your request: {str(e)}"
        metadata = {"error": str(e), "is_first_message": is_first_message}
    
    # Add assistant message to database
    ai_msg_success, ai_msg_message, assistant_message = chat_service.add_message(
        session_id=session_id,
        user_id=user_id,
        role="assistant",
        content=ai_response_content,
        metadata=metadata
    )
    
    if not ai_msg_success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ai_msg_message
        )
    
    return {
        "user_message": user_message,
        "assistant_message": assistant_message,
        "is_first_message": is_first_message
    }


@router.put("/sessions/{session_id}/title")
async def update_session_title(
    session_id: str,
    title: str,
    user_id: str = Depends(get_current_user)
):
    """
    Update the title of a chat session.
    """
    success, message = chat_service.update_session_title(
        session_id=session_id,
        user_id=user_id,
        title=title
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "success": True,
        "message": message
    }


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Delete a chat session (soft delete - marks as inactive).
    """
    success, message = chat_service.delete_session(
        session_id=session_id,
        user_id=user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "success": True,
        "message": message
    }
