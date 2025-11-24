"""
Database module initialization
"""
from app.db.weaviate_client import weaviate_manager, get_weaviate_client

__all__ = ["weaviate_manager", "get_weaviate_client"]
