# Contributing to AIxWord

Thank you for your interest in AIxWord! This document provides guidelines for contributing to the project.

## Project Status

This is an academic assignment project for the Quadlift Advanced Tech Architects program. While external contributions are not currently accepted, this guide documents the development workflow for team members and future reference.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ (for frontend development)
- Git
- OpenAI API key

### Backend Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd AIxWord
   ```

2. Set up the backend:
   ```bash
   cd backend
   
   # On macOS/Linux:
   ./setup.sh
   
   # On Windows:
   setup.bat
   ```

3. Configure environment:
   ```bash
   # Edit .env and add your OPENAI_API_KEY
   nano .env
   ```

4. Verify setup:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pytest
   ```

### Frontend Setup (Coming in Round 4)

Frontend setup instructions will be added when frontend development begins.

## Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Critical fixes for production

### Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the coding standards below

3. Write tests for your changes

4. Run the test suite:
   ```bash
   cd backend
   make test
   ```

5. Check code quality:
   ```bash
   make lint
   make type-check
   make format
   ```

6. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

7. Push to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```

## Coding Standards

### Python (Backend)

- **Style Guide**: Follow PEP 8
- **Formatter**: Black (line length: 100)
- **Linter**: Ruff
- **Type Hints**: Required for all functions
- **Docstrings**: Required for all public APIs (Google style)

Example:
```python
def calculate_fill_rate(grid: CrosswordGrid) -> float:
    """
    Calculate the fill rate of a crossword grid.
    
    Args:
        grid: The crossword grid to analyze
        
    Returns:
        Fill rate as a float between 0.0 and 1.0
        
    Raises:
        ValueError: If grid is empty or invalid
    """
    # Implementation
    pass
```

### TypeScript/JavaScript (Frontend)

- **Style Guide**: Airbnb JavaScript Style Guide
- **Formatter**: Prettier
- **Linter**: ESLint
- **Type Safety**: TypeScript strict mode

### Commit Messages

Follow the Conventional Commits specification:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add word validation to grid engine
fix: resolve intersection detection bug
docs: update API documentation
test: add tests for pattern matching
```

## Testing Guidelines

### Test Coverage

- Maintain minimum 90% code coverage
- All new features must include tests
- All bug fixes must include regression tests

### Test Categories

- **Unit Tests**: Test individual functions/classes in isolation
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete user workflows

### Writing Tests

```python
import pytest
from backend.domain.grid import CrosswordGrid

def test_grid_initialization():
    """Test that grid initializes with correct size."""
    grid = CrosswordGrid(size=8)
    assert grid.size == 8
    assert len(grid.cells) == 8
    assert len(grid.cells[0]) == 8

def test_word_placement():
    """Test word placement on grid."""
    grid = CrosswordGrid(size=8)
    placement = WordPlacement(
        word="HELLO",
        start_row=0,
        start_col=0,
        direction=Direction.ACROSS,
        clue="A greeting",
        number=1
    )
    result = grid.place_word(placement)
    assert result is True
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/domain/test_grid.py

# Run specific test
pytest tests/domain/test_grid.py::test_grid_initialization

# Run with markers
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

## Code Review Process

1. All changes must be reviewed before merging
2. Reviewers check for:
   - Code quality and style
   - Test coverage
   - Documentation
   - Performance implications
   - Security considerations

3. Address review comments
4. Obtain approval from at least one reviewer
5. Merge to develop branch

## Documentation

### Code Documentation

- All public APIs must have docstrings
- Complex algorithms should have inline comments
- Use type hints for all function parameters and returns

### API Documentation

- API endpoints are auto-documented via FastAPI
- Update OpenAPI schemas when adding new endpoints
- Provide example requests/responses

### User Documentation

- Update README.md for user-facing changes
- Update backend/README.md for developer changes
- Keep documentation in sync with code

## Performance Guidelines

- Profile code before optimizing
- Use async/await for I/O operations
- Cache expensive computations when appropriate
- Monitor LLM API usage and costs

## Security Guidelines

- Never commit API keys or secrets
- Use environment variables for configuration
- Validate all user inputs
- Sanitize data before LLM calls
- Follow OWASP security best practices

## Debugging

### Enable Debug Logging

```bash
export LOG_LEVEL=DEBUG
```

### Using Python Debugger

```python
import ipdb; ipdb.set_trace()
```

### Common Issues

1. **Import errors**: Ensure package is installed with `pip install -e .`
2. **OpenAI API errors**: Check API key in `.env` file
3. **Test failures**: Run `pytest -v` for detailed output
4. **Type errors**: Run `mypy .` to identify issues

## Getting Help

- Review the assignment documents in `documents/`
- Check existing issues and pull requests
- Consult the project README files
- Review the strategic plan in `.sasva/generated-plans/`

## License

By contributing to AIxWord, you agree that your contributions will be licensed under the MIT License.

---

**Note**: This is an academic project. The contribution guidelines are provided for educational purposes and team coordination.
