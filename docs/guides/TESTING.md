# Testing Guide

This document provides comprehensive information about testing the AIxWord application, including test strategies, frameworks, best practices, and detailed instructions for running and writing tests.

## Table of Contents

- [Overview](#overview)
- [Testing Philosophy](#testing-philosophy)
- [Test Structure](#test-structure)
- [Backend Testing](#backend-testing)
- [Frontend Testing](#frontend-testing)
- [End-to-End Testing](#end-to-end-testing)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [Continuous Integration](#continuous-integration)
- [Best Practices](#best-practices)

---

## Overview

### Testing Stack

**Backend:**
- **Framework**: pytest
- **Async Support**: pytest-asyncio
- **HTTP Testing**: httpx
- **Mocking**: unittest.mock
- **Coverage**: pytest-cov

**Frontend:**
- **Framework**: Vitest
- **Testing Library**: @testing-library/react
- **DOM Environment**: jsdom
- **E2E**: Playwright

### Test Types

1. **Unit Tests**: Test individual functions and classes in isolation
2. **Integration Tests**: Test interactions between components
3. **End-to-End Tests**: Test complete user workflows
4. **Performance Tests**: Measure and verify performance characteristics

### Coverage Goals

| Layer | Target | Current |
|-------|--------|---------|
| Backend Overall | ≥ 90% | ~92% |
| Domain Layer | ≥ 95% | ~96% |
| Agent Layer | ≥ 90% | ~91% |
| API Layer | ≥ 85% | ~88% |
| Frontend Overall | ≥ 80% | ~85% |
| Components | ≥ 85% | ~87% |
| Hooks | ≥ 90% | ~92% |

---

## Testing Philosophy

### Principles

1. **Test Behavior, Not Implementation**
   - Focus on what the code does, not how it does it
   - Tests should survive refactoring
   - Test from the user's perspective

2. **Write Tests First (TDD)**
   - Write failing test
   - Write minimal code to pass
   - Refactor with confidence

3. **Keep Tests Simple**
   - One assertion per test (when possible)
   - Clear test names
   - Minimal setup

4. **Test the Right Things**
   - Happy paths
   - Error cases
   - Edge cases
   - Integration points

5. **Fast Feedback**
   - Tests should run quickly
   - Parallelize when possible
   - Mock external dependencies

### Test Pyramid

```
        /\
       /  \
      / E2E \
     /______\
    /        \
   /Integration\
  /____________\
 /              \
/  Unit Tests    \
/________________\
```

- **70% Unit Tests**: Fast, isolated, numerous
- **20% Integration Tests**: Test component interactions
- **10% E2E Tests**: Test critical user flows

---

## Test Structure

### Backend Test Organization

```
backend/tests/
├── __init__.py
├── conftest.py                 # Shared fixtures
├── domain/                     # Domain layer tests
│   ├── test_grid.py
│   ├── test_pattern.py
│   ├── test_validator.py
│   └── test_word.py
├── agents/                     # Agent layer tests
│   ├── test_planner.py
│   ├── test_word_generator.py
│   ├── test_orchestrator.py
│   ├── test_workflow.py
│   └── test_state.py
├── api/                        # API layer tests
│   ├── test_main.py
│   ├── test_puzzle.py
│   └── test_schemas.py
├── llm/                        # LLM layer tests
│   ├── test_client.py
│   └── test_prompts.py
├── integration/                # Integration tests
│   └── test_ai_assistance.py
├── test_integration_smoke.py   # Smoke tests
├── test_integration_e2e.py     # E2E integration tests
└── test_api_integration.py     # API integration tests
```

### Frontend Test Organization

```
frontend/src/
├── components/
│   ├── __tests__/
│   │   ├── AIAssistancePanel.test.tsx
│   │   ├── HintModal.test.tsx
│   │   ├── ConfirmationDialog.test.tsx
│   │   ├── SolutionAnimation.test.tsx
│   │   └── AIAssistanceIntegration.test.tsx
│   └── ...
├── hooks/
│   ├── __tests__/
│   │   └── useAIAssistance.test.tsx
│   └── ...
└── ...

frontend/e2e/
├── puzzle-generation.spec.ts
├── manual-solving.spec.ts
├── ai-assistance.spec.ts
└── complete-workflow.spec.ts
```

---

## Backend Testing

### Unit Tests

#### Testing Domain Models

```python
# tests/domain/test_grid.py
import pytest
from backend.domain.grid import Grid, Cell

def test_grid_initialization():
    """Test that grid initializes with correct size."""
    grid = Grid(size=8)
    assert grid.size == 8
    assert len(grid.cells) == 64

def test_cell_placement():
    """Test placing a letter in a cell."""
    grid = Grid(size=8)
    grid.set_cell(0, 0, 'A')
    assert grid.get_cell(0, 0).value == 'A'

def test_invalid_cell_position():
    """Test that invalid positions raise errors."""
    grid = Grid(size=8)
    with pytest.raises(ValueError):
        grid.set_cell(10, 10, 'A')
```

#### Testing Agents

```python
# tests/agents/test_planner.py
import pytest
from unittest.mock import AsyncMock, patch
from backend.agents.planner import PlannerAgent

@pytest.mark.asyncio
async def test_planner_generates_valid_plan():
    """Test that planner generates a valid plan."""
    with patch('backend.agents.planner.LLMClient') as mock_llm:
        mock_llm.return_value.generate.return_value = {
            "words": ["SCIENCE", "ATOM", "CELL"],
            "clues": ["Study of nature", "Smallest unit", "Basic unit"]
        }
        
        planner = PlannerAgent(mock_llm)
        plan = await planner.generate_plan("Science", grid_size=8)
        
        assert len(plan.words) == 3
        assert "SCIENCE" in plan.words
        assert len(plan.clues) == 3

@pytest.mark.asyncio
async def test_planner_handles_llm_failure():
    """Test that planner handles LLM failures gracefully."""
    with patch('backend.agents.planner.LLMClient') as mock_llm:
        mock_llm.return_value.generate.side_effect = Exception("LLM Error")
        
        planner = PlannerAgent(mock_llm)
        
        with pytest.raises(Exception):
            await planner.generate_plan("Science", grid_size=8)
```

#### Testing API Endpoints

```python
# tests/api/test_puzzle.py
import pytest
from httpx import AsyncClient, ASGITransport
from backend.api.main import app

@pytest.mark.asyncio
async def test_generate_puzzle_endpoint():
    """Test puzzle generation endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/puzzles/generate",
            json={
                "topic": "Science",
                "grid_size": 8,
                "difficulty": "medium"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "puzzle_id" in data
        assert "grid" in data
        assert data["topic"] == "Science"

@pytest.mark.asyncio
async def test_generate_puzzle_validation():
    """Test input validation for puzzle generation."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/puzzles/generate",
            json={
                "topic": "",  # Invalid: empty topic
                "grid_size": 8,
                "difficulty": "medium"
            }
        )
        
        assert response.status_code == 422  # Validation error
```

### Integration Tests

```python
# tests/test_integration_e2e.py
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from backend.api.main import app

@pytest.mark.asyncio
@pytest.mark.integration
async def test_complete_puzzle_workflow():
    """Test complete workflow: generate → solve → validate."""
    with patch('backend.agents.orchestrator.PuzzleOrchestrator') as mock_orch:
        # Mock successful generation
        mock_orch.return_value.generate_puzzle.return_value = {
            "success": True,
            "grid": {...},
            "word_count": 5
        }
        
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            # Step 1: Generate puzzle
            gen_response = await client.post(
                "/api/puzzles/generate",
                json={"topic": "Science", "grid_size": 8}
            )
            assert gen_response.status_code == 200
            puzzle_id = gen_response.json()["puzzle_id"]
            
            # Step 2: Solve a word
            with patch('backend.api.routes.puzzles.PuzzleSolver') as mock_solver:
                mock_solver.return_value.solve_word.return_value = (
                    "SCIENCE", 0.95, "Solved"
                )
                
                solve_response = await client.post(
                    f"/api/puzzles/{puzzle_id}/solve-word",
                    json={
                        "clue_number": 1,
                        "direction": "across",
                        "use_intersections": True
                    }
                )
                assert solve_response.status_code == 200
                assert solve_response.json()["success"] is True
```

### Fixtures

```python
# tests/conftest.py
import pytest
from typing import Any

@pytest.fixture
def sample_grid_dict() -> dict[str, Any]:
    """Provide a sample grid dictionary for testing."""
    return {
        "size": 8,
        "cells": [
            {"row": 0, "col": 0, "value": "S", "is_blocked": False, "number": 1},
            # ... more cells
        ],
        "words": [
            {
                "number": 1,
                "direction": "across",
                "word": "SCIENCE",
                "clue": "Study of the natural world",
                "start_row": 0,
                "start_col": 0,
            },
            # ... more words
        ],
    }

@pytest.fixture
async def test_client():
    """Provide an async HTTP client for testing."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
```

---

## Frontend Testing

### Component Tests

```typescript
// src/components/__tests__/AIAssistancePanel.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { AIAssistancePanel } from '../AIAssistancePanel';

describe('AIAssistancePanel', () => {
  it('renders all AI assistance buttons', () => {
    render(
      <AIAssistancePanel
        onSolveWord={vi.fn()}
        onSolvePuzzle={vi.fn()}
        onGetHint={vi.fn()}
        isLoading={false}
        hasActiveClue={true}
      />
    );
    
    expect(screen.getByRole('button', { name: /solve word/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /solve puzzle/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /get hint/i })).toBeInTheDocument();
  });
  
  it('disables solve word button when no clue is active', () => {
    render(
      <AIAssistancePanel
        onSolveWord={vi.fn()}
        onSolvePuzzle={vi.fn()}
        onGetHint={vi.fn()}
        isLoading={false}
        hasActiveClue={false}
      />
    );
    
    const solveWordButton = screen.getByRole('button', { name: /solve word/i });
    expect(solveWordButton).toBeDisabled();
  });
  
  it('calls onSolveWord when solve word button is clicked', () => {
    const onSolveWord = vi.fn();
    
    render(
      <AIAssistancePanel
        onSolveWord={onSolveWord}
        onSolvePuzzle={vi.fn()}
        onGetHint={vi.fn()}
        isLoading={false}
        hasActiveClue={true}
      />
    );
    
    const solveWordButton = screen.getByRole('button', { name: /solve word/i });
    fireEvent.click(solveWordButton);
    
    expect(onSolveWord).toHaveBeenCalledTimes(1);
  });
});
```

### Hook Tests

```typescript
// src/hooks/__tests__/useAIAssistance.test.tsx
import { renderHook, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useAIAssistance } from '../useAIAssistance';
import * as api from '../../services/api';

vi.mock('../../services/api');

describe('useAIAssistance', () => {
  const mockSetCellValue = vi.fn();
  const mockPuzzleId = 'test-puzzle-123';
  const mockActiveClue = { number: 1, direction: 'across' as const };
  
  beforeEach(() => {
    vi.clearAllMocks();
  });
  
  it('initializes with correct default state', () => {
    const { result } = renderHook(() =>
      useAIAssistance(mockPuzzleId, mockActiveClue, mockSetCellValue)
    );
    
    expect(result.current.isSolvingWord).toBe(false);
    expect(result.current.isSolvingPuzzle).toBe(false);
    expect(result.current.isGettingHint).toBe(false);
    expect(result.current.hintModal).toBeNull();
  });
  
  it('shows confirmation dialog when solve word is requested', () => {
    const { result } = renderHook(() =>
      useAIAssistance(mockPuzzleId, mockActiveClue, mockSetCellValue)
    );
    
    act(() => {
      result.current.showSolveWordConfirmation();
    });
    
    expect(result.current.confirmationDialog).not.toBeNull();
    expect(result.current.confirmationDialog?.actionType).toBe('solve-word');
  });
  
  it('solves word successfully', async () => {
    const mockResponse = {
      success: true,
      answer: 'SCIENCE',
      confidence: 0.95,
      reasoning: 'Solved based on clue',
      updated_cells: [
        { row: 0, col: 0, value: 'S' },
        { row: 0, col: 1, value: 'C' },
      ],
    };
    
    vi.mocked(api.apiClient.solveWord).mockResolvedValue(mockResponse);
    
    const { result } = renderHook(() =>
      useAIAssistance(mockPuzzleId, mockActiveClue, mockSetCellValue)
    );
    
    await act(async () => {
      result.current.showSolveWordConfirmation();
      result.current.confirmationDialog?.onConfirm();
    });
    
    await waitFor(() => {
      expect(result.current.isSolvingWord).toBe(false);
    });
    
    expect(mockSetCellValue).toHaveBeenCalled();
  });
});
```

### Integration Tests

```typescript
// src/components/__tests__/AIAssistanceIntegration.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { PuzzleContainerWithAI } from '../PuzzleContainerWithAI';
import * as api from '../../services/api';

vi.mock('../../services/api');

describe('AI Assistance Integration', () => {
  it('completes full AI assistance workflow', async () => {
    const mockPuzzle = {
      puzzle_id: 'test-123',
      grid: { /* grid data */ },
      clues: { /* clue data */ },
    };
    
    render(<PuzzleContainerWithAI puzzle={mockPuzzle} />);
    
    // Select a clue
    const clue = screen.getByTestId('clue-1-across');
    fireEvent.click(clue);
    
    // Click solve word
    const solveWordButton = screen.getByRole('button', { name: /solve word/i });
    fireEvent.click(solveWordButton);
    
    // Confirm
    const confirmButton = await screen.findByRole('button', { name: /confirm/i });
    fireEvent.click(confirmButton);
    
    // Wait for solution
    await waitFor(() => {
      expect(api.apiClient.solveWord).toHaveBeenCalled();
    });
  });
});
```

---

## End-to-End Testing

### Playwright Setup

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```

### E2E Test Example

```typescript
// e2e/complete-workflow.spec.ts
import { test, expect } from '@playwright/test';

test('complete user workflow', async ({ page }) => {
  // Navigate to app
  await page.goto('/');
  
  // Generate puzzle
  await page.fill('input[name="topic"]', 'Science');
  await page.click('button:has-text("Generate Puzzle")');
  
  // Wait for puzzle
  await page.waitForSelector('[data-testid="grid-container"]', {
    timeout: 90000
  });
  
  // Solve manually
  await page.click('[data-testid="cell-0-0"]');
  await page.keyboard.type('S');
  
  // Use AI assistance
  await page.click('[data-testid="clue-1-across"]');
  await page.click('button:has-text("Solve Word")');
  await page.click('button:has-text("Confirm")');
  
  // Verify solution
  await expect(page.locator('[data-testid="cell-0-0"]')).toHaveValue('S');
});
```

---

## Running Tests

### Backend Tests

```bash
# Run all tests
cd backend
python -m pytest

# Run with coverage
python -m pytest --cov=backend --cov-report=html

# Run specific test file
python -m pytest tests/domain/test_grid.py

# Run specific test
python -m pytest tests/domain/test_grid.py::test_grid_initialization

# Run with verbose output
python -m pytest -v

# Run integration tests only
python -m pytest -m integration

# Run in parallel
python -m pytest -n auto
```

### Frontend Tests

```bash
# Run all tests
cd frontend
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm test -- --watch

# Run specific test file
npm test -- AIAssistancePanel.test.tsx

# Run with UI
npm run test:ui
```

### E2E Tests

```bash
# Install Playwright
cd frontend
npm install -D @playwright/test
npx playwright install

# Run E2E tests (requires servers running)
npx playwright test

# Run specific test
npx playwright test e2e/ai-assistance.spec.ts

# Run in headed mode
npx playwright test --headed

# Run in debug mode
npx playwright test --debug

# Generate test report
npx playwright show-report
```

---

## Writing Tests

### Test Naming Conventions

```python
# Backend: test_<what>_<condition>_<expected>
def test_grid_initialization_with_size_8_creates_64_cells():
    pass

def test_planner_with_invalid_topic_raises_value_error():
    pass
```

```typescript
// Frontend: should <expected> when <condition>
it('should disable button when no clue is selected', () => {});

it('should call onSolveWord when button is clicked', () => {});
```

### Test Structure (AAA Pattern)

```python
def test_example():
    # Arrange: Set up test data and conditions
    grid = Grid(size=8)
    
    # Act: Perform the action being tested
    grid.set_cell(0, 0, 'A')
    
    # Assert: Verify the expected outcome
    assert grid.get_cell(0, 0).value == 'A'
```

### Mocking Best Practices

```python
# Mock external dependencies, not internal logic
with patch('backend.agents.planner.LLMClient') as mock_llm:
    mock_llm.return_value.generate.return_value = {...}
    # Test code

# Use AsyncMock for async functions
with patch('backend.api.routes.puzzles.PuzzleSolver.solve_word',
           new_callable=AsyncMock) as mock_solve:
    mock_solve.return_value = ("SCIENCE", 0.95, "Solved")
    # Test code
```

### Parameterized Tests

```python
@pytest.mark.parametrize("size,expected_cells", [
    (5, 25),
    (8, 64),
    (10, 100),
])
def test_grid_cell_count(size, expected_cells):
    grid = Grid(size=size)
    assert len(grid.cells) == expected_cells
```

---

## Test Coverage

### Measuring Coverage

```bash
# Backend
cd backend
python -m pytest --cov=backend --cov-report=html
open htmlcov/index.html

# Frontend
cd frontend
npm run test:coverage
open coverage/index.html
```

### Coverage Reports

```bash
# Terminal report
python -m pytest --cov=backend --cov-report=term-missing

# HTML report
python -m pytest --cov=backend --cov-report=html

# XML report (for CI)
python -m pytest --cov=backend --cov-report=xml
```

### Coverage Goals

- **Critical paths**: 100% coverage
- **Domain logic**: ≥ 95% coverage
- **Business logic**: ≥ 90% coverage
- **UI components**: ≥ 85% coverage
- **Utilities**: ≥ 95% coverage

---

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -e ".[dev]"
      - name: Run tests
        run: |
          cd backend
          python -m pytest --cov=backend --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          file: ./frontend/coverage/coverage-final.json
```

---

## Best Practices

### General

1. **Write tests first** (TDD)
2. **Keep tests independent**
3. **Use descriptive names**
4. **Test one thing at a time**
5. **Avoid test interdependencies**
6. **Clean up after tests**
7. **Use fixtures for common setup**
8. **Mock external dependencies**
9. **Test edge cases**
10. **Keep tests maintainable**

### Backend Specific

1. **Use async/await consistently**
2. **Mock LLM calls**
3. **Test error handling**
4. **Validate API responses**
5. **Test database transactions** (when added)

### Frontend Specific

1. **Test user interactions**
2. **Use Testing Library queries**
3. **Avoid implementation details**
4. **Test accessibility**
5. **Mock API calls**

### E2E Specific

1. **Test critical user flows**
2. **Use data-testid attributes**
3. **Wait for async operations**
4. **Handle timeouts gracefully**
5. **Test across browsers**

---

## Troubleshooting

### Common Issues

**Issue**: Tests fail intermittently
- **Solution**: Add proper waits, avoid race conditions

**Issue**: Slow test execution
- **Solution**: Mock external calls, run in parallel

**Issue**: Coverage not accurate
- **Solution**: Ensure all code paths are tested

**Issue**: E2E tests timeout
- **Solution**: Increase timeouts, check server status

---

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Best Practices](https://testingjavascript.com/)

---

For more information, see:
- [Testing Checklist](./TESTING_CHECKLIST.md)
- [Performance Guide](./PERFORMANCE.md)
- [Development Guide](./DEVELOPMENT.md)
