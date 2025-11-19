"""
AI service for generating ticket solutions using LLM with LangChain.
Handles root cause analysis and solution generation using structured prompts.
"""
from typing import Dict, List, Tuple  
from langchain_groq import ChatGroq 
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings
from app.services.prompts import get_ticket_resolution_prompt, prompt_config


class AIService:
    """Service for AI-powered ticket solution generation using LangChain."""
    
    def __init__(self):
        """Initialize the AI service with LangChain components."""
        self.llm = None
        self.output_parser = StrOutputParser()
    
    def _get_llm(self) -> ChatGroq:
        """Get or create the LLM instance."""
        if self.llm is None:
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            
            self.llm = ChatGroq(
                model=settings.GROQ_MODEL,
                temperature=settings.GROQ_TEMPERATURE,
                api_key=settings.GROQ_API_KEY
            )
        return self.llm
    
    def generate_solution(self, ticket_data: Dict, similar_tickets: List[Dict]) -> Tuple[str, str]:
        """
        Generate solution using LangChain ChatPromptTemplate with structured messages.
        
        Args:
            ticket_data: Dictionary containing ticket information (User Input Tickets)
            similar_tickets: List of similar tickets from vector DB (Retrieved from Cosine-Similarity)
            
        Returns:
            Tuple of (reasoning, solution)
        """
        try:
            # Get LLM instance
            llm = self._get_llm()
            
            # Get LangChain ChatPromptTemplate and variables
            chat_prompt, prompt_variables = get_ticket_resolution_prompt(
                ticket_data, 
                similar_tickets,
                include_example=True  # Include few-shot example
            )
            
            # Create LangChain chain: Prompt -> LLM -> Output Parser
            chain = chat_prompt | llm | self.output_parser
            
            # Execute the chain
            response_text = chain.invoke(prompt_variables)
            
            # Parse reasoning and solution
            reasoning, solution = self._parse_response(response_text)
            
            return reasoning, solution
        
        except Exception as e:
            return self._handle_error(e)
    
    def _parse_response(self, response_text: str) -> Tuple[str, str]:
        """Parse the LLM response into reasoning and solution."""
        reasoning = ""
        solution = ""
        
        # Use centralized markers from prompt config
        if prompt_config.ROOT_CAUSE_MARKER in response_text and prompt_config.RESOLUTION_MARKER in response_text:
            parts = response_text.split(prompt_config.RESOLUTION_MARKER)
            reasoning = parts[0].replace(prompt_config.ROOT_CAUSE_MARKER, "").strip()
            solution = parts[1].strip()
        else:
            # Fallback if format is not followed
            lines = response_text.split("\n", 1)
            reasoning = lines[0] if len(lines) > 0 else "Analysis based on incident description."
            solution = lines[1] if len(lines) > 1 else response_text
        
        return reasoning, solution
    
    def _handle_error(self, error: Exception) -> Tuple[str, str]:
        """Handle errors during AI generation."""
        error_msg = str(error)
        
        # Provide specific error messages
        if "API key" in error_msg.lower() or "authentication" in error_msg.lower():
            return (
                "Unable to generate root cause analysis. API authentication failed. Please check your GROQ_API_KEY in .env file.",
                "Unable to generate resolution steps. API authentication error - verify your Groq API key is correct."
            )
        elif "rate limit" in error_msg.lower():
            return (
                "Unable to generate root cause analysis. Rate limit exceeded.",
                "Unable to generate resolution steps. Try again in a moment or switch to llama-3.1-8b-instant model for higher rate limits."
            )
        else:
            return (
                f"Unable to generate root cause analysis. Error: {error_msg}",
                f"Unable to generate resolution steps. Please investigate manually. Error: {error_msg}"
            )


# Global instance
ai_service = AIService()


def get_ai_service() -> AIService:
    """
    Dependency function to get AI service.
    by FastAPI endpoints.
    """
    return ai_service
