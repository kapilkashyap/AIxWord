@echo off
REM AIxWord - Complete Project Setup Script (Windows)
REM This script sets up both backend and frontend in one go

setlocal enabledelayedexpansion

echo.
echo ========================================
echo    AIxWord - Complete Project Setup
echo ========================================
echo.
echo This script will set up the entire AIxWord project
echo Including backend (Python/FastAPI) and frontend (React/TypeScript)
echo.

REM ============================================================================
REM 1. Prerequisites Check
REM ============================================================================
echo ========================================
echo 1. Checking Prerequisites
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.11+
    exit /b 1
)
echo [OK] Python found
python --version

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js 18+
    exit /b 1
)
echo [OK] Node.js found
node --version

REM Check npm
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm not found. Please install npm
    exit /b 1
)
echo [OK] npm found
npm --version

echo.

REM ============================================================================
REM 2. Backend Setup
REM ============================================================================
echo ========================================
echo 2. Setting Up Backend
echo ========================================
echo.

cd backend

echo [STEP] Creating Python virtual environment...
if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)

echo [STEP] Activating virtual environment...
call venv\Scripts\activate.bat

echo [STEP] Upgrading pip...
python -m pip install --upgrade pip --quiet

echo [STEP] Installing backend package...
pip install -e . --quiet
echo [OK] Backend package installed

echo [STEP] Installing development dependencies...
if exist "requirements-dev.txt" (
    pip install -r requirements-dev.txt --quiet
    echo [OK] Development dependencies installed
)

echo [STEP] Setting up environment configuration...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [OK] Created .env from .env.example
        echo [WARNING] IMPORTANT: Edit backend\.env and add your OPENAI_API_KEY
    ) else (
        echo [WARNING] .env.example not found, skipping .env creation
    )
) else (
    echo [INFO] .env already exists
)

echo [STEP] Verifying backend installation...
python -c "import backend" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend package can be imported
) else (
    echo [ERROR] Backend package cannot be imported
)

cd ..

echo.

REM ============================================================================
REM 3. Frontend Setup
REM ============================================================================
echo ========================================
echo 3. Setting Up Frontend
echo ========================================
echo.

cd frontend

echo [STEP] Installing frontend dependencies...
call npm install --silent
echo [OK] Frontend dependencies installed

echo [STEP] Setting up environment configuration...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [OK] Created .env from .env.example
    ) else (
        echo [WARNING] .env.example not found, skipping .env creation
    )
) else (
    echo [INFO] .env already exists
)

cd ..

echo.

REM ============================================================================
REM 4. Verification
REM ============================================================================
echo ========================================
echo 4. Verifying Installation
echo ========================================
echo.

echo [STEP] Checking backend structure...
if exist "backend\domain" if exist "backend\agents" if exist "backend\api" (
    echo [OK] Backend structure verified
) else (
    echo [ERROR] Backend structure incomplete
)

echo [STEP] Checking frontend structure...
if exist "frontend\src" if exist "frontend\package.json" (
    echo [OK] Frontend structure verified
) else (
    echo [ERROR] Frontend structure incomplete
)

echo [STEP] Checking documentation...
if exist "README.md" if exist "docs" (
    echo [OK] Documentation found
) else (
    echo [WARNING] Some documentation may be missing
)

echo.

REM ============================================================================
REM 5. Summary
REM ============================================================================
echo ========================================
echo Setup Complete!
echo ========================================
echo.

echo [OK] Backend setup complete
echo [OK] Frontend setup complete
echo.

echo Next steps:
echo.
echo   1. Configure your OpenAI API key:
echo      Edit backend\.env and add: OPENAI_API_KEY=sk-your-key-here
echo.
echo   2. Start the backend server:
echo      cd backend
echo      venv\Scripts\activate
echo      python run_server.py
echo      Backend will run at: http://localhost:8000
echo.
echo   3. In a new terminal, start the frontend:
echo      cd frontend
echo      npm run dev
echo      Frontend will run at: http://localhost:5173
echo.
echo   4. Run tests (optional):
echo      Backend: cd backend ^&^& pytest
echo      Frontend: cd frontend ^&^& npm test
echo.
echo   5. View API documentation:
echo      http://localhost:8000/docs (when backend is running)
echo.

echo For more information:
echo   - Quick Start: docs\QUICK_START_GUIDE.md
echo   - User Guide: docs\USER_GUIDE.md
echo   - Architecture: docs\ARCHITECTURE.md
echo   - API Reference: docs\API.md
echo.

echo [WARNING] IMPORTANT: Don't forget to add your OpenAI API key to backend\.env!
echo.

echo Happy coding! 🚀
echo.

pause
