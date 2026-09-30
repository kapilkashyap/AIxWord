@echo off
REM Development setup script for AIxWord backend (Windows)

echo 🚀 Setting up AIxWord Backend...

REM Check Python version
echo 📋 Checking Python version...
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 🔨 Creating virtual environment...
    python -m venv venv
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install package in editable mode
echo 📦 Installing backend package...
pip install -e .

REM Install development dependencies
echo 🛠️  Installing development dependencies...
pip install -r requirements-dev.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env and add your OPENAI_API_KEY
) else (
    echo ✅ .env file already exists
)

echo.
echo ✨ Setup complete!
echo.
echo Next steps:
echo 1. Activate the virtual environment: venv\Scripts\activate.bat
echo 2. Edit .env and add your OPENAI_API_KEY
echo 3. Run tests: pytest
echo 4. Start development server: uvicorn backend.api.main:app --reload
echo.

pause
