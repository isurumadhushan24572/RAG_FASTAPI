@echo off
echo ========================================
echo   AGENTIC RAG - SETUP SCRIPT
echo ========================================
echo.

echo Step 1: Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not running
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo [OK] Docker is installed

echo.
echo Step 2: Starting Weaviate Vector Database...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start Weaviate
    pause
    exit /b 1
)
echo [OK] Weaviate is starting...

echo.
echo Step 3: Waiting for Weaviate to be ready...
timeout /t 10 /nobreak >nul
echo [OK] Weaviate should be ready

echo.
echo Step 4: Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    echo Please install Python 3.10+ from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python is installed

echo.
echo Step 5: Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

echo.
echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Run the application: python run.py
echo 2. Test it: python test_demo.py
echo 3. API docs: http://localhost:8000/docs
echo.
echo Press any key to start the application...
pause >nul

echo.
echo Starting application...
python run.py
