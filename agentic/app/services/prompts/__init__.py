"""
Prompts module initialization.
"""
from app.services.prompts.prompt_templates import (
    create_agent_prompt,
    create_rag_synthesis_prompt,
    create_document_qa_prompt,
    create_web_search_synthesis_prompt,
    create_conversational_prompt,
    get_prompt_template,
    PROMPT_TEMPLATES,
)

__all__ = [
    "create_agent_prompt",
    "create_rag_synthesis_prompt",
    "create_document_qa_prompt",
    "create_web_search_synthesis_prompt",
    "create_conversational_prompt",
    "get_prompt_template",
    "PROMPT_TEMPLATES",
]
