"""
LangChain-based prompt management for ticket resolution.
Loads prompt templates from separate files for easy modification.
"""
from typing import Dict, List
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate


# Base directory for prompt templates
PROMPT_TEMPLATES_DIR = Path(__file__).parent / "prompt_templates"


# Load a prompt template from a text file
def load_template_file(filename: str) -> str:
    """Load a prompt template from a text file."""
    template_path = PROMPT_TEMPLATES_DIR / filename
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt template not found: {template_path}")


class PromptConfig:
    """Configuration for prompt behavior and formatting."""
    
    # Response format markers
    ROOT_CAUSE_MARKER = "ROOT CAUSE:"
    RESOLUTION_MARKER = "RESOLUTION:"
    
    # Similarity thresholds
    MIN_SIMILARITY_THRESHOLD = 0.85
    HIGH_CONFIDENCE_THRESHOLD = 0.95
    
    # Context limits
    MAX_SIMILAR_TICKETS = 5
    MAX_CONTEXT_LENGTH = 10000  # characters


class PromptTemplateManager:
    """Manages LangChain prompt templates loaded from separate files."""
    
    def __init__(self):
        # Load message templates from files
        self.system_message = load_template_file("system_message.txt")
        self.human_message_template = load_template_file("human_message.txt")
        self.ai_example_message = load_template_file("ai_example_message.txt")
        
        # Load helper templates
        self.similar_ticket_item_template = load_template_file("similar_ticket_item.txt")
        self.no_similar_tickets_template = load_template_file("no_similar_tickets.txt")
    
    def build_similar_tickets_context(self, similar_tickets: List[Dict]) -> str:
        """Build the similar tickets context section."""
        if not similar_tickets:
            return self.no_similar_tickets_template
        
        # Build list of similar tickets
        tickets_text = ""
        for i, ticket in enumerate(similar_tickets, 1):
            similarity_percent = f"{ticket['similarity_score'] * 100:.1f}"
            tickets_text += self.similar_ticket_item_template.format(
                number=i,
                similarity_percent=similarity_percent,
                title=ticket['title'],
                description=ticket['description'],
                solution=ticket['solution'],
                reasoning=ticket['reasoning']
            )
        
        return f"### Similar Past Cloud Application Issues (85%+ match confidence):\n\n{tickets_text}"
    
    def create_chat_prompt(self, include_example: bool = True) -> ChatPromptTemplate:
        """
        Create a LangChain ChatPromptTemplate with system, human, and optional AI example messages.
        
        Args:
            include_example: Whether to include the AI example message (few-shot learning)
        
        Returns:
            ChatPromptTemplate ready for use with LLM
        """
        messages = [
            ("system", self.system_message),
        ]
        
        # Add few-shot example if requested
        if include_example:
            # Use a simplified human message for the example
            example_human = """### Current Incident Details:
**Title:** Database Connection Timeout
**Description:** Users experiencing timeout errors when trying to access the application. Error logs show 'Connection pool exhausted' messages.
**Category:** Database
**Severity:** Critical
**Application:** user-service
**Environment:** production
**Affected Users:** 500+

### Similar Past Cloud Application Issues (85%+ match confidence):
Past tickets showed similar connection pool issues during high load periods.

### Your Task:
Provide root cause analysis and resolution."""
            
            messages.extend([
                ("human", example_human),
                ("ai", self.ai_example_message)
            ])
        
        # Add the actual human message template with variables
        messages.append(("human", self.human_message_template))
        
        return ChatPromptTemplate.from_messages(messages)


# Global instances
prompt_config = PromptConfig()
prompt_manager = PromptTemplateManager()


def get_ticket_resolution_prompt(ticket_data: Dict, similar_tickets: List[Dict], include_example: bool = True) -> ChatPromptTemplate:
    """
    Create a LangChain ChatPromptTemplate for ticket resolution.
    
    Args:
        ticket_data: Current ticket information
        similar_tickets: List of similar past tickets
        include_example: Whether to include few-shot example (default: True)
    
    Returns:
        ChatPromptTemplate with all variables populated except the final invocation
    """
    # Build similar tickets context
    similar_tickets_context = prompt_manager.build_similar_tickets_context(similar_tickets)
    
    # Create the chat prompt
    chat_prompt = prompt_manager.create_chat_prompt(include_example=include_example)
    
    # Return the template with partial variables filled
    # The actual invocation will happen in the AI service
    return chat_prompt, {
        "title": ticket_data.get('title', 'N/A'),
        "description": ticket_data.get('description', 'N/A'),
        "category": ticket_data.get('category', 'N/A'),
        "severity": ticket_data.get('severity', 'N/A'),
        "application": ticket_data.get('application', 'N/A'),
        "environment": ticket_data.get('environment', 'N/A'),
        "affected_users": ticket_data.get('affected_users', 'N/A'),
        "similar_tickets_context": similar_tickets_context
    }
