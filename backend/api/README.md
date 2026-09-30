# AIxWord FastAPI Application

This directory contains the FastAPI REST API implementation for the AIxWord crossword puzzle application.

## Overview

The API provides endpoints for:
- **Puzzle Generation**: Generate crossword puzzles from topics using AI
- **Puzzle Management**: Retrieve, list, and delete puzzles
- **AI Solving**: Solve entire puzzles or individual words with AI assistance
- **Hints**: Get AI-generated hints for specific words
- **Validation**: Validate user solutions

## Architecture

```
api/
├── main.py              # FastAPI application entry point
├── dependencies.py      # Dependency injection utilities
├── schemas.py          # Pydantic request/response models
└── routes/
    ├── __init__.py     # Routes package
    ├── health.py       # Health check endpoints
    └── puzzles.py      # Puzzle management endpoints
```

## Quick Start

### 1. Setup Environment

Create a `.env` file in the backend directory:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your-api-key-here
```

### 2. Install Dependencies

```bash
# From backend directory
pip install -e .
```

### 3. Run the Server

```bash
# Option 1: Using the run script
python3 run_server.py

# Option 2: Using uvicorn directly
uvicorn backend.api.main:app --reload

# Option 3: Using the main module
python3 -m backend.api.main
```

The server will start at `http://localhost:8000`

### 4. Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Checks

#### GET /api/health
Check if the API is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "service": "aixword-backend",
  "version": "0.1.0",
  "config": {
    "grid_size": 8,
    "max_iterations": 50,
    "openai_model": "gpt-4-turbo-preview"
  }
}
```

#### GET /api/ready
Check if the API is ready to accept requests.

**Response:**
```json
{
  "status": "ready",
  "message": "Service is ready to accept requests"
}
```

### Puzzle Generation

#### POST /api/puzzles/generate
Generate a new crossword puzzle from a topic.

**Request Body:**
```json
{
  "topic": "Science",
  "grid_size": 8,
  "min_words": 8,
  "max_words": 15,
  "difficulty": "medium",
  "max_iterations": 50
}
```

**Response:**
```json
{
  "success": true,
  "puzzle": {
    "puzzle_id": "uuid-here",
    "topic": "Science",
    "grid_size": 8,
    "cells": [...],
    "clues_across": [...],
    "clues_down": [...],
    "word_count": 12,
    "fill_rate": 0.75,
    "difficulty": "medium",
    "created_at": "2026-09-28T17:00:00",
    "metadata": {}
  },
  "status": "completed",
  "iterations": 15,
  "error_message": null
}
```

**Note:** This endpoint may take 30-60 seconds to complete as it uses AI to generate the puzzle.

### Puzzle Management

#### GET /api/puzzles/{puzzle_id}
Get a specific puzzle by ID.

**Response:**
```json
{
  "puzzle_id": "uuid-here",
  "topic": "Science",
  "grid_size": 8,
  "cells": [...],
  "clues_across": [...],
  "clues_down": [...],
  "word_count": 12,
  "fill_rate": 0.75,
  "difficulty": "medium",
  "created_at": "2026-09-28T17:00:00",
  "metadata": {}
}
```

#### GET /api/puzzles/
List all generated puzzles.

**Response:**
```json
[
  {
    "puzzle_id": "uuid-1",
    "topic": "Science",
    ...
  },
  {
    "puzzle_id": "uuid-2",
    "topic": "History",
    ...
  }
]
```

#### DELETE /api/puzzles/{puzzle_id}
Delete a puzzle.

**Response:** 204 No Content

### AI Solving

#### POST /api/puzzles/{puzzle_id}/solve
Solve the entire puzzle with AI.

**Request Body:**
```json
{
  "use_hints": true
}
```

**Response:**
```json
{
  "success": true,
  "answer": "Complete puzzle solution",
  "confidence": 1.0,
  "reasoning": "Solution retrieved from generated puzzle",
  "updated_cells": [...]
}
```

#### POST /api/puzzles/{puzzle_id}/solve-word
Solve a specific word with AI.

**Request Body:**
```json
{
  "clue_number": 1,
  "direction": "across",
  "use_intersections": true
}
```

**Response:**
```json
{
  "success": true,
  "answer": "ATOM",
  "confidence": 1.0,
  "reasoning": "Solution for clue: Basic unit of matter",
  "updated_cells": [...]
}
```

### Hints

#### POST /api/puzzles/{puzzle_id}/hint
Get a hint for a specific word.

**Request Body:**
```json
{
  "clue_number": 1,
  "direction": "across",
  "hint_type": "letter"
}
```

**Hint Types:**
- `letter`: Reveal a single letter
- `definition`: Provide an alternative definition
- `synonym`: Provide a synonym or related word

**Response:**
```json
{
  "success": true,
  "hint": "The first letter is 'A'",
  "hint_type": "letter",
  "revealed_letter": "A",
  "position": 0
}
```

### Validation

#### POST /api/puzzles/{puzzle_id}/validate
Validate the user's solution.

**Request Body:**
```json
{
  "cells": [
    {
      "row": 0,
      "col": 0,
      "value": "A",
      "is_blocked": false,
      "number": 1
    },
    ...
  ]
}
```

**Response:**
```json
{
  "is_valid": true,
  "is_complete": false,
  "errors": [],
  "correct_count": 15,
  "total_count": 48,
  "accuracy": 0.3125
}
```

## Request/Response Schemas

All request and response schemas are defined in `schemas.py` using Pydantic models. Key schemas include:

### Request Schemas
- `PuzzleGenerateRequest`: Puzzle generation parameters
- `SolvePuzzleRequest`: Full puzzle solve options
- `SolveWordRequest`: Single word solve options
- `HintRequest`: Hint request parameters
- `ValidateRequest`: Solution validation data

### Response Schemas
- `PuzzleResponse`: Complete puzzle data
- `PuzzleGenerateResponse`: Generation result
- `SolveResponse`: Solve operation result
- `HintResponse`: Hint data
- `ValidateResponse`: Validation results
- `ErrorResponse`: Standard error format

## Dependencies

The API uses FastAPI's dependency injection system for:

### Orchestrator Dependency
```python
from backend.api.dependencies import OrchestratorDep

@router.post("/generate")
async def generate_puzzle(orchestrator: OrchestratorDep):
    # orchestrator is automatically injected
    result = await orchestrator.generate_puzzle_async(...)
```

### Settings Dependency
```python
from backend.api.dependencies import SettingsDep

@router.get("/config")
async def get_config(settings: SettingsDep):
    # settings is automatically injected
    return {"grid_size": settings.grid_size}
```

## Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `204 No Content`: Successful deletion
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

All errors return a consistent format:
```json
{
  "error": "error_type",
  "message": "Human-readable error message",
  "details": {}
}
```

## CORS Configuration

CORS is configured to allow requests from:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000` (React default)

To add more origins, update the `CORS_ORIGINS` environment variable:
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://your-domain.com
```

## Storage

Currently, puzzles are stored in-memory using a dictionary. This means:
- ✅ Fast access
- ✅ No database setup required
- ❌ Data is lost when server restarts
- ❌ Not suitable for production

**Future Enhancement:** Replace with database storage (PostgreSQL, MongoDB, etc.)

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/api/health

# Generate puzzle
curl -X POST http://localhost:8000/api/puzzles/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Science", "grid_size": 8}'

# Get puzzle
curl http://localhost:8000/api/puzzles/{puzzle_id}

# Solve word
curl -X POST http://localhost:8000/api/puzzles/{puzzle_id}/solve-word \
  -H "Content-Type: application/json" \
  -d '{"clue_number": 1, "direction": "across"}'
```

### Using Python requests

```python
import requests

# Generate puzzle
response = requests.post(
    "http://localhost:8000/api/puzzles/generate",
    json={"topic": "Science", "grid_size": 8}
)
puzzle = response.json()

# Get hint
response = requests.post(
    f"http://localhost:8000/api/puzzles/{puzzle['puzzle']['puzzle_id']}/hint",
    json={"clue_number": 1, "direction": "across", "hint_type": "letter"}
)
hint = response.json()
```

### Using the Interactive Docs

Visit http://localhost:8000/docs for an interactive API explorer where you can:
- View all endpoints and their parameters
- Try out requests directly in the browser
- See example responses
- Download OpenAPI specification

## Performance Considerations

### Puzzle Generation
- Takes 30-60 seconds depending on complexity
- Uses async/await for non-blocking execution
- Consider implementing:
  - Progress updates via WebSocket
  - Background task queue (Celery, RQ)
  - Caching for repeated topics

### Rate Limiting
Currently no rate limiting is implemented. For production, consider:
- Adding rate limiting middleware
- Implementing request throttling
- Using API keys for authentication

## Logging

The API uses Python's standard logging module. Configure log level via environment:

```env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

Logs include:
- Request/response information
- Puzzle generation progress
- Error details with stack traces
- Performance metrics

## Development

### Running in Development Mode

```bash
# With auto-reload
uvicorn backend.api.main:app --reload --log-level debug

# Or use the run script
python3 run_server.py
```

### Verifying Setup

```bash
# Run verification script
python3 verify_api_setup.py
```

This checks:
- All modules can be imported
- FastAPI app is configured correctly
- Routes are registered
- Dependencies work
- Schemas are valid

## Production Deployment

For production deployment:

1. **Use a production ASGI server:**
   ```bash
   gunicorn backend.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Set production environment variables:**
   ```env
   LOG_LEVEL=WARNING
   ENABLE_DOCS=false
   ```

3. **Add authentication/authorization**

4. **Implement rate limiting**

5. **Use a proper database**

6. **Add monitoring and alerting**

7. **Configure HTTPS/TLS**

## Troubleshooting

### Import Errors
```bash
# Ensure package is installed
pip install -e .

# Check Python path
python3 -c "import sys; print(sys.path)"
```

### OpenAI API Errors
```bash
# Check API key is set
echo $OPENAI_API_KEY

# Verify .env file exists
cat .env
```

### Port Already in Use
```bash
# Change port in .env
API_PORT=8001

# Or specify when running
uvicorn backend.api.main:app --port 8001
```

### CORS Errors
```bash
# Add your frontend URL to CORS_ORIGINS in .env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://your-frontend-url
```

## Next Steps

1. **Frontend Integration**: Connect React frontend to these endpoints
2. **RAG Implementation**: Add document upload and RAG-based puzzle generation
3. **Database**: Replace in-memory storage with persistent database
4. **Authentication**: Add user authentication and authorization
5. **WebSocket**: Add real-time progress updates for puzzle generation
6. **Caching**: Implement Redis caching for frequently accessed puzzles
7. **Testing**: Add comprehensive API tests

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [OpenAPI Specification](https://swagger.io/specification/)
