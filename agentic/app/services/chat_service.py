"""
Chat service for managing chat sessions and messages.
Handles conversation history with memory window (5 messages + first message).
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict
from sqlalchemy.orm import Session

from app.db.models import ChatSession, ChatMessage, User
from app.db.postgres_client import postgres_manager


class ChatService:
    """Service class for chat session and message management."""
    
    def __init__(self):
        """Initialize ChatService."""
        pass
    
    def _get_db(self) -> Session:
        """Get database session."""
        return postgres_manager.SessionLocal()
    
    def _find_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """Find user by user_id."""
        return db.query(User).filter(User.user_id == user_id).first()
    
    def create_session(
        self, 
        user_id: str, 
        title: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        Create a new chat session for a user.
        
        Args:
            user_id: User ID
            title: Optional session title (default: "New Conversation")
        
        Returns:
            (success, message, session_data)
        """
        db = None
        try:
            db = self._get_db()
            
            # Verify user exists
            user = self._find_user_by_id(db, user_id)
            if not user:
                return False, "User not found", None
            
            # Generate session ID
            session_id = f"session_{uuid.uuid4().hex[:16]}"
            
            # Create session
            new_session = ChatSession(
                session_id=session_id,
                user_id=user_id,
                title=title or "New Conversation",
                is_active=True
            )
            
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            
            return True, "Session created successfully", {
                "session_id": new_session.session_id,
                "title": new_session.title,
                "created_at": new_session.created_at.isoformat(),
                "is_active": new_session.is_active
            }
            
        except Exception as e:
            if db:
                db.rollback()
            print(f"Error creating chat session: {str(e)}")
            return False, f"Failed to create session: {str(e)}", None
        finally:
            if db:
                db.close()
    
    def get_user_sessions(
        self, 
        user_id: str, 
        include_inactive: bool = False
    ) -> Tuple[bool, str, List[Dict]]:
        """
        Get all chat sessions for a user.
        
        Args:
            user_id: User ID
            include_inactive: Include inactive sessions
        
        Returns:
            (success, message, sessions_list)
        """
        db = None
        try:
            db = self._get_db()
            
            query = db.query(ChatSession).filter(ChatSession.user_id == user_id)
            
            if not include_inactive:
                query = query.filter(ChatSession.is_active == True)
            
            sessions = query.order_by(ChatSession.updated_at.desc()).all()
            
            sessions_data = [
                {
                    "session_id": session.session_id,
                    "title": session.title,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                    "is_active": session.is_active,
                    "message_count": len(session.messages)
                }
                for session in sessions
            ]
            
            return True, "Sessions retrieved successfully", sessions_data
            
        except Exception as e:
            print(f"Error getting user sessions: {str(e)}")
            return False, f"Failed to get sessions: {str(e)}", []
        finally:
            if db:
                db.close()
    
    def get_session_messages(
        self, 
        session_id: str, 
        user_id: str
    ) -> Tuple[bool, str, List[Dict]]:
        """
        Get all messages for a chat session.
        
        Args:
            session_id: Session ID
            user_id: User ID (for authorization)
        
        Returns:
            (success, message, messages_list)
        """
        db = None
        try:
            db = self._get_db()
            
            # Get session and verify ownership
            session = db.query(ChatSession).filter(
                ChatSession.session_id == session_id,
                ChatSession.user_id == user_id
            ).first()
            
            if not session:
                return False, "Session not found or access denied", []
            
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at.asc()).all()
            
            messages_data = [
                {
                    "message_id": msg.message_id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                    "metadata": msg.metadata_json
                }
                for msg in messages
            ]
            
            return True, "Messages retrieved successfully", messages_data
            
        except Exception as e:
            print(f"Error getting session messages: {str(e)}")
            return False, f"Failed to get messages: {str(e)}", []
        finally:
            if db:
                db.close()
    
    def add_message(
        self, 
        session_id: str, 
        user_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        Add a message to a chat session.
        
        Args:
            session_id: Session ID
            user_id: User ID (for authorization)
            role: Message role ('user' or 'assistant')
            content: Message content
            metadata: Optional metadata dict
        
        Returns:
            (success, message, message_data)
        """
        db = None
        try:
            db = self._get_db()
            
            # Get session and verify ownership
            session = db.query(ChatSession).filter(
                ChatSession.session_id == session_id,
                ChatSession.user_id == user_id
            ).first()
            
            if not session:
                return False, "Session not found or access denied", None
            
            # Generate message ID
            message_id = f"msg_{uuid.uuid4().hex[:16]}"
            
            # Create message
            new_message = ChatMessage(
                message_id=message_id,
                session_id=session_id,
                role=role,
                content=content,
                metadata_json=metadata
            )
            
            db.add(new_message)
            
            # Update session's updated_at timestamp
            session.updated_at = datetime.now(timezone.utc)
            
            db.commit()
            db.refresh(new_message)
            
            return True, "Message added successfully", {
                "message_id": new_message.message_id,
                "role": new_message.role,
                "content": new_message.content,
                "created_at": new_message.created_at.isoformat(),
                "metadata": new_message.metadata_json
            }
            
        except Exception as e:
            if db:
                db.rollback()
            print(f"Error adding message: {str(e)}")
            return False, f"Failed to add message: {str(e)}", None
        finally:
            if db:
                db.close()
    
    def get_conversation_context(
        self, 
        session_id: str, 
        user_id: str
    ) -> Tuple[bool, str, List[Dict]]:
        """
        Get conversation context with memory window.
        Strategy: Last 5 message pairs + always include first message pair.
        
        Args:
            session_id: Session ID
            user_id: User ID (for authorization)
        
        Returns:
            (success, message, context_messages)
        """
        db = None
        try:
            db = self._get_db()
            
            # Get session and verify ownership
            session = db.query(ChatSession).filter(
                ChatSession.session_id == session_id,
                ChatSession.user_id == user_id
            ).first()
            
            if not session:
                return False, "Session not found or access denied", []
            
            # Get all messages ordered by creation time
            all_messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at.asc()).all()
            
            if not all_messages:
                return True, "No messages in session", []
            
            # Convert to dict format
            messages_list = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in all_messages
            ]
            
            # Memory strategy: window size 5 + first message pair
            if len(messages_list) <= 12:  # 6 pairs or less, return all
                return True, "Context retrieved", messages_list
            
            # Get first message pair (first user message + first assistant response)
            first_pair = []
            if len(messages_list) >= 2:
                first_pair = messages_list[:2]
            
            # Get last 5 message pairs (10 messages)
            last_messages = messages_list[-10:]
            
            # Combine: first pair + last 5 pairs (avoid duplicates)
            if len(messages_list) > 12:
                context_messages = first_pair + last_messages
            else:
                context_messages = messages_list
            
            return True, "Context retrieved with memory window", context_messages
            
        except Exception as e:
            print(f"Error getting conversation context: {str(e)}")
            return False, f"Failed to get context: {str(e)}", []
        finally:
            if db:
                db.close()
    
    def update_session_title(
        self, 
        session_id: str, 
        user_id: str, 
        title: str
    ) -> Tuple[bool, str]:
        """
        Update chat session title.
        
        Args:
            session_id: Session ID
            user_id: User ID (for authorization)
            title: New title
        
        Returns:
            (success, message)
        """
        db = None
        try:
            db = self._get_db()
            
            session = db.query(ChatSession).filter(
                ChatSession.session_id == session_id,
                ChatSession.user_id == user_id
            ).first()
            
            if not session:
                return False, "Session not found or access denied"
            
            session.title = title
            session.updated_at = datetime.now(timezone.utc)
            
            db.commit()
            
            return True, "Session title updated successfully"
            
        except Exception as e:
            if db:
                db.rollback()
            print(f"Error updating session title: {str(e)}")
            return False, f"Failed to update title: {str(e)}"
        finally:
            if db:
                db.close()
    
    def delete_session(
        self, 
        session_id: str, 
        user_id: str
    ) -> Tuple[bool, str]:
        """
        Mark a chat session as inactive (soft delete).
        
        Args:
            session_id: Session ID
            user_id: User ID (for authorization)
        
        Returns:
            (success, message)
        """
        db = None
        try:
            db = self._get_db()
            
            session = db.query(ChatSession).filter(
                ChatSession.session_id == session_id,
                ChatSession.user_id == user_id
            ).first()
            
            if not session:
                return False, "Session not found or access denied"
            
            session.is_active = False
            session.updated_at = datetime.now(timezone.utc)
            
            db.commit()
            
            return True, "Session deleted successfully"
            
        except Exception as e:
            if db:
                db.rollback()
            print(f"Error deleting session: {str(e)}")
            return False, f"Failed to delete session: {str(e)}"
        finally:
            if db:
                db.close()


# Singleton instance
chat_service = ChatService()
