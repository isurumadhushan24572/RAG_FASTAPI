# Agentic RAG Application - Complete Setup Guide

## 🎯 Overview

You now have a complete **Agentic RAG Application** with the following features:

✅ **Agentic System**: LangChain tool-calling agent with multi-step reasoning  
✅ **Web Search Tool**: Real-time web search using Tavily or DuckDuckGo  
✅ **Vector Search Tool**: Semantic search through stored documents  
✅ **Full Document Storage**: Documents stored complete (no chunking)  
✅ **LangChain Prompts**: ChatPromptTemplate for all prompts  
✅ **Docker Vector DB**: Only Weaviate runs in Docker  
✅ **Local Backend**: FastAPI runs locally for easy development  

## 📁 Project Structure

```
agentic/
├── app/
│   ├── api/                    # FastAPI endpoints
│   │   ├── health.py          # Health check
│   │   ├── documents.py       # Document CRUD
│   │   └── agent.py           # Agent queries
│   ├── core/
│   │   └── config.py          # Configuration
│   ├── db/
│   │   └── weaviate_client.py # Vector DB client
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── services/
│   │   ├── agents/            # Agentic RAG
│   │   │   └── agentic_rag_service.py
│   │   ├── tools/             # Agent tools
│   │   │   ├── vector_search_tool.py
│   │   │   └── web_search_tool.py
│   │   ├── prompts/           # LangChain prompts
│   │   │   └── prompt_templates.py
│   │   ├── embedding_service.py
│   │   └── document_service.py
│   └── main.py                # FastAPI app
├── docs/
│   ├── QUICKSTART.md          # Quick start guide
│   └── ARCHITECTURE.md        # Architecture docs
├── docker-compose.yml         # Vector DB only
├── requirements.txt           # Python dependencies
├── run.py                     # Application entry point
├── test_demo.py              # Demo script
├── .env                       # Environment variables
├── .env.example               # Example env file
├── .gitignore                 # Git ignore
└── README.md                  # Main documentation
```

## 🚀 Quick Start (3 Steps)

### Step 1: Start Vector Database

```bash
cd agentic
docker-compose up -d
```

Verify it's running:
```bash
docker ps
```

You should see: `agentic_weaviate_db` on ports 8080 and 50051

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI, Uvicorn
- LangChain, Groq
- Weaviate client
- Sentence Transformers
- Tavily, DuckDuckGo

### Step 3: Run the Application

```bash
python run.py
```

The app will start on **http://localhost:8000**

## 🧪 Test the System

Run the demo script:
```bash
python test_demo.py
```

This will:
1. Check health
2. Upload sample documents
3. Search documents
4. Query the agent with different tool combinations

## 📚 API Endpoints

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /status` - System status

### Document Management
- `POST /documents/upload` - Upload a document
- `GET /documents/list` - List all documents
- `POST /documents/search` - Search documents
- `GET /documents/{id}` - Get specific document
- `DELETE /documents/{id}` - Delete document

### Agent
- `POST /agent/query` - Query the agent
- `GET /agent/info` - Agent capabilities

### Interactive Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 💡 Usage Examples

### Upload a Document

```python
import requests

response = requests.post(
    "http://localhost:8000/documents/upload",
    json={
        "title": "My Document",
        "content": "Full document content here...",
        "document_type": "text",
        "source": "manual_upload"
    }
)
print(response.json())
```

### Query the Agent

```python
response = requests.post(
    "http://localhost:8000/agent/query",
    json={
        "query": "What is machine learning?",
        "use_web_search": True,
        "use_vector_search": True
    }
)
result = response.json()
print(result['answer'])
```

## 🔧 Configuration

Edit `.env` file:

```env
# Vector Database
WEAVIATE_HOST=localhost
WEAVIATE_PORT=8080

# API Keys
GROQ_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here  # Optional for web search

# Agent Settings
AGENT_MAX_ITERATIONS=15
AGENT_MAX_EXECUTION_TIME=120

# Embedding Model
EMBEDDING_MODEL=all-mpnet-base-v2
```

## 🎨 Key Features Explained

### 1. No Chunking
Documents are stored complete, preserving full context:
```python
# Document stored as-is
{
    "title": "...",
    "content": "Full document...",  # Not split!
    "embedding": [...]  # Single embedding for full doc
}
```

### 2. LangChain Agent
The agent uses tools intelligently:
```
User Query → Agent Reasoning → Tool Selection → Execution → Answer
```

Tools:
- **vector_search**: Searches your documents
- **web_search**: Searches the internet

### 3. LangChain ChatPromptTemplate
All prompts use structured templates:
```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an AI assistant..."),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
```

### 4. Docker for Vector DB Only
- ✅ Weaviate runs in Docker (isolated, persistent)
- ✅ FastAPI runs locally (easy debugging, hot reload)

## 🔍 How the Agent Works

### Example: "What are Python best practices?"

1. **Agent receives query**
2. **Agent thinks**: "This might be in stored documents"
3. **Agent uses vector_search tool**
   - Searches Weaviate
   - Finds relevant documents
4. **Agent synthesizes answer** from documents
5. **Returns answer with sources**

### Example: "What's the latest AI news?"

1. **Agent receives query**
2. **Agent thinks**: "This requires current information"
3. **Agent uses web_search tool**
   - Searches via Tavily/DuckDuckGo
   - Gets recent results
4. **Agent synthesizes answer** from web results
5. **Returns answer with URLs**

### Example: "Compare our ML docs with industry trends"

1. **Agent receives query**
2. **Agent thinks**: "Need both internal and external info"
3. **Agent uses vector_search tool** → Gets internal docs
4. **Agent uses web_search tool** → Gets current trends
5. **Agent compares** both sources
6. **Returns comprehensive answer**

## 📊 Monitoring

### Console Logs
Watch the agent work in real-time:
```
🤖 Agent executing query: What are Python best practices?
✅ Vector search tool enabled
✅ Web search tool enabled
🔍 Agent step 1: Using vector_search
📝 Found 3 similar documents
✅ Agent completed in 2.34s
```

### LangSmith Tracing
If enabled in `.env`:
- Visit https://smith.langchain.com
- See detailed agent traces
- Monitor LLM calls
- Track tool usage

## 🐛 Troubleshooting

### Issue: Cannot connect to Weaviate
```
❌ Failed to connect to Weaviate
```
**Solution**:
```bash
docker-compose up -d
```

### Issue: Import errors
```
ModuleNotFoundError: No module named 'langchain'
```
**Solution**:
```bash
pip install -r requirements.txt
```

### Issue: Web search not working
**Solution**: Set TAVILY_API_KEY in `.env` or use DuckDuckGo (no key needed)

### Issue: Agent takes too long
**Solution**: Increase timeout in `.env`:
```
AGENT_MAX_EXECUTION_TIME=180
```

## 🎯 Next Steps

### 1. Upload Your Documents
```python
# Upload PDFs, text files, or any content
requests.post(
    "http://localhost:8000/documents/upload",
    json={
        "title": "Your Document",
        "content": "Your content...",
        "document_type": "pdf",
        "metadata": {"category": "technical"}
    }
)
```

### 2. Customize Prompts
Edit `app/services/prompts/prompt_templates.py` to customize agent behavior

### 3. Add Custom Tools
Create new tools in `app/services/tools/` following the existing pattern

### 4. Monitor with LangSmith
Enable in `.env` and track all agent interactions

## 🌐 API Documentation

Full interactive docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📝 Important Notes

### Document Storage
- Documents stored **complete** (not chunked)
- One embedding per document
- Full context preserved

### Agent Behavior
- Uses tools intelligently
- Can use multiple tools in sequence
- Tracks all steps for transparency

### Web Search
- Tavily: Best quality, requires API key
- DuckDuckGo: Free, no key needed, rate limited

### Costs
- **Groq LLM**: Free tier available
- **Tavily**: Free tier available
- **Embeddings**: Local, no cost
- **Vector DB**: Local, no cost

## 🛑 Stopping the Application

1. Stop FastAPI: `Ctrl+C` in terminal
2. Stop Weaviate: `docker-compose down`
3. Remove data: `docker-compose down -v` (⚠️ deletes all documents)

## 📖 Documentation

- `docs/QUICKSTART.md` - Quick start guide
- `docs/ARCHITECTURE.md` - Detailed architecture
- `README.md` - Project overview

## ✅ What You Have

✨ **Complete agentic RAG system**  
✨ **Multi-tool agent** (web + vector search)  
✨ **LangChain ChatPromptTemplate** for all prompts  
✨ **Full document storage** (no chunking)  
✨ **Docker for vector DB only**  
✨ **Local FastAPI** for easy development  
✨ **Production-ready architecture**  

## 🚀 Start Building!

```bash
# Start everything
docker-compose up -d
python run.py

# In another terminal, test it
python test_demo.py

# Start building your application!
```

**Happy building! 🎉**
