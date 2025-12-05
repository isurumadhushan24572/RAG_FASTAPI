# Agentic RAG Application - Complete Setup Guide

## 🎯 Overview

You now have a complete **Agentic RAG Application** with the following features:

✅ **Agentic System**: LangChain tool-calling agent with multi-step reasoning  
✅ **Frontend Dashboard**: React + Vite dashboard for ticket management  
✅ **Web Search Tool**: Real-time web search using Tavily or DuckDuckGo  
✅ **Vector Search Tool**: Semantic search through stored documents  
✅ **Full Document Storage**: Documents stored complete (no chunking)  
✅ **Docker Vector DB**: Only Weaviate runs in Docker  
✅ **Local Backend**: FastAPI runs locally for easy development  

## 📁 Project Structure

```
agentic/
├── app/
│   ├── api/                    # FastAPI endpoints
│   │   ├── tickets.py         # Ticket management
│   │   ├── documents.py       # Document CRUD
│   │   └── agent.py           # Agent queries
│   ├── services/
│   │   ├── agents/            # Agentic RAG
│   │   └── tools/             # Agent tools
│   └── main.py                # FastAPI app
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   └── App.jsx            # Main app
│   └── vite.config.js         # Vite config
├── docs/
│   ├── QUICKSTART.md          # Quick start guide
│   └── ARCHITECTURE.md        # Architecture docs
├── docker-compose.yml         # Vector DB only
├── requirements.txt           # Python dependencies
├── run.py                     # Application entry point
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

### Step 2: Backend Setup

```bash
# Install Dependencies
pip install -r requirements.txt

# Run Backend
python run.py
```

The backend will start on **http://localhost:8000**

### Step 3: Frontend Setup

Open a new terminal:
```bash
cd frontend

# Install Dependencies
npm install

# Run Frontend
npm run dev
```

The frontend will start on **http://localhost:5173**

## 🧪 Test the System

1. Open **http://localhost:5173** in your browser.
2. Check the **Dashboard** for ticket stats.
3. Click **"New Ticket"** and submit a query like:
   > "My Azure Data Factory pipeline is failing with error 2108."
4. Watch the AI analyze the issue and provide a solution in a new tab.

## 📚 API Endpoints

### Ticket Management
- `POST /api/v1/tickets/submit-user-input` - Submit ticket for AI analysis
- `GET /api/v1/tickets/stats` - Get dashboard statistics
- `GET /api/v1/tickets` - List all tickets

### Agent
- `POST /agent/query` - Query the agent directly

### Interactive Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

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

### 1. Ticket Resolution Flow
When a user submits a ticket:
1. **Vector Search**: Finds similar past tickets (85% similarity).
2. **Agent Analysis**: Uses web search and internal docs to find a solution.
3. **Response**: Returns a structured solution with "Root Cause" and "Steps".

### 2. Dashboard
Visualizes ticket data:
- **Severity**: High, Medium, Low distribution.
- **Status**: Open vs Resolved.
- **Environment**: Production, Staging, Dev.

### 3. LangChain Agent
The agent uses tools intelligently:
```
User Query → Agent Reasoning → Tool Selection → Execution → Answer
```

## 🐛 Troubleshooting

### Issue: Frontend cannot connect to Backend
**Solution**: Ensure Backend is running on port 8000 and CORS is enabled in `.env`.

### Issue: Cannot connect to Weaviate
**Solution**: `docker-compose up -d`

### Issue: Web search not working
**Solution**: Set TAVILY_API_KEY in `.env` or use DuckDuckGo.

## 🛑 Stopping the Application

1. Stop Frontend: `Ctrl+C`
2. Stop Backend: `Ctrl+C`
3. Stop Weaviate: `docker-compose down`

## 📖 Documentation

- `docs/QUICKSTART.md` - Quick start guide
- `docs/ARCHITECTURE.md` - Detailed architecture
- `README.md` - Project overview

## ✅ What You Have

✨ **Complete agentic RAG system**  
✨ **React Frontend Dashboard**  
✨ **Multi-tool agent** (web + vector search)  
✨ **Full document storage** (no chunking)  
✨ **Docker for vector DB only**  
✨ **Local FastAPI** for easy development  

**Happy building! 🎉**

