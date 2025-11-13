# 📂 Project Structure - RAG Backend

Detailed explanation of the project organization and architecture.

---

## 🌳 Directory Tree

```
rag-backend/
│
├── 📂 app/                         # Main application package
│   ├── 📄 __init__.py              # Package initialization
│   ├── 📄 main.py                  # FastAPI app + CORS + routes
│   │
│   ├── 📂 api/                     # API endpoints (routes)
│   │   ├── 📄 __init__.py
│   │   ├── 📄 health.py            # Health check endpoints
│   │   ├── 📄 tickets.py           # Ticket CRUD operations
│   │   └── 📄 collections.py       # Weaviate collection management
│   │
│   ├── 📂 core/                    # Core configuration
│   │   ├── 📄 __init__.py
│   │   └── 📄 config.py            # Settings with pydantic-settings
│   │
│   ├── 📂 db/                      # Database clients
│   │   ├── 📄 __init__.py
│   │   └── 📄 weaviate_client.py   # Weaviate connection & utils
│   │
│   ├── 📂 models/                  # Data models
│   │   ├── 📄 __init__.py
│   │   └── 📄 schemas.py           # Pydantic models for API
│   │
│   └── 📂 services/                # Business logic layer
│       ├── 📄 __init__.py
│       ├── 📄 ticket_service.py    # Ticket operations
│       ├── 📄 embedding_service.py # Embedding generation
│       ├── 📄 ai_service.py        # LLM integration (Groq)
│       └── 📄 prompts.py           # LLM prompt templates
│
├── 📂 docker/                      # Docker configuration
│   └── 📄 Dockerfile               # Multi-stage Docker build
│
├── 📂 scripts/                     # Utility scripts
│   └── (setup, migration, etc.)
│
├── 📂 tests/                       # Test suite
│   ├── 📄 __init__.py
│   ├── 📄 test_api.py              # API endpoint tests
│   ├── 📄 test_services.py         # Service layer tests
│   └── 📄 conftest.py              # Pytest fixtures
│
├── 📂 docs/                        # Additional documentation
│   ├── 📄 API_REFERENCE.md         # API endpoint reference
│   ├── 📄 DEPLOYMENT.md            # Deployment guide
│   └── 📄 ARCHITECTURE.md          # Architecture diagrams
│
├── 📂 .vscode/                     # VS Code settings
│   ├── 📄 settings.json            # Editor settings
│   └── 📄 launch.json              # Debug configurations
│
├── 📄 .env                         # Environment variables (local)
├── 📄 .env.example                 # Environment template
├── 📄 .dockerignore                # Docker build exclusions
├── 📄 .gitignore                   # Git exclusions
├── 📄 docker-compose.yml           # Multi-service orchestration
├── 📄 requirements.txt             # Python dependencies
├── 📄 run.py                       # Application entry point
├── 📄 README.md                    # Main documentation
├── 📄 QUICKSTART.md                # Quick start guide
└── 📄 STRUCTURE.md                 # This file
```

---

## 📦 Module Breakdown

### 1. `app/` - Main Application

**Purpose**: Core application code following clean architecture principles.

#### `app/main.py`
- FastAPI application instance
- CORS middleware configuration
- Router registration
- Startup/shutdown events
- Root endpoints

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RAG Backend API")
app.add_middleware(CORSMiddleware, ...)
app.include_router(tickets.router, prefix="/tickets")
```

---

### 2. `app/api/` - API Endpoints

**Purpose**: HTTP route handlers (controllers in MVC pattern).

#### `api/health.py`
- Health check endpoint
- Database connection verification
- System status monitoring

#### `api/tickets.py`
- `POST /tickets/` - Create ticket
- `GET /tickets/` - List tickets
- `GET /tickets/{id}` - Get ticket
- `PUT /tickets/{id}` - Update ticket
- `DELETE /tickets/{id}` - Delete ticket
- `POST /tickets/search` - Semantic search

#### `api/collections.py`
- `GET /collections/` - List Weaviate collections
- `POST /collections/` - Create collection
- `DELETE /collections/{name}` - Delete collection

**Pattern**: Routes → Services → Database

---

### 3. `app/core/` - Core Configuration

**Purpose**: Application configuration and settings.

#### `core/config.py`
- Environment variable loading
- Settings validation with Pydantic
- Configuration for all services

```python
class Settings(BaseSettings):
    WEAVIATE_HOST: str
    WEAVIATE_PORT: int
    GROQ_API_KEY: str
    ...
    
    class Config:
        env_file = ".env"
```

---

### 4. `app/db/` - Database Layer

**Purpose**: Database clients and connection management.

#### `db/weaviate_client.py`
- Weaviate client initialization
- Connection pooling
- Helper functions for CRUD operations
- Schema management

```python
def get_weaviate_client():
    client = weaviate.connect_to_local(...)
    return client
```

---

### 5. `app/models/` - Data Models

**Purpose**: Data validation and serialization.

#### `models/schemas.py`
- Pydantic models for requests
- Response schemas
- Data validation rules
- Type hints

```python
class TicketCreate(BaseModel):
    title: str
    description: str
    priority: str = "medium"

class TicketResponse(TicketCreate):
    id: str
    created_at: datetime
```

---

### 6. `app/services/` - Business Logic

**Purpose**: Core business logic separated from HTTP layer.

#### `services/ticket_service.py`
- Ticket CRUD operations
- Business rules enforcement
- Data transformation

#### `services/embedding_service.py`
- Text embedding generation
- Sentence Transformer model loading
- Vector caching

```python
class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer('all-mpnet-base-v2')
    
    def generate_embedding(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()
```

#### `services/ai_service.py`
- LLM integration (Groq)
- RAG pipeline orchestration
- Context retrieval + generation

#### `services/prompts.py`
- Prompt templates
- Prompt engineering
- Few-shot examples

---

### 7. `docker/` - Docker Configuration

#### `docker/Dockerfile`
Multi-stage build:
1. **Base stage**: Install system dependencies
2. **Dependencies stage**: Install Python packages
3. **Final stage**: Copy app code and run

```dockerfile
FROM python:3.11-slim as base
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

---

### 8. `tests/` - Test Suite

**Purpose**: Automated testing for quality assurance.

```
tests/
├── test_api.py           # API endpoint tests
├── test_services.py      # Service layer tests
├── test_embeddings.py    # Embedding tests
└── conftest.py           # Pytest fixtures
```

**Testing Stack**:
- pytest - Testing framework
- pytest-cov - Coverage reporting
- httpx - Async HTTP client for API tests

---

## 🔄 Request Flow

```
1. HTTP Request
   ↓
2. FastAPI Route (app/api/)
   ↓
3. Pydantic Validation (app/models/)
   ↓
4. Service Layer (app/services/)
   ↓
5. Database Layer (app/db/)
   ↓
6. Weaviate / External APIs
   ↓
7. Response Processing
   ↓
8. HTTP Response
```

### Example: Create Ticket

```python
# 1. Route (app/api/tickets.py)
@router.post("/", response_model=TicketResponse)
async def create_ticket(ticket: TicketCreate):
    # 2. Call service
    return await ticket_service.create(ticket)

# 3. Service (app/services/ticket_service.py)
async def create(ticket_data: TicketCreate):
    # 4. Generate embedding
    embedding = embedding_service.generate(ticket_data.description)
    
    # 5. Save to Weaviate
    weaviate_client.data.insert(...)
    
    return ticket_response
```

---

## 🏗️ Architecture Patterns

### 1. **Clean Architecture**
- Separation of concerns
- Dependency inversion
- Testable components

### 2. **Repository Pattern**
- Database abstraction in `db/`
- Service layer doesn't know about Weaviate specifics

### 3. **Dependency Injection**
- FastAPI's dependency injection for services
- Reusable dependencies

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/tickets/")
def list_tickets(db: Session = Depends(get_db)):
    ...
```

### 4. **Service Layer Pattern**
- Business logic in services
- Thin controllers in API layer

---

## 📋 File Naming Conventions

- **Modules**: `snake_case.py` (e.g., `ticket_service.py`)
- **Classes**: `PascalCase` (e.g., `TicketService`)
- **Functions**: `snake_case` (e.g., `create_ticket`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_TICKETS`)
- **Private**: Prefix with `_` (e.g., `_internal_method`)

---

## 🔧 Configuration Files

### `docker-compose.yml`
- Multi-service orchestration
- Backend + Weaviate services
- Network configuration
- Volume management

### `requirements.txt`
- Python dependencies
- Pinned versions for reproducibility

### `.env` / `.env.example`
- Environment variables
- API keys and secrets
- Service configuration

### `.dockerignore`
- Excludes files from Docker build context
- Speeds up builds
- Reduces image size

### `.gitignore`
- Excludes files from version control
- Protects secrets
- Ignores build artifacts

---

## 🎯 Best Practices Implemented

✅ **Modular Structure** - Clear separation of concerns  
✅ **Type Hints** - Full Python type annotations  
✅ **Pydantic Models** - Data validation  
✅ **Async/Await** - Asynchronous operations  
✅ **Environment Config** - 12-factor app principles  
✅ **Docker Multi-stage** - Optimized images  
✅ **Health Checks** - Monitoring endpoints  
✅ **CORS Configuration** - Security best practices  
✅ **Clean Code** - Readable and maintainable  
✅ **Documentation** - Comprehensive docs  

---

## 📚 Further Reading

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Weaviate Docs**: https://weaviate.io/developers/weaviate
- **Pydantic Docs**: https://docs.pydantic.dev
- **Docker Best Practices**: https://docs.docker.com/develop/dev-best-practices/

---

## 🔄 Adding New Features

### To Add a New Endpoint:

1. **Create model** in `app/models/schemas.py`
2. **Add service method** in `app/services/`
3. **Create route** in `app/api/`
4. **Register router** in `app/main.py`
5. **Write tests** in `tests/`

### Example: Add Comment Feature

```python
# 1. Model (models/schemas.py)
class CommentCreate(BaseModel):
    ticket_id: str
    text: str

# 2. Service (services/comment_service.py)
def create_comment(comment: CommentCreate):
    ...

# 3. Route (api/comments.py)
@router.post("/comments/")
def create_comment(comment: CommentCreate):
    return comment_service.create_comment(comment)

# 4. Register (main.py)
app.include_router(comments.router, prefix="/comments")
```

---

**Understanding the structure helps maintain and scale the application! 🚀**
