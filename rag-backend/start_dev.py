# 🐍 Python Script - Start Backend Server

"""
Local development server starter script.
Use this for development with hot-reload enabled.

For Docker deployment, use docker-compose.yml instead.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Start the FastAPI development server."""
    
    print("=" * 60)
    print("🚀 Starting RAG Backend Server")
    print("=" * 60)
    print()
    print("📍 API will be available at: http://localhost:8000")
    print("📚 API Docs (Swagger): http://localhost:8000/docs")
    print("📚 API Docs (ReDoc): http://localhost:8000/redoc")
    print()
    print("⚠️  Make sure Weaviate is running:")
    print("   docker-compose up weaviate -d")
    print()
    print("🔄 Hot-reload is enabled - code changes will auto-restart")
    print("❌ Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  WARNING: .env file not found!")
        print("   Copy .env.example to .env and configure it")
        print()
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(1)
    
    try:
        # Run uvicorn directly
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
