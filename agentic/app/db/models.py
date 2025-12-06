"""
SQLAlchemy database models for PostgreSQL.
Defines User, ChatSession, and ChatMessage tables.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.db.postgres_client import Base


class User(Base):
    """User model for authentication and profile data."""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)  # user_abc123
    
    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Email verification
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_code = Column(String(10), nullable=True)
    verification_code_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Password reset
    reset_code = Column(String(10), nullable=True)
    reset_code_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(user_id='{self.user_id}', email='{self.email}')>"


class ChatSession(Base):
    """Chat session model for conversation metadata."""
    
    __tablename__ = "chat_sessions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(50), unique=True, index=True, nullable=False)  # session_abc123
    
    # Foreign key to User
    user_id = Column(String(50), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Session metadata
    title = Column(String(500), nullable=True)  # Auto-generated from first message
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")
    
    def __repr__(self):
        return f"<ChatSession(session_id='{self.session_id}', title='{self.title}')>"


class ChatMessage(Base):
    """Chat message model for individual messages in conversations."""
    
    __tablename__ = "chat_messages"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message_id = Column(String(50), unique=True, index=True, nullable=False)  # msg_abc123
    
    # Foreign key to ChatSession
    session_id = Column(String(50), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Message data
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    
    # Metadata (JSON stored as Text, can be parsed)
    metadata_json = Column(Text, nullable=True)  # Store LLM provider, similar tickets, etc. as JSON string
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage(message_id='{self.message_id}', role='{self.role}')>"
