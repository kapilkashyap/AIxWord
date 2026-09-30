# AIxWord - Development Guide

**Version:** 1.0.0  
**Last Updated:** September 29, 2026

---

## Table of Contents

1. [Introduction](#introduction)
2. [Development Environment Setup](#development-environment-setup)
3. [Project Structure](#project-structure)
4. [Backend Development](#backend-development)
5. [Frontend Development](#frontend-development)
6. [Testing](#testing)
7. [Code Quality](#code-quality)
8. [Debugging](#debugging)
9. [Common Development Tasks](#common-development-tasks)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)
12. [Contributing](#contributing)

---

## Introduction

This guide provides comprehensive information for developers working on the AIxWord project. Whether you're setting up your development environment, implementing new features, or debugging issues, this guide will help you navigate the codebase effectively.

### Prerequisites

**Required:**
- Python 3.11 or higher
- Node.js 18 or higher
- Git
- OpenAI API key

**Recommended:**
- VS Code or PyCharm
- Postman or similar API testing tool
- Docker (optional, for containerized development)

### Quick Start for Developers

```bash
# Clone repository
git clone <repository-url>
cd AIxWord

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
pip install -r requirements-dev.txt
cp .env.example .env
# Edit .env and add OPENAI_API_KEY

# Setup frontend
cd ../frontend
npm install
cp .env.example .env

# Run tests
cd ../backend && pytest
cd ../frontend && npm test

# Start development servers
cd ../backend && python run_server.py  # Terminal 1
cd ../frontend && npm run dev          # Terminal 2
```

---

## Development Environment Setup

### Backend Setup

#### 1. Python Environment

**Install Python 3.11+:**

```bash
# macOS (using Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3.11-dev

# Windows
# Download from python.org
```

**Verify Installation:**
```bash
python3 --version  # Should be 3.11 or higher
```

#### 2. Virtual Environment

**Create and Activate:**

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Verify activation
which python  # Should point to venv/bin/python
```

#### 3. Install Dependencies

**Production Dependencies:**
```bash
pip install -e .
```

**Development Dependencies:**
```bash
pip install -r requirements-dev.txt
```

**Dependencies Installed:**
- FastAPI - Web framework
- LangGraph - Multi-agent orchestration
- OpenAI - LLM integration
- Pydantic - Data validation
- Uvicorn - ASGI server
- Pytest - Testing framework
- Black - Code formatting
- Ruff - Linting
- MyPy - Type checking
- Coverage - Test coverage

#### 4. Environment Configuration

**Create `.env` file:**
```bash
cp .env.example .env
```

**Edit `.env`:**
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# Grid Configuration
DEFAULT_GRID_SIZE=8
MAX_ITERATIONS=50
MIN_FILL_RATE=0.6

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=DEBUG  # Use DEBUG for development
CORS_ORIGINS=["http://localhost:5173"]

# Development Settings
ENVIRONMENT=development
DEBUG=true
```

#### 5. Verify Backend Setup

**Run Verification Script:**
```bash
python verify_setup.py
```

**Expected Output:**
```
✓ Python version: 3.11.x
✓ Virtual environment: Active
✓ Dependencies: Installed
✓ Environment variables: Configured
✓ OpenAI API: Connected
✓ Backend setup: Complete
```

### Frontend Setup

#### 1. Node.js Environment

**Install Node.js 18+:**

```bash
# macOS (using Homebrew)
brew install node@18

# Ubuntu/Debian (using NodeSource)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Windows
# Download from nodejs.org
```

**Verify Installation:**
```bash
node --version  # Should be 18 or higher
npm --version   # Should be 9 or higher
```

#### 2. Install Dependencies

```bash
cd frontend

# Install dependencies
npm install

# Verify installation
npm list --depth=0
```

**Dependencies Installed:**
- React 18 - UI framework
- TypeScript - Type safety
- Vite - Build tool
- Tailwind CSS - Styling
- Axios - HTTP client
- Vitest - Testing framework
- React Testing Library - Component testing

#### 3. Environment Configuration

**Create `.env` file:**
```bash
cp .env.example .env
```

**Edit `.env`:**
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_ENVIRONMENT=development
VITE_DEBUG=true
```

#### 4. Verify Frontend Setup

**Run Development Server:**
```bash
npm run dev
```

**Expected Output:**
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### IDE Setup

#### VS Code

**Recommended Extensions:**

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-typescript-next"
  ]
}
```

**Settings (`.vscode/settings.json`):**

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

#### PyCharm

**Configuration:**

1. **Interpreter**: Set to `backend/venv/bin/python`
2. **Code Style**: Enable Black formatter
3. **Inspections**: Enable type checking with MyPy
4. **Run Configurations**: Create configurations for:
   - Run Server: `python run_server.py`
   - Run Tests: `pytest`
   - Run Coverage: `pytest --cov=backend`

---

## Project Structure

### Backend Structure

```
backend/
├── agents/                 # Multi-agent system
│   ├── __init__.py
│   ├── planner.py         # PlannerAgent - Strategic planning
│   ├── word_generator.py  # WordGeneratorAgent - Word placement
│   ├── state.py           # Shared agent state
│   ├── workflow.py        # LangGraph workflow
│   └── orchestrator.py    # High-level orchestration API
├── domain/                # Domain models and business logic
│   ├── __init__.py
│   ├── models.py          # Core data models (Cell, WordPlacement, Clue)
│   ├── grid.py            # CrosswordGrid engine
│   ├── word.py            # Word domain model
│   ├── pattern.py         # Pattern matching
│   └── validator.py       # Validation logic
├── llm/                   # LLM integration
│   ├── __init__.py
│   ├── client.py          # OpenAI client wrapper
│   └── prompts.py         # Prompt templates
├── api/                   # FastAPI routes
│   ├── __init__.py
│   ├── main.py            # FastAPI application
│   ├── routes.py          # API route handlers
│   ├── puzzle.py          # Puzzle-specific endpoints
│   └── schemas.py         # Request/response schemas
├── tests/                 # Test suite
│   ├── domain/            # Domain tests
│   ├── agents/            # Agent tests
│   ├── llm/               # LLM tests
│   ├── api/               # API tests
│   └── conftest.py        # Pytest fixtures
├── config.py              # Configuration management
├── main.py                # Application entry point
├── run_server.py          # Development server script
├── pyproject.toml         # Python project configuration
├── pytest.ini             # Pytest configuration
├── mypy.ini               # MyPy configuration
└── requirements-dev.txt   # Development dependencies
```

### Frontend Structure

```
frontend/
├── src/
│   ├── components/        # React components
│   │   ├── CrosswordGrid.tsx      # Main grid component
│   │   ├── GridCell.tsx           # Individual cell
│   │   ├── CluePanel.tsx          # Clue display
│   │   ├── PuzzleGenerator.tsx    # Generation UI
│   │   ├── SolvingControls.tsx    # Solving controls
│   │   ├── AIAssistancePanel.tsx  # AI assistance UI
│   │   ├── HintModal.tsx          # Hint display
│   │   ├── ConfirmationDialog.tsx # Confirmation dialogs
│   │   ├── SolutionAnimation.tsx  # Solution animation
│   │   ├── index.ts               # Component exports
│   │   └── __tests__/             # Component tests
│   ├── hooks/             # Custom React hooks
│   │   ├── useAPI.ts              # API integration
│   │   ├── usePuzzle.ts           # Puzzle state
│   │   ├── useSolving.ts          # Solving logic
│   │   ├── useAIAssistance.ts     # AI assistance
│   │   ├── index.ts               # Hook exports
│   │   └── __tests__/             # Hook tests
│   ├── services/          # API client
│   │   └── api.ts                 # Axios client
│   ├── types/             # TypeScript types
│   │   ├── puzzle.ts              # Puzzle types
│   │   ├── api.ts                 # API types
│   │   └── aiAssistance.ts        # AI assistance types
│   ├── utils/             # Utility functions
│   │   ├── grid.ts                # Grid utilities
│   │   ├── validation.ts          # Validation
│   │   └── keyboard.ts            # Keyboard handling
│   ├── App.tsx            # Root component
│   ├── main.tsx           # Application entry
│   └── index.css          # Global styles
├── public/                # Static assets
├── package.json           # Node dependencies
├── tsconfig.json          # TypeScript configuration
├── vite.config.ts         # Vite configuration
├── tailwind.config.js     # Tailwind configuration
└── vitest.config.ts       # Vitest configuration
```

### Key Architectural Patterns

#### Backend: Clean Architecture

**Layers:**
1. **Domain Layer**: Pure business logic, no external dependencies
2. **Application Layer**: Use cases and orchestration (agents, workflow)
3. **Infrastructure Layer**: External services (LLM, API)
4. **Presentation Layer**: API endpoints and schemas

**Dependency Rule**: Inner layers don't depend on outer layers

#### Frontend: Component-Based Architecture

**Patterns:**
1. **Container/Presentation**: Smart containers, dumb components
2. **Custom Hooks**: Reusable logic extraction
3. **Context API**: Global state management
4. **Service Layer**: API abstraction

---

## Backend Development

### Adding a New Agent

**1. Create Agent Class:**

```python
# backend/agents/my_agent.py

from typing import Dict, Any
from backend.agents.state import AgentState
from backend.llm.client import LLMClient

class MyAgent:
    """Description of what this agent does."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute agent logic."""
        # Agent implementation
        return state
```

**2. Add to Workflow:**

```python
# backend/agents/workflow.py

def my_agent_node(state: AgentState) -> AgentState:
    """Node for MyAgent."""
    agent = MyAgent(llm_client=get_llm_client())
    return agent.execute(state)

# Add to workflow
workflow.add_node("my_agent", my_agent_node)
workflow.add_edge("previous_node", "my_agent")
```

**3. Write Tests:**

```python
# backend/tests/agents/test_my_agent.py

import pytest
from backend.agents.my_agent import MyAgent
from backend.agents.state import AgentState

@pytest.fixture
def agent(mock_llm_client):
    return MyAgent(llm_client=mock_llm_client)

def test_my_agent_execution(agent):
    state = AgentState(...)
    result = agent.execute(state)
    assert result.status == "expected_status"
```

### Adding a New API Endpoint

**1. Define Schema:**

```python
# backend/api/schemas.py

from pydantic import BaseModel, Field

class MyRequest(BaseModel):
    """Request schema."""
    param1: str = Field(..., description="Parameter 1")
    param2: int = Field(default=10, description="Parameter 2")

class MyResponse(BaseModel):
    """Response schema."""
    result: str
    metadata: Dict[str, Any]
```

**2. Implement Endpoint:**

```python
# backend/api/routes.py

from fastapi import APIRouter, HTTPException
from backend.api.schemas import MyRequest, MyResponse

router = APIRouter()

@router.post("/my-endpoint", response_model=MyResponse)
async def my_endpoint(request: MyRequest):
    """Endpoint description."""
    try:
        # Implementation
        result = process_request(request)
        return MyResponse(result=result, metadata={})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**3. Write Tests:**

```python
# backend/tests/api/test_routes.py

from fastapi.testclient import TestClient

def test_my_endpoint(client: TestClient):
    response = client.post(
        "/api/my-endpoint",
        json={"param1": "value", "param2": 20}
    )
    assert response.status_code == 200
    assert response.json()["result"] == "expected"
```

### Working with the Grid Engine

**Creating a Grid:**

```python
from backend.domain.grid import CrosswordGrid
from backend.domain.models import Direction

# Create 8×8 grid
grid = CrosswordGrid(size=8)

# Place a word
success = grid.place_word(
    word="PYTHON",
    row=0,
    col=0,
    direction=Direction.ACROSS
)

# Check fill rate
fill_rate = grid.calculate_fill_rate()

# Find available spaces
spaces = grid.find_available_spaces()

# Serialize grid
grid_dict = grid.to_dict()
```

**Validating Placements:**

```python
from backend.domain.validator import GridValidator

validator = GridValidator()

# Validate word
is_valid = validator.validate_word("PYTHON")

# Validate placement
can_place = validator.can_place_word(
    grid=grid,
    word="PYTHON",
    row=0,
    col=0,
    direction=Direction.ACROSS
)
```

### Working with LLM

**Using LLM Client:**

```python
from backend.llm.client import LLMClient
from backend.llm.prompts import WORD_GENERATION_PROMPT

# Create client
client = LLMClient(api_key="your-key")

# Generate completion
prompt = WORD_GENERATION_PROMPT.format(
    topic="Science",
    lengths=[5, 6, 7],
    existing_words=["ATOM", "CELL"]
)

response = await client.generate_completion(
    prompt=prompt,
    temperature=0.7,
    response_format={"type": "json_object"}
)

# Parse response
data = json.loads(response)
words = data["words"]
```

**Creating Custom Prompts:**

```python
# backend/llm/prompts.py

MY_CUSTOM_PROMPT = """
You are a {role}.

Context: {context}
Task: {task}

Requirements:
1. {requirement1}
2. {requirement2}

Return JSON:
{{
  "result": "...",
  "reasoning": "..."
}}
"""
```

### Running the Backend

**Development Server:**

```bash
# Using run_server.py
python run_server.py

# Using uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# With custom log level
uvicorn backend.main:app --reload --log-level debug
```

**Production Server:**

```bash
# Using gunicorn with uvicorn workers
gunicorn backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

---

## Frontend Development

### Adding a New Component

**1. Create Component:**

```typescript
// frontend/src/components/MyComponent.tsx

import React from 'react';
import styles from './MyComponent.module.css';

interface MyComponentProps {
  prop1: string;
  prop2?: number;
  onAction?: () => void;
}

export const MyComponent: React.FC<MyComponentProps> = ({
  prop1,
  prop2 = 10,
  onAction
}) => {
  return (
    <div className={styles.container}>
      <h2>{prop1}</h2>
      <button onClick={onAction}>Action</button>
    </div>
  );
};
```

**2. Create Styles:**

```css
/* frontend/src/components/MyComponent.module.css */

.container {
  @apply p-4 bg-white rounded-lg shadow;
}

.container h2 {
  @apply text-xl font-bold mb-2;
}

.container button {
  @apply px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600;
}
```

**3. Create Type Definitions:**

```typescript
// frontend/src/components/MyComponent.module.css.d.ts

declare const styles: {
  readonly container: string;
};

export default styles;
```

**4. Export Component:**

```typescript
// frontend/src/components/index.ts

export { MyComponent } from './MyComponent';
```

**5. Write Tests:**

```typescript
// frontend/src/components/__tests__/MyComponent.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import { MyComponent } from '../MyComponent';

describe('MyComponent', () => {
  it('renders with props', () => {
    render(<MyComponent prop1="Test" />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  it('calls onAction when button clicked', () => {
    const onAction = vi.fn();
    render(<MyComponent prop1="Test" onAction={onAction} />);
    
    fireEvent.click(screen.getByText('Action'));
    expect(onAction).toHaveBeenCalled();
  });
});
```

### Creating Custom Hooks

**1. Create Hook:**

```typescript
// frontend/src/hooks/useMyHook.ts

import { useState, useEffect } from 'react';

interface UseMyHookOptions {
  option1: string;
  option2?: number;
}

interface UseMyHookReturn {
  data: any;
  loading: boolean;
  error: Error | null;
  refetch: () => void;
}

export const useMyHook = (options: UseMyHookOptions): UseMyHookReturn => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch logic
      const result = await fetch(`/api/endpoint?param=${options.option1}`);
      setData(result);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [options.option1]);

  return { data, loading, error, refetch: fetchData };
};
```

**2. Export Hook:**

```typescript
// frontend/src/hooks/index.ts

export { useMyHook } from './useMyHook';
```

**3. Write Tests:**

```typescript
// frontend/src/hooks/__tests__/useMyHook.test.tsx

import { renderHook, waitFor } from '@testing-library/react';
import { useMyHook } from '../useMyHook';

describe('useMyHook', () => {
  it('fetches data', async () => {
    const { result } = renderHook(() => 
      useMyHook({ option1: 'test' })
    );

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBeDefined();
    });
  });
});
```

### Working with API

**Using API Service:**

```typescript
import { api } from '@/services/api';

// Generate puzzle
const puzzle = await api.generatePuzzle({
  topic: 'Science',
  grid_size: 8,
  min_words: 8,
  max_words: 15
});

// Get puzzle
const existingPuzzle = await api.getPuzzle(puzzleId);

// Solve word
const solution = await api.solveWord(puzzleId, {
  word_number: 1,
  direction: 'across'
});
```

**Adding New API Methods:**

```typescript
// frontend/src/services/api.ts

class APIClient {
  // ... existing methods

  async myNewMethod(param: string): Promise<MyResponse> {
    const response = await this.client.post<MyResponse>(
      '/api/my-endpoint',
      { param }
    );
    return response.data;
  }
}
```

### Running the Frontend

**Development Server:**

```bash
# Start dev server
npm run dev

# Start with custom port
npm run dev -- --port 3000

# Start with host exposed
npm run dev -- --host
```

**Build for Production:**

```bash
# Build
npm run build

# Preview build
npm run preview
```

---

## Testing

### Backend Testing

#### Running Tests

**All Tests:**
```bash
cd backend
pytest
```

**With Coverage:**
```bash
pytest --cov=backend --cov-report=html
open htmlcov/index.html
```

**Specific Tests:**
```bash
# Test file
pytest tests/domain/test_grid.py

# Test class
pytest tests/domain/test_grid.py::TestCrosswordGrid

# Test method
pytest tests/domain/test_grid.py::TestCrosswordGrid::test_initialization

# By marker
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

**Parallel Execution:**
```bash
pytest -n auto
```

#### Writing Tests

**Unit Test Example:**

```python
# tests/domain/test_my_module.py

import pytest
from backend.domain.my_module import MyClass

@pytest.fixture
def my_instance():
    """Fixture for MyClass instance."""
    return MyClass(param="value")

def test_my_method(my_instance):
    """Test MyClass.my_method."""
    result = my_instance.my_method()
    assert result == "expected"

def test_my_method_with_error(my_instance):
    """Test error handling."""
    with pytest.raises(ValueError):
        my_instance.my_method(invalid_param=True)
```

**Integration Test Example:**

```python
# tests/test_integration_my_feature.py

import pytest
from backend.agents.orchestrator import PuzzleOrchestrator

@pytest.mark.integration
async def test_puzzle_generation_flow():
    """Test complete puzzle generation flow."""
    orchestrator = PuzzleOrchestrator()
    
    result = await orchestrator.generate_puzzle(
        topic="Science",
        grid_size=8
    )
    
    assert result.status == "completed"
    assert len(result.placed_words) >= 8
    assert result.grid.calculate_fill_rate() >= 0.6
```

**API Test Example:**

```python
# tests/api/test_my_endpoint.py

from fastapi.testclient import TestClient

def test_my_endpoint_success(client: TestClient):
    """Test successful request."""
    response = client.post(
        "/api/my-endpoint",
        json={"param": "value"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "expected"

def test_my_endpoint_validation_error(client: TestClient):
    """Test validation error."""
    response = client.post(
        "/api/my-endpoint",
        json={"invalid": "data"}
    )
    
    assert response.status_code == 422
```

### Frontend Testing

#### Running Tests

**All Tests:**
```bash
cd frontend
npm test
```

**Watch Mode:**
```bash
npm test -- --watch
```

**With Coverage:**
```bash
npm test -- --coverage
```

**Specific Tests:**
```bash
# Test file
npm test -- GridCell.test.tsx

# Test pattern
npm test -- --grep "renders correctly"
```

#### Writing Tests

**Component Test Example:**

```typescript
// src/components/__tests__/MyComponent.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import { MyComponent } from '../MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent prop1="Test" />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  it('handles user interaction', () => {
    const onAction = vi.fn();
    render(<MyComponent prop1="Test" onAction={onAction} />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(onAction).toHaveBeenCalledTimes(1);
  });

  it('updates on prop change', () => {
    const { rerender } = render(<MyComponent prop1="Initial" />);
    expect(screen.getByText('Initial')).toBeInTheDocument();
    
    rerender(<MyComponent prop1="Updated" />);
    expect(screen.getByText('Updated')).toBeInTheDocument();
  });
});
```

**Hook Test Example:**

```typescript
// src/hooks/__tests__/useMyHook.test.tsx

import { renderHook, act, waitFor } from '@testing-library/react';
import { useMyHook } from '../useMyHook';

describe('useMyHook', () => {
  it('initializes with default state', () => {
    const { result } = renderHook(() => useMyHook({ option1: 'test' }));
    
    expect(result.current.data).toBeNull();
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('fetches data on mount', async () => {
    const { result } = renderHook(() => useMyHook({ option1: 'test' }));
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBeDefined();
    });
  });

  it('refetches data', async () => {
    const { result } = renderHook(() => useMyHook({ option1: 'test' }));
    
    await waitFor(() => expect(result.current.loading).toBe(false));
    
    act(() => {
      result.current.refetch();
    });
    
    expect(result.current.loading).toBe(true);
  });
});
```

---

## Code Quality

### Backend Code Quality

#### Formatting with Black

**Format Code:**
```bash
cd backend

# Format all files
black .

# Check without modifying
black --check .

# Format specific file
black backend/domain/grid.py
```

**Configuration (pyproject.toml):**
```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
```

#### Linting with Ruff

**Lint Code:**
```bash
# Lint all files
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Lint specific file
ruff check backend/domain/grid.py
```

**Configuration (pyproject.toml):**
```toml
[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]
```

#### Type Checking with MyPy

**Type Check:**
```bash
# Check all files
mypy .

# Check specific file
mypy backend/domain/grid.py

# Check with strict mode
mypy --strict backend/domain/grid.py
```

**Configuration (mypy.ini):**
```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

### Frontend Code Quality

#### Linting with ESLint

**Lint Code:**
```bash
cd frontend

# Lint all files
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix

# Lint specific file
npm run lint -- src/components/MyComponent.tsx
```

**Configuration (.eslintrc.json):**
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended"
  ],
  "rules": {
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "react/react-in-jsx-scope": "off"
  }
}
```

#### Formatting with Prettier

**Format Code:**
```bash
# Format all files
npm run format

# Check without modifying
npm run format -- --check
```

**Configuration (.prettierrc):**
```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}
```

#### Type Checking

**Type Check:**
```bash
# Check types
npm run type-check

# Watch mode
npm run type-check -- --watch
```

### Pre-commit Hooks

**Setup (using pre-commit):**

```yaml
# .pre-commit-config.yaml

repos:
  - repo: https://github.com/psf/black
    rev: 23.x.x
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.x.x
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.x.x
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

**Install:**
```bash
pip install pre-commit
pre-commit install
```

---

## Debugging

### Backend Debugging

#### Using Python Debugger

**Add Breakpoint:**
```python
import pdb

def my_function():
    x = 10
    pdb.set_trace()  # Debugger will stop here
    y = x * 2
    return y
```

**Debugger Commands:**
- `n` - Next line
- `s` - Step into function
- `c` - Continue execution
- `p variable` - Print variable
- `l` - List code
- `q` - Quit debugger

#### VS Code Debugging

**Launch Configuration (.vscode/launch.json):**

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "backend.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": false
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    },
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "${file}",
        "-v"
      ]
    }
  ]
}
```

#### Logging

**Configure Logging:**

```python
import logging

# Configure logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use logger
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

**View Logs:**
```bash
# Backend logs
tail -f backend.log

# Uvicorn logs
uvicorn backend.main:app --log-level debug
```

### Frontend Debugging

#### Browser DevTools

**Console Logging:**
```typescript
console.log('Variable:', variable);
console.error('Error:', error);
console.table(arrayOfObjects);
console.group('Group Name');
console.log('Item 1');
console.log('Item 2');
console.groupEnd();
```

**Debugger Statement:**
```typescript
function myFunction() {
  const x = 10;
  debugger;  // Browser will pause here
  const y = x * 2;
  return y;
}
```

#### React DevTools

**Install:**
- Chrome: React Developer Tools extension
- Firefox: React Developer Tools extension

**Features:**
- Component tree inspection
- Props and state viewing
- Performance profiling
- Hook inspection

#### VS Code Debugging

**Launch Configuration (.vscode/launch.json):**

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Chrome: Frontend",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/frontend/src",
      "sourceMapPathOverrides": {
        "webpack:///src/*": "${webRoot}/*"
      }
    }
  ]
}
```

---

## Common Development Tasks

### Creating a New Feature

**1. Create Feature Branch:**
```bash
git checkout -b feature/my-feature
```

**2. Implement Backend:**
```bash
# Add domain logic
# Add agent logic (if needed)
# Add API endpoint
# Write tests
pytest tests/my_feature/
```

**3. Implement Frontend:**
```bash
# Add components
# Add hooks
# Add API integration
# Write tests
npm test -- MyFeature
```

**4. Test Integration:**
```bash
# Start backend
cd backend && python run_server.py

# Start frontend
cd frontend && npm run dev

# Manual testing
# Automated E2E tests (if applicable)
```

**5. Code Quality:**
```bash
# Backend
cd backend
black .
ruff check --fix .
mypy .
pytest --cov=backend

# Frontend
cd frontend
npm run lint -- --fix
npm run format
npm run type-check
npm test -- --coverage
```

**6. Commit and Push:**
```bash
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature
```

### Updating Dependencies

**Backend:**
```bash
cd backend

# Update all dependencies
pip install --upgrade -r requirements-dev.txt

# Update specific package
pip install --upgrade fastapi

# Freeze dependencies
pip freeze > requirements.txt
```

**Frontend:**
```bash
cd frontend

# Update all dependencies
npm update

# Update specific package
npm install react@latest

# Check for outdated packages
npm outdated
```

### Database Migrations (Future)

When database is added:

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

---

## Best Practices

### Backend Best Practices

**1. Type Hints:**
```python
# Good
def calculate_fill_rate(grid: CrosswordGrid) -> float:
    return grid.filled_cells / grid.total_cells

# Bad
def calculate_fill_rate(grid):
    return grid.filled_cells / grid.total_cells
```

**2. Docstrings:**
```python
def place_word(word: str, row: int, col: int) -> bool:
    """
    Place a word on the grid.
    
    Args:
        word: The word to place
        row: Starting row (0-indexed)
        col: Starting column (0-indexed)
    
    Returns:
        True if placement successful, False otherwise
    
    Raises:
        ValueError: If word is invalid
        GridException: If placement violates constraints
    """
    pass
```

**3. Error Handling:**
```python
# Good
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise CustomException("User-friendly message") from e

# Bad
try:
    result = risky_operation()
except:
    pass
```

**4. Dependency Injection:**
```python
# Good
class MyAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

# Bad
class MyAgent:
    def __init__(self):
        self.llm_client = LLMClient()  # Hard-coded dependency
```

### Frontend Best Practices

**1. Component Props:**
```typescript
// Good
interface MyComponentProps {
  title: string;
  count?: number;
  onAction: () => void;
}

export const MyComponent: React.FC<MyComponentProps> = ({
  title,
  count = 0,
  onAction
}) => {
  // ...
};

// Bad
export const MyComponent = (props: any) => {
  // ...
};
```

**2. Custom Hooks:**
```typescript
// Good - Extract reusable logic
const useMyFeature = () => {
  const [state, setState] = useState();
  // Logic here
  return { state, setState };
};

// Bad - Logic in component
const MyComponent = () => {
  const [state, setState] = useState();
  // Complex logic here
};
```

**3. Error Boundaries:**
```typescript
// Good - Wrap components
<ErrorBoundary>
  <MyComponent />
</ErrorBoundary>

// Bad - No error handling
<MyComponent />
```

**4. Memoization:**
```typescript
// Good - Memoize expensive calculations
const expensiveValue = useMemo(() => {
  return calculateExpensiveValue(data);
}, [data]);

// Bad - Recalculate on every render
const expensiveValue = calculateExpensiveValue(data);
```

---

## Troubleshooting

### Common Backend Issues

**Issue: Import Errors**
```bash
# Solution: Install package in editable mode
pip install -e .
```

**Issue: OpenAI API Errors**
```bash
# Solution: Check API key
echo $OPENAI_API_KEY

# Solution: Check rate limits
# Wait and retry, or upgrade plan
```

**Issue: Tests Failing**
```bash
# Solution: Clear pytest cache
pytest --cache-clear

# Solution: Run specific test
pytest tests/path/to/test.py -v
```

### Common Frontend Issues

**Issue: Module Not Found**
```bash
# Solution: Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Issue: Type Errors**
```bash
# Solution: Regenerate type definitions
npm run type-check

# Solution: Check tsconfig.json
```

**Issue: Build Errors**
```bash
# Solution: Clear cache
rm -rf dist .vite
npm run build
```

---

## Contributing

### Contribution Workflow

1. **Fork Repository**
2. **Create Feature Branch**: `git checkout -b feature/my-feature`
3. **Make Changes**: Implement feature with tests
4. **Run Tests**: Ensure all tests pass
5. **Code Quality**: Run linters and formatters
6. **Commit**: Use conventional commits
7. **Push**: `git push origin feature/my-feature`
8. **Pull Request**: Create PR with description

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Example:**
```
feat(agents): add new planning strategy

Implement alternative planning strategy that prioritizes
longer words for better grid utilization.

Closes #123
```

---

## Additional Resources

### Documentation

- [Architecture Documentation](ARCHITECTURE.md)
- [API Reference](API.md)
- [User Guide](USER_GUIDE.md)
- [Multi-Agent System](MULTI_AGENT_SYSTEM.md)
- [Frontend Architecture](FRONTEND.md)

### External Resources

**Backend:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)

**Frontend:**
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

---

**Version:** 1.0.0  
**Last Updated:** September 29, 2026  
**Maintained By:** AIxWord Development Team

---

*For questions or issues, please refer to the [Troubleshooting](#troubleshooting) section or consult the team.*
