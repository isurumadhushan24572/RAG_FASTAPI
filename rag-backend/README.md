# 🚀 RAG Backend - FastAPI + Weaviate Vector Database

> **Production-ready backend service** for Retrieval-Augmented Generation (RAG) applications with FastAPI and Weaviate vector database.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Weaviate](https://img.shields.io/badge/Weaviate-Latest-orange.svg)](https://weaviate.io/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Docker Deployment](#-docker-deployment)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

- ✅ **FastAPI Framework** - Modern, fast, async API framework
- ✅ **Weaviate Vector DB** - Scalable vector search and storage
- ✅ **Semantic Search** - Local embeddings with Sentence Transformers
- ✅ **LLM Integration** - Groq API for fast inference
- ✅ **Modular Architecture** - Clean separation of concerns
- ✅ **Docker Ready** - Multi-stage builds with optimization
- ✅ **Health Checks** - Built-in monitoring endpoints
- ✅ **CORS Support** - Configurable cross-origin requests
- ✅ **Environment Config** - Flexible configuration management
- ✅ **Auto Documentation** - Swagger UI & ReDoc included
- ✅ **Hot Reload** - Development mode with auto-restart

---

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Frontend      │─────▶│  FastAPI Backend │─────▶│  Weaviate DB    │
│  (React/Vite)   │      │   (Python 3.11)  │      │  (Vector Store) │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   Groq LLM API  │
                         └─────────────────┘
```

---

## 🛠️ Tech Stack

### Core Technologies
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server for production
- **Pydantic** - Data validation and settings management
- **Weaviate** - Vector database with gRPC support

### AI & ML
- **Sentence Transformers** - Local text embeddings (`all-mpnet-base-v2`)
- **LangChain Groq** - LLM integration for RAG
- **Groq API** - Fast LLM inference

### Development
- **Python 3.11** - Latest stable Python
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** installed
- **Docker & Docker Compose** installed
- **Groq API Key** ([Get one here](https://console.groq.com))

### 1. Clone or Navigate to Project

```bash
cd c:\Users\ISURU\OneDrive\Desktop\1BT\Projects\RAG_PROJECTS\rag-backend
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# Required: GROQ_API_KEY
```

### 3. Run with Docker (Recommended)

```bash
# Start all services (Backend + Weaviate)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Access API at http://localhost:8000
```

### 4. Run Locally (Alternative)

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run application
python run.py

# Access API at http://localhost:8000
```

---

## 📁 Project Structure

```
rag-backend/
├── app/                        # Main application package
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   │
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── health.py           # Health check endpoints
│   │   ├── tickets.py          # Ticket CRUD operations
│   │   └── collections.py      # Collection management
│   │
│   ├── core/                   # Core configuration
│   │   ├── __init__.py
│   │   └── config.py           # Settings management
│   │
│   ├── db/                     # Database clients
│   │   ├── __init__.py
│   │   └── weaviate_client.py  # Weaviate connection
│   │
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   └── schemas.py          # Request/response models
│   │
│   └── services/               # Business logic
│       ├── __init__.py
│       ├── ticket_service.py   # Ticket operations
│       ├── embedding_service.py # Embedding generation
│       ├── ai_service.py       # LLM integration
│       └── prompts.py          # LLM prompts
│
├── docker/                     # Docker configuration
│   └── Dockerfile              # Multi-stage build
│
├── scripts/                    # Utility scripts
│   └── (future scripts)
│
├── tests/                      # Test suite
│   └── (future tests)
│
├── docs/                       # Documentation
│   └── (API docs, guides)
│
├── .env                        # Environment variables (local)
├── .env.example                # Environment template
├── .dockerignore               # Docker ignore rules
├── .gitignore                  # Git ignore rules
├── docker-compose.yml          # Docker orchestration
├── requirements.txt            # Python dependencies
├── run.py                      # Application entry point
└── README.md                   # This file
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Weaviate Configuration
WEAVIATE_HOST=localhost        # Use 'weaviate' in Docker
WEAVIATE_PORT=8080
WEAVIATE_GRPC_PORT=50051

# FastAPI Configuration
API_HOST=0.0.0.0
API_PORT=8000

# CORS Configuration
CORS_ORIGINS=*                 # Comma-separated origins

# API Keys
GROQ_API_KEY=your_key_here     # Required
HUGGINGFACEHUB_API_TOKEN=...   # Optional

# LangSmith (Optional Tracing)
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=RAG-Backend

# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
```

### Port Configuration

| Service | Port | Description |
|---------|------|-------------|
| FastAPI | 8000 | REST API endpoints |
| Weaviate | 8080 | Vector database HTTP |
| Weaviate gRPC | 50051 | Weaviate gRPC API |

---

## 📚 API Documentation

### Interactive Docs

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | API information |
| POST | `/tickets/` | Create ticket |
| GET | `/tickets/` | List all tickets |
| GET | `/tickets/{id}` | Get ticket by ID |
| POST | `/tickets/search` | Semantic search |
| DELETE | `/tickets/{id}` | Delete ticket |
| GET | `/collections/` | List collections |

### Example Request

```bash
# Health check
curl http://localhost:8000/health

# Create ticket
curl -X POST http://localhost:8000/tickets/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Login Issue",
    "description": "Cannot login to account",
    "priority": "high"
  }'

# Semantic search
curl -X POST http://localhost:8000/tickets/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "password reset problems",
    "limit": 5
  }'
```

---

## 💻 Development

### Local Development Setup

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
cp .env.example .env
# Edit .env with your configuration

# 4. Run with hot-reload
python run.py

# Server starts at http://localhost:8000
```

### Development Features

- ✅ **Hot Reload** - Auto-restart on code changes
- ✅ **Debug Mode** - Detailed error messages
- ✅ **API Docs** - Auto-generated Swagger UI
- ✅ **CORS Enabled** - Frontend development support

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/

# Run tests
pytest tests/
```

---

## 🐳 Docker Deployment

### Build and Run

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f weaviate

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Docker Commands

```bash
# Rebuild specific service
docker-compose build backend

# Restart service
docker-compose restart backend

# Execute command in container
docker-compose exec backend bash

# View container stats
docker stats rag_fastapi_backend

# Check health status
docker inspect rag_fastapi_backend | grep -A 10 Health
```

### Production Deployment

For production, modify `docker-compose.yml`:

```yaml
# Remove volume mounts for source code
# Use production CORS_ORIGINS
# Set DEBUG=false
# Add resource limits
# Use secrets for API keys
```

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

### API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test with HTTPie
http GET http://localhost:8000/health

# Load testing with Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Change port in .env
API_PORT=8001

# Or stop existing service
docker-compose down
```

#### 2. Weaviate Connection Error

```bash
# Check if Weaviate is running
curl http://localhost:8080/v1/.well-known/ready

# Check Docker logs
docker-compose logs weaviate

# Restart Weaviate
docker-compose restart weaviate
```

#### 3. Module Import Errors

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=/app  # or set in .env

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 4. Groq API Errors

```bash
# Verify API key in .env
echo $GROQ_API_KEY

# Test API key
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

#### 5. Docker Build Fails

```bash
# Clean build cache
docker-compose build --no-cache backend

# Remove old images
docker system prune -a
```

### Logs and Debugging

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Check container status
docker-compose ps

# Inspect container
docker inspect rag_fastapi_backend
```

---

## 📦 Dependencies

See `requirements.txt` for complete list:

```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
weaviate-client>=4.0.0
python-dotenv>=1.0.0
requests>=2.31.0
sentence-transformers>=2.2.2
langchain-groq>=0.1.0
```

---

## 🔐 Security

### Production Checklist

- [ ] Change default API keys
- [ ] Configure specific CORS origins
- [ ] Enable authentication (JWT)
- [ ] Use HTTPS/TLS
- [ ] Set up rate limiting
- [ ] Enable API key rotation
- [ ] Configure firewall rules
- [ ] Use Docker secrets for sensitive data
- [ ] Enable audit logging
- [ ] Regular security updates

---

## 📈 Performance

### Optimization Tips

1. **Use Production ASGI Server**
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Enable Caching**
   - Cache embeddings
   - Use Redis for session storage

3. **Database Optimization**
   - Configure Weaviate indexing
   - Use batch operations

4. **Docker Optimization**
   - Multi-stage builds (already configured)
   - Minimize layer size
   - Use .dockerignore

---

## 🤝 Contributing

```bash
# 1. Create feature branch
git checkout -b feature/your-feature

# 2. Make changes and test
pytest

# 3. Commit changes
git commit -m "Add your feature"

# 4. Push and create PR
git push origin feature/your-feature
```

---

## 📄 License

This project is part of the RAG Project suite.

---

## 🆘 Support

- **Documentation**: Check `/docs` folder
- **API Docs**: http://localhost:8000/docs
- **Issues**: Report bugs or request features

---

## 🎯 Next Steps

1. ✅ **Setup Complete** - Backend is running
2. 🔄 **Test API** - Use Swagger UI
3. 📊 **Monitor** - Check health endpoints
4. 🚀 **Deploy** - Configure for production
5. 🧪 **Test** - Write unit and integration tests

---

**Built with ❤️ using FastAPI, Weaviate, and Python**

