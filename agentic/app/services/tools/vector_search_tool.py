"""
Vector database search tool for agents.
Provides semantic search capability using Weaviate.
"""
from typing import Optional, List, Dict, Any
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import Field
from app.services.document_service import get_document_service
from app.core.config import settings


class VectorSearchTool(BaseTool):
    """Tool for searching documents in the vector database."""
    
    name: str = "vector_search"
    description: str = (
        "Search for relevant documents in the knowledge base using semantic search. "
        "Use this tool when you need to find information from stored documents. "
        "Input should be a search query describing what information you're looking for."
    )
    
    max_results: int = Field(default=5, description="Maximum number of results to return")
    collection_name: Optional[str] = Field(default=None, description="Collection name to search in")
    
    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Execute vector search.
        
        Args:
            query: Search query
            run_manager: Callback manager
            
        Returns:
            Formatted search results as string
        """
        try:
            document_service = get_document_service()
            
            # Use provided collection_name or fall back to default from settings
            target_collection = self.collection_name or settings.DOCUMENTS_COLLECTION_NAME
            
            # Perform search
            results = document_service.search_documents(
                query=query,
                limit=self.max_results,
                threshold=settings.SIMILARITY_THRESHOLD,
                collection_name=target_collection
            )
            
            if not results:
                return "No relevant documents found in the knowledge base."
            
            # Format results
            formatted_results = []
            for i, doc in enumerate(results, 1):
                formatted_results.append(
                    f"Document {i}:\n"
                    f"Title: {doc['title']}\n"
                    f"Similarity: {doc['similarity_score']:.2%}\n"
                    f"Content: {doc['content'][:500]}...\n"
                    f"Source: {doc.get('source', 'unknown')}\n"
                )
            
            return "\n---\n".join(formatted_results)
        
        except Exception as e:
            return f"Error searching vector database: {str(e)}"
    
    async def _arun(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Async version of run."""
        return self._run(query, run_manager)


def create_vector_search_tool(max_results: int = None, collection_name: Optional[str] = None) -> VectorSearchTool:
    """
    Factory function to create a vector search tool.
    
    Args:
        max_results: Maximum number of results to return (uses default from settings if not provided)
        collection_name: Optional collection name (uses default from settings if not provided)
        
    Returns:
        Configured VectorSearchTool instance
    """
    if max_results is None:
        max_results = settings.DEFAULT_SEARCH_LIMIT
    return VectorSearchTool(max_results=max_results, collection_name=collection_name)
