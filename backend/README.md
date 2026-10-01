# AIxWord Backend

Python FastAPI backend for the AIxWord interactive crossword puzzle application.

## Overview

The backend implements a multi-agent system using LangGraph to generate and solve crossword puzzles. It provides RESTful APIs for puzzle generation, solving, and AI assistance.

## Architecture

### Core Components

1. **Domain Layer** (`domain/`)
   - Pure business logic and domain models
   - Grid engine for crossword management
   - Word validation and pattern matching
   - No external dependencies (except Pydantic)

2. **Agent Layer** (`agents/`)
   - LangGraph-based multi-agent system
   - PlannerAgent: Strategic puzzle planning
   - WordGeneratorAgent: Word placement execution
   - Workflow orchestration and state management

3. **LLM Layer** (`llm/`)
   - OpenAI client wrapper
   - Prompt template management
   - Response parsing and validation

4. **API Layer** (`api/`)
   - FastAPI route handlers
   - Request/response schemas
   - Error handling and validation

## Setup

### Requirements

- Python 3.11 or higher
- OpenAI API key

### Installation

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install package:
   ```bash
   pip install -e .
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/domain/test_grid.py

# Run with markers
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type check
mypy .
```

### Running the Server

```bash
# Development mode with auto-reload
uvicorn backend.api.main:app --reload

# Production mode
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```

## Configuration

Configuration is managed through environment variables. See `.env.example` for all available options.

### Key Settings

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: gpt-4-turbo-preview)
- `GRID_SIZE`: Default grid size (default: 8)
- `MAX_ITERATIONS`: Max puzzle generation attempts (default: 50)
- `MIN_FILL_RATE`: Minimum puzzle fill rate (default: 0.6)

## Scripts & Verification Tools

Backend verification and testing scripts are available in `.internal/scripts/backend/`:

### Verification Scripts
- **Setup & Configuration**: `verify_setup.py`, `verify_api_setup.py`
- **LLM & AI**: `check_available_models.py`, `test_openai_connection.py`, `verify_llm.py`
- **Domain Logic**: `verify_domain.py`, `verify_validation.py`
- **Agent System**: `verify_planner.py`, `verify_word_generator.py`, `verify_orchestration.py`
- **API Endpoints**: `verify_puzzle_api.py`
- **Bug Fixes**: `verify_recursion_fix.py`, `verify_ssl_fix.py`

### Testing Scripts
- **Demo Data**: `demo_data.py` - Generate test data
- **API Testing**: `test_api_manual.py`, `test_puzzle_endpoints.py`
- **Unit Tests**: `test_solver_unit.py`

**Full Documentation**: [Backend Scripts README](../.internal/scripts/backend/README.md)

**Quick Usage**:
```bash
# Verify setup
python .internal/scripts/backend/verification/verify_setup.py

# Check LLM connection
python .internal/scripts/backend/verification/test_openai_connection.py

# Verify domain logic
python .internal/scripts/backend/verification/verify_domain.py
```

## Documentation

Comprehensive backend documentation is available in the `docs/backend/` directory:

### Architecture & Design
- **[Backend Architecture](../docs/backend/architecture/BACKEND_ARCHITECTURE.md)** - Complete system architecture and design principles
- **[Multi-Agent System](../docs/backend/architecture/MULTI_AGENT_SYSTEM.md)** - AI agent orchestration with LangGraph

### API Documentation
- **[API Reference](../docs/backend/api/API.md)** - Core API endpoints and usage
- **[Complete API Reference](../docs/backend/api/API_REFERENCE_COMPLETE.md)** - Comprehensive API documentation
- **[Puzzle API Endpoints](../docs/backend/api/PUZZLE_API_ENDPOINTS.md)** - Detailed puzzle endpoint docs

### Guides
- **[Testing Guide](../docs/backend/guides/TESTING.md)** - Testing strategy and practices
- **[Performance Guide](../docs/backend/guides/PERFORMANCE.md)** - Performance optimization

### Deployment
- **[Deployment Guide](../docs/backend/deployment/DEPLOYMENT.md)** - Production deployment and Docker setup

### Technical Deep Dive
- **[Technical Documentation Index](../docs/backend/technical-deep-dive/README_TECHNICAL_DOCS.md)** - Advanced technical docs
- **[AI Concepts & Implementation](../docs/backend/technical-deep-dive/AI_CONCEPTS_AND_IMPLEMENTATION.md)** - AI/ML implementation details
- **[Architecture Deep Dive](../docs/backend/technical-deep-dive/ARCHITECTURE_DEEP_DIVE.md)** - Detailed architectural patterns

### Related Documentation
- **[Frontend Documentation](../docs/frontend/README.md)** - React/TypeScript frontend docs
- **[User Guide](../docs/guides/USER_GUIDE.md)** - End-user documentation
- **[Quick Start](../docs/guides/QUICK_START.md)** - Getting started guide
- **[Development Guide](../docs/guides/DEVELOPMENT.md)** - Development workflow

## API Endpoints

### Puzzle Generation

- `POST /api/puzzles/generate` - Generate new puzzle from topic
- `GET /api/puzzles/{puzzle_id}` - Get puzzle by ID
- `GET /api/puzzles` - List all puzzles

### Puzzle Solving

- `POST /api/puzzles/{puzzle_id}/solve` - Solve entire puzzle with AI
- `POST /api/puzzles/{puzzle_id}/solve-word` - Solve specific word
- `POST /api/puzzles/{puzzle_id}/hint` - Get hint for word
- `POST /api/puzzles/{puzzle_id}/validate` - Validate user solution

### Documentation

- `/docs` - Swagger UI (interactive API documentation)
- `/redoc` - ReDoc (alternative API documentation)

## Domain Models

### Core Models

- **Cell**: Represents a single grid cell with position, value, and metadata
- **WordPlacement**: Defines word position, direction, and clue
- **Clue**: Clue information with number, direction, and answer
- **Direction**: Enum for ACROSS/DOWN orientation

### Grid Engine

The `CrosswordGrid` class provides:
- Grid initialization and management
- Word placement with collision detection
- Intersection validation
- Pattern matching for partial words
- Fill rate calculation
- State serialization/deserialization

### Validation

Multi-layered validation ensures:
- Valid word characters and length
- Grid boundary compliance
- Intersection compatibility
- Minimum fill rate requirements

## Multi-Agent System

### Agent Architecture

```
User Request
     ↓
PlannerAgent (Strategic Planning)
     ↓
WordGeneratorAgent (Execution)
     ↓
Validation & Refinement
     ↓
Final Puzzle
```

### State Management

Agents communicate through shared state:
- Current grid state
- Placed words and clues
- Remaining words to place
- Iteration count
- Error messages

### Workflow

1. **Planning Phase**: PlannerAgent analyzes topic and creates word list
2. **Generation Phase**: WordGeneratorAgent places words on grid
3. **Validation Phase**: Check fill rate and puzzle quality
4. **Refinement Phase**: Iterate if needed (up to MAX_ITERATIONS)

## Testing Strategy

### Test Categories

- **Unit Tests** (`tests/domain/`): Pure domain logic, 95%+ coverage
- **Integration Tests** (`tests/agents/`): Agent coordination and workflow
- **LLM Tests** (`tests/llm/`): LLM client and prompt validation (mocked)
- **API Tests** (`tests/api/`): Endpoint behavior and error handling

### Running Tests

**Quick test run (no coverage):**
```bash
./run_tests.sh quick
```

**Run all tests with coverage:**
```bash
./run_tests.sh all
```

**Run specific test suites:**
```bash
./run_tests.sh domain      # Domain tests only
./run_tests.sh llm         # LLM tests only
./run_tests.sh grid        # Grid tests only
./run_tests.sh word        # Word tests only
```

**Validate test status:**
```bash
python3 validate_tests.py
```

**Manual pytest commands:**
```bash
# Run all available tests
pytest tests/domain/ tests/llm/ -v

# Run with coverage report
pytest tests/domain/ tests/llm/ --cov=backend --cov-report=html

# Run specific test file
pytest tests/domain/test_grid.py -v

# Run specific test
pytest tests/domain/test_grid.py::TestGridInitialization::test_default_grid_size -v
```

### Test Results

**Current Status:** ✅ 246/246 tests passing

| Module | Tests | Status | Coverage |
|--------|-------|--------|----------|
| `domain/grid.py` | 46 | ✅ PASS | 97% |
| `domain/word.py` | 47 | ✅ PASS | 100% |
| `domain/pattern.py` | 58 | ✅ PASS | 97% |
| `domain/validator.py` | 54 | ✅ PASS | 86% |
| `llm/client.py` | 17 | ✅ PASS | 85% |
| `llm/prompts.py` | 24 | ✅ PASS | 100% |
| `agents/workflow.py` | - | ⚠️ SKIP | Requires langgraph |
| `agents/state.py` | - | ⚠️ SKIP | Requires langgraph |

See [TEST_RESULTS.md](TEST_RESULTS.md) for detailed test execution report.

### Mocking Strategy

- Mock OpenAI API calls in tests to avoid costs and rate limits
- Use fixtures for common test data (grids, words, placements)
- Test both success and failure scenarios

## Performance Considerations

- Puzzle generation typically takes 30-60 seconds
- Use async/await throughout for non-blocking operations
- Consider caching for repeated topic requests (future)
- WebSocket support for real-time progress updates (future)

## Error Handling

- Graceful degradation: return partial results if LLM fails
- User-friendly error messages in API responses
- Retry logic for transient OpenAI API failures
- Comprehensive logging for debugging

## Future Enhancements

- [ ] RAG integration for document-based puzzles
- [ ] Variable grid sizes (4×4 to 20×20)
- [ ] Difficulty levels
- [ ] Puzzle templates and themes
- [ ] Multi-language support
- [ ] Puzzle sharing and export

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure package is installed with `pip install -e .`
2. **OpenAI API errors**: Check API key in `.env` file
3. **Test failures**: Run `pytest -v` for detailed output
4. **Type errors**: Run `mypy .` to identify type issues

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
```

## Contributing

This is an assignment project. For development:

1. Create feature branch
2. Write tests first (TDD)
3. Implement feature
4. Ensure all tests pass
5. Run code quality checks
6. Update documentation

## License

MIT License - See LICENSE file for details.
