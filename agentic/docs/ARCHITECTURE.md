# Agentic RAG - Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User / Client                          │
│             (React Frontend / Browser)                      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Requests (JSON)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Application                        │
│                    (Runs Locally)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Endpoints                            │  │
│  │  • /tickets/* - Ticket Management & Stats            │  │
│  │  • /agent/query - Agentic RAG queries                │  │
│  │  • /documents/* - Document management                │  │
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

### 1. Frontend (React + Vite)
- **Dashboard**: Visualizes ticket statistics (Severity, Status, Environment).
- **Ticket Form**: User interface for submitting support tickets.
- **Ticket Result**: Displays AI-generated solutions and similar past tickets.
- **Tech Stack**: React, Tailwind CSS, Chart.js, Axios.

### 2. FastAPI Application (Local)

#### API Layer (`app/api/`)
- **tickets.py**: Ticket submission, retrieval, and stats endpoints.
- **agent.py**: Agentic RAG query endpoint.
- **documents.py**: Document CRUD operations.
- **health.py**: Health check endpoint.

#### Core (`app/core/`)
- **config.py**: Configuration management with environment variables.

#### Database (`app/db/`)
- **weaviate_client.py**: Weaviate connection and collection management.

#### Services (`app/services/`)

**embedding_service.py**
- Loads sentence-transformers model (`all-mpnet-base-v2`).
- Generates embeddings for documents and queries.

**agents/** (Agentic System)
- **agentic_rag_service.py**: Main agent orchestration using LangChain.
- Coordinates multiple tools (Vector Search, Web Search).

**tools/** (Agent Tools)
- **vector_search_tool.py**: Searches vector database for internal knowledge.
- **web_search_tool.py**: Searches web (Tavily/DuckDuckGo) for external info.

### 3. Vector Database (Docker)

**Weaviate**
- Version: Latest
- Storage: Persistent volume
- Access: HTTP (8080) and gRPC (50051)
- Vectorizer: None (using local embeddings)

## Data Flow

### Ticket Submission & Resolution Flow

```
1. User submits ticket (Frontend)
   ↓
2. POST /api/v1/tickets/submit-user-input
   ↓
3. Search Vector DB for Similar Tickets (85% threshold)
   ↓
4. Agentic RAG Service Analysis
   ├─→ Agent plans solution strategy
   ├─→ Tool: Vector Search (Internal Docs)
   ├─→ Tool: Web Search (External Info)
   └─→ Agent synthesizes solution
   ↓
5. Return Response (JSON)
   ├─→ AI Reasoning (Root Cause)
   ├─→ Step-by-step Solution
   └─→ List of Similar Past Tickets
   ↓
6. Frontend displays result in new tab
```

### Dashboard Stats Flow

```
1. Frontend loads Dashboard
   ↓
2. GET /api/v1/tickets/stats
   ↓
3. Weaviate: Fetch all tickets
   ↓
4. Backend: Aggregate counts (Severity, Status, Environment)
   ↓
5. Return Stats JSON
   ↓
6. Frontend renders Charts (Chart.js)
```

## Key Design Decisions

### 1. No Chunking
- **Decision**: Store documents as complete units.
- **Rationale**: Preserves full context for the agent, simpler management.

### 2. Local Embeddings
- **Decision**: Use sentence-transformers locally.
- **Rationale**: No API costs, fast inference, offline capability.

### 3. Docker for Vector DB Only
- **Decision**: Run only Weaviate in Docker.
- **Rationale**: Easier local development for backend/frontend code.

### 4. LangChain Agent Framework
- **Decision**: Use LangChain's tool-calling agent.
- **Rationale**: Structured tool usage, automatic reasoning loop.

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React + Vite | User Interface |
| Styling | Tailwind CSS | Responsive Design |
| API Framework | FastAPI | REST API endpoints |
| Agent Framework | LangChain | Agent orchestration |
| LLM Provider | Groq | Fast inference (Llama 3) |
| Vector DB | Weaviate | Semantic search |
| Embeddings | Sentence Transformers | Local embeddings |
| Web Search | Tavily/DuckDuckGo | Real-time web search |

