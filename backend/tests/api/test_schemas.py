"""
Unit tests for API schemas.

This module tests the Pydantic schemas used for API request/response
validation and serialization.
"""

import pytest
from pydantic import ValidationError

from backend.api.schemas import (
    CellResponse,
    ClueResponse,
    ErrorResponse,
    HintRequest,
    HintResponse,
    PuzzleGenerateRequest,
    PuzzleGenerateResponse,
    PuzzleResponse,
    SolvePuzzleRequest,
    SolveResponse,
    SolveWordRequest,
    ValidateRequest,
    ValidateResponse,
)
from backend.api.schemas import (
    ValidationError as ValidationErrorSchema,
)


class TestPuzzleGenerateRequest:
    """Test suite for PuzzleGenerateRequest schema."""

    def test_valid_request_minimal(self):
        """Test valid request with minimal fields."""
        request = PuzzleGenerateRequest(topic="Science")

        assert request.topic == "Science"
        assert request.grid_size == 8  # Default
        assert request.min_words == 8  # Default
        assert request.max_words == 15  # Default
        assert request.difficulty == "medium"  # Default
        assert request.max_iterations == 50  # Default

    def test_valid_request_full(self):
        """Test valid request with all fields."""
        request = PuzzleGenerateRequest(
            topic="History",
            grid_size=10,
            min_words=10,
            max_words=20,
            difficulty="hard",
            max_iterations=100,
        )

        assert request.topic == "History"
        assert request.grid_size == 10
        assert request.min_words == 10
        assert request.max_words == 20
        assert request.difficulty == "hard"
        assert request.max_iterations == 100

    def test_invalid_topic_empty(self):
        """Test that empty topic is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PuzzleGenerateRequest(topic="")

        errors = exc_info.value.errors()
        assert any("topic" in str(e) for e in errors)

    def test_invalid_grid_size_too_small(self):
        """Test that grid size below minimum is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PuzzleGenerateRequest(topic="Science", grid_size=3)

        errors = exc_info.value.errors()
        assert any("grid_size" in str(e) for e in errors)

    def test_invalid_grid_size_too_large(self):
        """Test that grid size above maximum is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PuzzleGenerateRequest(topic="Science", grid_size=21)

        errors = exc_info.value.errors()
        assert any("grid_size" in str(e) for e in errors)

    def test_invalid_difficulty(self):
        """Test that invalid difficulty is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PuzzleGenerateRequest(topic="Science", difficulty="impossible")

        errors = exc_info.value.errors()
        assert any("difficulty" in str(e) for e in errors)

    def test_invalid_max_iterations_zero(self):
        """Test that zero max_iterations is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PuzzleGenerateRequest(topic="Science", max_iterations=0)

        errors = exc_info.value.errors()
        assert any("max_iterations" in str(e) for e in errors)

    def test_topic_max_length(self):
        """Test topic maximum length validation."""
        # Should work at max length
        request = PuzzleGenerateRequest(topic="A" * 100)
        assert len(request.topic) == 100

        # Should fail above max length
        with pytest.raises(ValidationError):
            PuzzleGenerateRequest(topic="A" * 101)


class TestClueResponse:
    """Test suite for ClueResponse schema."""

    def test_valid_clue_with_answer(self):
        """Test valid clue with answer."""
        clue = ClueResponse(
            number=1,
            direction="across",
            text="Basic unit of matter",
            answer="ATOM",
            start_row=0,
            start_col=0,
            length=4,
        )

        assert clue.number == 1
        assert clue.direction == "across"
        assert clue.text == "Basic unit of matter"
        assert clue.answer == "ATOM"
        assert clue.start_row == 0
        assert clue.start_col == 0
        assert clue.length == 4

    def test_valid_clue_without_answer(self):
        """Test valid clue without answer (for unsolved puzzles)."""
        clue = ClueResponse(
            number=1,
            direction="down",
            text="Basic unit of matter",
            start_row=0,
            start_col=0,
            length=4,
        )

        assert clue.answer is None

    def test_invalid_direction(self):
        """Test that invalid direction is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ClueResponse(
                number=1,
                direction="diagonal",
                text="Test clue",
                start_row=0,
                start_col=0,
                length=4,
            )

        errors = exc_info.value.errors()
        assert any("direction" in str(e) for e in errors)

    def test_invalid_negative_position(self):
        """Test that negative positions are rejected."""
        with pytest.raises(ValidationError):
            ClueResponse(
                number=1,
                direction="across",
                text="Test clue",
                start_row=-1,
                start_col=0,
                length=4,
            )


class TestCellResponse:
    """Test suite for CellResponse schema."""

    def test_valid_cell_with_value(self):
        """Test valid cell with value."""
        cell = CellResponse(
            row=0,
            col=0,
            value="A",
            is_blocked=False,
            number=1,
        )

        assert cell.row == 0
        assert cell.col == 0
        assert cell.value == "A"
        assert cell.is_blocked is False
        assert cell.number == 1

    def test_valid_cell_empty(self):
        """Test valid empty cell."""
        cell = CellResponse(row=0, col=0)

        assert cell.row == 0
        assert cell.col == 0
        assert cell.value is None
        assert cell.is_blocked is False
        assert cell.number is None

    def test_valid_cell_blocked(self):
        """Test valid blocked cell."""
        cell = CellResponse(row=0, col=0, is_blocked=True)

        assert cell.is_blocked is True

    def test_invalid_negative_position(self):
        """Test that negative positions are rejected."""
        with pytest.raises(ValidationError):
            CellResponse(row=-1, col=0)


class TestPuzzleResponse:
    """Test suite for PuzzleResponse schema."""

    def test_valid_puzzle_response(self):
        """Test valid puzzle response."""
        puzzle = PuzzleResponse(
            puzzle_id="test-id",
            topic="Science",
            grid_size=8,
            cells=[
                CellResponse(row=0, col=0, value="A", number=1),
            ],
            clues_across=[
                ClueResponse(
                    number=1,
                    direction="across",
                    text="Test clue",
                    answer="ATOM",
                    start_row=0,
                    start_col=0,
                    length=4,
                )
            ],
            clues_down=[],
            word_count=1,
            fill_rate=0.5,
            difficulty="medium",
            created_at="2026-09-28T12:00:00",
        )

        assert puzzle.puzzle_id == "test-id"
        assert puzzle.topic == "Science"
        assert puzzle.grid_size == 8
        assert len(puzzle.cells) == 1
        assert len(puzzle.clues_across) == 1
        assert len(puzzle.clues_down) == 0
        assert puzzle.word_count == 1
        assert puzzle.fill_rate == 0.5
        assert puzzle.difficulty == "medium"

    def test_invalid_fill_rate_above_one(self):
        """Test that fill rate above 1.0 is rejected."""
        with pytest.raises(ValidationError):
            PuzzleResponse(
                puzzle_id="test-id",
                topic="Science",
                grid_size=8,
                cells=[],
                clues_across=[],
                clues_down=[],
                word_count=1,
                fill_rate=1.5,
                difficulty="medium",
                created_at="2026-09-28T12:00:00",
            )

    def test_invalid_fill_rate_negative(self):
        """Test that negative fill rate is rejected."""
        with pytest.raises(ValidationError):
            PuzzleResponse(
                puzzle_id="test-id",
                topic="Science",
                grid_size=8,
                cells=[],
                clues_across=[],
                clues_down=[],
                word_count=1,
                fill_rate=-0.1,
                difficulty="medium",
                created_at="2026-09-28T12:00:00",
            )


class TestPuzzleGenerateResponse:
    """Test suite for PuzzleGenerateResponse schema."""

    def test_valid_success_response(self):
        """Test valid success response."""
        puzzle = PuzzleResponse(
            puzzle_id="test-id",
            topic="Science",
            grid_size=8,
            cells=[],
            clues_across=[],
            clues_down=[],
            word_count=1,
            fill_rate=0.5,
            difficulty="medium",
            created_at="2026-09-28T12:00:00",
        )

        response = PuzzleGenerateResponse(
            success=True,
            puzzle=puzzle,
            status="completed",
            iterations=10,
        )

        assert response.success is True
        assert response.puzzle is not None
        assert response.status == "completed"
        assert response.iterations == 10
        assert response.error_message is None

    def test_valid_failure_response(self):
        """Test valid failure response."""
        response = PuzzleGenerateResponse(
            success=False,
            puzzle=None,
            status="failed",
            iterations=5,
            error_message="Generation failed",
        )

        assert response.success is False
        assert response.puzzle is None
        assert response.status == "failed"
        assert response.error_message == "Generation failed"


class TestSolvePuzzleRequest:
    """Test suite for SolvePuzzleRequest schema."""

    def test_valid_request_default(self):
        """Test valid request with default values."""
        request = SolvePuzzleRequest()

        assert request.use_hints is True

    def test_valid_request_explicit(self):
        """Test valid request with explicit values."""
        request = SolvePuzzleRequest(use_hints=False)

        assert request.use_hints is False


class TestSolveWordRequest:
    """Test suite for SolveWordRequest schema."""

    def test_valid_request(self):
        """Test valid solve word request."""
        request = SolveWordRequest(
            clue_number=1,
            direction="across",
            use_intersections=True,
        )

        assert request.clue_number == 1
        assert request.direction == "across"
        assert request.use_intersections is True

    def test_invalid_clue_number_zero(self):
        """Test that clue number zero is rejected."""
        with pytest.raises(ValidationError):
            SolveWordRequest(clue_number=0, direction="across")

    def test_invalid_direction(self):
        """Test that invalid direction is rejected."""
        with pytest.raises(ValidationError):
            SolveWordRequest(clue_number=1, direction="diagonal")


class TestHintRequest:
    """Test suite for HintRequest schema."""

    def test_valid_request_default(self):
        """Test valid hint request with default hint type."""
        request = HintRequest(clue_number=1, direction="across")

        assert request.clue_number == 1
        assert request.direction == "across"
        assert request.hint_type == "letter"

    def test_valid_request_all_hint_types(self):
        """Test valid hint request with all hint types."""
        for hint_type in ["letter", "definition", "synonym"]:
            request = HintRequest(
                clue_number=1,
                direction="across",
                hint_type=hint_type,
            )
            assert request.hint_type == hint_type

    def test_invalid_hint_type(self):
        """Test that invalid hint type is rejected."""
        with pytest.raises(ValidationError):
            HintRequest(
                clue_number=1,
                direction="across",
                hint_type="invalid",
            )


class TestSolveResponse:
    """Test suite for SolveResponse schema."""

    def test_valid_success_response(self):
        """Test valid success response."""
        response = SolveResponse(
            success=True,
            answer="ATOM",
            confidence=0.95,
            reasoning="Based on the clue",
            updated_cells=[
                CellResponse(row=0, col=0, value="A"),
            ],
        )

        assert response.success is True
        assert response.answer == "ATOM"
        assert response.confidence == 0.95
        assert response.reasoning == "Based on the clue"
        assert len(response.updated_cells) == 1

    def test_valid_failure_response(self):
        """Test valid failure response."""
        response = SolveResponse(success=False)

        assert response.success is False
        assert response.answer is None
        assert response.confidence == 0.0
        assert response.reasoning is None
        assert len(response.updated_cells) == 0

    def test_invalid_confidence_above_one(self):
        """Test that confidence above 1.0 is rejected."""
        with pytest.raises(ValidationError):
            SolveResponse(success=True, confidence=1.5)

    def test_invalid_confidence_negative(self):
        """Test that negative confidence is rejected."""
        with pytest.raises(ValidationError):
            SolveResponse(success=True, confidence=-0.1)


class TestHintResponse:
    """Test suite for HintResponse schema."""

    def test_valid_letter_hint(self):
        """Test valid letter hint response."""
        response = HintResponse(
            success=True,
            hint="The letter at position 1 is 'A'",
            hint_type="letter",
            revealed_letter="A",
            position=0,
        )

        assert response.success is True
        assert response.hint_type == "letter"
        assert response.revealed_letter == "A"
        assert response.position == 0

    def test_valid_definition_hint(self):
        """Test valid definition hint response."""
        response = HintResponse(
            success=True,
            hint="Think about chemistry",
            hint_type="definition",
        )

        assert response.success is True
        assert response.hint_type == "definition"
        assert response.revealed_letter is None
        assert response.position is None


class TestValidateRequest:
    """Test suite for ValidateRequest schema."""

    def test_valid_request(self):
        """Test valid validation request."""
        request = ValidateRequest(
            cells=[
                CellResponse(row=0, col=0, value="A"),
                CellResponse(row=0, col=1, value="T"),
            ]
        )

        assert len(request.cells) == 2

    def test_valid_empty_request(self):
        """Test valid empty validation request."""
        request = ValidateRequest(cells=[])

        assert len(request.cells) == 0


class TestValidationErrorSchema:
    """Test suite for ValidationError schema."""

    def test_valid_error(self):
        """Test valid validation error."""
        error = ValidationErrorSchema(
            row=0,
            col=1,
            expected="T",
            actual="X",
            message="Expected 'T', got 'X'",
        )

        assert error.row == 0
        assert error.col == 1
        assert error.expected == "T"
        assert error.actual == "X"
        assert error.message == "Expected 'T', got 'X'"

    def test_valid_error_no_actual(self):
        """Test valid validation error with no actual value."""
        error = ValidationErrorSchema(
            row=0,
            col=1,
            expected="T",
            message="Cell is empty",
        )

        assert error.actual is None


class TestValidateResponse:
    """Test suite for ValidateResponse schema."""

    def test_valid_correct_response(self):
        """Test valid response for correct solution."""
        response = ValidateResponse(
            is_valid=True,
            is_complete=True,
            errors=[],
            correct_count=10,
            total_count=10,
            accuracy=1.0,
        )

        assert response.is_valid is True
        assert response.is_complete is True
        assert len(response.errors) == 0
        assert response.correct_count == 10
        assert response.total_count == 10
        assert response.accuracy == 1.0

    def test_valid_incorrect_response(self):
        """Test valid response for incorrect solution."""
        response = ValidateResponse(
            is_valid=False,
            is_complete=True,
            errors=[
                ValidationErrorSchema(
                    row=0,
                    col=1,
                    expected="T",
                    actual="X",
                    message="Wrong letter",
                )
            ],
            correct_count=9,
            total_count=10,
            accuracy=0.9,
        )

        assert response.is_valid is False
        assert response.is_complete is True
        assert len(response.errors) == 1
        assert response.accuracy == 0.9

    def test_valid_incomplete_response(self):
        """Test valid response for incomplete solution."""
        response = ValidateResponse(
            is_valid=True,
            is_complete=False,
            errors=[],
            correct_count=5,
            total_count=10,
            accuracy=0.5,
        )

        assert response.is_valid is True
        assert response.is_complete is False
        assert response.accuracy == 0.5


class TestErrorResponse:
    """Test suite for ErrorResponse schema."""

    def test_valid_error_minimal(self):
        """Test valid error response with minimal fields."""
        error = ErrorResponse(
            error="validation_error",
            message="Invalid input",
        )

        assert error.error == "validation_error"
        assert error.message == "Invalid input"
        assert error.details is None

    def test_valid_error_with_details(self):
        """Test valid error response with details."""
        error = ErrorResponse(
            error="generation_failed",
            message="Puzzle generation failed",
            details={"reason": "timeout", "iterations": 50},
        )

        assert error.error == "generation_failed"
        assert error.message == "Puzzle generation failed"
        assert error.details is not None
        assert error.details["reason"] == "timeout"
        assert error.details["iterations"] == 50


class TestSchemaIntegration:
    """Integration tests for schema interactions."""

    def test_puzzle_response_serialization(self):
        """Test that PuzzleResponse can be serialized to dict."""
        puzzle = PuzzleResponse(
            puzzle_id="test-id",
            topic="Science",
            grid_size=8,
            cells=[
                CellResponse(row=0, col=0, value="A", number=1),
            ],
            clues_across=[
                ClueResponse(
                    number=1,
                    direction="across",
                    text="Test clue",
                    answer="ATOM",
                    start_row=0,
                    start_col=0,
                    length=4,
                )
            ],
            clues_down=[],
            word_count=1,
            fill_rate=0.5,
            difficulty="medium",
            created_at="2026-09-28T12:00:00",
        )

        # Serialize to dict
        puzzle_dict = puzzle.model_dump()

        assert isinstance(puzzle_dict, dict)
        assert puzzle_dict["puzzle_id"] == "test-id"
        assert puzzle_dict["topic"] == "Science"
        assert len(puzzle_dict["cells"]) == 1
        assert len(puzzle_dict["clues_across"]) == 1

    def test_puzzle_response_json_serialization(self):
        """Test that PuzzleResponse can be serialized to JSON."""
        puzzle = PuzzleResponse(
            puzzle_id="test-id",
            topic="Science",
            grid_size=8,
            cells=[],
            clues_across=[],
            clues_down=[],
            word_count=0,
            fill_rate=0.0,
            difficulty="medium",
            created_at="2026-09-28T12:00:00",
        )

        # Serialize to JSON
        json_str = puzzle.model_dump_json()

        assert isinstance(json_str, str)
        assert "test-id" in json_str
        assert "Science" in json_str
