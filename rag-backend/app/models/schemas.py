"""
Pydantic models for request/response validation.
Contains all data models used throughout the application.
"""
from typing import Optional, Dict, Any, List  # import type hints
from pydantic import BaseModel  # import BaseModel for Pydantic models


# ===================== TICKET MODELS =====================

class TicketModel(BaseModel):
    """Pydantic model for ticket data validation"""
    ticket_id: str
    title: str
    description: str
    category: str
    status: str
    severity: str
    application: str
    affected_users: str
    environment: str
    solution: str
    reasoning: str
    timestamp: str


class TicketSubmissionModel(BaseModel):
    """Model for submitting a new ticket to get AI-generated solution"""
    title: str
    description: str
    category: str
    severity: str = "Medium"
    application: str = ""
    affected_users: str = ""
    environment: str = "Production"
    collection_name: Optional[str] = None  # Collection to search for similar tickets


# ===================== RESPONSE MODELS =====================

class TicketResponse(BaseModel):
    """Response model for ticket operations"""
    success: bool
    message: str
    ticket_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class AITicketResponse(BaseModel):
    """Response model for AI-generated ticket solution"""
    success: bool
    ticket_id: str
    status: str  # "Resolved" or "Open"
    reasoning: str  # Root cause analysis
    solution: str  # Resolution steps
    similar_tickets: List[Dict[str, Any]]  # Similar tickets found
    message: str


# ===================== COLLECTION MODELS =====================

class CollectionPropertyModel(BaseModel):
    """Model for defining a property in a collection"""
    name: str
    data_type: str  # TEXT, NUMBER, BOOLEAN, DATE, etc.
    description: Optional[str] = None


class CreateCollectionModel(BaseModel):
    """Model for creating a new collection"""
    name: str
    description: Optional[str] = None
    properties: List[CollectionPropertyModel]
    use_vectorizer: bool = False  # Whether to use automatic vectorization
