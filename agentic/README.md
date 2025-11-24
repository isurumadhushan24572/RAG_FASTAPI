# Agentic RAG Application

An advanced agentic RAG (Retrieval-Augmented Generation) system with web search capabilities and full document storage.

## Features

- **Agentic Architecture**: Multi-agent system with specialized tools
- **Web Search Integration**: Real-time web search for up-to-date information
- **Vector Database**: Weaviate for semantic search (documents stored whole, not chunked)
- **LangChain Integration**: Using ChatPromptTemplate for structured prompts
- **Local Hosting**: FastAPI backend runs locally, only Vector DB in Docker
- **Tool-Based Agents**: Agents with vector search and web search tools

## Architecture

```
agentic/
├── app/                    # Main application code
│   ├── api/               # FastAPI endpoints
│   ├── core/              # Configuration and settings
│   ├── db/                # Vector database client
│   ├── models/            # Pydantic schemas
│   ├── services/          # Business logic
│   │   ├── agents/        # Agent implementations
│   │   ├── tools/         # Agent tools (web search, vector search)
│   │   └── prompts/       # LangChain prompt templates
│   └── main.py            # FastAPI application
├── docker/                # Docker configuration (Vector DB only)
├── docs/                  # Documentation
└── tests/                 # Test files
```

## Setup

### 1. Start Vector Database (Docker)
```bash
cd agentic
docker-compose up -d
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Copy `.env.example` to `.env` and add your API keys.

### 4. Run Application (Locally)
```bash
python run.py
```

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /documents/upload` - Upload documents (stored whole)
- `POST /agent/query` - Query the agentic system
- `GET /documents/list` - List all documents

## Technology Stack

- **FastAPI**: Web framework
- **LangChain**: Agent orchestration and prompt templates
- **Weaviate**: Vector database
- **Sentence Transformers**: Local embeddings
- **Tavily/DuckDuckGo**: Web search
- **Groq**: LLM provider
