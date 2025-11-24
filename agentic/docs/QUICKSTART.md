# Agentic RAG - Quick Start Guide

## Overview

This agentic RAG system uses LangChain agents with multiple tools to intelligently answer questions using:
- **Vector Search**: Semantic search through stored documents
- **Web Search**: Real-time web search for current information
- **Full Document Storage**: Documents stored complete (no chunking)

## Prerequisites

- Python 3.10+
- Docker Desktop
- Groq API Key (get from https://console.groq.com)
- Tavily API Key (optional, get from https://tavily.com)

## Setup Instructions

### 1. Start Vector Database (Docker)

```bash
cd agentic
docker-compose up -d
```

Verify Weaviate is running:
```bash
docker ps
```

You should see `agentic_weaviate_db` running on ports 8080 and 50051.

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn
- LangChain & Groq
- Weaviate client
- Sentence Transformers
- Web search tools

### 3. Configure Environment

The `.env` file is already configured with your API keys. To add Tavily for web search:

1. Get Tavily API key from https://tavily.com
2. Update `.env`:
   ```
   TAVILY_API_KEY=your_tavily_key_here
   ```

### 4. Run the Application

```bash
python run.py
```

The application will:
- Load the embedding model
- Connect to Weaviate
- Initialize the Documents collection
- Start FastAPI on http://localhost:8000

## API Usage

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Upload a Document

```bash
curl -X POST http://localhost:8000/documents/upload \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Best Practices",
    "content": "Python best practices include: Use virtual environments, follow PEP 8 style guide, write unit tests, use type hints, document your code with docstrings, and handle exceptions properly.",
    "document_type": "text",
    "source": "programming_guide"
  }'
```

### 3. Query the Agent

```bash
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are Python best practices?",
    "use_web_search": true,
    "use_vector_search": true
  }'
```

### 4. Search Documents

```bash
curl -X POST http://localhost:8000/documents/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python programming",
    "limit": 5
  }'
```

### 5. List All Documents

```bash
curl http://localhost:8000/documents/list
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## How It Works

### Agent Workflow

1. **User Query**: Submit a question via `/agent/query`
2. **Agent Planning**: The LangChain agent analyzes the query and decides which tools to use
3. **Tool Execution**: 
   - Uses `vector_search` to find relevant documents
   - Uses `web_search` for current information
   - Can use multiple tools in sequence
4. **Answer Generation**: Synthesizes information from all sources
5. **Response**: Returns answer with sources and agent steps

### Document Storage

- Documents are stored **complete** (not chunked)
- Full content is embedded using sentence-transformers
- Semantic search finds entire relevant documents
- Preserves document context and structure

### Agent Tools

#### Vector Search Tool
- Searches stored documents
- Uses semantic similarity
- Returns top relevant documents
- Best for: Internal knowledge base

#### Web Search Tool
- Searches the internet
- Uses Tavily or DuckDuckGo
- Returns current information
- Best for: Recent events, current data

## Example Queries

### Query with Vector Search Only
```json
{
  "query": "Explain the content in our documents about machine learning",
  "use_web_search": false,
  "use_vector_search": true
}
```

### Query with Web Search Only
```json
{
  "query": "What are the latest AI developments in 2025?",
  "use_web_search": true,
  "use_vector_search": false
}
```

### Query with Both Tools
```json
{
  "query": "Compare our internal ML guidelines with current industry best practices",
  "use_web_search": true,
  "use_vector_search": true
}
```

## Troubleshooting

### Weaviate Connection Error
```
❌ Failed to connect to Weaviate
```
**Solution**: Start Weaviate with `docker-compose up -d`

### Embedding Model Loading Slow
First time loading the model downloads it from HuggingFace. Subsequent runs use cached model.

### Web Search Not Working
- Check if TAVILY_API_KEY is set in `.env`
- Or use DuckDuckGo (no API key needed, but rate limited)

### Agent Timeout
Increase in `.env`:
```
AGENT_MAX_EXECUTION_TIME=180
```

## Stopping the Application

1. Stop FastAPI: Press `Ctrl+C`
2. Stop Weaviate: `docker-compose down`

To remove all data: `docker-compose down -v`

## Next Steps

- Upload your documents via `/documents/upload`
- Test agent queries via `/agent/query`
- Monitor agent reasoning in the console logs
- Check LangSmith for detailed traces (if enabled)
