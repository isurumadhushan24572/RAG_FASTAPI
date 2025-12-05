# Agentic RAG Support System

An advanced **Agentic RAG (Retrieval-Augmented Generation)** system designed for IT support and ticket resolution. It combines a **FastAPI** backend with a **React** frontend, featuring a multi-agent system that uses vector search and web search to solve support tickets automatically.

## 🚀 Features

- **Agentic Architecture**: Intelligent agents that plan and execute multi-step reasoning.
- **Dual-Tool System**:
  - **Vector Search**: Semantically searches internal knowledge base (Weaviate).
  - **Web Search**: Real-time internet search (Tavily/DuckDuckGo) for up-to-date info.
- **Ticket Management**:
  - Submit tickets via a responsive UI.
  - AI-generated solutions with "Root Cause Analysis" and "Step-by-Step Resolution".
  - Automatic duplicate detection (finding similar past tickets).
- **Dashboard**: Real-time analytics of ticket severity, status, and environment.
- **Full Document Storage**: Documents are stored complete (no chunking) for better context.
- **Modern Stack**:
  - **Backend**: FastAPI, LangChain, Weaviate (Docker), Groq/Gemini LLMs.
  - **Frontend**: React, Vite, Tailwind CSS, Chart.js.

## 🏗️ Architecture

```
agentic/
├── app/                    # Backend Application
│   ├── api/               # FastAPI Endpoints (Tickets, Agents, Docs)
│   ├── services/          # Business Logic
│   │   ├── agents/        # LangChain Agent Logic
│   │   └── tools/         # Custom Tools (Vector & Web Search)
│   └── db/                # Weaviate Client
├── frontend/              # Frontend Application
│   ├── src/
│   │   ├── components/    # Dashboard, TicketForm, TicketResult
│   │   └── App.jsx        # Main Routing
│   └── vite.config.js     # Vite Configuration
├── docker-compose.yml     # Vector Database (Weaviate)
└── docs/                  # Documentation
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js & npm
- Docker Desktop

### 1. Start Vector Database
Run Weaviate in Docker:
```bash
docker-compose up -d
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure Environment
# Copy .env.example to .env and add your API keys (Groq, Tavily, etc.)

# Run Backend Server
python run.py
```
Backend runs at: `http://localhost:8000`

### 3. Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Start Development Server
npm run dev
```
Frontend runs at: `http://localhost:5173`

## 💡 Usage

1. **Dashboard**: Open the frontend to see an overview of ticket stats.
2. **Submit Ticket**: Click "New Ticket", fill in the details (Title, Description, etc.).
3. **AI Analysis**: The system will:
   - Search for similar past tickets.
   - Use the Agent to research the issue (internal docs + web).
   - Generate a solution and open it in a new tab.
4. **Review**: See the AI's reasoning, recommended solution, and referenced similar tickets.

## 📚 Documentation

- [**Quick Start Guide**](docs/QUICKSTART.md) - Detailed setup instructions.
- [**Architecture**](docs/ARCHITECTURE.md) - Deep dive into the system design.
- [**Setup Guide**](docs/SETUP_GUIDE.md) - Comprehensive installation guide.

## 🔧 Technology Stack

- **LLM**: Groq (Llama 3), Gemini, or Anthropic.
- **Vector DB**: Weaviate (Local Docker).
- **Embeddings**: Sentence Transformers (Local).
- **Frameworks**: FastAPI (Python), React (JS).
- **Orchestration**: LangChain.
