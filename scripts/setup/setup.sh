#!/bin/bash
# Development setup script for AIxWord backend

set -e

echo "🚀 Setting up AIxWord Backend..."

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔨 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install package in editable mode
echo "📦 Installing backend package..."
pip install -e .

# Install development dependencies
echo "🛠️  Installing development dependencies..."
pip install -r requirements-dev.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Edit .env and add your OPENAI_API_KEY"
echo "3. Run tests: pytest"
echo "4. Start development server: uvicorn backend.api.main:app --reload"
echo ""
