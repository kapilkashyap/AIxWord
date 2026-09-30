"""
End-to-End Integration Tests for AIxWord Application.

This module contains comprehensive end-to-end tests that verify the complete
user workflow through the AIxWord application. These tests exercise the full
stack from API endpoints through agents to domain models, ensuring all
components work together correctly.

Test Coverage:
- Complete puzzle generation workflow (topic → agents → grid → API response)
- Puzzle retrieval and listing operations
- AI-powered solving (full puzzle and individual words)
- Hint generation and validation
- Error handling and edge cases
- Multi-puzzle scenarios
- Concurrent operations
- State management across operations

These tests use real HTTP requests to the FastAPI application and mock only
the LLM calls to ensure deterministic behavior without external API dependencies.
"""

import asyncio
import json
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
def sample_science_grid_dict() -> dict[str, Any]:
    """Create a sample science-themed grid dictionary for testing."""
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
            # GENE (across, row 4)
            {"row": 4, "col": 1, "value": "G", "is_blocked": False, "number": None},
            {"row": 4, "col": 2, "value": "E", "is_blocked": False, "number": None},
            {"row": 4, "col": 3, "value": "N", "is_blocked": False, "number": None},
            {"row": 4, "col": 4, "value": "E", "is_blocked": False, "number": None},
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
            {
                "number": 3,
                "direction": "across",
                "word": "AGENE",
                "clue": "Unit of heredity",
                "start_row": 4,
                "start_col": 0,
            },
        ],
    }


@pytest.fixture
def mock_successful_generation(sample_science_grid_dict) -> PuzzleGenerationResult:
    """Create a mock successful puzzle generation result."""
    return PuzzleGenerationResult(
        success=True,
        grid=sample_science_grid_dict,
        status="completed",
        word_count=4,
        fill_rate=0.28,
        iterations=8,
        error_message=None,
        metadata={
            "generation_time": 42.5,
            "planner_iterations": 5,
            "executor_iterations": 3,
        },
    )


@pytest.fixture
def mock_failed_generation() -> PuzzleGenerationResult:
    """Create a mock failed puzzle generation result."""
    return PuzzleGenerationResult(
        success=False,
        grid=None,
        status="failed",
        word_count=0,
        fill_rate=0.0,
        iterations=50,
        error_message="Failed to generate puzzle: insufficient valid words found for topic",
        metadata={"max_iterations_reached": True},
    )


@pytest.fixture
def mock_llm_solve_word_response() -> dict[str, Any]:
    """Create a mock LLM response for word solving."""
    return {
        "answer": "SCIENCE",
        "confidence": 0.95,
        "reasoning": "The clue 'Study of the natural world' directly refers to science, which is a 7-letter word matching the pattern.",
    }


@pytest.fixture
def mock_llm_hint_response() -> dict[str, Any]:
    """Create a mock LLM response for hint generation."""
    return {
        "hint": "Think about the systematic study of the physical and natural world",
        "hint_type": "definition",
        "confidence": 0.9,
    }


@pytest.fixture
async def async_client() -> AsyncClient:
    """Create an async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(autouse=True)
def clear_puzzle_storage():
    """Clear puzzle storage before each test."""
    from backend.api.routes.puzzles import _puzzle_storage
    _puzzle_storage.clear()
    yield
    _puzzle_storage.clear()


# ============================================================================
# E2E Test Suite: Complete User Workflows
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
class TestCompleteUserWorkflow:
    """
    End-to-end tests for complete user workflows.

    These tests simulate real user interactions from start to finish,
    verifying that all components work together correctly.
    """

    async def test_full_puzzle_lifecycle(
        self,
        async_client: AsyncClient,
        mock_successful_generation: PuzzleGenerationResult,
    ):
        """
        Test complete puzzle lifecycle: generate → retrieve → solve → validate.

        This test simulates a user:
        1. Generating a new puzzle on a topic
        2. Retrieving the puzzle details
        3. Attempting to solve words
        4. Validating the solution
        """
        # Step 1: Generate puzzle
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle_async",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_successful_generation

            gen_response = await async_client.post(
                "/api/puzzles/generate",
                json={
                    "topic": "Science",
                    "grid_size": 8,
                    "min_words": 4,
                    "max_words": 10,
                    "difficulty": "medium",
                    "max_iterations": 50,
                },
            )

        # Verify generation response
        assert gen_response.status_code == 201
        gen_data = gen_response.json()
        assert gen_data["success"] is True
        assert gen_data["puzzle"] is not None

        puzzle_id = gen_data["puzzle"]["puzzle_id"]
        assert puzzle_id is not None
        assert gen_data["puzzle"]["topic"] == "Science"
        assert gen_data["puzzle"]["grid_size"] == 8
        assert gen_data["puzzle"]["word_count"] == 4
        assert gen_data["status"] == "completed"
        assert gen_data["iterations"] == 8

        # Verify puzzle structure
        puzzle = gen_data["puzzle"]
        assert len(puzzle["cells"]) > 0
        assert len(puzzle["clues_across"]) > 0
        assert puzzle["fill_rate"] > 0.0
        assert "created_at" in puzzle

        # Step 2: Retrieve puzzle
        get_response = await async_client.get(f"/api/puzzles/{puzzle_id}")
        assert get_response.status_code == 200

        retrieved_puzzle = get_response.json()
        assert retrieved_puzzle["puzzle_id"] == puzzle_id
        assert retrieved_puzzle["topic"] == "Science"
        assert retrieved_puzzle["word_count"] == puzzle["word_count"]

        # Step 3: Solve a word with AI
        with patch(
            "backend.llm.client.LLMClient.chat_completion_async",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(
                    message=MagicMock(
                        content=json.dumps({
                            "answer": "SCIENCE",
                            "confidence": 0.95,
                            "reasoning": "Study of natural world",
                        })
                    )
                )
            ]
            mock_llm.return_value = mock_response

            solve_response = await async_client.post(
                f"/api/puzzles/{puzzle_id}/solve-word",
                json={"clue_number": 1, "direction": "across"},
            )

        assert solve_response.status_code == 200
        solve_data = solve_response.json()
        assert solve_data["success"] is True
        assert solve_data["answer"] == "SCIENCE"
        assert solve_data["confidence"] > 0.0
        assert "reasoning" in solve_data

        # Step 4: Validate solution
        validate_response = await async_client.post(
            f"/api/puzzles/{puzzle_id}/validate",
            json={
                "cells": [
                    {"row": 0, "col": 0, "value": "S"},
                    {"row": 0, "col": 1, "value": "C"},
                    {"row": 0, "col": 2, "value": "I"},
                    {"row": 0, "col": 3, "value": "E"},
                    {"row": 0, "col": 4, "value": "N"},
                    {"row": 0, "col": 5, "value": "C"},
                    {"row": 0, "col": 6, "value": "E"},
                ]
            },
        )

        assert validate_response.status_code == 200
        validate_data = validate_response.json()
        assert validate_data["is_valid"] is True
        assert validate_data["correct_count"] > 0

    async def test_puzzle_generation_with_hints_workflow(
        self,
        async_client: AsyncClient,
        mock_successful_generation: PuzzleGenerationResult,
    ):
        """
        Test workflow: generate puzzle → get stuck → request hints → solve.

        Simulates a user who needs help solving the puzzle.
        """
        # Generate puzzle
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle_async",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_successful_generation

            gen_response = await async_client.post(
                "/api/puzzles/generate",
                json={
                    "topic": "Science",
                    "grid_size": 8,
                    "min_words": 4,
                    "max_words": 10,
                },
            )

        assert gen_response.status_code == 201
        puzzle_id = gen_response.json()["puzzle"]["puzzle_id"]

        # Request hint for a clue
        with patch(
            "backend.llm.client.LLMClient.chat_completion_async",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(
                    message=MagicMock(
                        content=json.dumps({
                            "hint": "Think about systematic study of nature",
                            "hint_type": "definition",
                            "confidence": 0.9,
                        })
                    )
                )
            ]
            mock_llm.return_value = mock_response

            hint_response = await async_client.post(
                f"/api/puzzles/{puzzle_id}/hint",
                json={
                    "clue_number": 1,
                    "direction": "across",
                    "hint_type": "definition",
                },
            )

        assert hint_response.status_code == 200
        hint_data = hint_response.json()
        assert hint_data["success"] is True
        assert "hint" in hint_data
        assert len(hint_data["hint"]) > 0
        assert hint_data["hint_type"] == "definition"

        # After getting hint, solve the word
        with patch(
            "backend.llm.client.LLMClient.chat_completion_async",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(
                    message=MagicMock(
                        content=json.dumps({
                            "answer": "SCIENCE",
                            "confidence": 0.95,
                            "reasoning": "Based on the hint about systematic study",
                        })
                    )
                )
            ]
            mock_llm.return_value = mock_response

            solve_response = await async_client.post(
                f"/api/puzzles/{puzzle_id}/solve-word",
                json={"clue_number": 1, "direction": "across"},
            )

        assert solve_response.status_code == 200
        assert solve_response.json()["answer"] == "SCIENCE"

    async def test_multiple_puzzles_workflow(
        self,
        async_client: AsyncClient,
        mock_successful_generation: PuzzleGenerationResult,
    ):
        """
        Test managing multiple puzzles: generate several → list → retrieve each.

        Simulates a user creating and managing multiple puzzles.
        """
        puzzle_ids = []

        # Generate 3 puzzles with different topics
        topics = ["Science", "History", "Technology"]

        for topic in topics:
            with patch(
                "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle_async",
                new_callable=AsyncMock,
            ) as mock_generate:
                # Customize grid for each topic
                custom_grid = dict(mock_successful_generation.grid)
                custom_grid["words"][0]["clue"] = f"{topic} related clue"

                custom_result = PuzzleGenerationResult(
                    success=True,
                    grid=custom_grid,
                    status="completed",
                    word_count=4,
                    fill_rate=0.28,
                    iterations=8,
                    error_message=None,
                    metadata={},
                )
                mock_generate.return_value = custom_result

                response = await async_client.post(
                    "/api/puzzles/generate",
                    json={
                        "topic": topic,
                        "grid_size": 8,
                        "min_words": 4,
                        "max_words": 10,
                    },
                )

            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            puzzle_ids.append(data["puzzle"]["puzzle_id"])

        # List all puzzles
        list_response = await async_client.get("/api/puzzles/")
        assert list_response.status_code == 200

        puzzles_list = list_response.json()
        assert isinstance(puzzles_list, list)
        assert len(puzzles_list) == 3

        # Verify each puzzle can be retrieved
        for puzzle_id in puzzle_ids:
            get_response = await async_client.get(f"/api/puzzles/{puzzle_id}")
            assert get_response.status_code == 200
            puzzle = get_response.json()
            assert puzzle["puzzle_id"] == puzzle_id
            assert puzzle["topic"] in topics

    async def test_solve_entire_puzzle_workflow(
        self,
        async_client: AsyncClient,
        mock_successful_generation: PuzzleGenerationResult,
    ):
        """
        Test solving entire puzzle at once with AI assistance.

        Simulates a user requesting AI to solve the complete puzzle.
        """
        # Generate puzzle
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle_async",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_successful_generation

            gen_response = await async_client.post(
                "/api/puzzles/generate",
                json={
                    "topic": "Science",
                    "grid_size": 8,
                    "min_words": 4,
                    "max_words": 10,
                },
            )

        puzzle_id = gen_response.json()["puzzle"]["puzzle_id"]

        # Solve entire puzzle
        with patch(
            "backend.llm.client.LLMClient.chat_completion_async",
            new_callable=AsyncMock,
        ) as mock_llm:
            # Mock multiple LLM calls for each word
            mock_responses = []
            words = ["SCIENCE", "CELL", "ATOM", "AGENE"]

            for word in words:
                mock_resp = MagicMock()
                mock_resp.choices = [
                    MagicMock(
                        message=MagicMock(
                            content=json.dumps({
                                "answer": word,
                                "confidence": 0.9,
                                "reasoning": f"Solved {word}",
                            })
                        )
                    )
                ]
                mock_responses.append(mock_resp)

            mock_llm.side_effect = mock_responses

            solve_response = await async_client.post(
                f"/api/puzzles/{puzzle_id}/solve",
                json={"strategy": "complete"},
            )

        assert solve_response.status_code == 200
        solve_data = solve_response.json()
        assert solve_data["success"] is True
        assert "updated_cells" in solve_data
        assert len(solve_data["updated_cells"]) > 0


@pytest.mark.asyncio
@pytest.mark.integration
class TestErrorHandlingE2E:
    """
    End-to-end tests for error handling and edge cases.

    These tests verify that the system handles errors gracefully
    and provides meaningful feedback to users.
    """

    async def test_invalid_puzzle_generation_request(self, async_client: AsyncClient):
        """Test error handling for invalid puzzle generation requests."""
        # Empty topic
        response = await async_client.post(
            "/api/puzzles/generate",
            json={
                "topic": "",
                "grid_size": 8,
                "min_words": 4,
                "max_words": 10,
            },
        )
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

        # Invalid grid size
        response = await async_client.post(
            "/api/puzzles/generate",
            json={
                "topic": "Science",
                "grid_size": 2,  # Too small
                "min_words": 4,
                "max_words": 10,
            },
        )
        assert response.status_code == 422

        # Min words > max words
        response = await async_client.post(
            "/api/puzzles/generate",
            json={
                "topic": "Science",
                "grid_size": 8,
                "min_words": 20,
                "max_words": 10,
            },
        )
        # Should be caught by validation or orchestrator
        assert response.status_code in [400, 422]

    async def test_puzzle_generation_failure_handling(
        self,
        async_client: AsyncClient,
        mock_failed_generation: PuzzleGenerationResult,
    ):
        """Test handling of puzzle generation failures."""
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle_async",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_failed_generation

            response = await async_client.post(
                "/api/puzzles/generate",
                json={
                    "topic": "VeryObscureTopic",
                    "grid_size": 8,
                    "min_words": 4,
                    "max_words": 10,
                },
            )

        # Should return 201 but with success=False
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is False
        assert data["puzzle"] is None
        assert data["error_message"] is not None
        assert "failed" in data["error_message"].lower() or "insufficient" in data["error_message"].lower()

    async def test_nonexistent_puzzle_operations(self, async_client: AsyncClient):
        """Test operations on non-existent puzzles."""
        fake_id = "nonexistent-puzzle-id"

        # Get puzzle
        response = await async_client.get(f"/api/puzzles/{fake_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

        # Solve word
        response = await async_client.post(
            f"/api/puzzles/{fake_id}/solve-word",
            json={"clue_number": 1, "direction": "across"},
        )
        assert response.status_code == 404

        # Get hint
        response = await async_client.post(
            f"/api/puzzles/{fake_id}/hint",
            json={"clue_number": 1, "direction": "across"},
        )
        assert response.status_code == 404

        # Validate solution
        response = await async_client.post(
            f"/api/puzzles/{fake_id}/validate",
            json={"cells": []},
        )
        assert response.status_code == 404

    async def test_invalid_solve_requests(
        self,
        async_client: AsyncClient,
        mock_successful_generation: PuzzleGenerationResult,
    ):
        """Test error handling for invalid solve requests."""
        # First create a puzzle
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle_async",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_successful_generation

            gen_response = await async_client.post(
                "/api/puzzles/generate",
                json={"topic": "Science", "grid_size": 8, "min_words": 4, "max_words": 10},
            )

        puzzle_id = gen_response.json()["puzzle"]["puzzle_id"]

        # Invalid clue number
        response = await async_client.post(
            f"/api/puzzles/{puzzle_id}/solve-word",
            json={"clue_number": 999, "direction": "across"},
        )
        assert response.status_code in [400, 404]

        # Invalid direction
        response = await async_client.post(
            f"/api/puzzles/{puzzle_id}/solve-word",
            json={"clue_number": 1, "direction": "diagonal"},
        )
        assert response.status_code == 422

    async def test_llm_failure_handling(
        self,
        async_client: AsyncClient,
        mock_successful_generation: PuzzleGenerationResult,
    ):
        """Test handling of LLM API failures during solving."""
        # Generate puzzle
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle_async",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_successful_generation

            gen_response = await async_client.post(
                "/api/puzzles/generate",
                json={"topic": "Science", "grid_size": 8, "min_words": 4, "max_words": 10},
            )

        puzzle_id = gen_response.json()["puzzle"]["puzzle_id"]

        # Mock LLM failure
        with patch(
            "backend.llm.client.LLMClient.chat_completion_async",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.side_effect = Exception("LLM API error")

            response = await async_client.post(
                f"/api/puzzles/{puzzle_id}/solve-word",
                json={"clue_number": 1, "direction": "across"},
            )

        # Should handle error gracefully - solver returns fallback answer with low confidence
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Fallback answer should have very low confidence
        assert data["confidence"] == 0.0
        # Reasoning should indicate an error
        assert "error" in data["reasoning"].lower()


@pytest.mark.asyncio
@pytest.mark.integration
class TestConcurrentOperations:
    """
    End-to-end tests for concurrent operations.

    These tests verify that the system handles multiple simultaneous
    requests correctly without race conditions or data corruption.
    """

    async def test_concurrent_puzzle_generation(
        self,
        async_client: AsyncClient,
        mock_successful_generation: PuzzleGenerationResult,
    ):
        """Test generating multiple puzzles concurrently."""
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle_async",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_successful_generation

            # Create 5 concurrent generation requests
            tasks = []
            for i in range(5):
                task = async_client.post(
                    "/api/puzzles/generate",
                    json={
                        "topic": f"Topic{i}",
                        "grid_size": 8,
                        "min_words": 4,
                        "max_words": 10,
                    },
                )
                tasks.append(task)

            # Execute concurrently
            responses = await asyncio.gather(*tasks)

        # Verify all succeeded
        puzzle_ids = set()
        for response in responses:
            assert response.status_code == 201
            data = response.json()
            assert data["success"] is True
            puzzle_ids.add(data["puzzle"]["puzzle_id"])

        # Verify all puzzles have unique IDs
        assert len(puzzle_ids) == 5

    async def test_concurrent_operations_on_same_puzzle(
        self,
        async_client: AsyncClient,
        mock_successful_generation: PuzzleGenerationResult,
    ):
        """Test concurrent operations on the same puzzle."""
        # Generate puzzle
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle_async",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_successful_generation

            gen_response = await async_client.post(
                "/api/puzzles/generate",
                json={"topic": "Science", "grid_size": 8, "min_words": 4, "max_words": 10},
            )

        puzzle_id = gen_response.json()["puzzle"]["puzzle_id"]

        # Perform concurrent operations
        with patch(
            "backend.llm.client.LLMClient.chat_completion_async",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(
                    message=MagicMock(
                        content=json.dumps({
                            "answer": "SCIENCE",
                            "confidence": 0.9,
                            "reasoning": "Test",
                        })
                    )
                )
            ]
            mock_llm.return_value = mock_response

            # Concurrent: retrieve, solve, hint
            tasks = [
                async_client.get(f"/api/puzzles/{puzzle_id}"),
                async_client.post(
                    f"/api/puzzles/{puzzle_id}/solve-word",
                    json={"clue_number": 1, "direction": "across"},
                ),
                async_client.post(
                    f"/api/puzzles/{puzzle_id}/hint",
                    json={"clue_number": 1, "direction": "across"},
                ),
            ]

            responses = await asyncio.gather(*tasks)

        # Verify all operations succeeded
        assert responses[0].status_code == 200  # Get
        assert responses[1].status_code == 200  # Solve
        assert responses[2].status_code == 200  # Hint


@pytest.mark.asyncio
@pytest.mark.integration
class TestDataConsistency:
    """
    End-to-end tests for data consistency.

    These tests verify that data remains consistent across operations
    and that the system maintains referential integrity.
    """

    async def test_puzzle_data_consistency(
        self,
        async_client: AsyncClient,
        mock_successful_generation: PuzzleGenerationResult,
    ):
        """Test that puzzle data remains consistent across operations."""
        # Generate puzzle
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle_async",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_successful_generation

            gen_response = await async_client.post(
                "/api/puzzles/generate",
                json={"topic": "Science", "grid_size": 8, "min_words": 4, "max_words": 10},
            )

        original_puzzle = gen_response.json()["puzzle"]
        puzzle_id = original_puzzle["puzzle_id"]

        # Retrieve puzzle multiple times
        for _ in range(3):
            get_response = await async_client.get(f"/api/puzzles/{puzzle_id}")
            retrieved_puzzle = get_response.json()

            # Verify consistency
            assert retrieved_puzzle["puzzle_id"] == original_puzzle["puzzle_id"]
            assert retrieved_puzzle["topic"] == original_puzzle["topic"]
            assert retrieved_puzzle["grid_size"] == original_puzzle["grid_size"]
            assert retrieved_puzzle["word_count"] == original_puzzle["word_count"]
            assert len(retrieved_puzzle["cells"]) == len(original_puzzle["cells"])

    async def test_clue_answer_consistency(
        self,
        async_client: AsyncClient,
        mock_successful_generation: PuzzleGenerationResult,
    ):
        """Test that clues and answers remain consistent."""
        # Generate puzzle
        with patch(
            "backend.agents.orchestrator.PuzzleOrchestrator.generate_puzzle_async",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = mock_successful_generation

            gen_response = await async_client.post(
                "/api/puzzles/generate",
                json={"topic": "Science", "grid_size": 8, "min_words": 4, "max_words": 10},
            )

        puzzle = gen_response.json()["puzzle"]
        puzzle["puzzle_id"]

        # Verify clues have answers
        for clue in puzzle["clues_across"] + puzzle["clues_down"]:
            assert clue["answer"] is not None
            assert len(clue["answer"]) == clue["length"]
            assert clue["answer"].isupper()
            assert clue["answer"].isalpha()

        # Verify cells match word placements
        cells_dict = {(cell["row"], cell["col"]): cell["value"] for cell in puzzle["cells"]}

        for clue in puzzle["clues_across"]:
            word = clue["answer"]
            row = clue["start_row"]
            col = clue["start_col"]

            for i, letter in enumerate(word):
                cell_value = cells_dict.get((row, col + i))
                if cell_value:  # Cell might not be in the list if empty
                    assert cell_value == letter


@pytest.mark.asyncio
@pytest.mark.integration
class TestHealthAndMonitoring:
    """
    End-to-end tests for health checks and monitoring endpoints.

    These tests verify that monitoring and health check endpoints
    work correctly and provide accurate information.
    """

    async def test_health_check_endpoint(self, async_client: AsyncClient):
        """Test health check endpoint returns correct status."""
        response = await async_client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
        assert data["version"] == "0.1.0"

    async def test_root_endpoint(self, async_client: AsyncClient):
        """Test root endpoint provides API information."""
        response = await async_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


# ============================================================================
# Test Execution
# ============================================================================

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short", "-m", "integration"])
