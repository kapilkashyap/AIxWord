"""
Integration tests for AI assistance features.

This module contains comprehensive integration tests for AI-powered features:
- Solving entire puzzles with AI
- Solving individual words with AI
- Generating hints for words
- Error handling and edge cases
- Performance and timeout handling

These tests use real HTTP requests to the FastAPI application and mock only
the LLM calls to ensure deterministic behavior without external API dependencies.
"""

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from backend.agents.orchestrator import PuzzleGenerationResult
from backend.api.main import app


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_puzzle_grid() -> dict[str, Any]:
    """Create a sample puzzle grid for AI assistance testing."""
    return {
        "size": 8,
        "cells": [
            # SCIENCE (across, row 0)
            {"row": 0, "col": 0, "value": "S", "is_blocked": False, "number": 1},
            {"row": 0, "col": 1, "value": "C", "is_blocked": False, "number": None},
            {"row": 0, "col": 2, "value": "I", "is_blocked": False, "number": None},
            {"row": 0, "col": 3, "value": "E", "is_blocked": False, "number": None},
            {"row": 0, "col": 4, "value": "N", "is_blocked": False, "number": None},
            {"row": 0, "col": 5, "value": "C", "is_blocked": False, "number": None},
            {"row": 0, "col": 6, "value": "E", "is_blocked": False, "number": None},
            # CELL (across, row 2)
            {"row": 2, "col": 0, "value": "C", "is_blocked": False, "number": 2},
            {"row": 2, "col": 1, "value": "E", "is_blocked": False, "number": None},
            {"row": 2, "col": 2, "value": "L", "is_blocked": False, "number": None},
            {"row": 2, "col": 3, "value": "L", "is_blocked": False, "number": None},
            # ATOM (down, col 0)
            {"row": 4, "col": 0, "value": "A", "is_blocked": False, "number": 3},
            {"row": 5, "col": 0, "value": "T", "is_blocked": False, "number": None},
            {"row": 6, "col": 0, "value": "O", "is_blocked": False, "number": None},
            {"row": 7, "col": 0, "value": "M", "is_blocked": False, "number": None},
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
            {
                "number": 2,
                "direction": "across",
                "word": "CELL",
                "clue": "Basic unit of life",
                "start_row": 2,
                "start_col": 0,
            },
            {
                "number": 3,
                "direction": "down",
                "word": "ATOM",
                "clue": "Smallest unit of matter",
                "start_row": 4,
                "start_col": 0,
            },
        ],
    }


@pytest.fixture
def mock_generation_result(sample_puzzle_grid):
    """Create a mock successful generation result."""
    return PuzzleGenerationResult(
        success=True,
        grid=sample_puzzle_grid,
        status="completed",
        word_count=3,
        fill_rate=0.65,
        iterations=5,
        error_message=None,
        metadata={"generation_time": 45.2},
    )


# ============================================================================
# AI Assistance Integration Tests
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
class TestAIAssistanceSolveWord:
    """Integration tests for AI-powered word solving."""

    async def test_solve_word_success(self, mock_generation_result, sample_puzzle_grid):
        """Test successful word solving with AI."""
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_generation_result

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # First, generate a puzzle
                response = await client.post(
                    "/api/puzzles/generate",
                    json={"topic": "Science", "grid_size": 8, "difficulty": "medium"},
                )
                assert response.status_code == 201
                puzzle_data = response.json()
                puzzle_id = puzzle_data["puzzle"]["puzzle_id"]

                # Mock the solver
                with patch(
                    "backend.api.routes.puzzles.PuzzleSolver.solve_word",
                    new_callable=AsyncMock,
                ) as mock_solve:
                    # Mock solver returns the word solution
                    mock_solve.return_value = (
                        "SCIENCE",
                        0.95,
                        "Solved based on clue and intersections",
                    )

                    # Solve a word
                    solve_response = await client.post(
                        f"/api/puzzles/{puzzle_id}/solve-word",
                        json={
                            "clue_number": 1,
                            "direction": "across",
                            "use_intersections": True,
                        },
                    )

                    assert solve_response.status_code == 200
                    solve_data = solve_response.json()

                    # Verify response structure
                    assert solve_data["success"] is True
                    assert solve_data["answer"] == "SCIENCE"
                    assert solve_data["confidence"] == 0.95
                    assert "reasoning" in solve_data
                    assert "updated_cells" in solve_data

                    # Verify updated cells
                    updated_cells = solve_data["updated_cells"]
                    assert len(updated_cells) == 7  # SCIENCE has 7 letters
                    assert all(cell["value"] in "SCIENCE" for cell in updated_cells)

    async def test_solve_word_not_found(self, mock_generation_result):
        """Test solving a word that doesn't exist."""
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_generation_result

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Generate a puzzle
                response = await client.post(
                    "/api/puzzles/generate",
                    json={"topic": "Science", "grid_size": 8, "difficulty": "medium"},
                )
                assert response.status_code == 201
                puzzle_id = response.json()["puzzle"]["puzzle_id"]

                # Try to solve non-existent word
                solve_response = await client.post(
                    f"/api/puzzles/{puzzle_id}/solve-word",
                    json={
                        "clue_number": 999,
                        "direction": "across",
                        "use_intersections": True,
                    },
                )

                assert solve_response.status_code == 404
                error_data = solve_response.json()
                assert "not found" in error_data["detail"].lower()

    async def test_solve_word_puzzle_not_found(self):
        """Test solving word for non-existent puzzle."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            solve_response = await client.post(
                "/api/puzzles/nonexistent-id/solve-word",
                json={
                    "clue_number": 1,
                    "direction": "across",
                    "use_intersections": True,
                },
            )

            assert solve_response.status_code == 404
            error_data = solve_response.json()
            assert "puzzle not found" in error_data["detail"].lower()

    async def test_solve_word_with_intersections(self, mock_generation_result):
        """Test solving word with intersection constraints."""
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_generation_result

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Generate a puzzle
                response = await client.post(
                    "/api/puzzles/generate",
                    json={"topic": "Science", "grid_size": 8, "difficulty": "medium"},
                )
                assert response.status_code == 201
                puzzle_id = response.json()["puzzle"]["puzzle_id"]

                # Mock the solver with intersections
                with patch(
                    "backend.api.routes.puzzles.PuzzleSolver.solve_word",
                    new_callable=AsyncMock,
                ) as mock_solve:
                    mock_solve.return_value = (
                        "CELL",
                        0.98,
                        "Solved using intersections with SCIENCE",
                    )

                    # Solve word with intersections
                    solve_response = await client.post(
                        f"/api/puzzles/{puzzle_id}/solve-word",
                        json={
                            "clue_number": 2,
                            "direction": "across",
                            "use_intersections": True,
                        },
                    )

                    assert solve_response.status_code == 200
                    solve_data = solve_response.json()
                    assert solve_data["success"] is True
                    assert solve_data["confidence"] >= 0.9
                    assert "intersection" in solve_data["reasoning"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
class TestAIAssistanceSolvePuzzle:
    """Integration tests for AI-powered full puzzle solving."""

    async def test_solve_puzzle_success(self, mock_generation_result, sample_puzzle_grid):
        """Test successful full puzzle solving with AI."""
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_generation_result

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Generate a puzzle
                response = await client.post(
                    "/api/puzzles/generate",
                    json={"topic": "Science", "grid_size": 8, "difficulty": "medium"},
                )
                assert response.status_code == 201
                puzzle_id = response.json()["puzzle"]["puzzle_id"]

                # Mock the solver
                with patch(
                    "backend.api.routes.puzzles.PuzzleSolver.solve_puzzle",
                    new_callable=AsyncMock,
                ) as mock_solve:
                    # Mock solver returns all cells
                    all_cells = sample_puzzle_grid["cells"]
                    mock_solve.return_value = (
                        all_cells,
                        0.92,
                        "Solved entire puzzle successfully",
                    )

                    # Solve entire puzzle
                    solve_response = await client.post(
                        f"/api/puzzles/{puzzle_id}/solve",
                        json={"use_hints": True},
                    )

                    assert solve_response.status_code == 200
                    solve_data = solve_response.json()

                    # Verify response structure
                    assert solve_data["success"] is True
                    assert solve_data["confidence"] >= 0.9
                    assert "reasoning" in solve_data
                    assert "updated_cells" in solve_data

                    # Verify all cells are returned
                    updated_cells = solve_data["updated_cells"]
                    assert len(updated_cells) > 0
                    assert all("row" in cell and "col" in cell for cell in updated_cells)

    async def test_solve_puzzle_not_found(self):
        """Test solving non-existent puzzle."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            solve_response = await client.post(
                "/api/puzzles/nonexistent-id/solve",
                json={"use_hints": True},
            )

            assert solve_response.status_code == 404
            error_data = solve_response.json()
            assert "puzzle not found" in error_data["detail"].lower()

    async def test_solve_puzzle_with_hints(self, mock_generation_result, sample_puzzle_grid):
        """Test solving puzzle with hints enabled."""
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_generation_result

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Generate a puzzle
                response = await client.post(
                    "/api/puzzles/generate",
                    json={"topic": "Science", "grid_size": 8, "difficulty": "medium"},
                )
                assert response.status_code == 201
                puzzle_id = response.json()["puzzle"]["puzzle_id"]

                # Mock the solver
                with patch(
                    "backend.api.routes.puzzles.PuzzleSolver.solve_puzzle",
                    new_callable=AsyncMock,
                ) as mock_solve:
                    mock_solve.return_value = (
                        sample_puzzle_grid["cells"],
                        0.95,
                        "Solved with hints for better accuracy",
                    )

                    # Solve with hints
                    solve_response = await client.post(
                        f"/api/puzzles/{puzzle_id}/solve",
                        json={"use_hints": True},
                    )

                    assert solve_response.status_code == 200
                    solve_data = solve_response.json()
                    assert solve_data["success"] is True
                    assert "hint" in solve_data["reasoning"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
class TestAIAssistanceHints:
    """Integration tests for AI-powered hint generation."""

    async def test_get_hint_definition(self, mock_generation_result):
        """Test getting a definition hint."""
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_generation_result

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Generate a puzzle
                response = await client.post(
                    "/api/puzzles/generate",
                    json={"topic": "Science", "grid_size": 8, "difficulty": "medium"},
                )
                assert response.status_code == 201
                puzzle_id = response.json()["puzzle"]["puzzle_id"]

                # Mock the hint generator
                with patch(
                    "backend.api.routes.puzzles.PuzzleSolver.generate_hint",
                    new_callable=AsyncMock,
                ) as mock_hint:
                    mock_hint.return_value = (
                        "Think about the systematic study of nature",
                        None,
                        None,
                    )

                    # Get definition hint
                    hint_response = await client.post(
                        f"/api/puzzles/{puzzle_id}/hint",
                        json={
                            "clue_number": 1,
                            "direction": "across",
                            "hint_type": "definition",
                        },
                    )

                    assert hint_response.status_code == 200
                    hint_data = hint_response.json()

                    # Verify response structure
                    assert hint_data["success"] is True
                    assert "hint" in hint_data
                    assert hint_data["hint_type"] == "definition"
                    assert len(hint_data["hint"]) > 0

    async def test_get_hint_letter(self, mock_generation_result):
        """Test getting a letter hint."""
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_generation_result

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Generate a puzzle
                response = await client.post(
                    "/api/puzzles/generate",
                    json={"topic": "Science", "grid_size": 8, "difficulty": "medium"},
                )
                assert response.status_code == 201
                puzzle_id = response.json()["puzzle"]["puzzle_id"]

                # Mock the hint generator
                with patch(
                    "backend.api.routes.puzzles.PuzzleSolver.generate_hint",
                    new_callable=AsyncMock,
                ) as mock_hint:
                    mock_hint.return_value = (
                        "The first letter is S",
                        "S",
                        0,
                    )

                    # Get letter hint
                    hint_response = await client.post(
                        f"/api/puzzles/{puzzle_id}/hint",
                        json={
                            "clue_number": 1,
                            "direction": "across",
                            "hint_type": "letter",
                        },
                    )

                    assert hint_response.status_code == 200
                    hint_data = hint_response.json()

                    # Verify response structure
                    assert hint_data["success"] is True
                    assert hint_data["hint_type"] == "letter"
                    assert hint_data["revealed_letter"] == "S"
                    assert hint_data["position"] == 0

    async def test_get_hint_synonym(self, mock_generation_result):
        """Test getting a synonym hint."""
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_generation_result

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Generate a puzzle
                response = await client.post(
                    "/api/puzzles/generate",
                    json={"topic": "Science", "grid_size": 8, "difficulty": "medium"},
                )
                assert response.status_code == 201
                puzzle_id = response.json()["puzzle"]["puzzle_id"]

                # Mock the hint generator
                with patch(
                    "backend.api.routes.puzzles.PuzzleSolver.generate_hint",
                    new_callable=AsyncMock,
                ) as mock_hint:
                    mock_hint.return_value = (
                        "Another word for this could be 'knowledge' or 'learning'",
                        None,
                        None,
                    )

                    # Get synonym hint
                    hint_response = await client.post(
                        f"/api/puzzles/{puzzle_id}/hint",
                        json={
                            "clue_number": 1,
                            "direction": "across",
                            "hint_type": "synonym",
                        },
                    )

                    assert hint_response.status_code == 200
                    hint_data = hint_response.json()
                    assert hint_data["success"] is True
                    assert hint_data["hint_type"] == "synonym"

    async def test_get_hint_word_not_found(self, mock_generation_result):
        """Test getting hint for non-existent word."""
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_generation_result

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Generate a puzzle
                response = await client.post(
                    "/api/puzzles/generate",
                    json={"topic": "Science", "grid_size": 8, "difficulty": "medium"},
                )
                assert response.status_code == 201
                puzzle_id = response.json()["puzzle"]["puzzle_id"]

                # Try to get hint for non-existent word
                hint_response = await client.post(
                    f"/api/puzzles/{puzzle_id}/hint",
                    json={
                        "clue_number": 999,
                        "direction": "across",
                        "hint_type": "definition",
                    },
                )

                assert hint_response.status_code == 404
                error_data = hint_response.json()
                assert "not found" in error_data["detail"].lower()

    async def test_get_hint_puzzle_not_found(self):
        """Test getting hint for non-existent puzzle."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            hint_response = await client.post(
                "/api/puzzles/nonexistent-id/hint",
                json={
                    "clue_number": 1,
                    "direction": "across",
                    "hint_type": "definition",
                },
            )

            assert hint_response.status_code == 404
            error_data = hint_response.json()
            assert "puzzle not found" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
class TestAIAssistanceErrorHandling:
    """Integration tests for AI assistance error handling."""

    async def test_solve_word_solver_failure(self, mock_generation_result):
        """Test handling of solver failures."""
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_generation_result

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Generate a puzzle
                response = await client.post(
                    "/api/puzzles/generate",
                    json={"topic": "Science", "grid_size": 8, "difficulty": "medium"},
                )
                assert response.status_code == 201
                puzzle_id = response.json()["puzzle"]["puzzle_id"]

                # Mock solver to raise exception
                with patch(
                    "backend.api.routes.puzzles.PuzzleSolver.solve_word",
                    new_callable=AsyncMock,
                ) as mock_solve:
                    mock_solve.side_effect = Exception("Solver failed")

                    # Try to solve word
                    solve_response = await client.post(
                        f"/api/puzzles/{puzzle_id}/solve-word",
                        json={
                            "clue_number": 1,
                            "direction": "across",
                            "use_intersections": True,
                        },
                    )

                    assert solve_response.status_code == 500
                    error_data = solve_response.json()
                    assert "failed" in error_data["detail"].lower()

    async def test_hint_generation_failure(self, mock_generation_result):
        """Test handling of hint generation failures."""
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_generation_result

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Generate a puzzle
                response = await client.post(
                    "/api/puzzles/generate",
                    json={"topic": "Science", "grid_size": 8, "difficulty": "medium"},
                )
                assert response.status_code == 201
                puzzle_id = response.json()["puzzle"]["puzzle_id"]

                # Mock hint generator to raise exception
                with patch(
                    "backend.api.routes.puzzles.PuzzleSolver.generate_hint",
                    new_callable=AsyncMock,
                ) as mock_hint:
                    mock_hint.side_effect = Exception("Hint generation failed")

                    # Try to get hint
                    hint_response = await client.post(
                        f"/api/puzzles/{puzzle_id}/hint",
                        json={
                            "clue_number": 1,
                            "direction": "across",
                            "hint_type": "definition",
                        },
                    )

                    assert hint_response.status_code == 500
                    error_data = hint_response.json()
                    assert "failed" in error_data["detail"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
class TestAIAssistancePerformance:
    """Integration tests for AI assistance performance."""

    async def test_solve_word_response_time(self, mock_generation_result):
        """Test that solve word responds within reasonable time."""
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_generation_result

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Generate a puzzle
                response = await client.post(
                    "/api/puzzles/generate",
                    json={"topic": "Science", "grid_size": 8, "difficulty": "medium"},
                )
                assert response.status_code == 201
                puzzle_id = response.json()["puzzle"]["puzzle_id"]

                # Mock fast solver
                with patch(
                    "backend.api.routes.puzzles.PuzzleSolver.solve_word",
                    new_callable=AsyncMock,
                ) as mock_solve:
                    mock_solve.return_value = ("SCIENCE", 0.95, "Solved")

                    # Measure response time
                    import time
                    start_time = time.time()

                    solve_response = await client.post(
                        f"/api/puzzles/{puzzle_id}/solve-word",
                        json={
                            "clue_number": 1,
                            "direction": "across",
                            "use_intersections": True,
                        },
                    )

                    end_time = time.time()
                    duration = end_time - start_time

                    assert solve_response.status_code == 200
                    # Should respond within 5 seconds (with mocked solver)
                    assert duration < 5.0

    async def test_concurrent_ai_operations(self, mock_generation_result):
        """Test handling of concurrent AI operations."""
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_generation_result

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Generate a puzzle
                response = await client.post(
                    "/api/puzzles/generate",
                    json={"topic": "Science", "grid_size": 8, "difficulty": "medium"},
                )
                assert response.status_code == 201
                puzzle_id = response.json()["puzzle"]["puzzle_id"]

                # Mock solver and hint generator
                with patch(
                    "backend.api.routes.puzzles.PuzzleSolver.solve_word",
                    new_callable=AsyncMock,
                ) as mock_solve, patch(
                    "backend.api.routes.puzzles.PuzzleSolver.generate_hint",
                    new_callable=AsyncMock,
                ) as mock_hint:
                    mock_solve.return_value = ("SCIENCE", 0.95, "Solved")
                    mock_hint.return_value = ("Hint text", None, None)

                    # Make concurrent requests
                    tasks = [
                        client.post(
                            f"/api/puzzles/{puzzle_id}/solve-word",
                            json={
                                "clue_number": 1,
                                "direction": "across",
                                "use_intersections": True,
                            },
                        ),
                        client.post(
                            f"/api/puzzles/{puzzle_id}/hint",
                            json={
                                "clue_number": 2,
                                "direction": "across",
                                "hint_type": "definition",
                            },
                        ),
                    ]

                    responses = await asyncio.gather(*tasks)

                    # Both should succeed
                    assert all(r.status_code == 200 for r in responses)
