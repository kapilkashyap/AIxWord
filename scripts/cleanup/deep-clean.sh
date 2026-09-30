#!/usr/bin/env bash
# Deep Clean Script - Remove all unwanted files and caches
# This script removes temporary files, caches, and build artifacts

set -e

echo "🧹 AIxWord Deep Clean"
echo "===================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter for deleted items
deleted_count=0

echo -e "${YELLOW}Step 1: Removing .DS_Store files...${NC}"
find . -name ".DS_Store" -type f -delete 2>/dev/null && echo "✓ Removed .DS_Store files" || echo "✓ No .DS_Store files found"

echo ""
echo -e "${YELLOW}Step 2: Removing Python cache files...${NC}"
find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null && echo "✓ Removed __pycache__ directories" || echo "✓ No __pycache__ directories found"
find backend -name "*.pyc" -type f -delete 2>/dev/null && echo "✓ Removed .pyc files" || echo "✓ No .pyc files found"
find backend -name "*.pyo" -type f -delete 2>/dev/null && echo "✓ Removed .pyo files" || echo "✓ No .pyo files found"

echo ""
echo -e "${YELLOW}Step 3: Removing pytest cache...${NC}"
if [ -d "backend/.pytest_cache" ]; then
    rm -rf backend/.pytest_cache
    echo "✓ Removed .pytest_cache"
else
    echo "✓ No .pytest_cache found"
fi

echo ""
echo -e "${YELLOW}Step 4: Removing build artifacts...${NC}"
if [ -d "backend/aixword_backend.egg-info" ]; then
    rm -rf backend/aixword_backend.egg-info
    echo "✓ Removed egg-info"
else
    echo "✓ No egg-info found"
fi

if [ -d "backend/dist" ]; then
    rm -rf backend/dist
    echo "✓ Removed backend/dist"
else
    echo "✓ No backend/dist found"
fi

if [ -d "backend/build" ]; then
    rm -rf backend/build
    echo "✓ Removed backend/build"
else
    echo "✓ No backend/build found"
fi

echo ""
echo -e "${YELLOW}Step 5: Removing frontend build artifacts...${NC}"
if [ -d "frontend/dist" ]; then
    rm -rf frontend/dist
    echo "✓ Removed frontend/dist"
else
    echo "✓ No frontend/dist found"
fi

echo ""
echo -e "${YELLOW}Step 6: Removing temporary files...${NC}"
find . -name "*.tmp" -type f -delete 2>/dev/null && echo "✓ Removed .tmp files" || echo "✓ No .tmp files found"
find . -name "*.swp" -type f -delete 2>/dev/null && echo "✓ Removed .swp files" || echo "✓ No .swp files found"
find . -name "*.swo" -type f -delete 2>/dev/null && echo "✓ Removed .swo files" || echo "✓ No .swo files found"
find . -name "*~" -type f -delete 2>/dev/null && echo "✓ Removed backup files" || echo "✓ No backup files found"

echo ""
echo -e "${YELLOW}Step 7: Removing log files (keeping SASVA logs)...${NC}"
find backend frontend -name "*.log" -type f -delete 2>/dev/null && echo "✓ Removed log files" || echo "✓ No log files found"

echo ""
echo -e "${YELLOW}Step 8: Checking for duplicate scripts...${NC}"
# List any potential duplicate files
duplicates=$(find . -maxdepth 2 -type f \( -name "restart*.sh" -o -name "setup*.sh" -o -name "verify*.py" -o -name "test_*.py" -o -name "diagnose*.py" \) 2>/dev/null | grep -v node_modules | grep -v venv | grep -v ".sasva" | grep -v "/scripts/" | grep -v "/tools/" | grep -v "/tests/" || true)

if [ -n "$duplicates" ]; then
    echo -e "${YELLOW}Found potential duplicate files outside scripts/tools directories:${NC}"
    echo "$duplicates"
    echo ""
    echo -e "${YELLOW}Review these files manually. They may need to be moved or deleted.${NC}"
else
    echo "✓ No duplicate scripts found"
fi

echo ""
echo -e "${GREEN}✅ Deep clean complete!${NC}"
echo ""
echo "Project is now clean and ready for demo/development."
echo ""
echo "To rebuild:"
echo "  Backend: cd backend && pip install -e \".[dev]\""
echo "  Frontend: cd frontend && npm install"
