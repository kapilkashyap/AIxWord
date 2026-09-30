"""
Pydantic schemas for API requests and responses.

This module defines all request and response models used by the FastAPI endpoints.
These schemas provide validation, serialization, and documentation for the API.
"""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

# ============================================================================
# Puzzle Generation Schemas
# ============================================================================

class PuzzleGenerateRequest(BaseModel):
    """
    Request schema for puzzle generation.

    Attributes:
        topic: Topic for puzzle generation (e.g., "Science", "History")
        grid_size: Size of the grid (NxN), default 8
        min_words: Minimum number of words to place, default 8
        max_words: Maximum number of words to place, default 15
        difficulty: Difficulty level (easy, medium, hard), default medium
        max_iterations: Maximum iterations allowed, default 50
    """
    topic: str = Field(
        ...,
        description="Topic for puzzle generation",
        min_length=1,
        max_length=100,
        examples=["Science", "History", "Technology"]
    )
    grid_size: int = Field(
        default=8,
        ge=4,
        le=20,
        description="Grid size (NxN)"
    )
    min_words: int = Field(
        default=8,
        ge=4,
        description="Minimum number of words"
    )
    max_words: int = Field(
        default=15,
        ge=4,
        description="Maximum number of words"
    )
    difficulty: Literal["easy", "medium", "hard"] = Field(
        default="medium",
        description="Difficulty level"
    )
    max_iterations: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum iterations allowed"
    )


class ClueResponse(BaseModel):
    """
    Response schema for a single clue.

    Attributes:
        number: Clue number
        direction: Direction (across or down)
        text: Clue text
        answer: Answer word (may be hidden for unsolved puzzles)
        start_row: Starting row position
        start_col: Starting column position
        length: Length of the answer
    """
    number: int = Field(..., description="Clue number")
    direction: Literal["across", "down"] = Field(..., description="Direction")
    text: str = Field(..., description="Clue text")
    answer: Optional[str] = Field(None, description="Answer word (uppercase)")
    start_row: int = Field(..., ge=0, description="Starting row")
    start_col: int = Field(..., ge=0, description="Starting column")
    length: int = Field(..., ge=1, description="Answer length")


class CellResponse(BaseModel):
    """
    Response schema for a grid cell.

    Attributes:
        row: Row position
        col: Column position
        value: Letter in the cell (None if empty)
        is_blocked: Whether this cell is blocked
        number: Clue number if this cell starts a word
    """
    row: int = Field(..., ge=0, description="Row position")
    col: int = Field(..., ge=0, description="Column position")
    value: Optional[str] = Field(None, description="Cell value (uppercase letter)")
    is_blocked: bool = Field(False, description="Whether cell is blocked")
    number: Optional[int] = Field(None, description="Clue number")


class PuzzleResponse(BaseModel):
    """
    Response schema for a complete puzzle.

    Attributes:
        puzzle_id: Unique puzzle identifier
        topic: Topic of the puzzle
        grid_size: Size of the grid
        cells: List of all cells in the grid
        clues_across: List of across clues
        clues_down: List of down clues
        word_count: Number of words in the puzzle
        fill_rate: Grid fill rate (0.0 to 1.0)
        difficulty: Difficulty level
        created_at: Creation timestamp
        metadata: Additional metadata
    """
    puzzle_id: str = Field(..., description="Unique puzzle identifier")
    topic: str = Field(..., description="Puzzle topic")
    grid_size: int = Field(..., ge=4, description="Grid size (NxN)")
    cells: list[CellResponse] = Field(..., description="Grid cells")
    clues_across: list[ClueResponse] = Field(..., description="Across clues")
    clues_down: list[ClueResponse] = Field(..., description="Down clues")
    word_count: int = Field(..., ge=0, description="Number of words")
    fill_rate: float = Field(..., ge=0.0, le=1.0, description="Grid fill rate")
    difficulty: str = Field(..., description="Difficulty level")
    created_at: str = Field(..., description="Creation timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PuzzleGenerateResponse(BaseModel):
    """
    Response schema for puzzle generation.

    Attributes:
        success: Whether generation was successful
        puzzle: Generated puzzle (if successful)
        status: Generation status
        iterations: Number of iterations executed
        error_message: Error message (if failed)
    """
    success: bool = Field(..., description="Whether generation was successful")
    puzzle: Optional[PuzzleResponse] = Field(None, description="Generated puzzle")
    status: str = Field(..., description="Generation status")
    iterations: int = Field(default=0, ge=0, description="Iterations executed")
    error_message: Optional[str] = Field(None, description="Error message if failed")


# ============================================================================
# Puzzle Solving Schemas
# ============================================================================

class SolvePuzzleRequest(BaseModel):
    """
    Request schema for solving entire puzzle.

    Attributes:
        use_hints: Whether to use existing clues as hints
    """
    use_hints: bool = Field(
        default=True,
        description="Whether to use existing clues as hints"
    )


class SolveWordRequest(BaseModel):
    """
    Request schema for solving a specific word.

    Attributes:
        clue_number: Clue number to solve
        direction: Direction of the word (across or down)
        use_intersections: Whether to use intersecting letters as hints
    """
    clue_number: int = Field(..., ge=1, description="Clue number")
    direction: Literal["across", "down"] = Field(..., description="Word direction")
    use_intersections: bool = Field(
        default=True,
        description="Whether to use intersecting letters"
    )


class HintRequest(BaseModel):
    """
    Request schema for getting a hint.

    Attributes:
        clue_number: Clue number for hint
        direction: Direction of the word (across or down)
        hint_type: Type of hint (letter, definition, synonym)
    """
    clue_number: int = Field(..., ge=1, description="Clue number")
    direction: Literal["across", "down"] = Field(..., description="Word direction")
    hint_type: Literal["letter", "definition", "synonym"] = Field(
        default="letter",
        description="Type of hint to provide"
    )


class SolveResponse(BaseModel):
    """
    Response schema for solve operations.

    Attributes:
        success: Whether solve was successful
        answer: The answer word or full solution
        confidence: Confidence score (0.0 to 1.0)
        reasoning: Explanation of the solution
        updated_cells: List of cells that were updated
    """
    success: bool = Field(..., description="Whether solve was successful")
    answer: Optional[str] = Field(None, description="Answer word or solution")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score")
    reasoning: Optional[str] = Field(None, description="Explanation of solution")
    updated_cells: list[CellResponse] = Field(
        default_factory=list,
        description="Cells that were updated"
    )


class HintResponse(BaseModel):
    """
    Response schema for hint requests.

    Attributes:
        success: Whether hint generation was successful
        hint: The hint text
        hint_type: Type of hint provided
        revealed_letter: Letter revealed (if hint_type is 'letter')
        position: Position of revealed letter (if applicable)
    """
    success: bool = Field(..., description="Whether hint generation was successful")
    hint: str = Field(..., description="Hint text")
    hint_type: str = Field(..., description="Type of hint")
    revealed_letter: Optional[str] = Field(None, description="Revealed letter")
    position: Optional[int] = Field(None, description="Position of revealed letter")


# ============================================================================
# Validation Schemas
# ============================================================================

class ValidateRequest(BaseModel):
    """
    Request schema for validating user solution.

    Attributes:
        cells: List of cells with user's answers
    """
    cells: list[CellResponse] = Field(..., description="User's cell values")


class ValidationError(BaseModel):
    """
    Schema for a single validation error.

    Attributes:
        row: Row position of error
        col: Column position of error
        expected: Expected value
        actual: Actual value provided
        message: Error message
    """
    row: int = Field(..., ge=0, description="Row position")
    col: int = Field(..., ge=0, description="Column position")
    expected: str = Field(..., description="Expected value")
    actual: Optional[str] = Field(None, description="Actual value")
    message: str = Field(..., description="Error message")


class ValidateResponse(BaseModel):
    """
    Response schema for validation.

    Attributes:
        is_valid: Whether the solution is valid
        is_complete: Whether the puzzle is completely filled
        errors: List of validation errors
        correct_count: Number of correct cells
        total_count: Total number of cells to fill
        accuracy: Accuracy percentage (0.0 to 1.0)
    """
    is_valid: bool = Field(..., description="Whether solution is valid")
    is_complete: bool = Field(..., description="Whether puzzle is complete")
    errors: list[ValidationError] = Field(
        default_factory=list,
        description="Validation errors"
    )
    correct_count: int = Field(..., ge=0, description="Number of correct cells")
    total_count: int = Field(..., ge=0, description="Total cells to fill")
    accuracy: float = Field(..., ge=0.0, le=1.0, description="Accuracy percentage")


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """
    Standard error response schema.

    Attributes:
        error: Error type or code
        message: Human-readable error message
        details: Additional error details
    """
    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Error message")
    details: Optional[dict[str, Any]] = Field(None, description="Additional details")
