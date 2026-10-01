# AIxWord API Reference

**Version:** 1.0.0  
**Last Updated:** September 28, 2026  
**Base URL:** `http://localhost:8000` (Development)

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Request/Response Format](#requestresponse-format)
4. [Error Handling](#error-handling)
5. [Endpoints](#endpoints)
   - [Health Check](#health-check)
   - [Puzzle Management](#puzzle-management)
   - [Puzzle Solving](#puzzle-solving)
6. [Data Models](#data-models)
7. [Examples](#examples)
8. [Rate Limiting](#rate-limiting)
9. [Best Practices](#best-practices)

---

## Overview

The AIxWord API provides RESTful endpoints for generating, retrieving, solving, and managing AI-powered crossword puzzles. The API uses JSON for all requests and responses and follows standard HTTP conventions.

### Key Features

- **Puzzle Generation**: AI-powered crossword puzzle generation from topics
- **Puzzle Retrieval**: Get puzzles by ID or list all puzzles
- **AI Solving**: Solve entire puzzles or individual words with AI
- **Hint Generation**: Get contextual hints for specific words
- **Solution Validation**: Validate user solutions and get feedback
- **Puzzle Management**: Delete puzzles from storage

### API Characteristics

- **Protocol**: HTTP/1.1, HTTPS (production)
- **Format**: JSON (application/json)
- **Encoding**: UTF-8
- **CORS**: Enabled for configured origins
- **Async**: All endpoints are async-capable
- **Timeout**: 120 seconds for generation, 30 seconds for other operations

---

## Authentication

**Current Version**: No authentication required

**Future Versions**: Will support API key authentication

```http
Authorization: Bearer <api_key>
```

---

## Request/Response Format

### Request Headers

```http
Content-Type: application/json
Accept: application/json
```

### Response Headers

```http
Content-Type: application/json
X-Request-ID: <unique-request-id>
```

### Standard Response Structure

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "metadata": { ... }
}
```

**Error Response:**
```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": { ... }
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Response Format

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid puzzle generation parameters",
  "details": {
    "field": "grid_size",
    "issue": "must be between 4 and 20"
  }
}
```

### Common Error Codes

| Error Code | Description |
|------------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `PUZZLE_NOT_FOUND` | Puzzle ID not found |
| `GENERATION_FAILED` | Puzzle generation failed |
| `LLM_ERROR` | LLM API error |
| `INTERNAL_ERROR` | Internal server error |

---

## Endpoints

### Health Check

#### GET /health

Check API health status.

**Request:**
```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-09-28T12:00:00Z"
}
```

**Status Codes:**
- `200 OK`: Service is healthy
- `503 Service Unavailable`: Service is unhealthy

---

### Puzzle Management

#### POST /api/puzzles/generate

Generate a new crossword puzzle.

**Request:**
```http
POST /api/puzzles/generate HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "topic": "Science",
  "grid_size": 8,
  "min_words": 8,
  "max_words": 15,
  "difficulty": "medium",
  "max_iterations": 50
}
```

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `topic` | string | Yes | - | Topic for puzzle generation (1-100 chars) |
| `grid_size` | integer | No | 8 | Grid size (4-20) |
| `min_words` | integer | No | 8 | Minimum number of words (≥4) |
| `max_words` | integer | No | 15 | Maximum number of words (≥4) |
| `difficulty` | string | No | "medium" | Difficulty level: "easy", "medium", "hard" |
| `max_iterations` | integer | No | 50 | Maximum iterations (1-100) |

**Response:**
```json
{
  "success": true,
  "puzzle": {
    "puzzle_id": "550e8400-e29b-41d4-a716-446655440000",
    "topic": "Science",
    "grid_size": 8,
    "cells": [
      {
        "row": 0,
        "col": 0,
        "value": "A",
        "is_blocked": false,
        "number": 1
      },
      ...
    ],
    "clues_across": [
      {
        "number": 1,
        "direction": "across",
        "text": "Study of living organisms",
        "answer": "BIOLOGY",
        "start_row": 0,
        "start_col": 0,
        "length": 7
      },
      ...
    ],
    "clues_down": [
      {
        "number": 1,
        "direction": "down",
        "text": "Smallest unit of life",
        "answer": "ATOM",
        "start_row": 0,
        "start_col": 0,
        "length": 4
      },
      ...
    ],
    "word_count": 12,
    "fill_rate": 0.65,
    "difficulty": "medium",
    "created_at": "2026-09-28T12:00:00Z",
    "metadata": {
      "iterations": 25,
      "generation_time": 45.2
    }
  },
  "status": "completed",
  "iterations": 25
}
```

**Status Codes:**
- `200 OK`: Puzzle generated successfully
- `400 Bad Request`: Invalid parameters
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Generation failed

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/puzzles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Science",
    "grid_size": 8,
    "difficulty": "medium"
  }'
```

**Example (Python):**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/puzzles/generate",
    json={
        "topic": "Science",
        "grid_size": 8,
        "difficulty": "medium"
    }
)

puzzle = response.json()["puzzle"]
print(f"Generated puzzle: {puzzle['puzzle_id']}")
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/api/puzzles/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    topic: 'Science',
    grid_size: 8,
    difficulty: 'medium',
  }),
});

const data = await response.json();
console.log('Generated puzzle:', data.puzzle.puzzle_id);
```

---

#### GET /api/puzzles/

List all puzzles.

**Request:**
```http
GET /api/puzzles/ HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
[
  {
    "puzzle_id": "550e8400-e29b-41d4-a716-446655440000",
    "topic": "Science",
    "grid_size": 8,
    "word_count": 12,
    "fill_rate": 0.65,
    "difficulty": "medium",
    "created_at": "2026-09-28T12:00:00Z"
  },
  ...
]
```

**Status Codes:**
- `200 OK`: List retrieved successfully

**Example (cURL):**
```bash
curl http://localhost:8000/api/puzzles/
```

---

#### GET /api/puzzles/{puzzle_id}

Get a specific puzzle by ID.

**Request:**
```http
GET /api/puzzles/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "puzzle_id": "550e8400-e29b-41d4-a716-446655440000",
  "topic": "Science",
  "grid_size": 8,
  "cells": [...],
  "clues_across": [...],
  "clues_down": [...],
  "word_count": 12,
  "fill_rate": 0.65,
  "difficulty": "medium",
  "created_at": "2026-09-28T12:00:00Z",
  "metadata": {}
}
```

**Status Codes:**
- `200 OK`: Puzzle retrieved successfully
- `404 Not Found`: Puzzle not found

**Example (cURL):**
```bash
curl http://localhost:8000/api/puzzles/550e8400-e29b-41d4-a716-446655440000
```

---

#### DELETE /api/puzzles/{puzzle_id}

Delete a puzzle.

**Request:**
```http
DELETE /api/puzzles/550e8400-e29b-41d4-a716-446655440000 HTTP/1.1
Host: localhost:8000
```

**Response:**
```json
{
  "success": true,
  "message": "Puzzle deleted successfully"
}
```

**Status Codes:**
- `200 OK`: Puzzle deleted successfully
- `404 Not Found`: Puzzle not found

**Example (cURL):**
```bash
curl -X DELETE http://localhost:8000/api/puzzles/550e8400-e29b-41d4-a716-446655440000
```

---

### Puzzle Solving

#### POST /api/puzzles/{puzzle_id}/solve

Solve the entire puzzle using AI.

**Request:**
```http
POST /api/puzzles/550e8400-e29b-41d4-a716-446655440000/solve HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "use_hints": true
}
```

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `use_hints` | boolean | No | true | Whether to use existing clues as hints |

**Response:**
```json
{
  "success": true,
  "answer": "COMPLETE_SOLUTION",
  "confidence": 0.95,
  "reasoning": "Solved all clues using AI",
  "updated_cells": [
    {
      "row": 0,
      "col": 0,
      "value": "B",
      "is_blocked": false,
      "number": 1
    },
    ...
  ]
}
```

**Status Codes:**
- `200 OK`: Puzzle solved successfully
- `404 Not Found`: Puzzle not found
- `500 Internal Server Error`: Solving failed

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/puzzles/550e8400-e29b-41d4-a716-446655440000/solve \
  -H "Content-Type: application/json" \
  -d '{"use_hints": true}'
```

**Example (Python):**
```python
response = requests.post(
    f"http://localhost:8000/api/puzzles/{puzzle_id}/solve",
    json={"use_hints": True}
)

solution = response.json()
print(f"Confidence: {solution['confidence']}")
```

---

#### POST /api/puzzles/{puzzle_id}/solve-word

Solve a specific word using AI.

**Request:**
```http
POST /api/puzzles/550e8400-e29b-41d4-a716-446655440000/solve-word HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "clue_number": 1,
  "direction": "across",
  "use_intersections": true
}
```

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `clue_number` | integer | Yes | - | Clue number to solve (≥1) |
| `direction` | string | Yes | - | Direction: "across" or "down" |
| `use_intersections` | boolean | No | true | Whether to use intersecting letters as hints |

**Response:**
```json
{
  "success": true,
  "answer": "BIOLOGY",
  "confidence": 0.92,
  "reasoning": "The clue 'Study of living organisms' strongly suggests BIOLOGY, which fits the 7-letter pattern and intersects correctly with existing words.",
  "updated_cells": [
    {
      "row": 0,
      "col": 0,
      "value": "B",
      "is_blocked": false,
      "number": 1
    },
    {
      "row": 0,
      "col": 1,
      "value": "I",
      "is_blocked": false,
      "number": null
    },
    ...
  ]
}
```

**Status Codes:**
- `200 OK`: Word solved successfully
- `404 Not Found`: Puzzle or clue not found
- `500 Internal Server Error`: Solving failed

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/puzzles/550e8400-e29b-41d4-a716-446655440000/solve-word \
  -H "Content-Type: application/json" \
  -d '{
    "clue_number": 1,
    "direction": "across",
    "use_intersections": true
  }'
```

**Example (JavaScript):**
```javascript
const response = await fetch(
  `http://localhost:8000/api/puzzles/${puzzleId}/solve-word`,
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      clue_number: 1,
      direction: 'across',
      use_intersections: true,
    }),
  }
);

const solution = await response.json();
console.log('Answer:', solution.answer);
console.log('Confidence:', solution.confidence);
```

---

#### POST /api/puzzles/{puzzle_id}/hint

Get a hint for a specific word.

**Request:**
```http
POST /api/puzzles/550e8400-e29b-41d4-a716-446655440000/hint HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "clue_number": 1,
  "direction": "across",
  "hint_type": "letter"
}
```

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `clue_number` | integer | Yes | - | Clue number (≥1) |
| `direction` | string | Yes | - | Direction: "across" or "down" |
| `hint_type` | string | No | "letter" | Hint type: "letter", "definition", "synonym" |

**Response:**
```json
{
  "success": true,
  "hint": "The first letter is 'B'",
  "hint_type": "letter",
  "revealed_letter": "B",
  "position": 0
}
```

**Hint Types:**

| Type | Description | Example |
|------|-------------|---------|
| `letter` | Reveals a letter at a specific position | "The first letter is 'B'" |
| `definition` | Provides an alternative definition | "It's the science of life" |
| `synonym` | Provides a synonym or related word | "Similar to 'life science'" |

**Status Codes:**
- `200 OK`: Hint generated successfully
- `404 Not Found`: Puzzle or clue not found
- `500 Internal Server Error`: Hint generation failed

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/puzzles/550e8400-e29b-41d4-a716-446655440000/hint \
  -H "Content-Type: application/json" \
  -d '{
    "clue_number": 1,
    "direction": "across",
    "hint_type": "letter"
  }'
```

---

#### POST /api/puzzles/{puzzle_id}/validate

Validate user's solution.

**Request:**
```http
POST /api/puzzles/550e8400-e29b-41d4-a716-446655440000/validate HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "cells": [
    {
      "row": 0,
      "col": 0,
      "value": "B",
      "is_blocked": false,
      "number": 1
    },
    ...
  ]
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cells` | array | Yes | Array of cells with user's answers |

**Response:**
```json
{
  "is_valid": true,
  "is_complete": true,
  "errors": [],
  "correct_count": 48,
  "total_count": 48,
  "accuracy": 1.0
}
```

**Error Response (with validation errors):**
```json
{
  "is_valid": false,
  "is_complete": false,
  "errors": [
    {
      "row": 0,
      "col": 2,
      "expected": "O",
      "actual": "A",
      "message": "Incorrect letter at position (0, 2)"
    }
  ],
  "correct_count": 45,
  "total_count": 48,
  "accuracy": 0.9375
}
```

**Status Codes:**
- `200 OK`: Validation completed
- `404 Not Found`: Puzzle not found
- `422 Unprocessable Entity`: Invalid cell data

**Example (Python):**
```python
response = requests.post(
    f"http://localhost:8000/api/puzzles/{puzzle_id}/validate",
    json={"cells": user_cells}
)

validation = response.json()
print(f"Accuracy: {validation['accuracy'] * 100}%")
print(f"Errors: {len(validation['errors'])}")
```

---

## Data Models

### Cell

Represents a single grid cell.

```json
{
  "row": 0,
  "col": 0,
  "value": "A",
  "is_blocked": false,
  "number": 1
}
```

| Field | Type | Description |
|-------|------|-------------|
| `row` | integer | Row position (0-indexed) |
| `col` | integer | Column position (0-indexed) |
| `value` | string\|null | Letter (A-Z) or null if empty |
| `is_blocked` | boolean | Whether cell is a black square |
| `number` | integer\|null | Clue number if word starts here |

### Clue

Represents a crossword clue.

```json
{
  "number": 1,
  "direction": "across",
  "text": "Study of living organisms",
  "answer": "BIOLOGY",
  "start_row": 0,
  "start_col": 0,
  "length": 7
}
```

| Field | Type | Description |
|-------|------|-------------|
| `number` | integer | Clue number |
| `direction` | string | "across" or "down" |
| `text` | string | Clue text |
| `answer` | string | Answer word (uppercase) |
| `start_row` | integer | Starting row position |
| `start_col` | integer | Starting column position |
| `length` | integer | Answer length |

### Puzzle

Represents a complete crossword puzzle.

```json
{
  "puzzle_id": "550e8400-e29b-41d4-a716-446655440000",
  "topic": "Science",
  "grid_size": 8,
  "cells": [...],
  "clues_across": [...],
  "clues_down": [...],
  "word_count": 12,
  "fill_rate": 0.65,
  "difficulty": "medium",
  "created_at": "2026-09-28T12:00:00Z",
  "metadata": {}
}
```

| Field | Type | Description |
|-------|------|-------------|
| `puzzle_id` | string | Unique puzzle identifier (UUID) |
| `topic` | string | Puzzle topic |
| `grid_size` | integer | Grid size (NxN) |
| `cells` | array | Array of all cells |
| `clues_across` | array | Array of across clues |
| `clues_down` | array | Array of down clues |
| `word_count` | integer | Number of words in puzzle |
| `fill_rate` | number | Grid fill rate (0.0-1.0) |
| `difficulty` | string | Difficulty level |
| `created_at` | string | Creation timestamp (ISO 8601) |
| `metadata` | object | Additional metadata |

---

## Examples

### Complete Workflow Example (Python)

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Generate a puzzle
print("Generating puzzle...")
response = requests.post(
    f"{BASE_URL}/api/puzzles/generate",
    json={
        "topic": "Science",
        "grid_size": 8,
        "difficulty": "medium"
    }
)

puzzle = response.json()["puzzle"]
puzzle_id = puzzle["puzzle_id"]
print(f"Generated puzzle: {puzzle_id}")
print(f"Words: {puzzle['word_count']}, Fill rate: {puzzle['fill_rate']}")

# 2. Get a hint for a word
print("\nGetting hint for 1-across...")
response = requests.post(
    f"{BASE_URL}/api/puzzles/{puzzle_id}/hint",
    json={
        "clue_number": 1,
        "direction": "across",
        "hint_type": "letter"
    }
)

hint = response.json()
print(f"Hint: {hint['hint']}")

# 3. Solve a specific word
print("\nSolving 1-across...")
response = requests.post(
    f"{BASE_URL}/api/puzzles/{puzzle_id}/solve-word",
    json={
        "clue_number": 1,
        "direction": "across",
        "use_intersections": True
    }
)

solution = response.json()
print(f"Answer: {solution['answer']}")
print(f"Confidence: {solution['confidence']}")

# 4. Solve entire puzzle
print("\nSolving entire puzzle...")
response = requests.post(
    f"{BASE_URL}/api/puzzles/{puzzle_id}/solve",
    json={"use_hints": True}
)

full_solution = response.json()
print(f"Puzzle solved! Confidence: {full_solution['confidence']}")

# 5. Validate solution
print("\nValidating solution...")
response = requests.post(
    f"{BASE_URL}/api/puzzles/{puzzle_id}/validate",
    json={"cells": full_solution["updated_cells"]}
)

validation = response.json()
print(f"Valid: {validation['is_valid']}")
print(f"Complete: {validation['is_complete']}")
print(f"Accuracy: {validation['accuracy'] * 100}%")

# 6. List all puzzles
print("\nListing all puzzles...")
response = requests.get(f"{BASE_URL}/api/puzzles/")
puzzles = response.json()
print(f"Total puzzles: {len(puzzles)}")

# 7. Delete puzzle
print(f"\nDeleting puzzle {puzzle_id}...")
response = requests.delete(f"{BASE_URL}/api/puzzles/{puzzle_id}")
print("Puzzle deleted")
```

### Complete Workflow Example (JavaScript)

```javascript
const BASE_URL = 'http://localhost:8000';

async function completeWorkflow() {
  try {
    // 1. Generate a puzzle
    console.log('Generating puzzle...');
    let response = await fetch(`${BASE_URL}/api/puzzles/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: 'Science',
        grid_size: 8,
        difficulty: 'medium',
      }),
    });
    
    let data = await response.json();
    const puzzle = data.puzzle;
    const puzzleId = puzzle.puzzle_id;
    console.log(`Generated puzzle: ${puzzleId}`);
    console.log(`Words: ${puzzle.word_count}, Fill rate: ${puzzle.fill_rate}`);

    // 2. Get a hint
    console.log('\nGetting hint for 1-across...');
    response = await fetch(`${BASE_URL}/api/puzzles/${puzzleId}/hint`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        clue_number: 1,
        direction: 'across',
        hint_type: 'letter',
      }),
    });
    
    data = await response.json();
    console.log(`Hint: ${data.hint}`);

    // 3. Solve a word
    console.log('\nSolving 1-across...');
    response = await fetch(`${BASE_URL}/api/puzzles/${puzzleId}/solve-word`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        clue_number: 1,
        direction: 'across',
        use_intersections: true,
      }),
    });
    
    data = await response.json();
    console.log(`Answer: ${data.answer}`);
    console.log(`Confidence: ${data.confidence}`);

    // 4. Solve entire puzzle
    console.log('\nSolving entire puzzle...');
    response = await fetch(`${BASE_URL}/api/puzzles/${puzzleId}/solve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ use_hints: true }),
    });
    
    data = await response.json();
    console.log(`Puzzle solved! Confidence: ${data.confidence}`);

    // 5. Validate solution
    console.log('\nValidating solution...');
    response = await fetch(`${BASE_URL}/api/puzzles/${puzzleId}/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cells: data.updated_cells }),
    });
    
    data = await response.json();
    console.log(`Valid: ${data.is_valid}`);
    console.log(`Complete: ${data.is_complete}`);
    console.log(`Accuracy: ${data.accuracy * 100}%`);

    // 6. Delete puzzle
    console.log(`\nDeleting puzzle ${puzzleId}...`);
    await fetch(`${BASE_URL}/api/puzzles/${puzzleId}`, {
      method: 'DELETE',
    });
    console.log('Puzzle deleted');

  } catch (error) {
    console.error('Error:', error.message);
  }
}

completeWorkflow();
```

---

## Rate Limiting

**Current Version**: No rate limiting

**Future Versions**: Will implement rate limiting

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

**Limits (Planned):**
- Puzzle generation: 10 per hour per IP
- Solve operations: 100 per hour per IP
- Other operations: 1000 per hour per IP

---

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
except ValueError as e:
    print(f"JSON decode error: {e}")
```

### 2. Timeouts

Set appropriate timeouts for long-running operations:

```python
# Puzzle generation can take 30-60 seconds
response = requests.post(
    url,
    json=data,
    timeout=120  # 2 minutes
)
```

### 3. Retry Logic

Implement retry logic for transient failures:

```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

response = session.post(url, json=data)
```

### 4. Validation

Validate data before sending requests:

```python
def validate_puzzle_request(data):
    assert 1 <= len(data['topic']) <= 100, "Topic must be 1-100 chars"
    assert 4 <= data.get('grid_size', 8) <= 20, "Grid size must be 4-20"
    assert data.get('difficulty', 'medium') in ['easy', 'medium', 'hard']
    return True

if validate_puzzle_request(request_data):
    response = requests.post(url, json=request_data)
```

### 5. Async Operations

Use async/await for better performance:

```javascript
// Parallel requests
const [puzzle1, puzzle2] = await Promise.all([
  fetch(`${BASE_URL}/api/puzzles/${id1}`).then(r => r.json()),
  fetch(`${BASE_URL}/api/puzzles/${id2}`).then(r => r.json()),
]);
```

### 6. Caching

Cache puzzle data to reduce API calls:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_puzzle(puzzle_id):
    response = requests.get(f"{BASE_URL}/api/puzzles/{puzzle_id}")
    return response.json()
```

---

## Interactive API Documentation

The API provides interactive documentation using Swagger UI and ReDoc:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

These interfaces allow you to:
- Explore all endpoints
- View request/response schemas
- Test API calls directly in the browser
- Download OpenAPI specification

---

## Support

### Getting Help

1. **Documentation**: Check this API reference and [ARCHITECTURE.md](ARCHITECTURE.md)
2. **Interactive Docs**: Use Swagger UI at http://localhost:8000/docs
3. **Examples**: Review code examples in this document
4. **Source Code**: Check the backend implementation in `backend/api/`

### Reporting Issues

If you encounter API issues:
1. Check the error response for details
2. Verify request parameters match the schema
3. Check server logs for detailed error information
4. Review the interactive documentation

---

**Document Version:** 1.0.0  
**Last Updated:** September 28, 2026  
**Maintained By:** AIxWord Development Team
