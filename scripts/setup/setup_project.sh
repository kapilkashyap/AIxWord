#!/bin/bash
# AIxWord - Complete Project Setup Script
# This script sets up both backend and frontend in one go

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_step() {
    echo -e "\n${BLUE}▶${NC} $1"
}

# Start setup
clear
echo -e "${CYAN}"
cat << "EOF"
   ___    ____     _       __               __
  /   |  /  _/  __| |     / /___  _________/ /
 / /| |  / /   / /| | /| / / __ \/ ___/ __  / 
/ ___ |_/ /   / /_| |/ |/ / /_/ / /  / /_/ /  
/_/  |_/___/  \____|__/|__/\____/_/   \__,_/   
                                                
    Complete Project Setup
EOF
echo -e "${NC}"

print_info "This script will set up the entire AIxWord project"
print_info "Including backend (Python/FastAPI) and frontend (React/TypeScript)"
echo ""

# ============================================================================
# 1. Prerequisites Check
# ============================================================================
print_header "1. Checking Prerequisites"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3 not found. Please install Python 3.11+"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"
else
    print_error "Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION found"
else
    print_error "npm not found. Please install npm"
    exit 1
fi

# ============================================================================
# 2. Backend Setup
# ============================================================================
print_header "2. Setting Up Backend"

cd backend

print_step "Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

print_step "Activating virtual environment..."
source venv/bin/activate

print_step "Upgrading pip..."
pip install --upgrade pip --quiet

print_step "Installing backend package..."
pip install -e . --quiet
print_success "Backend package installed"

print_step "Installing development dependencies..."
if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt --quiet
    print_success "Development dependencies installed"
fi

print_step "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Created .env from .env.example"
        print_warning "⚠ IMPORTANT: Edit backend/.env and add your OPENAI_API_KEY"
    else
        print_warning ".env.example not found, skipping .env creation"
    fi
else
    print_info ".env already exists"
fi

print_step "Verifying backend installation..."
if python3 -c "import backend" 2>/dev/null; then
    print_success "Backend package can be imported"
else
    print_error "Backend package cannot be imported"
fi

cd ..

# ============================================================================
# 3. Frontend Setup
# ============================================================================
print_header "3. Setting Up Frontend"

cd frontend

print_step "Installing frontend dependencies..."
npm install --silent
print_success "Frontend dependencies installed"

print_step "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Created .env from .env.example"
    else
        print_warning ".env.example not found, skipping .env creation"
    fi
else
    print_info ".env already exists"
fi

cd ..

# ============================================================================
# 4. Verification
# ============================================================================
print_header "4. Verifying Installation"

print_step "Checking backend structure..."
if [ -d "backend/domain" ] && [ -d "backend/agents" ] && [ -d "backend/api" ]; then
    print_success "Backend structure verified"
else
    print_error "Backend structure incomplete"
fi

print_step "Checking frontend structure..."
if [ -d "frontend/src" ] && [ -f "frontend/package.json" ]; then
    print_success "Frontend structure verified"
else
    print_error "Frontend structure incomplete"
fi

print_step "Checking documentation..."
if [ -f "README.md" ] && [ -d "docs" ]; then
    print_success "Documentation found"
else
    print_warning "Some documentation may be missing"
fi

# ============================================================================
# 5. Summary
# ============================================================================
print_header "Setup Complete!"

echo -e "${GREEN}✓ Backend setup complete${NC}"
echo -e "${GREEN}✓ Frontend setup complete${NC}"
echo ""

print_info "Next steps:"
echo ""
echo "  1. Configure your OpenAI API key:"
echo -e "     ${CYAN}Edit backend/.env and add: OPENAI_API_KEY=sk-your-key-here${NC}"
echo ""
echo "  2. Start the backend server:"
echo -e "     ${CYAN}cd backend${NC}"
echo -e "     ${CYAN}source venv/bin/activate${NC}"
echo -e "     ${CYAN}python run_server.py${NC}"
echo -e "     Backend will run at: ${GREEN}http://localhost:8000${NC}"
echo ""
echo "  3. In a new terminal, start the frontend:"
echo -e "     ${CYAN}cd frontend${NC}"
echo -e "     ${CYAN}npm run dev${NC}"
echo -e "     Frontend will run at: ${GREEN}http://localhost:5173${NC}"
echo ""
echo "  4. Run tests (optional):"
echo -e "     Backend: ${CYAN}cd backend && pytest${NC}"
echo -e "     Frontend: ${CYAN}cd frontend && npm test${NC}"
echo ""
echo "  5. View API documentation:"
echo -e "     ${GREEN}http://localhost:8000/docs${NC} (when backend is running)"
echo ""

print_info "For more information:"
echo "  - Quick Start: docs/QUICK_START_GUIDE.md"
echo "  - User Guide: docs/USER_GUIDE.md"
echo "  - Architecture: docs/ARCHITECTURE.md"
echo "  - API Reference: docs/API.md"
echo ""

print_warning "IMPORTANT: Don't forget to add your OpenAI API key to backend/.env!"
echo ""

echo -e "${GREEN}Happy coding! 🚀${NC}"
