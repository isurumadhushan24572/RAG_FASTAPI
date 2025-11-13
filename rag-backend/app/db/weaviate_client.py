
# Weaviate database client management.
# Handles connection lifecycle and collection initialization.

import weaviate         # import weaviate client library
import weaviate.classes as wvc      # import weaviate classes module
from weaviate.classes.config import Property, DataType       # import Property and DataType for schema definition in a collection
from typing import Optional         # import Optional type hint 
from app.core.config import settings     # import application settings


class WeaviateManager:
    """Manager class for Weaviate client lifecycle."""
    
    # Initialize WeaviateManager with no client connected.
    def __init__(self): 
        self.client: Optional[weaviate.WeaviateClient] = None
    
    def connect(self) -> bool:
       # Connect to Weaviate instance and verify connection.
        try:
            # Connect to local Weaviate instance
            self.client = weaviate.connect_to_local(
                host=settings.WEAVIATE_HOST,
                port=settings.WEAVIATE_PORT,
                grpc_port=settings.WEAVIATE_GRPC_PORT,
            )
            
            # Verify connection
            if self.client.is_ready():
                print("✅ Successfully connected to Weaviate vector database")
                return True
            else:
                print("⚠️ Weaviate client connected but not ready")
                return False
                
        except Exception as e:
            print(f"❌ Failed to connect to Weaviate: {str(e)}")
            print("⚠️ Make sure Weaviate Docker container is running")
            print("💡 Run: docker-compose up -d")
            self.client = None
            return False
    
    def disconnect(self):
        """Close Weaviate connection."""
        if self.client is not None:
            try:
                self.client.close()
                print("✅ Weaviate connection closed successfully")
                print("💾 Collection data is persisted in Weaviate (will be available on next startup)")
            except Exception as e:
                print(f"⚠️ Error closing Weaviate connection: {str(e)}")
    
    def is_connected(self) -> bool:
        """Check if client is connected and ready."""
        return self.client is not None and self.client.is_ready()
    
    def get_client(self) -> Optional[weaviate.WeaviateClient]:
        """Get the Weaviate client instance."""
        return self.client
    
    def initialize_collections(self):
        """Initialize default collections on startup."""
        if self.client is None:
            return
         
        
        try:
            # Check if SupportTickets collection exists
            collection_exists = self.client.collections.exists(settings.TICKETS_COLLECTION_NAME)
            
            if collection_exists:
                print(f"✅ Collection '{settings.TICKETS_COLLECTION_NAME}' already exists (using existing collection)")
            else:
                print(f"📝 Collection '{settings.TICKETS_COLLECTION_NAME}' not found - creating new collection...")
                
                # Create collection with proper schema for tickets
                self.client.collections.create(
                    name=settings.TICKETS_COLLECTION_NAME,
                    description="Support ticket incidents with AI-generated solutions",
                    vectorizer_config=wvc.config.Configure.Vectorizer.none(),  # No automatic vectorization
                    properties=[
                        Property(name="ticket_id", data_type=DataType.TEXT, description="Unique ticket identifier"),
                        Property(name="title", data_type=DataType.TEXT, description="Ticket title/summary"),
                        Property(name="description", data_type=DataType.TEXT, description="Detailed problem description"),
                        Property(name="category", data_type=DataType.TEXT, description="Issue category"),
                        Property(name="status", data_type=DataType.TEXT, description="Ticket status (Open/Resolved)"),
                        Property(name="severity", data_type=DataType.TEXT, description="Severity level"),
                        Property(name="application", data_type=DataType.TEXT, description="Affected application/service"),
                        Property(name="affected_users", data_type=DataType.TEXT, description="Impact scope"),
                        Property(name="environment", data_type=DataType.TEXT, description="Environment (Production/Staging/etc)"),
                        Property(name="solution", data_type=DataType.TEXT, description="Resolution steps"),
                        Property(name="reasoning", data_type=DataType.TEXT, description="Root cause analysis"),
                        Property(name="timestamp", data_type=DataType.TEXT, description="Ticket creation timestamp"),
                    ]
                )
                print(f"✅ Collection '{settings.TICKETS_COLLECTION_NAME}' created successfully with empty data")
                print(f"ℹ️  Using local embeddings (sentence-transformers) for vectorization")
                
        except Exception as e:
            print(f"⚠️ Error handling collection: {str(e)}")


# Make class object available globally
weaviate_manager = WeaviateManager() 


def get_weaviate_client() -> Optional[weaviate.WeaviateClient]:
    """Dependency to get the Weaviate client instance."""
    return weaviate_manager.get_client()
