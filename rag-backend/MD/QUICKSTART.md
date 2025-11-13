# ⚡ Quick Start Guide - RAG Backend

Get your RAG backend up and running in **5 minutes**!

---

## 🎯 Prerequisites

- ✅ Docker & Docker Compose installed
- ✅ Groq API Key ([Get free key](https://console.groq.com))

---

## 🚀 5-Minute Setup

### Step 1: Navigate to Project (30 seconds)

```bash
cd c:\Users\ISURU\OneDrive\Desktop\1BT\Projects\RAG_PROJECTS\rag-backend
```

### Step 2: Configure Environment (1 minute)

```bash
# Copy environment template
copy .env.example .env

# Edit .env file and add your Groq API key
# Required: GROQ_API_KEY=your_actual_key_here
```

### Step 3: Start Services (2 minutes)

```bash
# Build and start backend + Weaviate
docker-compose up -d --build

# Wait for services to be healthy (30 seconds)
```

### Step 4: Verify Deployment (30 seconds)

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend

# Test health endpoint
curl http://localhost:8000/health
```

### Step 5: Access API (30 seconds)

Open in browser:
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Weaviate Console**: http://localhost:8080/v1/meta

---

## ✅ Verification Checklist

- [ ] Docker containers are running
- [ ] Health endpoint returns `{"status": "healthy"}`
- [ ] Swagger UI loads at `/docs`
- [ ] Weaviate is accessible at `:8080`
- [ ] No errors in logs

---

## 🎮 Quick Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild
docker-compose up -d --build

# Restart specific service
docker-compose restart backend

# Check status
docker-compose ps
```

---

## 🧪 Test Your API

### Using cURL

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Get API info
curl http://localhost:8000/

# 3. List collections
curl http://localhost:8000/collections/

# 4. Create a ticket
curl -X POST http://localhost:8000/tickets/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Ticket",
    "description": "Testing the API",
    "priority": "medium",
    "status": "open"
  }'
```

### Using Swagger UI

1. Go to http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. Fill in parameters
4. Click "Execute"
5. View response

---

## 🛑 Troubleshooting

### Services Won't Start

```bash
# Check if ports are available
netstat -ano | findstr :8000
netstat -ano | findstr :8080

# Stop conflicting services
docker-compose down

# Clean and rebuild
docker-compose down -v
docker-compose up -d --build
```

### Connection Refused

```bash
# Wait for services to be healthy
docker-compose ps

# Check logs for errors
docker-compose logs backend
docker-compose logs weaviate

# Verify Weaviate is ready
curl http://localhost:8080/v1/.well-known/ready
```

### API Key Error

```bash
# Verify .env file exists and has GROQ_API_KEY
cat .env | findstr GROQ

# Restart backend after updating .env
docker-compose restart backend
```

---

## 📊 What's Running?

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| FastAPI Backend | 8000 | http://localhost:8000 | REST API |
| Swagger UI | 8000 | http://localhost:8000/docs | API Documentation |
| Weaviate | 8080 | http://localhost:8080 | Vector Database |
| Weaviate gRPC | 50051 | - | gRPC API |

---

## 📁 Important Files

```
.env                    ← Your configuration
docker-compose.yml      ← Services definition
docker/Dockerfile       ← Backend image
app/                    ← Application code
requirements.txt        ← Python dependencies
run.py                  ← Entry point
```

---

## 🎓 Next Steps

1. ✅ **Explore API** - Use Swagger UI at `/docs`
2. 📝 **Create Tickets** - Test POST `/tickets/`
3. 🔍 **Search** - Try semantic search
4. 🔗 **Connect Frontend** - Point to `http://localhost:8000`
5. 📚 **Read Docs** - Check `README.md` for details

---

## 💡 Tips

- **Logs**: Always check logs if something fails
- **Health Checks**: Use `/health` to monitor status
- **CORS**: Update `CORS_ORIGINS` in `.env` for frontend
- **Performance**: Embeddings are cached for speed
- **Development**: Code changes auto-reload (volume mounted)

---

## 🆘 Need Help?

1. Check logs: `docker-compose logs -f backend`
2. Verify configuration: `cat .env`
3. Test health: `curl http://localhost:8000/health`
4. Review README.md for detailed docs
5. Check Weaviate: `curl http://localhost:8080/v1/.well-known/ready`

---

**🎉 You're ready to build with RAG!**
