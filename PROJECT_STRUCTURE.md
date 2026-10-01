# Project Structure

This document provides an overview of the AI-Powered Crossword Puzzle Generator project structure.

## Root Directory

```
crossword-puzzle-generator/
├── .internal/              # Internal tooling and documentation (not for public distribution)
├── .sasva/                 # SASVA AI workspace files (IDE-specific)
├── backend/                # Python backend application
├── docs/                   # Public documentation
├── frontend/               # React/TypeScript frontend application
├── LICENSE                 # Project license
├── overview.json           # Project overview metadata
├── overview_architecture.puml  # Architecture diagram (PlantUML)
├── PROJECT_STRUCTURE.md    # This file
└── README.md               # Main project README
```

## Backend Structure

```
backend/
├── agents/                 # Multi-agent system components
│   ├── clue_generator.py   # Clue generation agent
│   ├── orchestrator.py     # Multi-agent orchestrator
│   ├── planner.py          # Planning agent
│   ├── solver.py           # Puzzle solving agent
│   ├── validator.py        # Validation agent
│   └── word_generator.py   # Word generation agent
├── api/                    # FastAPI application
│   ├── main.py             # API entry point
│   ├── models.py           # Pydantic models
│   └── routes/             # API route handlers
│       ├── puzzle.py       # Puzzle generation endpoints
│       └── solve.py        # Puzzle solving endpoints
├── domain/                 # Domain models and logic
│   ├── crossword.py        # Crossword puzzle domain model
│   ├── grid.py             # Grid structure and operations
│   └── word_placement.py   # Word placement logic
├── llm/                    # LLM integration layer
│   ├── client.py           # OpenAI client wrapper
│   └── prompts.py          # Prompt templates
├── tests/                  # Backend tests
│   ├── test_agents.py      # Agent tests
│   ├── test_api.py         # API tests
│   ├── test_domain.py      # Domain logic tests
│   └── test_llm.py         # LLM integration tests
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── pyproject.toml          # Python project configuration
├── pytest.ini              # Pytest configuration
├── README.md               # Backend documentation
└── requirements.txt        # Python dependencies
```

## Frontend Structure

```
frontend/
├── e2e/                    # End-to-end tests (Playwright)
│   ├── puzzle-generation.spec.ts
│   └── puzzle-solving.spec.ts
├── public/                 # Static assets
│   └── vite.svg
├── src/                    # Source code
│   ├── api/                # API client
│   │   └── client.ts       # API client implementation
│   ├── components/         # React components
│   │   ├── examples/       # Component usage examples
│   │   │   ├── ClueList.example.tsx
│   │   │   ├── CluePanel.example.tsx
│   │   │   ├── CrosswordGrid.example.tsx
│   │   │   ├── SolvingControls.example.tsx
│   │   │   └── README.md
│   │   ├── __tests__/      # Component tests
│   │   ├── AIAssistance.tsx
│   │   ├── ClueDisplay.tsx
│   │   ├── ClueList.tsx
│   │   ├── CluePanel.tsx
│   │   ├── CrosswordGrid.tsx
│   │   ├── PuzzleGenerator.tsx
│   │   ├── SolvingControls.tsx
│   │   └── index.ts        # Component exports
│   ├── hooks/              # Custom React hooks
│   │   ├── useAPI.ts       # API integration hook
│   │   ├── useAIAssistance.ts  # AI assistance hook
│   │   └── usePuzzle.ts    # Puzzle state management hook
│   ├── types/              # TypeScript type definitions
│   │   └── index.ts        # Shared types
│   ├── utils/              # Utility functions
│   │   └── index.ts        # Helper functions
│   ├── App.css             # Application styles
│   ├── App.tsx             # Main application component
│   ├── index.css           # Global styles
│   ├── main.tsx            # Application entry point
│   └── vite-env.d.ts       # Vite type definitions
├── .eslintrc.cjs           # ESLint configuration
├── .gitignore              # Git ignore rules
├── index.html              # HTML entry point
├── package.json            # Node.js dependencies and scripts
├── postcss.config.js       # PostCSS configuration
├── README.md               # Frontend documentation
├── tailwind.config.js      # Tailwind CSS configuration
├── tsconfig.json           # TypeScript configuration
├── tsconfig.node.json      # TypeScript config for Node.js
├── vite.config.ts          # Vite configuration
└── vitest.config.ts        # Vitest configuration
```

## Documentation Structure

```
docs/
├── backend/                # Backend documentation
│   ├── architecture/       # Architecture documentation
│   │   ├── BACKEND_ARCHITECTURE.md
│   │   └── MULTI_AGENT_SYSTEM.md
│   ├── api/                # API documentation
│   │   ├── API.md
│   │   ├── API_REFERENCE_COMPLETE.md
│   │   └── PUZZLE_API_ENDPOINTS.md
│   ├── guides/             # Backend guides
│   │   ├── PERFORMANCE.md
│   │   └── TESTING.md
│   ├── deployment/         # Deployment documentation
│   │   └── DEPLOYMENT.md
│   ├── technical-deep-dive/  # Technical deep dives
│   │   ├── AI_CONCEPTS_AND_IMPLEMENTATION.md
│   │   ├── ARCHITECTURE_DEEP_DIVE.md
│   │   ├── FUTURE_ENHANCEMENTS_ROADMAP.md
│   │   ├── README_TECHNICAL_DOCS.md
│   │   └── TECHNICAL_QA_REFERENCE.md
│   └── README.md           # Backend docs index
├── frontend/               # Frontend documentation
│   ├── architecture/       # Frontend architecture
│   │   └── FRONTEND_ARCHITECTURE.md
│   ├── api/                # Frontend API documentation
│   │   └── TYPES_AND_API_CLIENT.md
│   ├── guides/             # Frontend guides
│   │   └── USER_GUIDE.md
│   └── README.md           # Frontend docs index
├── guides/                 # General guides
│   ├── CONTRIBUTING.md
│   ├── DEMO_DATA.md
│   ├── DEVELOPMENT.md
│   ├── FRONTEND.md
│   ├── QUICK_START.md
│   ├── TESTING_CHECKLIST.md
│   └── USER_GUIDE.md
└── README.md               # Documentation index
```

## Internal Tooling Structure

```
.internal/
├── development-history/    # Development phase summaries
│   ├── PHASE3_SUMMARY.md
│   ├── PHASE4_SUMMARY.md
│   ├── PHASE5_SUMMARY.md
│   └── PHASE6_ORCHESTRATION_SUMMARY.md
├── frontend/               # Frontend-specific internal docs
│   └── .internal/          # Legacy frontend phase docs
├── project-management/     # Project management documents
│   ├── ASSIGNMENT.md
│   ├── ASSIGNMENT_COMPLIANCE.md
│   ├── PROJECT_STATUS.md
│   └── (other project docs)
├── scripts/                # Verification and testing scripts
│   ├── backend/            # Backend scripts
│   │   ├── verification/   # 17 verification scripts
│   │   │   ├── verify_setup.py
│   │   │   ├── verify_api_setup.py
│   │   │   ├── verify_domain.py
│   │   │   ├── verify_llm.py
│   │   │   ├── verify_orchestration.py
│   │   │   └── (12 more scripts)
│   │   ├── testing/        # 5 testing scripts
│   │   │   ├── demo_data.py
│   │   │   ├── test_api_manual.py
│   │   │   └── (3 more scripts)
│   │   └── README.md       # Backend scripts documentation
│   ├── frontend/           # Frontend scripts
│   │   ├── verify_setup.js
│   │   ├── verify_types_and_api.js
│   │   ├── verify_puzzle_flow.cjs
│   │   ├── verify_clue_components.cjs
│   │   ├── verify_grid_components.cjs
│   │   └── README.md       # Frontend scripts documentation
│   ├── diagnostics/        # Diagnostic scripts
│   │   ├── diagnose_and_restart.sh
│   │   ├── diagnose_issue.sh
│   │   └── verify_project.sh
│   └── testing/            # General testing scripts
│       ├── run_all_tests.sh
│       ├── run_tests.sh
│       └── test_integration.sh
├── troubleshooting/        # Issue resolution logs
│   ├── ISSUE_RESOLUTION_SUMMARY.md
│   └── (15 more troubleshooting docs)
└── README.md               # Internal tooling index
```

## Key Files

### Root Level
- **README.md**: Main project documentation and getting started guide
- **LICENSE**: MIT License
- **PROJECT_STRUCTURE.md**: This file - project structure overview
- **overview.json**: Project metadata and configuration
- **overview_architecture.puml**: PlantUML architecture diagram

### Backend
- **backend/api/main.py**: FastAPI application entry point
- **backend/agents/orchestrator.py**: Multi-agent orchestration system
- **backend/domain/crossword.py**: Core crossword puzzle domain model
- **backend/llm/client.py**: OpenAI LLM integration
- **backend/requirements.txt**: Python dependencies
- **backend/pyproject.toml**: Python project configuration

### Frontend
- **frontend/src/main.tsx**: React application entry point
- **frontend/src/App.tsx**: Main application component
- **frontend/src/api/client.ts**: Backend API client
- **frontend/package.json**: Node.js dependencies and scripts
- **frontend/vite.config.ts**: Vite build configuration

### Documentation
- **docs/README.md**: Documentation index and navigation
- **docs/backend/README.md**: Backend documentation index
- **docs/frontend/README.md**: Frontend documentation index
- **docs/guides/QUICK_START.md**: Quick start guide
- **docs/guides/DEVELOPMENT.md**: Development guide

### Internal Tooling
- **.internal/scripts/backend/README.md**: Backend scripts documentation
- **.internal/scripts/frontend/README.md**: Frontend scripts documentation
- **.internal/project-management/PROJECT_STATUS.md**: Current project status

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **LLM Integration**: OpenAI API (GPT-4)
- **Testing**: pytest
- **Code Quality**: pylint, black, mypy

### Frontend
- **Language**: TypeScript
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Testing**: Vitest, Playwright
- **Code Quality**: ESLint, Prettier

### Infrastructure
- **Version Control**: Git
- **Package Management**: pip (backend), npm (frontend)
- **Environment**: .env files for configuration

## Development Workflow

1. **Backend Development**: Located in `backend/` directory
   - Run tests: `pytest`
   - Start server: `uvicorn api.main:app --reload`
   - Verify setup: `.internal/scripts/backend/verification/verify_setup.py`

2. **Frontend Development**: Located in `frontend/` directory
   - Run tests: `npm test`
   - Start dev server: `npm run dev`
   - Verify setup: `.internal/scripts/frontend/verify_setup.js`

3. **Documentation**: Located in `docs/` directory
   - Backend docs: `docs/backend/`
   - Frontend docs: `docs/frontend/`
   - General guides: `docs/guides/`

4. **Internal Tooling**: Located in `.internal/` directory
   - Verification scripts: `.internal/scripts/`
   - Project management: `.internal/project-management/`
   - Troubleshooting: `.internal/troubleshooting/`

## File Statistics

- **Total Files**: ~7,400+ (excluding node_modules, build artifacts)
- **Backend Python Files**: ~50 files
- **Frontend TypeScript/React Files**: ~60 files
- **Documentation Files**: ~30 public docs + ~45 internal docs
- **Test Files**: ~40 files (backend + frontend)
- **Scripts**: ~38 verification and testing scripts

## Notes

- The `.internal/` directory contains development history, project management documents, and internal tooling that is not intended for public distribution
- The `.sasva/` directory contains IDE-specific workspace files and should be ignored in version control
- All public-facing documentation is in the `docs/` directory
- Backend and frontend are completely separate applications that communicate via REST API
- The project follows a clean architecture pattern with clear separation of concerns

## Getting Started

For quick start instructions, see:
- **Quick Start Guide**: `docs/guides/QUICK_START.md`
- **Development Guide**: `docs/guides/DEVELOPMENT.md`
- **Backend README**: `backend/README.md`
- **Frontend README**: `frontend/README.md`

For detailed documentation, see:
- **Documentation Index**: `docs/README.md`
- **Backend Documentation**: `docs/backend/README.md`
- **Frontend Documentation**: `docs/frontend/README.md`
