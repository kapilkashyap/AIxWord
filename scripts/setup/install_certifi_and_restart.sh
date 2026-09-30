#!/bin/bash
# Install certifi and restart the server with SSL certificate configuration

set -e

echo "🔧 Installing certifi for SSL certificate support..."
echo ""

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run setup.sh first!"
    exit 1
fi

# Install certifi
echo "📦 Installing certifi..."
pip install certifi>=2023.7.22

# Reinstall the package to pick up new dependency
echo "📦 Reinstalling aixword-backend with new dependencies..."
pip install -e ".[dev]"

echo ""
echo "✅ certifi installed successfully!"
echo ""

# Kill existing server
echo "🛑 Stopping existing server..."
pkill -f "uvicorn main:app" 2>/dev/null || echo "   (no server was running)"

# Clear Python cache
echo "🧹 Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo ""
echo "🚀 Starting server with SSL certificate configuration..."
echo ""
echo "   SSL_CERT_FILE will be automatically configured to use certifi certificates"
echo "   This should resolve Zscaler/corporate proxy SSL issues"
echo ""

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
