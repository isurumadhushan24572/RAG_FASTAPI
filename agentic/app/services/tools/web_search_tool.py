"""
Web search tool for agents.
Provides real-time web search capability using Tavily or DuckDuckGo.
"""
from typing import Optional, Union
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import Field
from app.core.config import settings

# Try to import Tavily first, fallback to DuckDuckGo
try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

try:
    from duckduckgo_search import DDGS
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False


class WebSearchTool(BaseTool):
    """Tool for searching the web for real-time information."""
    
    name: str = "web_search"
    description: str = (
        "Search the web for current information, news, or facts. "
        "Use this tool when you need up-to-date information that might not be in the knowledge base, "
        "such as recent events, current data, or general knowledge. "
        "Input should be a clear search query."
    )
    
    max_results: int = Field(default=5, description="Maximum number of search results")
    search_engine: str = Field(default="tavily", description="Search engine to use (tavily or duckduckgo)")
    
    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Execute web search.
        
        Args:
            query: Search query
            run_manager: Callback manager
            
        Returns:
            Formatted search results as string
        """
        try:
            # Try Tavily first if configured
            if self.search_engine == "tavily" and TAVILY_AVAILABLE and settings.TAVILY_API_KEY:
                return self._search_with_tavily(query)
            
            # Fallback to DuckDuckGo
            elif DUCKDUCKGO_AVAILABLE:
                return self._search_with_duckduckgo(query)
            
            else:
                return "Web search is not available. Please configure TAVILY_API_KEY or install duckduckgo-search."
        
        except Exception as e:
            return f"Error performing web search: {str(e)}"
    
    def _search_with_tavily(self, query: str) -> str:
        """Search using Tavily API."""
        try:
            client = TavilyClient(api_key=settings.TAVILY_API_KEY)
            
            # Perform search
            response = client.search(
                query=query,
                max_results=self.max_results,
                search_depth="basic"
            )
            
            if not response.get("results"):
                return "No web search results found."
            
            # Format results
            formatted_results = []
            for i, result in enumerate(response["results"], 1):
                formatted_results.append(
                    f"Result {i}:\n"
                    f"Title: {result.get('title', 'N/A')}\n"
                    f"Content: {result.get('content', 'N/A')}\n"
                    f"URL: {result.get('url', 'N/A')}\n"
                )
            
            return "\n---\n".join(formatted_results)
        
        except Exception as e:
            return f"Tavily search error: {str(e)}"
    
    def _search_with_duckduckgo(self, query: str) -> str:
        """Search using DuckDuckGo."""
        try:
            ddgs = DDGS()
            
            # Perform search
            results = list(ddgs.text(query, max_results=self.max_results))
            
            if not results:
                return "No web search results found."
            
            # Format results
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(
                    f"Result {i}:\n"
                    f"Title: {result.get('title', 'N/A')}\n"
                    f"Content: {result.get('body', 'N/A')}\n"
                    f"URL: {result.get('href', 'N/A')}\n"
                )
            
            return "\n---\n".join(formatted_results)
        
        except Exception as e:
            return f"DuckDuckGo search error: {str(e)}"
    
    async def _arun(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Async version of run."""
        return self._run(query, run_manager)


def create_web_search_tool(
    max_results: int = 5,
    search_engine: str = "tavily"
) -> WebSearchTool:
    """
    Factory function to create a web search tool.
    
    Args:
        max_results: Maximum number of search results
        search_engine: Search engine to use (tavily or duckduckgo)
        
    Returns:
        Configured WebSearchTool instance
    """
    return WebSearchTool(max_results=max_results, search_engine=search_engine)
