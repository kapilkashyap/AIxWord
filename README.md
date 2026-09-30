# AIxWord - Multi-Agent Crossword Puzzle Generator

An AI-powered interactive crossword puzzle application demonstrating advanced multi-agent orchestration using LangGraph and OpenAI.

## 🎯 Overview

AIxWord is a proof-of-concept application that showcases:
- **Multi-agent AI system** with strategic planning and execution agents
- **LangGraph workflow orchestration** for iterative puzzle generation
- **Interactive web interface** for puzzle solving with AI assistance
- **Cost-optimized AI** using gpt-4o-mini (94% cheaper than gpt-4o)

## ✨ Features

- **Topic-based puzzle generation** - Generate 8×8 crossword puzzles on any topic
- **Manual solving** - Interactive grid with keyboard navigation
- **AI assistance** - Get hints, solve individual words, or auto-solve entire puzzles
- **Real-time progress tracking** - See your completion status as you solve
- **High-quality clues** - AI-generated crossword-style clues

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │  ← Interactive UI with grid, clues, controls
└────────┬────────┘
         │
    ┌────▼────────────────────────────────┐
    │      FastAPI Backend                │
    │  ┌──────────────────────────────┐   │
    │  │   Multi-Agent Orchestration  │   │
    │  │                              │   │
    │  │  ┌──────────┐  ┌──────────┐ │   │
    │  │  │ Planner  │→ │   Word   │ │   │
    │  │  │  Agent   │← │Generator │ │   │
    │  │  └──────────┘  └──────────┘ │   │
    │  │         LangGraph            │   │
    │  └──────────────────────────────┘   │
    │              ↓                       │
    │      ┌──────────────┐               │
    │      │  OpenAI API  │               │
    │      │ (gpt-4o-mini)│               │
    │      └──────────────┘               │
    └─────────────────────────────────────┘
```

### Multi-Agent System

**PlannerAgent** (Strategic Planning)
- Observes current grid state
- Decides next word placement
- Manages constraints and priorities

**WordGeneratorAgent** (Execution)
- Generates word candidates matching patterns
- Creates crossword-quality clues
- Validates against constraints

**LangGraph Workflow**
- Orchestrates agent communication
- Manages state transitions
- Handles iterative refinement

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd AIxWord

# Run setup script
./scripts/setup/setup_project.sh

# Or manually:
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"

# Frontend
cd ../frontend
npm install
```

### Configuration

Create `backend/.env`:
```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access:** http://localhost:5173

## 📖 Documentation

### For Users
- [Quick Start Guide](docs/guides/QUICK_START.md) - Get started in 5 minutes
- [User Guide](docs/guides/USER_GUIDE.md) - Complete feature walkthrough

### For Developers
- [Architecture Deep Dive](docs/interview-prep/ARCHITECTURE_DEEP_DIVE.md) - Multi-agent system design
- [AI Concepts & Implementation](docs/interview-prep/AI_CONCEPTS_AND_IMPLEMENTATION.md) - Prompt engineering, LangGraph
- [API Reference](docs/api/API_REFERENCE_COMPLETE.md) - Complete API documentation
- [Testing Guide](docs/guides/TESTING.md) - Running tests and verification

### For Interviews
- [Interview Q&A Guide](docs/interview-prep/INTERVIEW_QA_GUIDE.md) - 17 detailed technical questions
- [Future Enhancements Roadmap](docs/interview-prep/FUTURE_ENHANCEMENTS_ROADMAP.md) - RAG, persistence, scaling

### Troubleshooting
- [Issue Resolution Summary](docs/troubleshooting/ISSUE_RESOLUTION_SUMMARY.md) - Common issues and fixes
- [All Troubleshooting Docs](docs/troubleshooting/) - Detailed fix documentation

## 🛠️ Tech Stack

**Backend:**
- Python 3.9+
- FastAPI (async web framework)
- LangGraph (multi-agent orchestration)
- OpenAI API (gpt-4o-mini)
- Pydantic (data validation)

**Frontend:**
- React 18
- TypeScript
- Vite (build tool)
- Tailwind CSS

## 📊 Project Statistics

- **Lines of Code:** ~15,000
- **Test Coverage:** 95%+ on core domain logic
- **Tests:** 837 total (550 backend + 287 frontend)
- **Cost per Puzzle:** ~$0.0003 (gpt-4o-mini)
- **Generation Time:** 60-90 seconds
- **Success Rate:** 95%+

## 🎯 Key Achievements

✅ Multi-agent system with iterative refinement  
✅ LangGraph state machine orchestration  
✅ Structured JSON outputs via prompt engineering  
✅ Dynamic recursion limit scaling  
✅ Grid constraint validation  
✅ Cost optimization (94% savings with gpt-4o-mini)  
✅ Comprehensive test suite  
✅ Production-ready error handling

## 🔮 Future Enhancements

- **RAG Integration** - Upload documents, generate puzzles from content
- **Database Persistence** - PostgreSQL for puzzle storage
- **Multi-layer Caching** - Redis for 70% cost reduction
- **Async Processing** - Celery for background generation
- **Larger Grids** - 15×15 newspaper-style puzzles
- **Difficulty Levels** - Easy, medium, hard clue generation

See [Future Enhancements Roadmap](docs/interview-prep/FUTURE_ENHANCEMENTS_ROADMAP.md) for details.

## 📁 Project Structure

```
AIxWord/
├── backend/              # Python FastAPI backend
│   ├── agents/          # Multi-agent system (Planner, WordGenerator)
│   ├── api/             # FastAPI routes and schemas
│   ├── domain/          # Core domain logic (Grid, Word, Validator)
│   ├── llm/             # OpenAI client and prompts
│   └── tests/           # Backend test suite
├── frontend/            # React TypeScript frontend
│   ├── src/
│   │   ├── components/  # UI components (Grid, Clues, Controls)
│   │   ├── hooks/       # React hooks (usePuzzle, useSolving)
│   │   └── services/    # API client
│   └── tests/           # Frontend test suite
├── docs/                # Documentation
│   ├── architecture/    # Architecture and design docs
│   ├── api/             # API reference
│   ├── guides/          # User and developer guides
│   ├── troubleshooting/ # Issue fixes and debugging
│   └── interview-prep/  # Technical interview preparation
├── scripts/             # Utility scripts
│   ├── setup/           # Installation and setup
│   ├── testing/         # Test runners
│   └── diagnostics/     # Debugging and diagnostics
└── tools/               # Development tools
    ├── verification/    # Verification scripts
    └── testing/         # Test utilities
```

## 🧪 Testing

```bash
# Backend tests
cd backend
source venv/bin/activate
pytest

# Frontend tests
cd frontend
npm test

# All tests
./scripts/testing/run_all_tests.sh
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🤝 Contributing

See [CONTRIBUTING.md](docs/guides/CONTRIBUTING.md) for development guidelines.

## 📧 Contact

For questions or demo requests, please open an issue.

---

**Built with ❤️ as a demonstration of advanced AI engineering concepts**
