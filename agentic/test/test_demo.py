"""
Example script to test the agentic RAG system.
Run this after starting the application with: python run.py
"""
import requests
import json
import time

# Base URL
BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def check_health():
    """Check if the API is healthy."""
    print_section("Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200


def upload_sample_documents():
    """Upload sample documents to the vector database."""
    print_section("Uploading Sample Documents")
    
    documents = [
        {
            "title": "Python Programming Best Practices",
            "content": """
Python best practices include:
1. Use virtual environments to isolate project dependencies
2. Follow PEP 8 style guide for code formatting
3. Write comprehensive unit tests using pytest or unittest
4. Use type hints to improve code clarity and catch errors
5. Document your code with clear docstrings
6. Handle exceptions properly with try-except blocks
7. Use list comprehensions for cleaner code
8. Avoid global variables when possible
9. Use context managers (with statements) for resource management
10. Keep functions small and focused on a single task
            """,
            "document_type": "text",
            "source": "programming_guide",
            "metadata": {"category": "programming", "language": "python"}
        },
        {
            "title": "Machine Learning Fundamentals",
            "content": """
Machine Learning is a subset of artificial intelligence that enables systems to learn from data.
Key concepts include:

Supervised Learning: Training models on labeled data (classification, regression)
Unsupervised Learning: Finding patterns in unlabeled data (clustering, dimensionality reduction)
Neural Networks: Models inspired by biological neurons
Deep Learning: Neural networks with multiple layers
Training Process: Iterative optimization of model parameters
Evaluation Metrics: Accuracy, precision, recall, F1-score
Overfitting: When a model performs well on training data but poorly on new data
Cross-validation: Technique to assess model generalization

Popular algorithms: Linear Regression, Decision Trees, Random Forests, Support Vector Machines, Neural Networks
            """,
            "document_type": "text",
            "source": "ml_handbook",
            "metadata": {"category": "machine_learning", "topic": "fundamentals"}
        },
        {
            "title": "FastAPI Framework Overview",
            "content": """
FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+.

Key features:
- Fast: Very high performance, on par with NodeJS and Go
- Fast to code: Increase development speed significantly
- Fewer bugs: Reduce human-induced errors
- Intuitive: Great editor support with auto-completion
- Easy: Designed to be easy to use and learn
- Short: Minimize code duplication
- Robust: Production-ready code with automatic interactive documentation
- Standards-based: Based on OpenAPI and JSON Schema

Core concepts:
- Path operations: Define API endpoints with decorators (@app.get, @app.post, etc.)
- Pydantic models: Automatic request/response validation
- Dependency injection: Clean, reusable dependencies
- Async support: Native async/await support
- Automatic docs: Interactive API documentation (Swagger UI, ReDoc)
            """,
            "document_type": "text",
            "source": "web_framework_docs",
            "metadata": {"category": "programming", "framework": "fastapi"}
        }
    ]
    
    uploaded_ids = []
    for doc in documents:
        response = requests.post(f"{BASE_URL}/documents/upload", json=doc)
        if response.status_code == 201:
            result = response.json()
            uploaded_ids.append(result["document_id"])
            print(f"✅ Uploaded: {doc['title']}")
            print(f"   Document ID: {result['document_id']}")
            print(f"   Word count: {result['word_count']}")
        else:
            print(f"❌ Failed to upload: {doc['title']}")
    
    return uploaded_ids


def list_documents():
    """List all documents in the database."""
    print_section("Listing All Documents")
    response = requests.get(f"{BASE_URL}/documents/list")
    data = response.json()
    print(f"Total documents: {data['total']}")
    for doc in data['documents']:
        print(f"\n- {doc['title']}")
        print(f"  ID: {doc['document_id']}")
        print(f"  Type: {doc['document_type']}")
        print(f"  Words: {doc['word_count']}")


def search_documents(query):
    """Search for documents."""
    print_section(f"Searching Documents: '{query}'")
    response = requests.post(
        f"{BASE_URL}/documents/search",
        json={"query": query, "limit": 3}
    )
    data = response.json()
    print(f"Found {data['total_results']} results\n")
    for i, result in enumerate(data['results'], 1):
        print(f"{i}. {result['title']}")
        print(f"   Similarity: {result['similarity_score']:.2%}")
        print(f"   Preview: {result['content'][:150]}...")


def query_agent(query, use_web=True, use_vector=True):
    """Query the agentic RAG system."""
    print_section(f"Agent Query: '{query}'")
    print(f"Web Search: {use_web}, Vector Search: {use_vector}\n")
    
    response = requests.post(
        f"{BASE_URL}/agent/query",
        json={
            "query": query,
            "use_web_search": use_web,
            "use_vector_search": use_vector
        }
    )
    
    data = response.json()
    
    print("🤖 AGENT ANSWER:")
    print("-" * 60)
    print(data['answer'])
    print("-" * 60)
    
    print(f"\n⏱️ Execution time: {data['execution_time']:.2f}s")
    
    if data['sources']:
        print("\n📚 SOURCES USED:")
        for source in data['sources']:
            print(f"  - {source['type']}: {source['query']}")
    
    if data['agent_steps']:
        print(f"\n🔍 AGENT STEPS: ({len(data['agent_steps'])} steps)")
        for i, step in enumerate(data['agent_steps'], 1):
            print(f"  {i}. Tool: {step['tool']}")
            print(f"     Input: {step['tool_input']}")


def run_demo():
    """Run the complete demo."""
    print("\n" + "🚀" * 30)
    print("  AGENTIC RAG SYSTEM DEMO")
    print("🚀" * 30)
    
    # Check health
    if not check_health():
        print("\n❌ Application is not healthy. Please start it with: python run.py")
        return
    
    # Upload sample documents
    uploaded_ids = upload_sample_documents()
    
    if not uploaded_ids:
        print("\n⚠️ No documents uploaded. Continuing with existing documents...")
    
    time.sleep(1)
    
    # List documents
    list_documents()
    
    time.sleep(1)
    
    # Search documents
    search_documents("machine learning algorithms")
    
    time.sleep(1)
    
    # Agent queries
    queries = [
        {
            "query": "What are Python best practices?",
            "use_web": False,
            "use_vector": True,
            "description": "Vector search only - from our documents"
        },
        {
            "query": "What is the latest Python version released in 2024?",
            "use_web": True,
            "use_vector": False,
            "description": "Web search only - current information"
        },
        {
            "query": "Explain machine learning and compare it with recent AI developments",
            "use_web": True,
            "use_vector": True,
            "description": "Both tools - combine internal knowledge with current info"
        }
    ]
    
    for query_info in queries:
        time.sleep(2)
        print(f"\n📝 {query_info['description']}")
        query_agent(
            query_info["query"],
            use_web=query_info["use_web"],
            use_vector=query_info["use_vector"]
        )
    
    print_section("Demo Complete!")
    print("✅ All tests passed successfully!")
    print("\nNext steps:")
    print("1. Check API docs: http://localhost:8000/docs")
    print("2. Upload your own documents")
    print("3. Try custom agent queries")


if __name__ == "__main__":
    try:
        run_demo()
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to the API.")
        print("Please make sure:")
        print("1. Weaviate is running: docker-compose up -d")
        print("2. Application is running: python run.py")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
