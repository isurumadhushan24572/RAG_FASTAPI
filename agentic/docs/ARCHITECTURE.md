# Agentic RAG - Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User / Client                          │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Requests
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Application                        │
│                    (Runs Locally)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Endpoints                            │  │
│  │  • /health - Health check                            │  │
│  │  • /documents/* - Document management                │  │
│  │  • /agent/query - Agentic RAG queries                │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────┴────────────────────────────────┐  │
│  │            Services Layer                             │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │  │
│  │  │  Embedding  │  │   Document   │  │  Agentic   │  │  │
│  │  │   Service   │  │   Service    │  │    RAG     │  │  │
│  │  └─────────────┘  └──────────────┘  └────────────┘  │  │
│  │         │                 │                 │         │  │
│  └─────────┼─────────────────┼─────────────────┼─────────┘  │
│            │                 │                 │             │
│            │                 │          ┌──────┴──────┐      │
│            │                 │          │  LangChain  │      │
│            │                 │          │    Agent    │      │
│            │                 │          └──────┬──────┘      │
│            │                 │                 │             │
│            │                 │          ┌──────┴──────┐      │
│            │                 │          │   Tools     │      │
│            │                 │          │  ┌────────┐ │      │
│            │                 │          │  │ Vector │ │      │
│            │                 │          │  │ Search │ │      │
│            │                 │          │  └────────┘ │      │
│            │                 │          │  ┌────────┐ │      │
│            │                 │          │  │  Web   │ │      │
│            │                 │          │  │ Search │ │      │
│            │                 │          │  └────────┘ │      │
│            │                 │          └─────────────┘      │
└────────────┼─────────────────┼──────────────────────────────┘
             │                 │
             │                 ▼
             │    ┌─────────────────────────┐
             │    │   Weaviate Client       │
             │    └───────────┬─────────────┘
             │                │
             │                ▼
┌────────────┴──────────────────────────────────────────────┐
│               Docker Container                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │          Weaviate Vector Database                    │ │
│  │  • Port 8080 (HTTP)                                  │ │
│  │  • Port 50051 (gRPC)                                 │ │
│  │  • Persistent storage: Documents collection          │ │
│  │  • Full documents (no chunking)                      │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
             │
             ▼
   ┌──────────────────┐
   │  External APIs   │
   │  • Groq (LLM)    │
   │  • Tavily (Web)  │
   └──────────────────┘
```

## Components

### 1. FastAPI Application (Local)

#### API Layer (`app/api/`)
- **health.py**: Health check endpoint
- **documents.py**: Document CRUD operations
- **agent.py**: Agentic RAG query endpoint

#### Core (`app/core/`)
- **config.py**: Configuration management with environment variables

#### Database (`app/db/`)
- **weaviate_client.py**: Weaviate connection and collection management

#### Models (`app/models/`)
- **schemas.py**: Pydantic models for request/response validation

#### Services (`app/services/`)

**embedding_service.py**
- Loads sentence-transformers model
- Generates embeddings for documents and queries
- Uses `all-mpnet-base-v2` by default

**document_service.py**
- Manages documents in Weaviate
- Stores complete documents (no chunking)
- Provides semantic search

**agents/** (Agentic System)
- **agentic_rag_service.py**: Main agent orchestration
- Uses LangChain's tool-calling agent
- Coordinates multiple tools

**tools/** (Agent Tools)
- **vector_search_tool.py**: Searches vector database
- **web_search_tool.py**: Searches web (Tavily/DuckDuckGo)

**prompts/** (LangChain Prompts)
- **prompt_templates.py**: ChatPromptTemplate definitions
- Structured prompts for agent, RAG synthesis, Q&A

### 2. Vector Database (Docker)

**Weaviate**
- Version: Latest
- Storage: Persistent volume
- Access: HTTP (8080) and gRPC (50051)
- Vectorizer: None (using local embeddings)

**Documents Collection Schema:**
```python
{
    "document_id": TEXT,      # UUID
    "title": TEXT,            # Document title
    "content": TEXT,          # Full content (not chunked)
    "document_type": TEXT,    # pdf, txt, docx, etc.
    "metadata": TEXT,         # JSON string
    "source": TEXT,           # Origin/source
    "created_at": TEXT,       # ISO timestamp
    "word_count": INT,        # Word count
    # + vector (embedding)
}
```

## Data Flow

### Document Upload Flow

```
1. POST /documents/upload
   ↓
2. DocumentService.add_document()
   ↓
3. EmbeddingService.generate_embedding(content)
   ↓ [sentence-transformers]
4. Weaviate.insert(properties + vector)
   ↓
5. Return document_id
```

### Agent Query Flow

```
1. POST /agent/query
   ↓
2. AgenticRAGService.query()
   ↓
3. Initialize Tools (vector_search, web_search)
   ↓
4. Create LangChain Agent
   ↓
5. Agent analyzes query → decides which tools to use
   ↓
6. Tool Execution:
   ├─→ VectorSearchTool → DocumentService.search_documents()
   │                    → Weaviate semantic search
   │                    ← Return documents
   │
   └─→ WebSearchTool → Tavily/DuckDuckGo API
                     ← Return web results
   ↓
7. Agent synthesizes answer from tool results
   ↓
8. Return AgentResponse (answer + sources + steps)
```

### Semantic Search Flow

```
1. Query string
   ↓
2. EmbeddingService.generate_embedding(query)
   ↓
3. Weaviate.near_vector(query_embedding)
   ↓
4. Calculate similarity scores (1 - distance)
   ↓
5. Filter by threshold
   ↓
6. Return ranked documents
```

## Key Design Decisions

### 1. No Chunking
- **Decision**: Store documents as complete units
- **Rationale**: 
  - Preserves full context
  - Simpler document management
  - Better for agentic reasoning
- **Trade-off**: Larger embeddings, but modern models handle it well

### 2. Local Embeddings
- **Decision**: Use sentence-transformers locally
- **Rationale**:
  - No API costs for embeddings
  - Fast inference
  - Offline capability
- **Model**: `all-mpnet-base-v2` (768 dimensions)

### 3. Docker for Vector DB Only
- **Decision**: Run only Weaviate in Docker
- **Rationale**:
  - Easier local development
  - Direct access to code for debugging
  - Faster iteration
- **Backend**: Runs locally with `python run.py`

### 4. LangChain Agent Framework
- **Decision**: Use LangChain's tool-calling agent
- **Rationale**:
  - Structured tool usage
  - Automatic reasoning loop
  - Built-in error handling
- **Tools**: Custom tools for vector search and web search

### 5. ChatPromptTemplate
- **Decision**: Use LangChain ChatPromptTemplate
- **Rationale**:
  - Structured message format
  - Easy to maintain and version
  - Support for system/human/AI messages
- **Templates**: Separate templates for different use cases

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| API Framework | FastAPI | REST API endpoints |
| Server | Uvicorn | ASGI server |
| Agent Framework | LangChain | Agent orchestration |
| LLM Provider | Groq | Fast inference (Llama 3.3 70B) |
| Vector DB | Weaviate | Semantic search |
| Embeddings | Sentence Transformers | Local embeddings |
| Web Search | Tavily/DuckDuckGo | Real-time web search |
| Validation | Pydantic | Request/response models |
| Config | python-dotenv | Environment variables |

## Scaling Considerations

### Current Architecture (Development)
- Single instance
- Local embeddings
- Docker vector DB

### Production Recommendations

1. **Embedding Service**
   - Deploy as separate microservice
   - Use GPU acceleration
   - Cache frequent queries

2. **Vector Database**
   - Use managed Weaviate (Weaviate Cloud)
   - Or deploy with proper clustering
   - Set up backups

3. **API**
   - Deploy with gunicorn + uvicorn workers
   - Add load balancer
   - Enable rate limiting

4. **Agent**
   - Add queue system for long-running queries
   - Implement caching for repeated queries
   - Monitor token usage

## Security Considerations

1. **API Keys**: Stored in `.env`, never committed
2. **CORS**: Configured in settings
3. **Rate Limiting**: TODO (add for production)
4. **Authentication**: TODO (add for production)
5. **Input Validation**: Pydantic models

## Monitoring

### Available Endpoints
- `/health`: Application health
- `/status`: Detailed status
- `/docs`: API documentation

### LangSmith Integration
- Enabled in `.env`
- Traces agent execution
- Monitors LLM calls
- Tracks tool usage

## Future Enhancements

1. **Document Processing**
   - PDF parsing
   - Image extraction
   - Table handling

2. **Advanced Agent Features**
   - Multi-agent collaboration
   - Custom tool creation
   - Memory/conversation history

3. **Search Improvements**
   - Hybrid search (vector + keyword)
   - Reranking
   - Query expansion

4. **Production Features**
   - Authentication/authorization
   - Rate limiting
   - Caching layer
   - Background tasks
