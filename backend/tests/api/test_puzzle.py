"""
Unit tests for puzzle service layer.

This module tests the PuzzleService class which provides business logic
for puzzle management operations.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.agents.orchestrator import (
    PuzzleGenerationRequest,
    PuzzleGenerationResult,
)
from backend.api.models import PuzzleMetadata, PuzzleStore, StoredPuzzle
from backend.api.puzzle import PuzzleService, get_puzzle_service, reset_puzzle_service
from backend.api.schemas import CellResponse


class TestPuzzleService:
    """Test suite for PuzzleService."""

    @pytest.fixture
    def mock_orchestrator(self):
        """Create a mock orchestrator."""
        orchestrator = MagicMock()
        orchestrator.generate_puzzle_async = AsyncMock()
        return orchestrator

    @pytest.fixture
    def mock_store(self):
        """Create a mock puzzle store."""
        store = MagicMock(spec=PuzzleStore)
        store.save = MagicMock(return_value="test-puzzle-id")
        store.get = MagicMock(return_value=None)
        store.list_all = MagicMock(return_value=[])
        store.delete = MagicMock(return_value=True)
        store.update_progress = MagicMock(return_value=True)
        store.count = MagicMock(return_value=0)
        store.clear = MagicMock()
        return store

    @pytest.fixture
    def service(self, mock_orchestrator, mock_store):
        """Create a puzzle service with mocked dependencies."""
        return PuzzleService(orchestrator=mock_orchestrator, store=mock_store)

    @pytest.fixture
    def sample_generation_request(self):
        """Create a sample puzzle generation request."""
        return PuzzleGenerationRequest(
            topic="Science",
            grid_size=8,
            min_words=8,
            max_words=15,
            difficulty="medium",
            max_iterations=50,
        )

    @pytest.fixture
    def sample_generation_result(self):
        """Create a sample successful generation result."""
        return PuzzleGenerationResult(
            success=True,
            grid={
                "size": 8,
                "cells": [
                    {"row": 0, "col": 0, "value": "A", "is_blocked": False, "number": 1},
                    {"row": 0, "col": 1, "value": "T", "is_blocked": False, "number": None},
                    {"row": 0, "col": 2, "value": "O", "is_blocked": False, "number": None},
                    {"row": 0, "col": 3, "value": "M", "is_blocked": False, "number": None},
                ],
                "words": [
                    {
                        "number": 1,
                        "direction": "across",
                        "word": "ATOM",
                        "clue": "Basic unit of matter",
                        "start_row": 0,
                        "start_col": 0,
                    }
                ],
            },
            status="completed",
            word_count=1,
            fill_rate=0.5,
            iterations=10,
            error_message=None,
            metadata={"test": "data"},
        )

    @pytest.fixture
    def sample_stored_puzzle(self):
        """Create a sample stored puzzle."""
        metadata = PuzzleMetadata(
            id="test-puzzle-id",
            topic="Science",
            grid_size=8,
            difficulty="medium",
            word_count=1,
            fill_rate=0.5,
            iterations=10,
            status="completed",
        )

        return StoredPuzzle(
            metadata=metadata,
            grid_data={
                "size": 8,
                "cells": [
                    {"row": 0, "col": 0, "value": "A", "is_blocked": False, "number": 1},
                    {"row": 0, "col": 1, "value": "T", "is_blocked": False, "number": None},
                    {"row": 0, "col": 2, "value": "O", "is_blocked": False, "number": None},
                    {"row": 0, "col": 3, "value": "M", "is_blocked": False, "number": None},
                ],
                "words": [
                    {
                        "number": 1,
                        "direction": "across",
                        "word": "ATOM",
                        "clue": "Basic unit of matter",
                        "start_row": 0,
                        "start_col": 0,
                    }
                ],
            },
            clues=[
                {
                    "number": 1,
                    "direction": "across",
                    "text": "Basic unit of matter",
                    "answer": "ATOM",
                    "row": 0,
                    "col": 0,
                    "length": 4,
                }
            ],
            solution={
                "cells": [
                    {"row": 0, "col": 0, "value": "A"},
                    {"row": 0, "col": 1, "value": "T"},
                    {"row": 0, "col": 2, "value": "O"},
                    {"row": 0, "col": 3, "value": "M"},
                ]
            },
        )

    def test_service_initialization(self, service):
        """Test that service initializes correctly."""
        assert service is not None
        assert service.orchestrator is not None
        assert service.store is not None

    def test_get_puzzle_service_singleton(self):
        """Test that get_puzzle_service returns singleton."""
        reset_puzzle_service()

        service1 = get_puzzle_service()
        service2 = get_puzzle_service()

        assert service1 is service2

        reset_puzzle_service()

    @pytest.mark.asyncio
    async def test_generate_and_store_puzzle_success(
        self,
        service,
        mock_orchestrator,
        mock_store,
        sample_generation_request,
        sample_generation_result,
    ):
        """Test successful puzzle generation and storage."""
        # Setup mock
        mock_orchestrator.generate_puzzle_async.return_value = sample_generation_result

        # Execute
        success, puzzle, error = await service.generate_and_store_puzzle(
            sample_generation_request
        )

        # Verify
        assert success is True
        assert puzzle is not None
        assert error is None

        # Verify orchestrator was called
        mock_orchestrator.generate_puzzle_async.assert_called_once_with(
            sample_generation_request
        )

        # Verify store was called
        mock_store.save.assert_called_once()
        saved_puzzle = mock_store.save.call_args[0][0]
        assert isinstance(saved_puzzle, StoredPuzzle)
        assert saved_puzzle.metadata.topic == "Science"

    @pytest.mark.asyncio
    async def test_generate_and_store_puzzle_generation_failure(
        self,
        service,
        mock_orchestrator,
        mock_store,
        sample_generation_request,
    ):
        """Test puzzle generation failure."""
        # Setup mock to return failure
        failed_result = PuzzleGenerationResult(
            success=False,
            grid=None,
            status="failed",
            word_count=0,
            fill_rate=0.0,
            iterations=5,
            error_message="Generation failed",
            metadata={},
        )
        mock_orchestrator.generate_puzzle_async.return_value = failed_result

        # Execute
        success, puzzle, error = await service.generate_and_store_puzzle(
            sample_generation_request
        )

        # Verify
        assert success is False
        assert puzzle is None
        assert error == "Generation failed"

        # Verify store was not called
        mock_store.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_generate_and_store_puzzle_no_grid_data(
        self,
        service,
        mock_orchestrator,
        mock_store,
        sample_generation_request,
    ):
        """Test puzzle generation with no grid data."""
        # Setup mock to return success but no grid
        result = PuzzleGenerationResult(
            success=True,
            grid=None,
            status="completed",
            word_count=0,
            fill_rate=0.0,
            iterations=10,
            error_message=None,
            metadata={},
        )
        mock_orchestrator.generate_puzzle_async.return_value = result

        # Execute
        success, puzzle, error = await service.generate_and_store_puzzle(
            sample_generation_request
        )

        # Verify
        assert success is False
        assert puzzle is None
        assert "no grid data" in error.lower()

    @pytest.mark.asyncio
    async def test_generate_and_store_puzzle_with_custom_id(
        self,
        service,
        mock_orchestrator,
        mock_store,
        sample_generation_request,
        sample_generation_result,
    ):
        """Test puzzle generation with custom puzzle ID."""
        # Setup mock
        mock_orchestrator.generate_puzzle_async.return_value = sample_generation_result
        custom_id = "custom-puzzle-id"

        # Execute
        success, puzzle, error = await service.generate_and_store_puzzle(
            sample_generation_request,
            puzzle_id=custom_id,
        )

        # Verify
        assert success is True
        assert puzzle is not None
        assert puzzle.metadata.id == custom_id

    def test_get_puzzle(self, service, mock_store, sample_stored_puzzle):
        """Test retrieving a puzzle by ID."""
        # Setup mock
        mock_store.get.return_value = sample_stored_puzzle

        # Execute
        puzzle = service.get_puzzle("test-puzzle-id")

        # Verify
        assert puzzle is not None
        assert puzzle.metadata.id == "test-puzzle-id"
        mock_store.get.assert_called_once_with("test-puzzle-id")

    def test_get_puzzle_not_found(self, service, mock_store):
        """Test retrieving a non-existent puzzle."""
        # Setup mock
        mock_store.get.return_value = None

        # Execute
        puzzle = service.get_puzzle("nonexistent-id")

        # Verify
        assert puzzle is None

    def test_list_puzzles(self, service, mock_store, sample_stored_puzzle):
        """Test listing all puzzles."""
        # Setup mock
        mock_store.list_all.return_value = [sample_stored_puzzle]

        # Execute
        puzzles = service.list_puzzles()

        # Verify
        assert len(puzzles) == 1
        assert puzzles[0].metadata.id == "test-puzzle-id"
        mock_store.list_all.assert_called_once()

    def test_list_puzzles_empty(self, service, mock_store):
        """Test listing puzzles when none exist."""
        # Setup mock
        mock_store.list_all.return_value = []

        # Execute
        puzzles = service.list_puzzles()

        # Verify
        assert len(puzzles) == 0

    def test_delete_puzzle_success(self, service, mock_store):
        """Test deleting a puzzle."""
        # Setup mock
        mock_store.delete.return_value = True

        # Execute
        result = service.delete_puzzle("test-puzzle-id")

        # Verify
        assert result is True
        mock_store.delete.assert_called_once_with("test-puzzle-id")

    def test_delete_puzzle_not_found(self, service, mock_store):
        """Test deleting a non-existent puzzle."""
        # Setup mock
        mock_store.delete.return_value = False

        # Execute
        result = service.delete_puzzle("nonexistent-id")

        # Verify
        assert result is False

    def test_validate_solution_correct(self, service, mock_store, sample_stored_puzzle):
        """Test validating a correct solution."""
        # Setup mock
        mock_store.get.return_value = sample_stored_puzzle

        # Create user cells (correct solution)
        user_cells = [
            CellResponse(row=0, col=0, value="A", is_blocked=False, number=1),
            CellResponse(row=0, col=1, value="T", is_blocked=False, number=None),
            CellResponse(row=0, col=2, value="O", is_blocked=False, number=None),
            CellResponse(row=0, col=3, value="M", is_blocked=False, number=None),
        ]

        # Execute
        result = service.validate_solution("test-puzzle-id", user_cells)

        # Verify
        assert result is not None
        assert result.is_valid is True
        assert result.is_complete is True
        assert result.accuracy == 1.0
        assert len(result.errors) == 0

    def test_validate_solution_incorrect(self, service, mock_store, sample_stored_puzzle):
        """Test validating an incorrect solution."""
        # Setup mock
        mock_store.get.return_value = sample_stored_puzzle

        # Create user cells (incorrect solution)
        user_cells = [
            CellResponse(row=0, col=0, value="A", is_blocked=False, number=1),
            CellResponse(row=0, col=1, value="X", is_blocked=False, number=None),  # Wrong
            CellResponse(row=0, col=2, value="O", is_blocked=False, number=None),
            CellResponse(row=0, col=3, value="M", is_blocked=False, number=None),
        ]

        # Execute
        result = service.validate_solution("test-puzzle-id", user_cells)

        # Verify
        assert result is not None
        assert result.is_valid is False
        assert result.is_complete is True
        assert result.accuracy == 0.75  # 3 out of 4 correct
        assert len(result.errors) == 1
        assert result.errors[0].row == 0
        assert result.errors[0].col == 1

    def test_validate_solution_incomplete(self, service, mock_store, sample_stored_puzzle):
        """Test validating an incomplete solution."""
        # Setup mock
        mock_store.get.return_value = sample_stored_puzzle

        # Create user cells (incomplete solution)
        user_cells = [
            CellResponse(row=0, col=0, value="A", is_blocked=False, number=1),
            CellResponse(row=0, col=1, value="T", is_blocked=False, number=None),
        ]

        # Execute
        result = service.validate_solution("test-puzzle-id", user_cells)

        # Verify
        assert result is not None
        assert result.is_valid is True  # No errors in filled cells
        assert result.is_complete is False  # Not all cells filled
        assert result.accuracy == 0.5  # 2 out of 4 filled

    def test_validate_solution_puzzle_not_found(self, service, mock_store):
        """Test validating solution for non-existent puzzle."""
        # Setup mock
        mock_store.get.return_value = None

        # Execute
        result = service.validate_solution("nonexistent-id", [])

        # Verify
        assert result is None

    def test_convert_to_response(self, service, sample_stored_puzzle):
        """Test converting StoredPuzzle to PuzzleResponse."""
        # Execute
        response = service.convert_to_response(sample_stored_puzzle)

        # Verify
        assert response.puzzle_id == "test-puzzle-id"
        assert response.topic == "Science"
        assert response.grid_size == 8
        assert len(response.cells) == 4
        assert len(response.clues_across) == 1
        assert len(response.clues_down) == 0
        assert response.word_count == 1
        assert response.fill_rate == 0.5

    def test_convert_to_response_without_answers(self, service, sample_stored_puzzle):
        """Test converting StoredPuzzle to PuzzleResponse without answers."""
        # Execute
        response = service.convert_to_response(sample_stored_puzzle, include_answers=False)

        # Verify
        assert response.puzzle_id == "test-puzzle-id"
        # Cells should not have values
        for cell in response.cells:
            assert cell.value is None
        # Clues should not have answers
        for clue in response.clues_across:
            assert clue.answer is None

    def test_update_user_progress(self, service, mock_store):
        """Test updating user progress."""
        # Setup mock
        mock_store.update_progress.return_value = True

        # Create user cells
        user_cells = [
            CellResponse(row=0, col=0, value="A", is_blocked=False, number=1),
            CellResponse(row=0, col=1, value="T", is_blocked=False, number=None),
        ]

        # Execute
        result = service.update_user_progress("test-puzzle-id", user_cells)

        # Verify
        assert result is True
        mock_store.update_progress.assert_called_once()

        # Verify the progress data structure
        call_args = mock_store.update_progress.call_args
        assert call_args[0][0] == "test-puzzle-id"
        progress = call_args[0][1]
        assert "cells" in progress
        assert "updated_at" in progress
        assert len(progress["cells"]) == 2

    def test_update_user_progress_puzzle_not_found(self, service, mock_store):
        """Test updating progress for non-existent puzzle."""
        # Setup mock
        mock_store.update_progress.return_value = False

        # Execute
        result = service.update_user_progress("nonexistent-id", [])

        # Verify
        assert result is False
