# Agentic RAG - Quick Start Guide

## Overview

This agentic RAG system uses LangChain agents with multiple tools to intelligently answer questions using:
- **Vector Search**: Semantic search through stored documents
- **Web Search**: Real-time web search for current information
- **Full Document Storage**: Documents stored complete (no chunking)

## Prerequisites

- Python 3.10+
- Node.js & npm
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

### 2. Backend Setup

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Configure Environment:
1. Copy `.env.example` to `.env`
2. Add your API keys (Groq, Tavily, etc.)

Run the Backend:
```bash
python run.py
```
The backend will start on http://localhost:8000.

### 3. Frontend Setup

Open a new terminal and navigate to the frontend directory:
```bash
cd frontend
```

Install Node dependencies:
```bash
npm install
```

Start the Frontend:
```bash
npm run dev
```
The frontend will start on http://localhost:5173.

## Usage

1. Open http://localhost:5173 in your browser.
2. **Dashboard**: View real-time statistics of your support tickets.
3. **New Ticket**: Click "New Ticket" to submit a query.
4. **Result**: The AI will analyze your ticket and open the solution in a new tab.

## API Usage (Backend Only)

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

## Troubleshooting

### Weaviate Connection Error
```
❌ Failed to connect to Weaviate
```
**Solution**: Start Weaviate with `docker-compose up -d`

### Frontend Connection Error
If the frontend cannot connect to the backend, ensure the backend is running on port 8000 and CORS is configured correctly in `.env`.

### Agent Timeout
Increase in `.env`:
```
AGENT_MAX_EXECUTION_TIME=180
```

## Stopping the Application

1. Stop Frontend: Press `Ctrl+C`
2. Stop Backend: Press `Ctrl+C`
3. Stop Weaviate: `docker-compose down`

To remove all data: `docker-compose down -v`

