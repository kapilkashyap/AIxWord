# AIxWord Project Structure

Clean, organized project hierarchy for demo and development.

```
AIxWord/
│
├── README.md                    # Main project documentation
├── LICENSE                      # MIT License
├── PROJECT_STRUCTURE.md         # This file
├── DOCUMENTATION_REORGANIZATION_SUMMARY.md
│
├── backend/                     # Python FastAPI Backend
│   ├── agents/                  # Multi-Agent System
│   │   ├── __init__.py
│   │   ├── orchestrator.py      # Main orchestrator
│   │   ├── planner.py           # PlannerAgent
│   │   ├── planner_prompts.py   # Planner prompts
│   │   ├── word_generator.py    # WordGeneratorAgent
│   │   ├── word_generator_prompts.py
│   │   ├── workflow.py          # LangGraph workflow
│   │   └── state.py             # Workflow state management
│   │
│   ├── api/                     # FastAPI Routes & Schemas
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── puzzles.py       # Puzzle endpoints
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── puzzle.py        # Puzzle schemas
│   │   │   └── solve.py         # Solve schemas
│   │   └── services/
│   │       ├── __init__.py
│   │       └── solver.py        # Solver service
│   │
│   ├── domain/                  # Core Domain Logic
│   │   ├── __init__.py
│   │   ├── models.py            # Domain models
│   │   ├── grid.py              # Grid engine
│   │   ├── word.py              # Word placement
│   │   ├── pattern.py           # Pattern matching
│   │   └── validator.py         # Validation logic
│   │
│   ├── llm/                     # OpenAI Integration
│   │   ├── __init__.py
│   │   ├── client.py            # OpenAI client
│   │   └── prompts.py           # Prompt templates
│   │
│   ├── tests/                   # Backend Test Suite (550 tests)
│   │   ├── agents/              # Agent tests
│   │   ├── api/                 # API tests
│   │   ├── domain/              # Domain logic tests
│   │   └── llm/                 # LLM integration tests
│   │
│   ├── config.py                # Configuration management
│   ├── main.py                  # FastAPI application entry
│   ├── run_server.py            # Server runner
│   ├── pyproject.toml           # Python project config
│   ├── pytest.ini               # Pytest configuration
│   ├── mypy.ini                 # Type checking config
│   ├── Makefile                 # Build automation
│   ├── requirements.txt         # Production dependencies
│   ├── requirements-dev.txt     # Development dependencies
│   └── README.md                # Backend documentation
│
├── frontend/                    # React TypeScript Frontend
│   ├── src/
│   │   ├── components/          # React Components
│   │   │   ├── Grid.tsx         # Crossword grid
│   │   │   ├── Cell.tsx         # Grid cell
│   │   │   ├── CluePanel.tsx    # Clue display
│   │   │   ├── ClueList.tsx     # Clue list
│   │   │   ├── PuzzleGenerator.tsx
│   │   │   ├── SolvingControls.tsx
│   │   │   └── PuzzleStats.tsx
│   │   │
│   │   ├── hooks/               # React Hooks
│   │   │   ├── usePuzzle.ts     # Puzzle state management
│   │   │   └── useSolving.ts    # Solving logic
│   │   │
│   │   ├── services/            # API Client
│   │   │   └── api.ts           # Backend API client
│   │   │
│   │   ├── types/               # TypeScript Types
│   │   │   └── puzzle.ts        # Puzzle type definitions
│   │   │
│   │   ├── App.tsx              # Main app component
│   │   ├── main.tsx             # React entry point
│   │   └── index.css            # Global styles
│   │
│   ├── tests/                   # Frontend Test Suite (287 tests)
│   ├── package.json             # Node.js dependencies
│   ├── tsconfig.json            # TypeScript config
│   ├── vite.config.ts           # Vite build config
│   ├── tailwind.config.js       # Tailwind CSS config
│   └── README.md                # Frontend documentation
│
├── docs/                        # Public Documentation (21 documents)
│   ├── README.md                # Documentation index
│   │
│   ├── architecture/            # Architecture & Design (3 docs)
│   │   ├── ARCHITECTURE_DEEP_DIVE.md
│   │   ├── AI_CONCEPTS_AND_IMPLEMENTATION.md
│   │   └── FUTURE_ENHANCEMENTS_ROADMAP.md
│   │
│   ├── api/                     # API Documentation (2 docs)
│   │   ├── API_REFERENCE.md
│   │   └── PUZZLE_API_ENDPOINTS.md
│   │
│   ├── guides/                  # User & Developer Guides (11 docs)
│   │   ├── QUICK_START.md
│   │   ├── USER_GUIDE.md
│   │   ├── CONTRIBUTING.md
│   │   ├── TESTING.md
│   │   ├── DEPLOYMENT.md
│   │   ├── PROJECT_STATUS.md
│   │   ├── SERVER_MANAGEMENT.md
│   │   ├── DOCUMENTATION_INDEX.md
│   │   ├── DOCUMENTATION_CLEANUP_COMPLETE.md
│   │   ├── DOCUMENTATION_REORGANIZATION.md
│   │   └── PROJECT_CLEANUP_SUMMARY.md
│   │
│   └── technical-deep-dive/     # Technical Deep Dive (5 docs)
│       ├── ARCHITECTURE_DEEP_DIVE.md
│       ├── AI_CONCEPTS_AND_IMPLEMENTATION.md
│       ├── TECHNICAL_QA_REFERENCE.md
│       ├── FUTURE_ENHANCEMENTS_ROADMAP.md
│       └── README_TECHNICAL_DOCS.md
│
└── scripts/                     # Essential Utility Scripts (6 scripts)
    ├── setup/                   # Installation & Setup (3 scripts)
    │   ├── setup_project.sh     # Main project setup
    │   ├── setup.bat            # Windows backend setup
    │   └── install_certifi_and_restart.sh
    │
    └── cleanup/                 # Cleanup Scripts (3 scripts)
        ├── deep-clean.sh        # Deep project cleanup
        ├── restart-servers.sh   # Restart both servers
        └── stop-servers.sh      # Stop all servers
```

## 📊 Statistics

- **Total Lines of Code:** ~15,000
- **Backend Files:** 50+ Python modules
- **Frontend Files:** 30+ TypeScript/React components
- **Tests:** 837 (550 backend + 287 frontend)
- **Public Documentation:** 21 markdown files
- **Essential Scripts:** 6 utility scripts

## 🎯 Key Directories

### Source Code
- `backend/` - All backend Python code (agents, API, domain, LLM)
- `frontend/` - All frontend React/TypeScript code

### Public Documentation
- `docs/` - Professional documentation organized by category (shareable)
- `README.md` - Main project overview

### Utilities
- `scripts/` - Essential setup and cleanup scripts

### Configuration
- Root level - Only essential files (README, LICENSE, this file)
- `backend/` - Python configs (pyproject.toml, pytest.ini, mypy.ini)
- `frontend/` - Node configs (package.json, tsconfig.json, vite.config.ts)

## 🧹 Clean Structure Benefits

✅ **Demo-Ready** - Professional, organized hierarchy  
✅ **Public/Private Separation** - Clear distinction between shareable and internal docs  
✅ **Easy Navigation** - Logical categorization  
✅ **Clear Separation** - Source vs docs vs tools  
✅ **Scalable** - Room for growth  
✅ **Maintainable** - Easy to find and update files  

## 📝 File Naming Conventions

- **Source Code:** `snake_case.py`, `PascalCase.tsx`
- **Documentation:** `SCREAMING_SNAKE_CASE.md`
- **Scripts:** `kebab-case.sh`
- **Config Files:** Standard names (`pyproject.toml`, `package.json`)

## 🔒 What to Share Publicly

**✅ Safe to share:**
- Everything in `/docs` (21 professional documents)
- Root `README.md`, `LICENSE`, `PROJECT_STRUCTURE.md`
- `/backend` and `/frontend` source code
- `/scripts` essential utilities

**🔒 Keep private:**
- `.env` files and API keys
- Generated build artifacts
- Cache and temporary files

---

**Last Updated:** 2026-09-29  
**Project Version:** 1.0  
**Status:** Production-Ready for Demo
