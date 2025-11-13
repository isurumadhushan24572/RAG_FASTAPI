from typing import Dict, List # for type annotations
from pathlib import Path # for file path management


# Base directory for prompt templates
PROMPT_TEMPLATES_DIR = Path(__file__).parent / "prompt_templates"


def load_prompt_template(template_name: str) -> str:
    """Load a prompt template from a text file name."""

    template_path = PROMPT_TEMPLATES_DIR / f"{template_name}.txt"
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt template not found: {template_path}")


class PromptTemplates:
    """Collection of prompt templates for different AI operations."""
    
    # Load prompt templates from files
    TICKET_RESOLUTION_TEMPLATE = load_prompt_template("ticket_resolution")
    SIMILAR_TICKETS_CONTEXT_TEMPLATE = load_prompt_template("similar_tickets_context")
    NO_SIMILAR_TICKETS_TEMPLATE = load_prompt_template("no_similar_tickets")
    SIMILAR_TICKET_ITEM_TEMPLATE = load_prompt_template("similar_ticket_item")
    CUSTOM_PROMPT_TEMPLATE = load_prompt_template("custom_prompt")
    
    @staticmethod
    def build_similar_tickets_context(similar_tickets: List[Dict]) -> str:
        # Similar tickets context builder

        if not similar_tickets:
            return PromptTemplates.NO_SIMILAR_TICKETS_TEMPLATE
        
        # Build list of similar tickets
        similar_tickets_list = ""
        for i, ticket in enumerate(similar_tickets, 1):
            similarity_percent = f"{ticket['similarity_score'] * 100:.1f}"
            similar_tickets_list += PromptTemplates.SIMILAR_TICKET_ITEM_TEMPLATE.format(
                number=i,
                similarity_percent=similarity_percent,
                title=ticket['title'],
                description=ticket['description'],
                solution=ticket['solution'],
                reasoning=ticket['reasoning']
            )
        
        # Use the context template
        context = PromptTemplates.SIMILAR_TICKETS_CONTEXT_TEMPLATE.format(
            similar_tickets_list=similar_tickets_list
        )
        
        return context
    
    @staticmethod
    def ticket_resolution_prompt(ticket_data: Dict, context: str) -> str:
        """Generate the ticket resolution prompt."""

        return PromptTemplates.TICKET_RESOLUTION_TEMPLATE.format(
            title=ticket_data['title'],
            description=ticket_data['description'],
            category=ticket_data['category'],
            severity=ticket_data['severity'],
            application=ticket_data['application'],
            environment=ticket_data['environment'],
            affected_users=ticket_data['affected_users'],
            context=context
        )
    
    @staticmethod
    def custom_prompt(
        system_role: str,
        ticket_data: Dict,
        context: str,
        additional_instructions: str = ""
    ) -> str:
        """
        Generate a custom prompt with flexible parameters.
        
        Args:
            system_role: Role description for the AI (e.g., "expert DevOps engineer")
            ticket_data: Current ticket information
            context: Similar tickets context
            additional_instructions: Any additional instructions for the AI
            
        Returns:
            Custom prompt string
        """
        return PromptTemplates.CUSTOM_PROMPT_TEMPLATE.format(
            system_role=system_role,
            title=ticket_data.get('title', 'N/A'),
            description=ticket_data.get('description', 'N/A'),
            category=ticket_data.get('category', 'N/A'),
            severity=ticket_data.get('severity', 'N/A'),
            application=ticket_data.get('application', 'N/A'),
            environment=ticket_data.get('environment', 'N/A'),
            context=context,
            additional_instructions=additional_instructions
        )


class PromptConfig:
    """Configuration for prompt behavior and formatting."""
    
    # Response format markers
    ROOT_CAUSE_MARKER = "ROOT CAUSE:"
    RESOLUTION_MARKER = "RESOLUTION:"
    
    # Default system roles
    DEFAULT_SYSTEM_ROLE = "an expert cloud application support engineer"
    DEVOPS_ROLE = "an expert DevOps engineer specializing in cloud infrastructure"
    DATABASE_ROLE = "an expert database administrator with cloud expertise"
    SECURITY_ROLE = "an expert security engineer for cloud applications"
    
    # Similarity thresholds
    MIN_SIMILARITY_THRESHOLD = 0.85
    HIGH_CONFIDENCE_THRESHOLD = 0.95
    
    # Context limits
    MAX_SIMILAR_TICKETS = 5
    MAX_CONTEXT_LENGTH = 4000  # characters


# Singleton instance for easy access
prompt_templates = PromptTemplates()
prompt_config = PromptConfig()


# Export commonly used functions
def get_ticket_resolution_prompt(ticket_data: Dict, similar_tickets: List[Dict]) -> str:
    """Generate the ticket resolution prompt with similar tickets context."""
    
    context = prompt_templates.build_similar_tickets_context(similar_tickets)
    return prompt_templates.ticket_resolution_prompt(ticket_data, context)
