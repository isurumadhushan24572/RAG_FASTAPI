"""
Agentic RAG service.
Orchestrates LLM agents with tools for intelligent question answering.
"""
from typing import List, Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from langchain_core.messages import HumanMessage, AIMessage
import time
from app.core.config import settings
from app.services.tools import create_vector_search_tool, create_web_search_tool


class AgenticRAGService:
    """Service for agentic RAG with tool usage."""
    
    def __init__(self):
        """Initialize the agentic RAG service."""
        self.llm: Optional[ChatGroq] = None
        self.agent = None
        self.tools = []
    
    def _get_llm(self) -> ChatGroq:
        """Get or create the LLM instance."""
        if self.llm is None:
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not found in environment variables")
            
            self.llm = ChatGroq(
                model=settings.GROQ_MODEL,
                temperature=settings.GROQ_TEMPERATURE,
                api_key=settings.GROQ_API_KEY,
            )
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
            web_tool = create_web_search_tool(max_results=5)
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
                
                # Extract sources
                if action.tool == "web_search":
                    sources.append({
                        "type": "web_search",
                        "query": action.tool_input,
                    })
                elif action.tool == "vector_search":
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
