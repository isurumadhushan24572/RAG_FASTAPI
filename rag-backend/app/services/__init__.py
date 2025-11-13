"""Services module for business logic."""
from app.services.embedding_service import embedding_service, get_embedding_service
from app.services.ai_service import ai_service, get_ai_service
from app.services.ticket_service import ticket_service, get_ticket_service
from app.services.prompts import (
    prompt_templates,
    prompt_config,
    get_ticket_resolution_prompt,
)

__all__ = [
    "embedding_service",
    "get_embedding_service",
    "ai_service",
    "get_ai_service",
    "ticket_service",
    "get_ticket_service",
    "prompt_templates",
    "prompt_config",
    "get_ticket_resolution_prompt",
]
