# AIxWord API Reference - Complete Documentation

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

The AIxWord API provides RESTful endpoints for generating, retrieving, solving, and managing crossword puzzles. The API uses JSON for all requests and responses and follows standard HTTP conventions for status codes and methods.

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
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... }
  }
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content to return |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "topic",
      "issue": "Topic must be at least 1 character",
      "location": "body"
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `PUZZLE_NOT_FOUND` | 404 | Puzzle ID not found |
| `GENERATION_FAILED` | 500 | Puzzle generation failed |
| `INVALID_PARAMETERS` | 400 | Invalid request parameters |
| `WORD_NOT_FOUND` | 404 | Word not found in puzzle |
| `SOLVE_FAILED` | 500 | AI solving failed |
| `HINT_GENERATION_FAILED` | 500 | Hint generation failed |
| `INTERNAL_ERROR` | 500 | Internal server error |

---

## Endpoints

### Health Check

#### Check API Health

```http
GET /api/health
```

Check if the API is running and healthy.

**Response: 200 OK**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-09-28T12:00:00Z",
  "services": {
    "api": "healthy",
    "llm": "healthy"
  }
}
```

**Response: 503 Service Unavailable**
```json
{
  "status": "unhealthy",
  "version": "1.0.0",
  "timestamp": "2026-09-28T12:00:00Z",
  "services": {
    "api": "healthy",
    "llm": "unavailable"
  }
}
```

---

### Puzzle Management

#### Generate Puzzle

```http
POST /api/puzzles/generate
```

Generate a new crossword puzzle based on a topic using AI.

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

**Request Parameters:**

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `topic` | string | Yes | - | 1-100 chars | Topic for puzzle generation |
| `grid_size` | integer | No | 8 | 4-20 | Grid size (N×N) |
| `min_words` | integer | No | 8 | ≥4 | Minimum number of words |
| `max_words` | integer | No | 15 | ≥4 | Maximum number of words |
| `difficulty` | string | No | "medium" | easy/medium/hard | Difficulty level |
| `max_iterations` | integer | No | 50 | 1-100 | Maximum generation iterations |

**Response: 201 Created**
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
        "value": "S",
        "is_blocked": false,
        "number": 1
      }
      // ... more cells
    ],
    "clues_across": [
      {
        "number": 1,
        "direction": "across",
        "text": "Study of the natural world",
        "answer": "SCIENCE",
        "start_row": 0,
        "start_col": 0,
        "length": 7
      }
    ],
    "clues_down": [
      {
        "number": 2,
        "direction": "down",
        "text": "Smallest unit of matter",
        "answer": "ATOM",
        "start_row": 0,
        "start_col": 1,
        "length": 4
      }
    ],
    "word_count": 10,
    "fill_rate": 0.65,
    "difficulty": "medium",
    "created_at": "2026-09-28T12:00:00Z",
    "metadata": {
      "generation_time": 45.2,
      "iterations": 12,
      "llm_model": "gpt-4-turbo-preview"
    }
  },
  "status": "completed",
  "iterations": 12,
  "error_message": null
}
```

**Response: 400 Bad Request**
```json
{
  "error": {
    "code": "INVALID_PARAMETERS",
    "message": "Invalid request parameters",
    "details": {
      "min_words": "Must be less than or equal to max_words"
    }
  }
}
```

**Response: 500 Internal Server Error**
```json
{
  "success": false,
  "puzzle": null,
  "status": "failed",
  "iterations": 50,
  "error_message": "Failed to generate puzzle: Maximum iterations reached"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/puzzles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Science",
    "grid_size": 8,
    "min_words": 8,
    "max_words": 12,
    "difficulty": "medium"
  }'
```

---

#### Get Puzzle by ID

```http
GET /api/puzzles/{puzzle_id}
```

Retrieve a previously generated puzzle by its unique identifier.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `puzzle_id` | string (UUID) | Yes | Unique puzzle identifier |

**Response: 200 OK**
```json
{
  "puzzle_id": "550e8400-e29b-41d4-a716-446655440000",
  "topic": "Science",
  "grid_size": 8,
  "cells": [ ... ],
  "clues_across": [ ... ],
  "clues_down": [ ... ],
  "word_count": 10,
  "fill_rate": 0.65,
  "difficulty": "medium",
  "created_at": "2026-09-28T12:00:00Z",
  "metadata": { ... }
}
```

**Response: 404 Not Found**
```json
{
  "error": {
    "code": "PUZZLE_NOT_FOUND",
    "message": "Puzzle not found: 550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Example:**
```bash
curl http://localhost:8000/api/puzzles/550e8400-e29b-41d4-a716-446655440000
```

---

#### List All Puzzles

```http
GET /api/puzzles
```

Get a list of all generated puzzles, sorted by creation time (newest first).

**Response: 200 OK**
```json
[
  {
    "puzzle_id": "550e8400-e29b-41d4-a716-446655440000",
    "topic": "Science",
    "grid_size": 8,
    "word_count": 10,
    "fill_rate": 0.65,
    "difficulty": "medium",
    "created_at": "2026-09-28T12:00:00Z"
  },
  {
    "puzzle_id": "660e8400-e29b-41d4-a716-446655440001",
    "topic": "History",
    "grid_size": 8,
    "word_count": 12,
    "fill_rate": 0.70,
    "difficulty": "hard",
    "created_at": "2026-09-28T11:00:00Z"
  }
]
```

**Example:**
```bash
curl http://localhost:8000/api/puzzles
```

---

#### Delete Puzzle

```http
DELETE /api/puzzles/{puzzle_id}
```

Delete a puzzle from storage.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `puzzle_id` | string (UUID) | Yes | Unique puzzle identifier |

**Response: 204 No Content**

No response body.

**Response: 404 Not Found**
```json
{
  "error": {
    "code": "PUZZLE_NOT_FOUND",
    "message": "Puzzle not found: 550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/puzzles/550e8400-e29b-41d4-a716-446655440000
```

---

### Puzzle Solving

#### Solve Entire Puzzle

```http
POST /api/puzzles/{puzzle_id}/solve
```

Use AI to solve the entire crossword puzzle.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `puzzle_id` | string (UUID) | Yes | Unique puzzle identifier |

**Request Body:**
```json
{
  "use_hints": true
}
```

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `use_hints` | boolean | No | true | Whether to use existing clues as hints |

**Response: 200 OK**
```json
{
  "success": true,
  "answer": null,
  "confidence": 0.95,
  "reasoning": "Solved all words using AI based on clues and intersections",
  "updated_cells": [
    {
      "row": 0,
      "col": 0,
      "value": "S",
      "is_blocked": false,
      "number": 1
    }
    // ... all cells with solutions
  ]
}
```

**Response: 404 Not Found**
```json
{
  "error": {
    "code": "PUZZLE_NOT_FOUND",
    "message": "Puzzle not found: 550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Response: 500 Internal Server Error**
```json
{
  "success": false,
  "answer": null,
  "confidence": 0.0,
  "reasoning": null,
  "updated_cells": [],
  "error": "AI solving failed: OpenAI API error"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/puzzles/550e8400-e29b-41d4-a716-446655440000/solve \
  -H "Content-Type: application/json" \
  -d '{"use_hints": true}'
```

---

#### Solve Specific Word

```http
POST /api/puzzles/{puzzle_id}/solve-word
```

Use AI to solve a specific word in the puzzle.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `puzzle_id` | string (UUID) | Yes | Unique puzzle identifier |

**Request Body:**
```json
{
  "clue_number": 1,
  "direction": "across",
  "use_intersections": true
}
```

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `clue_number` | integer | Yes | - | Clue number to solve |
| `direction` | string | Yes | - | Direction: "across" or "down" |
| `use_intersections` | boolean | No | true | Use intersecting letters as hints |

**Response: 200 OK**
```json
{
  "success": true,
  "answer": "SCIENCE",
  "confidence": 0.98,
  "reasoning": "Solved based on clue 'Study of the natural world' and intersecting letters",
  "updated_cells": [
    {
      "row": 0,
      "col": 0,
      "value": "S",
      "is_blocked": false,
      "number": 1
    },
    {
      "row": 0,
      "col": 1,
      "value": "C",
      "is_blocked": false,
      "number": null
    }
    // ... cells for this word
  ]
}
```

**Response: 404 Not Found**
```json
{
  "error": {
    "code": "WORD_NOT_FOUND",
    "message": "Word not found: clue_number=1, direction=across"
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/puzzles/550e8400-e29b-41d4-a716-446655440000/solve-word \
  -H "Content-Type: application/json" \
  -d '{
    "clue_number": 1,
    "direction": "across",
    "use_intersections": true
  }'
```

---

#### Get Hint for Word

```http
POST /api/puzzles/{puzzle_id}/hint
```

Get an AI-generated hint to help solve a specific word.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `puzzle_id` | string (UUID) | Yes | Unique puzzle identifier |

**Request Body:**
```json
{
  "clue_number": 1,
  "direction": "across",
  "hint_type": "letter"
}
```

**Request Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `clue_number` | integer | Yes | - | Clue number for hint |
| `direction` | string | Yes | - | Direction: "across" or "down" |
| `hint_type` | string | No | "letter" | Type: "letter", "definition", or "synonym" |

**Hint Types:**

- **letter**: Reveal a single letter at a specific position
- **definition**: Provide an alternative definition or explanation
- **synonym**: Provide a synonym or related word

**Response: 200 OK (letter hint)**
```json
{
  "success": true,
  "hint": "The first letter is 'S'",
  "hint_type": "letter",
  "revealed_letter": "S",
  "position": 0
}
```

**Response: 200 OK (definition hint)**
```json
{
  "success": true,
  "hint": "This field includes physics, chemistry, and biology. It's a systematic study of the natural world.",
  "hint_type": "definition",
  "revealed_letter": null,
  "position": null
}
```

**Response: 200 OK (synonym hint)**
```json
{
  "success": true,
  "hint": "Think of words like 'knowledge', 'research', or 'study'",
  "hint_type": "synonym",
  "revealed_letter": null,
  "position": null
}
```

**Response: 404 Not Found**
```json
{
  "error": {
    "code": "WORD_NOT_FOUND",
    "message": "Word not found: clue_number=1, direction=across"
  }
}
```

**Example:**
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

#### Validate Solution

```http
POST /api/puzzles/{puzzle_id}/validate
```

Check if the user's solution is correct and get detailed feedback.

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `puzzle_id` | string (UUID) | Yes | Unique puzzle identifier |

**Request Body:**
```json
{
  "cells": [
    {
      "row": 0,
      "col": 0,
      "value": "S",
      "is_blocked": false,
      "number": 1
    },
    {
      "row": 0,
      "col": 1,
      "value": "C",
      "is_blocked": false,
      "number": null
    }
    // ... user's filled cells
  ]
}
```

**Response: 200 OK (valid solution)**
```json
{
  "is_valid": true,
  "is_complete": true,
  "errors": [],
  "correct_count": 64,
  "total_count": 64,
  "accuracy": 1.0
}
```

**Response: 200 OK (invalid solution)**
```json
{
  "is_valid": false,
  "is_complete": false,
  "errors": [
    {
      "row": 0,
      "col": 2,
      "expected": "I",
      "actual": "X",
      "message": "Incorrect letter at position (0, 2). Expected 'I', got 'X'"
    },
    {
      "row": 1,
      "col": 0,
      "expected": "T",
      "actual": null,
      "message": "Missing letter at position (1, 0). Expected 'T'"
    }
  ],
  "correct_count": 62,
  "total_count": 64,
  "accuracy": 0.96875
}
```

**Response: 404 Not Found**
```json
{
  "error": {
    "code": "PUZZLE_NOT_FOUND",
    "message": "Puzzle not found: 550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/puzzles/550e8400-e29b-41d4-a716-446655440000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "cells": [
      {"row": 0, "col": 0, "value": "S", "is_blocked": false, "number": 1},
      {"row": 0, "col": 1, "value": "C", "is_blocked": false, "number": null}
    ]
  }'
```

---

## Data Models

### Cell

Represents a single cell in the crossword grid.

```typescript
interface Cell {
  row: number;              // Row position (0-indexed)
  col: number;              // Column position (0-indexed)
  value: string | null;     // Letter in cell (uppercase A-Z) or null if empty
  is_blocked: boolean;      // Whether cell is a black square
  number: number | null;    // Clue number if cell starts a word
}
```

**Example:**
```json
{
  "row": 0,
  "col": 0,
  "value": "S",
  "is_blocked": false,
  "number": 1
}
```

---

### Clue

Represents a crossword clue with metadata.

```typescript
interface Clue {
  number: number;           // Clue number
  direction: 'across' | 'down';  // Word direction
  text: string;             // Clue text
  answer: string | null;    // Answer word (may be hidden)
  start_row: number;        // Starting row position
  start_col: number;        // Starting column position
  length: number;           // Length of answer
}
```

**Example:**
```json
{
  "number": 1,
  "direction": "across",
  "text": "Study of the natural world",
  "answer": "SCIENCE",
  "start_row": 0,
  "start_col": 0,
  "length": 7
}
```

---

### Puzzle

Complete puzzle data structure.

```typescript
interface Puzzle {
  puzzle_id: string;        // Unique identifier (UUID)
  topic: string;            // Puzzle topic
  grid_size: number;        // Grid size (N×N)
  cells: Cell[];            // All grid cells
  clues_across: Clue[];     // Across clues
  clues_down: Clue[];       // Down clues
  word_count: number;       // Number of words
  fill_rate: number;        // Grid fill rate (0.0-1.0)
  difficulty: string;       // Difficulty level
  created_at: string;       // ISO 8601 timestamp
  metadata: object;         // Additional metadata
}
```

---

### PuzzleGenerateRequest

Request for generating a new puzzle.

```typescript
interface PuzzleGenerateRequest {
  topic: string;                           // Required: 1-100 chars
  grid_size?: number;                      // Optional: 4-20, default 8
  min_words?: number;                      // Optional: ≥4, default 8
  max_words?: number;                      // Optional: ≥4, default 15
  difficulty?: 'easy' | 'medium' | 'hard'; // Optional: default 'medium'
  max_iterations?: number;                 // Optional: 1-100, default 50
}
```

---

### PuzzleGenerateResponse

Response from puzzle generation.

```typescript
interface PuzzleGenerateResponse {
  success: boolean;         // Whether generation succeeded
  puzzle: Puzzle | null;    // Generated puzzle (if successful)
  status: string;           // Status: 'completed', 'failed', etc.
  iterations: number;       // Number of iterations executed
  error_message: string | null;  // Error message (if failed)
}
```

---

### SolveResponse

Response from solve operations.

```typescript
interface SolveResponse {
  success: boolean;         // Whether solve succeeded
  answer: string | null;    // Answer word (for word solve)
  confidence: number;       // Confidence score (0.0-1.0)
  reasoning: string | null; // Explanation of solution
  updated_cells: Cell[];    // Cells with solutions
}
```

---

### HintResponse

Response from hint requests.

```typescript
interface HintResponse {
  success: boolean;         // Whether hint generation succeeded
  hint: string;             // Hint text
  hint_type: string;        // Type of hint provided
  revealed_letter: string | null;  // Revealed letter (if applicable)
  position: number | null;  // Position of revealed letter
}
```

---

### ValidateResponse

Response from solution validation.

```typescript
interface ValidateResponse {
  is_valid: boolean;        // Whether solution is valid
  is_complete: boolean;     // Whether puzzle is complete
  errors: ValidationError[]; // List of errors
  correct_count: number;    // Number of correct cells
  total_count: number;      // Total cells to fill
  accuracy: number;         // Accuracy (0.0-1.0)
}
```

---

### ValidationError

Details of a validation error.

```typescript
interface ValidationError {
  row: number;              // Row position of error
  col: number;              // Column position of error
  expected: string;         // Expected value
  actual: string | null;    // Actual value provided
  message: string;          // Error message
}
```

---

## Examples

### Complete Puzzle Generation Flow

```bash
#!/bin/bash

# 1. Generate puzzle
RESPONSE=$(curl -s -X POST http://localhost:8000/api/puzzles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Technology",
    "grid_size": 8,
    "min_words": 10,
    "max_words": 15,
    "difficulty": "medium"
  }')

# Extract puzzle ID
PUZZLE_ID=$(echo $RESPONSE | jq -r '.puzzle.puzzle_id')
echo "Generated puzzle: $PUZZLE_ID"

# 2. Get puzzle details
curl -s http://localhost:8000/api/puzzles/$PUZZLE_ID | jq '.'

# 3. Solve a specific word
curl -s -X POST http://localhost:8000/api/puzzles/$PUZZLE_ID/solve-word \
  -H "Content-Type: application/json" \
  -d '{
    "clue_number": 1,
    "direction": "across",
    "use_intersections": true
  }' | jq '.'

# 4. Get hint for a word
curl -s -X POST http://localhost:8000/api/puzzles/$PUZZLE_ID/hint \
  -H "Content-Type: application/json" \
  -d '{
    "clue_number": 2,
    "direction": "down",
    "hint_type": "letter"
  }' | jq '.'

# 5. Solve entire puzzle
curl -s -X POST http://localhost:8000/api/puzzles/$PUZZLE_ID/solve \
  -H "Content-Type: application/json" \
  -d '{"use_hints": true}' | jq '.'

# 6. Validate solution
curl -s -X POST http://localhost:8000/api/puzzles/$PUZZLE_ID/validate \
  -H "Content-Type: application/json" \
  -d @user_solution.json | jq '.'

# 7. Delete puzzle
curl -s -X DELETE http://localhost:8000/api/puzzles/$PUZZLE_ID
```

---

### Python Client Example

```python
import requests
from typing import Optional

class AIxWordClient:
    """Python client for AIxWord API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def generate_puzzle(
        self,
        topic: str,
        grid_size: int = 8,
        min_words: int = 8,
        max_words: int = 15,
        difficulty: str = "medium"
    ) -> dict:
        """Generate a new puzzle."""
        response = self.session.post(
            f"{self.base_url}/api/puzzles/generate",
            json={
                "topic": topic,
                "grid_size": grid_size,
                "min_words": min_words,
                "max_words": max_words,
                "difficulty": difficulty
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_puzzle(self, puzzle_id: str) -> dict:
        """Get puzzle by ID."""
        response = self.session.get(
            f"{self.base_url}/api/puzzles/{puzzle_id}"
        )
        response.raise_for_status()
        return response.json()
    
    def solve_puzzle(self, puzzle_id: str, use_hints: bool = True) -> dict:
        """Solve entire puzzle."""
        response = self.session.post(
            f"{self.base_url}/api/puzzles/{puzzle_id}/solve",
            json={"use_hints": use_hints}
        )
        response.raise_for_status()
        return response.json()
    
    def solve_word(
        self,
        puzzle_id: str,
        clue_number: int,
        direction: str,
        use_intersections: bool = True
    ) -> dict:
        """Solve specific word."""
        response = self.session.post(
            f"{self.base_url}/api/puzzles/{puzzle_id}/solve-word",
            json={
                "clue_number": clue_number,
                "direction": direction,
                "use_intersections": use_intersections
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_hint(
        self,
        puzzle_id: str,
        clue_number: int,
        direction: str,
        hint_type: str = "letter"
    ) -> dict:
        """Get hint for word."""
        response = self.session.post(
            f"{self.base_url}/api/puzzles/{puzzle_id}/hint",
            json={
                "clue_number": clue_number,
                "direction": direction,
                "hint_type": hint_type
            }
        )
        response.raise_for_status()
        return response.json()
    
    def validate_solution(self, puzzle_id: str, cells: list) -> dict:
        """Validate user solution."""
        response = self.session.post(
            f"{self.base_url}/api/puzzles/{puzzle_id}/validate",
            json={"cells": cells}
        )
        response.raise_for_status()
        return response.json()

# Usage example
if __name__ == "__main__":
    client = AIxWordClient()
    
    # Generate puzzle
    result = client.generate_puzzle(
        topic="Science",
        grid_size=8,
        min_words=10,
        difficulty="medium"
    )
    
    if result["success"]:
        puzzle_id = result["puzzle"]["puzzle_id"]
        print(f"Generated puzzle: {puzzle_id}")
        
        # Solve a word
        solution = client.solve_word(
            puzzle_id=puzzle_id,
            clue_number=1,
            direction="across"
        )
        print(f"Word solution: {solution['answer']}")
        
        # Get hint
        hint = client.get_hint(
            puzzle_id=puzzle_id,
            clue_number=2,
            direction="down",
            hint_type="letter"
        )
        print(f"Hint: {hint['hint']}")
```

---

### JavaScript/TypeScript Client Example

```typescript
import axios, { AxiosInstance } from 'axios';

interface PuzzleGenerateRequest {
  topic: string;
  grid_size?: number;
  min_words?: number;
  max_words?: number;
  difficulty?: 'easy' | 'medium' | 'hard';
}

interface PuzzleGenerateResponse {
  success: boolean;
  puzzle: Puzzle | null;
  status: string;
  iterations: number;
  error_message: string | null;
}

class AIxWordClient {
  private client: AxiosInstance;
  
  constructor(baseURL: string = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
  }
  
  async generatePuzzle(request: PuzzleGenerateRequest): Promise<PuzzleGenerateResponse> {
    const response = await this.client.post('/api/puzzles/generate', request);
    return response.data;
  }
  
  async getPuzzle(puzzleId: string): Promise<Puzzle> {
    const response = await this.client.get(`/api/puzzles/${puzzleId}`);
    return response.data;
  }
  
  async solvePuzzle(puzzleId: string, useHints: boolean = true): Promise<SolveResponse> {
    const response = await this.client.post(
      `/api/puzzles/${puzzleId}/solve`,
      { use_hints: useHints }
    );
    return response.data;
  }
  
  async solveWord(
    puzzleId: string,
    clueNumber: number,
    direction: 'across' | 'down',
    useIntersections: boolean = true
  ): Promise<SolveResponse> {
    const response = await this.client.post(
      `/api/puzzles/${puzzleId}/solve-word`,
      {
        clue_number: clueNumber,
        direction,
        use_intersections: useIntersections
      }
    );
    return response.data;
  }
  
  async getHint(
    puzzleId: string,
    clueNumber: number,
    direction: 'across' | 'down',
    hintType: 'letter' | 'definition' | 'synonym' = 'letter'
  ): Promise<HintResponse> {
    const response = await this.client.post(
      `/api/puzzles/${puzzleId}/hint`,
      {
        clue_number: clueNumber,
        direction,
        hint_type: hintType
      }
    );
    return response.data;
  }
  
  async validateSolution(puzzleId: string, cells: Cell[]): Promise<ValidateResponse> {
    const response = await this.client.post(
      `/api/puzzles/${puzzleId}/validate`,
      { cells }
    );
    return response.data;
  }
}

// Usage example
const client = new AIxWordClient();

async function main() {
  try {
    // Generate puzzle
    const result = await client.generatePuzzle({
      topic: 'Science',
      grid_size: 8,
      min_words: 10,
      difficulty: 'medium'
    });
    
    if (result.success && result.puzzle) {
      const puzzleId = result.puzzle.puzzle_id;
      console.log(`Generated puzzle: ${puzzleId}`);
      
      // Solve a word
      const solution = await client.solveWord(puzzleId, 1, 'across');
      console.log(`Word solution: ${solution.answer}`);
      
      // Get hint
      const hint = await client.getHint(puzzleId, 2, 'down', 'letter');
      console.log(`Hint: ${hint.hint}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

main();
```

---

## Rate Limiting

**Current Version**: No rate limiting

**Future Versions**: Will implement rate limiting

### Planned Rate Limits

- **Per Minute**: 60 requests
- **Per Hour**: 1000 requests
- **Per Day**: 10000 requests

### Rate Limit Headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640000000
```

### Rate Limit Exceeded Response

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "details": {
      "retry_after": 60,
      "limit": 60,
      "window": "minute"
    }
  }
}
```

---

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```typescript
try {
  const result = await client.generatePuzzle({ topic: 'Science' });
  if (result.success) {
    // Handle success
  } else {
    // Handle generation failure
    console.error(result.error_message);
  }
} catch (error) {
  if (axios.isAxiosError(error)) {
    // Handle HTTP errors
    console.error(error.response?.data);
  } else {
    // Handle other errors
    console.error(error);
  }
}
```

### 2. Timeouts

Set appropriate timeouts for long-running operations:

```typescript
const client = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 120000  // 2 minutes for puzzle generation
});
```

### 3. Retry Logic

Implement retry logic for transient failures:

```typescript
async function generatePuzzleWithRetry(
  request: PuzzleGenerateRequest,
  maxRetries: number = 3
): Promise<PuzzleGenerateResponse> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await client.generatePuzzle(request);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
  throw new Error('Max retries exceeded');
}
```

### 4. Caching

Cache puzzle data to reduce API calls:

```typescript
class CachedAIxWordClient extends AIxWordClient {
  private cache: Map<string, Puzzle> = new Map();
  
  async getPuzzle(puzzleId: string): Promise<Puzzle> {
    if (this.cache.has(puzzleId)) {
      return this.cache.get(puzzleId)!;
    }
    const puzzle = await super.getPuzzle(puzzleId);
    this.cache.set(puzzleId, puzzle);
    return puzzle;
  }
}
```

### 5. Validation

Validate inputs before sending requests:

```typescript
function validatePuzzleRequest(request: PuzzleGenerateRequest): void {
  if (!request.topic || request.topic.length < 1) {
    throw new Error('Topic is required');
  }
  if (request.grid_size && (request.grid_size < 4 || request.grid_size > 20)) {
    throw new Error('Grid size must be between 4 and 20');
  }
  if (request.min_words && request.max_words && request.min_words > request.max_words) {
    throw new Error('min_words must be less than or equal to max_words');
  }
}
```

---

## Interactive Documentation

For interactive API documentation with try-it-out functionality:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Support

For questions or issues:
1. Check this documentation
2. Review the interactive API docs at `/docs`
3. Check the main project README
4. Review test files for usage examples

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-09-28 | Initial complete API documentation |

---

**End of API Reference**
