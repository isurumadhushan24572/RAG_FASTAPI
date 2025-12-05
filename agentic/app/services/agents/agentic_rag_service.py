"""
Agentic RAG service.
Orchestrates LLM agents with tools for intelligent question answering.
"""
from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType
from langchain_core.messages import HumanMessage, AIMessage
import time
from app.core.config import settings
from app.services.tools import create_vector_search_tool, create_web_search_tool


class AgenticRAGService:
    """Service for agentic RAG with tool usage."""
    
    def __init__(self):
        """Initialize the agentic RAG service."""
        self.llm = None
        self.agent = None
        self.tools = []
        self.llm_provider = None  # Track which LLM provider is being used
    
    def _get_llm(self):
        """Get or create the LLM instance with Groq as priority, Gemini as fallback."""
        if self.llm is None:
            # Try Groq first (Priority 1)
            if settings.GROQ_API_KEY:
                try:
                    self.llm = ChatGroq(
                        model=settings.GROQ_MODEL,
                        temperature=settings.GROQ_TEMPERATURE,
                        api_key=settings.GROQ_API_KEY,
                    )
                    self.llm_provider = "Groq"
                    print(f"✅ Using Groq LLM: {settings.GROQ_MODEL}")
                except Exception as e:
                    print(f"⚠️ Failed to initialize Groq: {str(e)}")
                    self.llm = None
            
            # Fallback to Gemini if Groq is not available
            if self.llm is None:
                if settings.GEMINI_API_KEY:
                    try:
                        self.llm = ChatGoogleGenerativeAI(
                            model=settings.GEMINI_MODEL,
                            temperature=settings.GEMINI_TEMPERATURE,
                            google_api_key=settings.GEMINI_API_KEY,
                        )
                        self.llm_provider = "Gemini"
                        print(f"✅ Using Gemini LLM: {settings.GEMINI_MODEL}")
                    except Exception as e:
                        print(f"❌ Failed to initialize Gemini: {str(e)}")
                        raise ValueError("No LLM provider available. Please configure GROQ_API_KEY or GEMINI_API_KEY")
                else:
                    raise ValueError("No LLM API key found. Please configure GROQ_API_KEY or GEMINI_API_KEY in environment variables")
        
        return self.llm
    
    def _initialize_tools(
        self,
        use_web_search: bool = True,
        use_vector_search: bool = True,
        collection_name: Optional[str] = None
    ):
        """
        Initialize tools for the agent.
        
        Args:
            use_web_search: Enable web search tool
            use_vector_search: Enable vector search tool
            collection_name: Optional collection name for vector search
        """
        self.tools = []
        
        if use_vector_search:
            vector_tool = create_vector_search_tool(max_results=settings.DEFAULT_SEARCH_LIMIT, collection_name=collection_name)
            self.tools.append(vector_tool)
            target_collection = collection_name or settings.DOCUMENTS_COLLECTION_NAME
            print(f"✅ Vector search tool enabled (collection: {target_collection}, threshold: {settings.SIMILARITY_THRESHOLD}, max_results: {settings.DEFAULT_SEARCH_LIMIT})")
        
        if use_web_search:
            web_tool = create_web_search_tool(max_results=settings.DEFAULT_SEARCH_LIMIT, search_engine="tavily")
            self.tools.append(web_tool)
            print("✅ Web search tool enabled")
        
        if not self.tools:
            raise ValueError("At least one tool must be enabled")
    
    def _create_agent(self):
        """
        Create the agent with tools using initialize_agent.
        
        Returns:
            Configured agent
        """
        llm = self._get_llm()
        
        # Create agent using initialize_agent (more compatible)
        agent = initialize_agent(
            tools=self.tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=settings.AGENT_MAX_ITERATIONS,
            max_execution_time=settings.AGENT_MAX_EXECUTION_TIME,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )
        
        return agent
    
    def query(
        self,
        query: str,
        use_web_search: bool = True,
        use_vector_search: bool = True,
        collection_name: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Query the agentic RAG system.
        
        Args:
            query: User query
            use_web_search: Enable web search tool
            use_vector_search: Enable vector search tool
            collection_name: Optional collection name for vector search (uses default if not provided)
            chat_history: Optional chat history
            
        Returns:
            Dictionary with answer, sources, and agent steps
        """
        start_time = time.time()
        
        try:
            # Initialize tools with collection_name
            self._initialize_tools(use_web_search, use_vector_search, collection_name)
            
            # Create agent
            agent = self._create_agent()
            
            # Prepare input
            agent_input = {
                "input": query,
            }
            
            # Add chat history if provided
            if chat_history:
                messages = []
                for msg in chat_history:
                    if msg.get("role") == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg.get("role") == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
                agent_input["chat_history"] = messages
            
            # Execute agent
            print(f"🤖 Agent executing query: {query}")
            result = agent.invoke(agent_input)
            
            # Extract information
            answer = result.get("output", "No answer generated")
            intermediate_steps = result.get("intermediate_steps", [])
            
            # IMPORTANT: Capture the full agent reasoning from intermediate steps
            # The agent prints the structured response during execution but only returns "Final Answer"
            # We need to reconstruct the full output from the agent's thoughts
            full_agent_output = ""
            
            for step in intermediate_steps:
                action, observation = step
                # The action log contains the agent's thoughts and structured output
                if hasattr(action, 'log'):
                    full_agent_output += action.log + "\n"
            
            # If we captured the full output with ROOT CAUSE and RESOLUTION, use that instead
            # Use case-insensitive check
            full_output_upper = full_agent_output.upper()
            if ("ROOT CAUSE" in full_output_upper or "REASONING" in full_output_upper) and \
               ("SOLUTION" in full_output_upper or "RESOLUTION" in full_output_upper):
                # Only use full output if it seems to contain the final answer structure
                # Sometimes intermediate steps contain partial thoughts
                if len(full_agent_output) > len(answer):
                    answer = full_agent_output
            
            # Process agent steps
            agent_steps = []
            sources = []
            
            for step in intermediate_steps:
                action, observation = step
                
                step_info = {
                    "tool": action.tool,
                    "tool_input": action.tool_input,
                    "observation": observation[:500] + "..." if len(observation) > 500 else observation
                }
                agent_steps.append(step_info)
                
                # Extract sources with full details for vector search
                if action.tool == "web_search":
                    sources.append({
                        "type": "web_search",
                        "query": action.tool_input,
                    })
                elif action.tool == "vector_search":
                    # Parse the observation to extract ticket details
                    # The observation contains formatted text like "Document 1:\nTitle: ...\n"
                    try:
                        # Extract ticket IDs, titles, and similarity from observation
                        documents = observation.split("---")
                        for doc_text in documents:
                            if "Title:" in doc_text and "Similarity:" in doc_text:
                                # Extract title
                                title_start = doc_text.find("Title:") + 6
                                title_end = doc_text.find("\n", title_start)
                                title = doc_text[title_start:title_end].strip()
                                
                                # Extract similarity
                                sim_start = doc_text.find("Similarity:") + 11
                                sim_end = doc_text.find("\n", sim_start)
                                similarity_str = doc_text[sim_start:sim_end].strip()
                                
                                # Convert percentage string to float (e.g., "92.34%" -> 0.9234)
                                try:
                                    similarity = float(similarity_str.replace("%", "")) / 100
                                except:
                                    similarity = 0.0
                                
                                # Try to extract ticket_id from content
                                ticket_id = "N/A"
                                if "ticket_id" in doc_text.lower():
                                    # Look for patterns like "ticket_id: TKT-001"
                                    import re
                                    match = re.search(r'ticket[_\s]id[:\s]+([A-Z0-9-]+)', doc_text, re.IGNORECASE)
                                    if match:
                                        ticket_id = match.group(1)
                                
                                # Extract category and severity if present
                                category = "N/A"
                                severity = "N/A"
                                if "category" in doc_text.lower():
                                    cat_match = re.search(r'category[:\s]+([^\n]+)', doc_text, re.IGNORECASE)
                                    if cat_match:
                                        category = cat_match.group(1).strip()
                                if "severity" in doc_text.lower():
                                    sev_match = re.search(r'severity[:\s]+([^\n]+)', doc_text, re.IGNORECASE)
                                    if sev_match:
                                        severity = sev_match.group(1).strip()
                                
                                sources.append({
                                    "type": "vector_search",
                                    "query": action.tool_input,
                                    "ticket_id": ticket_id,
                                    "title": title,
                                    "similarity_score": similarity,
                                    "category": category,
                                    "severity": severity
                                })
                    except Exception as e:
                        # Fallback: just store basic info
                        sources.append({
                            "type": "vector_search",
                            "query": action.tool_input,
                        })
            
            execution_time = time.time() - start_time
            
            print(f"✅ Agent completed in {execution_time:.2f}s with {len(agent_steps)} steps")
            
            return {
                "query": query,
                "answer": answer,
                "sources": sources,
                "agent_steps": agent_steps,
                "execution_time": execution_time,
                "tools_used": [tool.name for tool in self.tools],
                "llm_provider": self.llm_provider,  # Include which LLM was used
            }
        
        except Exception as e:
            execution_time = time.time() - start_time
            error_message = f"Error executing agent: {str(e)}"
            print(f"❌ {error_message}")
            
            return {
                "query": query,
                "answer": error_message,
                "sources": [],
                "agent_steps": [],
                "execution_time": execution_time,
                "error": str(e),
            }


# Global instance
agentic_rag_service = AgenticRAGService()


def get_agentic_rag_service() -> AgenticRAGService:
    """Dependency to get agentic RAG service."""
    return agentic_rag_service
