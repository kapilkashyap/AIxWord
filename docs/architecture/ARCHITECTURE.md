# AIxWord - System Architecture Documentation

**Version:** 1.0.0  
**Last Updated:** September 28, 2026  
**Status:** Production Ready

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture Principles](#architecture-principles)
4. [Technology Stack](#technology-stack)
5. [System Architecture](#system-architecture)
6. [Backend Architecture](#backend-architecture)
7. [Frontend Architecture](#frontend-architecture)
8. [Multi-Agent System](#multi-agent-system)
9. [Data Flow](#data-flow)
10. [API Design](#api-design)
11. [Domain Model](#domain-model)
12. [State Management](#state-management)
13. [Security Architecture](#security-architecture)
14. [Performance & Scalability](#performance--scalability)
15. [Testing Strategy](#testing-strategy)
16. [Deployment Architecture](#deployment-architecture)
17. [Future Enhancements](#future-enhancements)

---

## Executive Summary

AIxWord is an AI-powered interactive crossword puzzle application that demonstrates advanced multi-agent system design using LangGraph and OpenAI's GPT-4. The system generates topic-based crossword puzzles through coordinated AI agents and provides an intuitive web interface for puzzle solving with AI assistance.

### Key Architectural Highlights

- **Multi-Agent Architecture**: Two specialized agents (PlannerAgent + WordGeneratorAgent) orchestrated by LangGraph
- **Clean Architecture**: Clear separation of concerns across domain, application, and infrastructure layers
- **Type-Safe**: Comprehensive TypeScript frontend and Pydantic-validated Python backend
- **Test-Driven**: 693 passing tests (547 backend + 146 frontend) with 71% overall coverage
- **Modern Stack**: FastAPI + React 18 + LangGraph + OpenAI GPT-4 Turbo
- **Production-Ready**: Comprehensive error handling, logging, and monitoring capabilities

### Core Capabilities

| Capability | Description | Status |
|------------|-------------|--------|
| **Puzzle Generation** | AI-generated crossword puzzles from any topic | ✅ Implemented |
| **Interactive Solving** | Manual puzzle solving with keyboard navigation | ✅ Implemented |
| **AI Assistance** | Solve individual words or entire puzzles with AI | ✅ Implemented |
| **Hint Generation** | Get additional clues for stuck words | ✅ Implemented |
| **Solution Validation** | Validate user answers in real-time | ✅ Implemented |
| **Document-Based RAG** | Generate puzzles from uploaded documents | 🔄 Planned |
| **Variable Grid Sizes** | Support 4×4 to 20×20 grids | 🔄 Planned |

---

## System Overview

### Purpose

AIxWord serves dual purposes:
1. **Academic Assignment**: Demonstrates multi-agent AI system implementation for the Quadlift Advanced Tech Architects program
2. **Interactive Application**: Provides an engaging crossword puzzle experience with AI-powered generation and solving

### System Boundaries

```
┌──────────────────────────────────────────────────────────────┐
│                        AIxWord System                        │
│                                                              │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │   Frontend   │◄───────►│   Backend    │                 │
│  │  React SPA   │  HTTP   │   FastAPI    │                 │
│  └──────────────┘         └──────┬───────┘                 │
│                                   │                          │
│                                   ▼                          │
│                          ┌────────────────┐                 │
│                          │  Multi-Agent   │                 │
│                          │    System      │                 │
│                          │  (LangGraph)   │                 │
│                          └────────┬───────┘                 │
│                                   │                          │
└───────────────────────────────────┼──────────────────────────┘
                                    │
                                    ▼
                          ┌─────────────────┐
                          │   OpenAI API    │
                          │   GPT-4 Turbo   │
                          └─────────────────┘
```

### User Interaction Flow

```
User → Frontend UI → API Client → FastAPI Backend → Multi-Agent System → LLM
                                                                           │
User ← Frontend UI ← API Client ← FastAPI Backend ← Multi-Agent System ←──┘
```

---

## Architecture Principles

### 1. Clean Architecture

The system follows Uncle Bob's Clean Architecture principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│              (React Components, API Routes)                  │
├─────────────────────────────────────────────────────────────┤
│                   Application Layer                          │
│         (Use Cases, Orchestration, Workflows)                │
├─────────────────────────────────────────────────────────────┤
│                     Domain Layer                             │
│        (Business Logic, Domain Models, Rules)                │
├─────────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                        │
│         (LLM Client, Storage, External Services)             │
└─────────────────────────────────────────────────────────────┘
```

**Key Benefits:**
- **Independence**: Business logic independent of frameworks and external services
- **Testability**: Each layer can be tested in isolation
- **Flexibility**: Easy to swap implementations (e.g., storage, LLM provider)
- **Maintainability**: Clear boundaries make code easier to understand and modify

### 2. Domain-Driven Design (DDD)

The domain model is at the heart of the system:

**Core Domain Entities:**
- `CrosswordGrid`: The puzzle grid with cells and words
- `Cell`: Individual grid cell with position and state
- `WordPlacement`: Specification for placing a word
- `Clue`: Crossword clue with metadata
- `Direction`: Enum for word orientation (ACROSS, DOWN)

**Domain Services:**
- `WordValidator`: Validates word placements and puzzle rules
- `GridBuilder`: Constructs and manipulates grids
- `Pattern`: Represents word patterns for matching

### 3. SOLID Principles

**Single Responsibility Principle (SRP)**
- Each class has one reason to change
- `PlannerAgent`: Only responsible for strategic planning
- `WordGeneratorAgent`: Only responsible for word generation
- `PuzzleOrchestrator`: Only responsible for workflow coordination

**Open/Closed Principle (OCP)**
- Open for extension, closed for modification
- Agent system can be extended with new agents without modifying existing code
- Storage interface allows different implementations

**Liskov Substitution Principle (LSP)**
- Interfaces can be substituted with implementations
- `LLMClient` interface allows different LLM providers

**Interface Segregation Principle (ISP)**
- Clients depend only on interfaces they use
- Separate interfaces for different concerns

**Dependency Inversion Principle (DIP)**
- High-level modules don't depend on low-level modules
- Both depend on abstractions (interfaces)

### 4. Separation of Concerns

**Backend Layers:**
```
api/          → HTTP endpoints, request/response handling
agents/       → Multi-agent system, workflow orchestration
domain/       → Business logic, domain models
llm/          → LLM integration, prompt management
```

**Frontend Layers:**
```
components/   → UI components (presentational + container)
hooks/        → State management, side effects
services/     → API client, external services
types/        → TypeScript type definitions
utils/        → Pure utility functions
```

---

## Technology Stack

### Backend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Core language |
| **FastAPI** | 0.104.1 | Web framework, API endpoints |
| **LangGraph** | 0.0.26 | Multi-agent workflow orchestration |
| **LangChain** | 0.1.0 | LLM integration framework |
| **OpenAI** | 1.6.1 | GPT-4 Turbo API client |
| **Pydantic** | 2.5.2 | Data validation, settings management |
| **Uvicorn** | 0.25.0 | ASGI server |
| **Pytest** | 7.4.3 | Testing framework |

### Frontend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.2.0 | UI framework |
| **TypeScript** | 5.3.3 | Type-safe JavaScript |
| **Vite** | 5.0.8 | Build tool, dev server |
| **Tailwind CSS** | 3.3.6 | Utility-first CSS framework |
| **Axios** | 1.6.2 | HTTP client |
| **Vitest** | 1.0.4 | Unit testing framework |
| **Playwright** | 1.40.1 | E2E testing framework |

### Development Tools

| Tool | Purpose |
|------|---------|
| **ESLint** | JavaScript/TypeScript linting |
| **Prettier** | Code formatting |
| **Black** | Python code formatting |
| **MyPy** | Python static type checking |
| **Ruff** | Python linting |

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Browser                          │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    React Application                       │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │  Puzzle  │  │   Grid   │  │   Clue   │  │    AI    │  │ │
│  │  │Generator │  │Component │  │  Panel   │  │Assistance│  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │              API Client (Axios)                       │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/JSON
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    API Layer                               │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │  Puzzle  │  │  Solve   │  │   Hint   │  │Validate  │  │ │
│  │  │Endpoints │  │Endpoints │  │Endpoints │  │Endpoints │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                  Service Layer                             │ │
│  │  ┌──────────────────┐  ┌──────────────────┐              │ │
│  │  │ PuzzleService    │  │  SolverService   │              │ │
│  │  └──────────────────┘  └──────────────────┘              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Multi-Agent System (LangGraph)                │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │           PuzzleOrchestrator                          │ │ │
│  │  │  ┌────────────────┐  ┌────────────────┐             │ │ │
│  │  │  │ PlannerAgent   │  │WordGenerator   │             │ │ │
│  │  │  │                │  │    Agent       │             │ │ │
│  │  │  └────────────────┘  └────────────────┘             │ │ │
│  │  │                                                       │ │ │
│  │  │  ┌────────────────────────────────────┐             │ │ │
│  │  │  │   LangGraph Workflow (StateGraph)  │             │ │ │
│  │  │  └────────────────────────────────────┘             │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                   Domain Layer                             │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │Crossword │  │   Cell   │  │   Word   │  │Validator │  │ │
│  │  │  Grid    │  │          │  │Placement │  │          │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Infrastructure Layer                          │ │
│  │  ┌──────────────────┐  ┌──────────────────┐              │ │
│  │  │   LLM Client     │  │  Puzzle Storage  │              │ │
│  │  │  (OpenAI API)    │  │  (In-Memory)     │              │ │
│  │  └──────────────────┘  └──────────────────┘              │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ API Calls
                              ▼
                    ┌─────────────────────┐
                    │    OpenAI API       │
                    │    GPT-4 Turbo      │
                    └─────────────────────┘
```

### Component Interaction

```
┌──────────────┐
│    User      │
└──────┬───────┘
       │
       │ 1. Generate Puzzle
       ▼
┌──────────────────┐
│ PuzzleGenerator  │
│   Component      │
└──────┬───────────┘
       │
       │ 2. POST /api/puzzles/generate
       ▼
┌──────────────────┐
│  Puzzle API      │
│   Endpoint       │
└──────┬───────────┘
       │
       │ 3. generate_and_store_puzzle()
       ▼
┌──────────────────┐
│ PuzzleService    │
└──────┬───────────┘
       │
       │ 4. generate_puzzle_async()
       ▼
┌──────────────────┐
│PuzzleOrchestrator│
└──────┬───────────┘
       │
       │ 5. Execute LangGraph Workflow
       ▼
┌──────────────────────────────────┐
│   LangGraph StateGraph           │
│                                  │
│  ┌────────────┐  ┌────────────┐ │
│  │  Planner   │→ │   Word     │ │
│  │   Agent    │  │ Generator  │ │
│  └────────────┘  └────────────┘ │
│         ↑              │         │
│         └──────────────┘         │
│         (iterate until done)     │
└──────────────┬───────────────────┘
               │
               │ 6. LLM API Calls
               ▼
        ┌──────────────┐
        │  OpenAI API  │
        └──────────────┘
```

---

## Backend Architecture

### Directory Structure

```
backend/
├── agents/                 # Multi-agent system
│   ├── __init__.py
│   ├── orchestrator.py    # High-level orchestration
│   ├── planner.py         # PlannerAgent implementation
│   ├── word_generator.py  # WordGeneratorAgent implementation
│   ├── workflow.py        # LangGraph workflow definition
│   ├── state.py           # Shared state management
│   ├── planner_prompts.py # Planner LLM prompts
│   └── word_generator_prompts.py
├── api/                   # FastAPI application
│   ├── __init__.py
│   ├── main.py           # FastAPI app initialization
│   ├── puzzle.py         # Puzzle service layer
│   ├── schemas.py        # Pydantic request/response models
│   ├── models.py         # API data models
│   ├── storage.py        # In-memory storage
│   ├── dependencies.py   # Dependency injection
│   └── middleware.py     # CORS, logging, error handling
├── domain/               # Domain layer
│   ├── __init__.py
│   ├── models.py        # Core domain models
│   ├── grid.py          # CrosswordGrid implementation
│   ├── validator.py     # Word validation logic
│   ├── pattern.py       # Pattern matching
│   └── builder.py       # Grid builder utilities
├── llm/                 # LLM integration
│   ├── __init__.py
│   ├── client.py        # OpenAI client wrapper
│   └── prompts.py       # Prompt templates
├── tests/               # Test suite
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── e2e/            # End-to-end tests
├── main.py             # Application entry point
├── config.py           # Configuration management
└── requirements.txt    # Python dependencies
```

### Layer Responsibilities

#### 1. API Layer (`api/`)

**Responsibilities:**
- HTTP request/response handling
- Input validation (Pydantic schemas)
- Error handling and formatting
- CORS configuration
- Request logging

**Key Components:**
- `main.py`: FastAPI application setup, middleware, routes
- `schemas.py`: Request/response Pydantic models
- `puzzle.py`: Puzzle service layer
- `storage.py`: In-memory puzzle storage
- `dependencies.py`: Dependency injection for services

#### 2. Multi-Agent Layer (`agents/`)

**Responsibilities:**
- Workflow orchestration (LangGraph)
- Agent coordination
- State management
- LLM interaction
- Puzzle generation logic

**Key Components:**
- `orchestrator.py`: High-level puzzle generation interface
- `workflow.py`: LangGraph StateGraph definition
- `planner.py`: Strategic planning agent
- `word_generator.py`: Word generation and placement agent
- `state.py`: Shared state across workflow

#### 3. Domain Layer (`domain/`)

**Responsibilities:**
- Business logic
- Domain models and rules
- Grid manipulation
- Word validation
- Pattern matching

**Key Components:**
- `models.py`: Core domain entities (Cell, WordPlacement, Clue, Direction)
- `grid.py`: CrosswordGrid implementation
- `validator.py`: Word placement validation
- `pattern.py`: Pattern matching for word generation
- `builder.py`: Grid construction utilities

#### 4. Infrastructure Layer (`llm/`)

**Responsibilities:**
- External service integration
- LLM API calls
- Prompt management
- Response parsing

**Key Components:**
- `client.py`: OpenAI API client wrapper
- `prompts.py`: Centralized prompt templates

### Dependency Flow

```
API Layer
    ↓ depends on
Multi-Agent Layer
    ↓ depends on
Domain Layer
    ↑ uses
Infrastructure Layer
```

**Key Principle:** Dependencies point inward. Domain layer has no dependencies on outer layers.

---

## Frontend Architecture

### Directory Structure

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── __tests__/       # Component tests
│   │   ├── Grid.tsx         # Main grid component
│   │   ├── Cell.tsx         # Individual cell
│   │   ├── CluePanel.tsx    # Clue display
│   │   ├── ClueList.tsx     # List of clues
│   │   ├── ClueItem.tsx     # Individual clue
│   │   ├── PuzzleGenerator.tsx
│   │   ├── PuzzleGeneratorForm.tsx
│   │   ├── PuzzleContainer.tsx
│   │   ├── PuzzleContainerWithAI.tsx
│   │   ├── SolvingControls.tsx
│   │   ├── AIAssistancePanel.tsx
│   │   ├── HintModal.tsx
│   │   ├── ConfirmationDialog.tsx
│   │   ├── SolutionAnimation.tsx
│   │   ├── GenerationProgress.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── ErrorMessage.tsx
│   │   └── *.module.css     # Component styles
│   ├── hooks/               # Custom React hooks
│   │   ├── __tests__/      # Hook tests
│   │   ├── useAPI.ts       # API call management
│   │   ├── usePuzzle.ts    # Puzzle state
│   │   ├── useSolving.ts   # Solving state
│   │   ├── useAIAssistance.ts
│   │   └── index.ts        # Hook exports
│   ├── services/           # External services
│   │   └── api.ts          # API client
│   ├── types/              # TypeScript types
│   │   ├── puzzle.ts       # Puzzle domain types
│   │   ├── api.ts          # API types
│   │   └── aiAssistance.ts # AI assistance types
│   ├── utils/              # Utility functions
│   │   ├── grid.ts         # Grid utilities
│   │   ├── validation.ts   # Validation helpers
│   │   └── keyboard.ts     # Keyboard navigation
│   ├── test/               # Test setup
│   │   └── setup.ts
│   ├── App.tsx             # Root component
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
├── e2e/                    # E2E tests
├── public/                 # Static assets
├── index.html
├── vite.config.ts
├── vitest.config.ts
├── tailwind.config.js
└── tsconfig.json
```

### Component Architecture

#### Container/Presentational Pattern

**Container Components** (Smart Components):
- Manage state and business logic
- Handle API calls and side effects
- Pass data and callbacks to presentational components

Examples:
- `PuzzleContainer`: Orchestrates puzzle flow
- `PuzzleGenerator`: Manages generation workflow
- `PuzzleContainerWithAI`: Adds AI assistance features

**Presentational Components** (Dumb Components):
- Focus on UI rendering
- Receive data via props
- Emit events via callbacks
- No direct API calls or complex state

Examples:
- `Grid`, `Cell`: Display grid
- `CluePanel`, `ClueList`, `ClueItem`: Display clues
- `SolvingControls`, `PuzzleActions`: Action buttons
- `AIAssistancePanel`, `HintModal`: AI features

#### Component Hierarchy

```
App
└── PuzzleContainerWithAI
    ├── PuzzleGenerator
    │   ├── PuzzleGeneratorForm
    │   └── GenerationProgress
    ├── Grid
    │   └── Cell (multiple)
    ├── CluePanel
    │   ├── ClueList (Across)
    │   │   └── ClueItem (multiple)
    │   └── ClueList (Down)
    │       └── ClueItem (multiple)
    ├── SolvingControls
    ├── AIAssistancePanel
    ├── HintModal
    ├── ConfirmationDialog
    └── SolutionAnimation
```

### State Management

#### Hook-Based State Management

The application uses custom React hooks for state management:

**1. usePuzzle**
- Manages puzzle data (grid, clues, metadata)
- Handles cell updates
- Tracks selected cell
- Provides puzzle operations

**2. useAPI**
- Manages API call state (loading, data, error)
- Provides generic API call wrapper
- Handles error states

**3. useSolving**
- Manages solving progress
- Tracks user answers
- Validates solutions
- Provides solving operations

**4. useAIAssistance**
- Manages AI assistance state
- Handles solve/hint requests
- Tracks AI operations
- Provides AI assistance operations

#### State Flow

```
User Action
    ↓
Event Handler (Component)
    ↓
Hook State Update
    ↓
Component Re-render
    ↓
UI Update
```

Example:
```typescript
// User types in cell
onCellChange(row, col, value)
    ↓
usePuzzle.updateCell(row, col, value)
    ↓
setCells([...cells with updated value])
    ↓
Grid re-renders with new cell value
```

### Type System

#### Core Types

**Puzzle Types** (`types/puzzle.ts`):
```typescript
interface Cell {
  row: number;
  col: number;
  value: string | null;
  is_blocked: boolean;
  number: number | null;
}

interface Clue {
  number: number;
  direction: 'across' | 'down';
  text: string;
  answer?: string;
  start_row: number;
  start_col: number;
  length: number;
}

interface Puzzle {
  puzzle_id: string;
  topic: string;
  grid_size: number;
  cells: Cell[];
  clues_across: Clue[];
  clues_down: Clue[];
  word_count: number;
  fill_rate: number;
  difficulty: string;
  created_at: string;
  metadata: Record<string, any>;
}
```

**API Types** (`types/api.ts`):
```typescript
interface PuzzleGenerateRequest {
  topic: string;
  grid_size?: number;
  min_words?: number;
  max_words?: number;
  difficulty?: 'easy' | 'medium' | 'hard';
  max_iterations?: number;
}

interface SolveWordRequest {
  clue_number: number;
  direction: 'across' | 'down';
  use_intersections?: boolean;
}

interface HintRequest {
  clue_number: number;
  direction: 'across' | 'down';
  hint_type?: 'letter' | 'definition' | 'synonym';
}
```

---

## Multi-Agent System

### Overview

The multi-agent system is the core of AIxWord's puzzle generation capability. It uses LangGraph to orchestrate two specialized agents that work together to create crossword puzzles.

### Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              PuzzleOrchestrator                             │
│  (High-level interface for puzzle generation)              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│           LangGraph Workflow (StateGraph)                   │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│  │Initialize│ -> │ Planner  │ -> │ Executor │            │
│  │          │    │  Agent   │    │  Agent   │            │
│  └──────────┘    └──────────┘    └────┬─────┘            │
│                        ▲                │                  │
│                        │                ▼                  │
│                        │         ┌──────────┐             │
│                        │         │ Should   │             │
│                        │         │Continue? │             │
│                        │         └────┬─────┘             │
│                        │              │                    │
│                        │      ┌───────┴────────┐          │
│                        │      │                │          │
│                        └──────┤ Continue       │ End      │
│                               │                │          │
│                               └────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### Workflow Phases

#### 1. Initialize Phase

**Purpose:** Set up initial state for puzzle generation

**Actions:**
- Create empty grid of specified size
- Initialize requirements (topic, min/max words, difficulty)
- Set iteration counter to 0
- Set status to "initializing"

**Output:** Initial AgentState with empty grid

#### 2. Planning Phase (PlannerAgent)

**Purpose:** Strategically plan word placements

**Responsibilities:**
- Analyze current grid state
- Generate word candidates based on topic
- Create placement plan (ordered list of positions)
- Decide when to stop (requirements met or max iterations)

**LLM Interaction:**
```python
# Planner prompt structure
system_prompt = """
You are a strategic planner for crossword puzzle generation.
Analyze the current grid and create a plan for placing words.
"""

user_prompt = f"""
Topic: {topic}
Grid Size: {grid_size}x{grid_size}
Current Words: {placed_words}
Fill Rate: {fill_rate}
Requirements: {min_words}-{max_words} words

Generate word candidates and create a placement plan.
"""
```

**Output:**
- Action: "ADD_WORD" or "STOP"
- Word candidates with metadata
- Placement plan (ordered positions)
- Reasoning for decisions

#### 3. Execution Phase (WordGeneratorAgent)

**Purpose:** Execute placement plan by generating and placing words

**Responsibilities:**
- Extract patterns from grid positions
- Generate words that fit patterns using LLM
- Validate word placements
- Place words on grid
- Handle placement failures

**LLM Interaction:**
```python
# Word generator prompt structure
system_prompt = """
You are a word generator for crossword puzzles.
Generate words that fit specific patterns and relate to the topic.
"""

user_prompt = f"""
Topic: {topic}
Pattern: {pattern}  # e.g., "A__LE" for 5-letter word
Direction: {direction}
Intersecting Words: {intersections}

Generate a word that fits this pattern.
"""
```

**Output:**
- Generated word with clue
- Confidence score
- Reasoning
- Alternative suggestions

#### 4. Decision Phase (should_continue)

**Purpose:** Determine whether to continue or end workflow

**Decision Logic:**
```python
def should_continue(state: AgentState) -> str:
    # Check if requirements are met
    if state.word_count >= state.requirements.min_words:
        if state.status == "completed":
            return "end"
    
    # Check if max iterations reached
    if state.iteration >= state.requirements.max_iterations:
        return "end"
    
    # Check if planner decided to stop
    if state.status == "stopped":
        return "end"
    
    # Continue planning and execution
    return "continue"
```

**Outcomes:**
- "continue": Loop back to planning phase
- "end": Finish workflow and return result

### Agent State

The agents share state through the `AgentState` class:

```python
class AgentState(TypedDict):
    # Requirements
    requirements: PuzzleRequirements
    
    # Current grid state
    grid: Optional[dict]  # Serialized CrosswordGrid
    
    # Workflow state
    iteration: int
    status: str  # "initializing", "planning", "executing", "completed", "stopped"
    
    # Planning state
    word_candidates: list[WordCandidate]
    placement_plan: list[PlacementPlan]
    
    # Execution state
    placed_words: list[str]
    failed_placements: list[dict]
    
    # Metadata
    metadata: dict
```

### Agent Communication

Agents communicate through shared state updates:

```
PlannerAgent
    ↓ updates state
    - word_candidates
    - placement_plan
    - status
    ↓
WordGeneratorAgent
    ↓ reads state
    - placement_plan
    ↓ updates state
    - grid (with new words)
    - placed_words
    - failed_placements
    ↓
PlannerAgent (next iteration)
    ↓ reads state
    - grid (current state)
    - placed_words
    - failed_placements
```

### Error Handling

**Graceful Degradation:**
- If LLM fails, retry with simplified prompt
- If word placement fails, try alternative words
- If max retries exceeded, continue with partial result
- Always return best-effort puzzle

**Error Recovery:**
```python
try:
    word_result = await generate_word(pattern, topic)
except LLMError:
    # Retry with simpler prompt
    word_result = await generate_word_simple(pattern)
except Exception:
    # Skip this placement, continue with next
    return state
```

---

## Data Flow

### Puzzle Generation Flow

```
1. User submits generation request
   ↓
2. Frontend sends POST /api/puzzles/generate
   ↓
3. API validates request (Pydantic schema)
   ↓
4. PuzzleService.generate_and_store_puzzle()
   ↓
5. PuzzleOrchestrator.generate_puzzle_async()
   ↓
6. LangGraph workflow executes
   ├─ Initialize: Create empty grid
   ├─ Loop:
   │  ├─ Planner: Generate word candidates
   │  ├─ Executor: Place words on grid
   │  └─ Decision: Continue or end?
   └─ End: Return final grid
   ↓
7. Convert grid to StoredPuzzle
   ↓
8. Save to PuzzleStore
   ↓
9. Return PuzzleResponse to frontend
   ↓
10. Frontend displays puzzle
```

### Puzzle Solving Flow

```
1. User clicks "Solve with AI"
   ↓
2. Frontend sends POST /api/puzzles/{id}/solve
   ↓
3. API retrieves puzzle from storage
   ↓
4. SolverService.solve_puzzle()
   ├─ Extract all clues
   ├─ For each clue:
   │  ├─ Get pattern from grid
   │  ├─ Call LLM to solve
   │  └─ Validate answer
   └─ Return complete solution
   ↓
5. Return SolveResponse with answers
   ↓
6. Frontend animates solution
```

### Word Hint Flow

```
1. User requests hint for word
   ↓
2. Frontend sends POST /api/puzzles/{id}/hint
   ↓
3. API retrieves puzzle and clue
   ↓
4. SolverService.get_hint()
   ├─ Get current clue
   ├─ Get pattern (with user's letters)
   ├─ Call LLM for hint
   └─ Format hint response
   ↓
5. Return HintResponse
   ↓
6. Frontend displays hint modal
```

---

## API Design

### RESTful Principles

The API follows REST conventions:

- **Resources**: Puzzles are the primary resource
- **HTTP Methods**: GET (retrieve), POST (create/action), DELETE (remove)
- **Status Codes**: 200 (success), 201 (created), 400 (bad request), 404 (not found), 500 (server error)
- **JSON Format**: All requests and responses use JSON

### Endpoint Structure

```
/api/
├── /health              # Health check
├── /puzzles/
│   ├── GET /           # List all puzzles
│   ├── POST /generate  # Generate new puzzle
│   ├── GET /{id}       # Get puzzle by ID
│   ├── DELETE /{id}    # Delete puzzle
│   ├── POST /{id}/solve        # Solve entire puzzle
│   ├── POST /{id}/solve-word   # Solve specific word
│   ├── POST /{id}/hint         # Get hint
│   └── POST /{id}/validate     # Validate solution
```

### Request/Response Patterns

**Standard Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "metadata": { ... }
}
```

**Standard Error Response:**
```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": { ... }
}
```

### API Versioning

Current version: v1 (implicit in `/api/` prefix)

Future versions will use explicit versioning:
- `/api/v2/puzzles/`

---

## Domain Model

### Core Entities

#### 1. Cell

Represents a single cell in the crossword grid.

```python
@dataclass
class Cell:
    row: int              # Row position (0-indexed)
    col: int              # Column position (0-indexed)
    value: Optional[str]  # Letter (A-Z) or None
    is_blocked: bool      # Black square?
    number: Optional[int] # Clue number if word starts here
```

**Invariants:**
- `value` must be single uppercase letter or None
- `row` and `col` must be non-negative
- `number` must be positive if set

#### 2. Direction

Enum for word orientation.

```python
class Direction(str, Enum):
    ACROSS = "across"  # Horizontal (left to right)
    DOWN = "down"      # Vertical (top to bottom)
```

#### 3. WordPlacement

Specification for placing a word on the grid.

```python
@dataclass
class WordPlacement:
    word: str           # Word to place (uppercase)
    start_row: int      # Starting row
    start_col: int      # Starting column
    direction: Direction # ACROSS or DOWN
    clue: str           # Clue text
    number: int         # Clue number
```

**Invariants:**
- `word` must be non-empty, uppercase letters only
- `start_row` and `start_col` must be non-negative
- `number` must be positive
- `clue` must be non-empty

#### 4. Clue

Crossword clue with metadata.

```python
@dataclass
class Clue:
    number: int         # Clue number
    direction: Direction # ACROSS or DOWN
    text: str           # Clue text
    answer: str         # Answer word
    start_row: int      # Starting row
    start_col: int      # Starting column
    length: int         # Answer length
```

#### 5. CrosswordGrid

The main puzzle grid.

```python
class CrosswordGrid:
    size: int                    # Grid size (NxN)
    cells: list[list[Cell]]      # 2D array of cells
    words: list[WordPlacement]   # Placed words
    
    # Methods
    def get_cell(row, col) -> Cell
    def set_cell(row, col, value)
    def can_place_word(placement) -> bool
    def place_word(placement) -> bool
    def get_fill_rate() -> float
    def to_dict() -> dict
```

### Domain Rules

**Word Placement Rules:**
1. Words must fit within grid boundaries
2. Words must be at least 2 letters long
3. Words can only intersect at matching letters
4. No adjacent parallel words (must have black square between)
5. Grid must be connected (no isolated sections)

**Grid Validation Rules:**
1. All cells must be within bounds
2. Cell values must be uppercase letters or None
3. Blocked cells cannot have values
4. Numbered cells must start at least one word

---

## State Management

### Backend State

**In-Memory Storage:**
- Puzzles stored in `PuzzleStore` (dictionary)
- No persistence between server restarts
- Thread-safe operations

**State Lifecycle:**
```
Generate → Store → Retrieve → Solve → Validate → Delete
```

### Frontend State

**Component State:**
- Local state with `useState`
- Derived state with `useMemo`
- Side effects with `useEffect`

**Global State:**
- Shared via custom hooks
- No global state library (Redux, MobX)
- Context API for theme/config (future)

**State Synchronization:**
- Optimistic updates for user input
- Server as source of truth
- Periodic validation against server

---

## Security Architecture

### Current Security Measures

**Input Validation:**
- Pydantic schemas validate all API inputs
- TypeScript types validate frontend data
- Sanitization of user-provided text

**CORS Configuration:**
- Configured allowed origins
- Credentials support disabled
- Preflight request handling

**Error Handling:**
- No sensitive information in error messages
- Generic errors for production
- Detailed errors in development

### Future Security Enhancements

**Authentication:**
- API key authentication
- JWT tokens for user sessions
- OAuth2 integration

**Rate Limiting:**
- Per-IP rate limits
- Per-user rate limits
- Puzzle generation throttling

**Data Protection:**
- HTTPS in production
- Input sanitization
- SQL injection prevention (when DB added)

---

## Performance & Scalability

### Current Performance

**Puzzle Generation:**
- Average time: 30-60 seconds
- Depends on: grid size, word count, LLM response time
- Async processing prevents blocking

**API Response Times:**
- GET puzzle: < 50ms
- Solve word: 2-5 seconds
- Solve puzzle: 10-30 seconds

### Optimization Strategies

**Backend:**
- Async/await throughout
- Connection pooling for LLM API
- Caching of common patterns
- Batch LLM requests where possible

**Frontend:**
- Code splitting with Vite
- Lazy loading of components
- Memoization of expensive computations
- Virtual scrolling for large grids (future)

### Scalability Considerations

**Horizontal Scaling:**
- Stateless API design
- Shared storage (Redis, PostgreSQL)
- Load balancer distribution

**Vertical Scaling:**
- Increase server resources
- Optimize LLM calls
- Cache frequently accessed data

---

## Testing Strategy

### Test Pyramid

```
        ┌─────────┐
        │   E2E   │  (10%)
        │  Tests  │
        └─────────┘
      ┌─────────────┐
      │ Integration │  (20%)
      │    Tests    │
      └─────────────┘
    ┌─────────────────┐
    │   Unit Tests    │  (70%)
    │                 │
    └─────────────────┘
```

### Backend Testing

**Unit Tests (547 tests):**
- Domain models and logic
- Agent behavior
- Validators and utilities
- Coverage: 75%

**Integration Tests:**
- API endpoints
- Workflow execution
- LLM integration (mocked)
- Coverage: 65%

**E2E Tests:**
- Full puzzle generation flow
- Solve operations
- Error scenarios

### Frontend Testing

**Component Tests (146 tests):**
- Component rendering
- User interactions
- Props validation
- Coverage: 68%

**Hook Tests:**
- State management
- Side effects
- API integration (mocked)

**E2E Tests (Playwright):**
- Puzzle generation flow
- Manual solving
- AI assistance features

### Test Execution

```bash
# Backend tests
cd backend
pytest                    # All tests
pytest tests/unit/       # Unit tests only
pytest --cov             # With coverage

# Frontend tests
cd frontend
npm test                 # Unit tests
npm run test:e2e        # E2E tests
npm run test:coverage   # With coverage
```

---

## Deployment Architecture

### Development Environment

```
┌─────────────────┐         ┌─────────────────┐
│   Frontend      │         │    Backend      │
│   Vite Dev      │◄───────►│   Uvicorn       │
│   localhost:5173│  HTTP   │   localhost:8000│
└─────────────────┘         └─────────────────┘
```

**Setup:**
```bash
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

### Production Deployment (Future)

```
┌─────────────┐
│   Nginx     │  (Reverse Proxy, Static Files)
│   :80/:443  │
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│  Frontend   │   │   Backend   │
│   (Static)  │   │  (Gunicorn) │
└─────────────┘   └─────────────┘
                        │
                        ▼
                  ┌─────────────┐
                  │  PostgreSQL │
                  │   Database  │
                  └─────────────┘
```

**Deployment Steps:**
1. Build frontend: `npm run build`
2. Configure Nginx for static files and API proxy
3. Run backend with Gunicorn: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
4. Set environment variables (API keys, database URL)
5. Configure SSL certificates
6. Set up monitoring and logging

---

## Future Enhancements

### Phase 2: RAG Integration

**Document Upload:**
- Upload PDF, TXT, DOCX files
- Extract text content
- Chunk and embed documents
- Store in vector database (Pinecone, Weaviate)

**RAG-Based Generation:**
- Query relevant document chunks
- Use as context for word generation
- Generate clues from document content

### Phase 3: Advanced Features

**Variable Grid Sizes:**
- Support 4×4 to 20×20 grids
- Adaptive difficulty based on size
- Optimized algorithms for large grids

**Difficulty Levels:**
- Easy: Simple words, direct clues
- Medium: Moderate vocabulary, wordplay
- Hard: Advanced vocabulary, cryptic clues

**Puzzle Templates:**
- Themed puzzles (holidays, events)
- Custom grid patterns
- Symmetric designs

### Phase 4: User Features

**User Accounts:**
- Save puzzles
- Track progress
- Leaderboards

**Social Features:**
- Share puzzles
- Collaborative solving
- Comments and ratings

**Puzzle Editor:**
- Manual puzzle creation
- Grid designer
- Clue editor

### Phase 5: Performance

**Caching:**
- Redis for puzzle cache
- LLM response cache
- Pattern matching cache

**Database:**
- PostgreSQL for persistence
- Puzzle history
- User data

**Monitoring:**
- Application metrics
- Error tracking (Sentry)
- Performance monitoring (New Relic)

---

## Conclusion

AIxWord demonstrates a well-architected, production-ready application that combines modern web technologies with advanced AI capabilities. The clean architecture, comprehensive testing, and thoughtful design decisions create a solid foundation for future enhancements while maintaining code quality and developer experience.

### Key Takeaways

1. **Multi-Agent Design**: LangGraph provides a powerful framework for coordinating AI agents
2. **Clean Architecture**: Clear separation of concerns enables maintainability and testability
3. **Type Safety**: TypeScript and Pydantic ensure data integrity across the stack
4. **Test Coverage**: Comprehensive testing provides confidence in code quality
5. **Extensibility**: Modular design allows easy addition of new features

### Resources

- **Source Code**: [GitHub Repository]
- **API Documentation**: http://localhost:8000/docs
- **User Guide**: [USER_GUIDE.md](../USER_GUIDE.md)
- **Testing Guide**: [TESTING.md](../TESTING.md)
- **Deployment Guide**: [DEPLOYMENT.md](../DEPLOYMENT.md)

---

**Document Version:** 1.0.0  
**Last Updated:** September 28, 2026  
**Maintained By:** AIxWord Development Team
