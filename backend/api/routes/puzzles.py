"""
Puzzle management endpoints.

This module provides REST API endpoints for:
- Generating crossword puzzles from topics
- Retrieving puzzle information
- Solving puzzles with AI assistance
- Getting hints for specific words
- Validating user solutions
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status

from backend.agents.orchestrator import PuzzleGenerationRequest

from ..dependencies import OrchestratorDep, SolverDep
from ..schemas import (
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
    ValidationError,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for puzzles (will be replaced with database in future)
# Key: puzzle_id, Value: puzzle data
_puzzle_storage: dict[str, dict[str, Any]] = {}


def _convert_grid_to_cells(grid_dict: dict[str, Any]) -> list[CellResponse]:
    """
    Convert grid dictionary to list of CellResponse objects.

    Args:
        grid_dict: Serialized grid dictionary

    Returns:
        List of CellResponse objects
    """
    cells = []
    # Grid.to_dict() returns cells as a 2D array (list of rows)
    # We need to flatten it to a list of cell dictionaries
    cells_2d = grid_dict.get("cells", [])
    for row in cells_2d:
        for cell_data in row:
            cells.append(
                CellResponse(
                    row=cell_data["row"],
                    col=cell_data["col"],
                    value=cell_data.get("value"),
                    is_blocked=cell_data.get("is_blocked", False),
                    number=cell_data.get("number"),
                )
            )
    return cells


def _convert_words_to_clues(
    grid_dict: dict[str, Any],
    include_answers: bool = True
) -> tuple[list[ClueResponse], list[ClueResponse]]:
    """
    Convert grid words to clue responses, separated by direction.

    Args:
        grid_dict: Serialized grid dictionary
        include_answers: Whether to include answers in clues

    Returns:
        Tuple of (across_clues, down_clues)
    """
    across_clues = []
    down_clues = []

    for word_data in grid_dict.get("words", []):
        # Grid.to_dict() uses "text" for the word, not "word"
        word_text = word_data["text"]
        clue = ClueResponse(
            number=word_data["number"],
            direction=word_data["direction"],
            text=word_data["clue"],
            answer=word_text if include_answers else None,
            start_row=word_data["start_row"],
            start_col=word_data["start_col"],
            length=len(word_text),
        )

        if word_data["direction"] == "across":
            across_clues.append(clue)
        else:
            down_clues.append(clue)

    # Sort by clue number
    across_clues.sort(key=lambda c: c.number)
    down_clues.sort(key=lambda c: c.number)

    return across_clues, down_clues


@router.post(
    "/generate",
    status_code=status.HTTP_201_CREATED,
    response_model=PuzzleGenerateResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Generation failed"},
    },
    summary="Generate a new crossword puzzle",
    description=(
        "Generate a new crossword puzzle based on a topic. "
        "The puzzle is created using a multi-agent system with AI."
    ),
)
async def generate_puzzle(
    request: PuzzleGenerateRequest,
    orchestrator: OrchestratorDep,
) -> PuzzleGenerateResponse:
    """
    Generate a new crossword puzzle from a topic.

    This endpoint uses the multi-agent system to generate a crossword puzzle
    based on the provided topic and parameters. The generation process may
    take 30-60 seconds depending on complexity.

    Args:
        request: Puzzle generation request with topic and parameters
        orchestrator: Puzzle orchestrator dependency

    Returns:
        PuzzleGenerateResponse with the generated puzzle or error

    Raises:
        HTTPException: If generation fails or request is invalid
    """
    logger.info(f"Received puzzle generation request for topic: {request.topic}")

    try:
        # Convert API request to orchestrator request
        gen_request = PuzzleGenerationRequest(
            topic=request.topic,
            grid_size=request.grid_size,
            min_words=request.min_words,
            max_words=request.max_words,
            difficulty=request.difficulty,
            max_iterations=request.max_iterations,
        )

        # Validate request
        is_valid, error_msg = orchestrator.validate_request(gen_request)
        if not is_valid:
            logger.warning(f"Invalid generation request: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )

        # Generate puzzle
        logger.info(f"Starting puzzle generation for topic: {request.topic}")
        result = await orchestrator.generate_puzzle_async(gen_request)

        if not result.success:
            logger.error(f"Puzzle generation failed: {result.error_message}")
            return PuzzleGenerateResponse(
                success=False,
                puzzle=None,
                status=result.status,
                iterations=result.iterations,
                error_message=result.error_message,
            )

        # Create puzzle response
        puzzle_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()

        cells = _convert_grid_to_cells(result.grid)
        clues_across, clues_down = _convert_words_to_clues(result.grid, include_answers=True)

        puzzle = PuzzleResponse(
            puzzle_id=puzzle_id,
            topic=request.topic,
            grid_size=request.grid_size,
            cells=cells,
            clues_across=clues_across,
            clues_down=clues_down,
            word_count=result.word_count,
            fill_rate=result.fill_rate,
            difficulty=request.difficulty,
            created_at=created_at,
            metadata=result.metadata,
        )

        # Store puzzle in memory
        _puzzle_storage[puzzle_id] = {
            "puzzle": puzzle.model_dump(),
            "grid_dict": result.grid,
            "created_at": created_at,
        }

        logger.info(
            f"Puzzle generated successfully: id={puzzle_id}, "
            f"words={result.word_count}, fill_rate={result.fill_rate:.2%}"
        )

        return PuzzleGenerateResponse(
            success=True,
            puzzle=puzzle,
            status=result.status,
            iterations=result.iterations,
            error_message=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during puzzle generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Puzzle generation failed: {str(e)}",
        ) from e


@router.get(
    "/{puzzle_id}",
    status_code=status.HTTP_200_OK,
    response_model=PuzzleResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Puzzle not found"},
    },
    summary="Get puzzle by ID",
    description="Retrieve a previously generated puzzle by its unique identifier",
)
async def get_puzzle(puzzle_id: str) -> PuzzleResponse:
    """
    Get a puzzle by its ID.

    Args:
        puzzle_id: Unique puzzle identifier

    Returns:
        PuzzleResponse with puzzle data

    Raises:
        HTTPException: If puzzle not found
    """
    logger.info(f"Retrieving puzzle: {puzzle_id}")

    if puzzle_id not in _puzzle_storage:
        logger.warning(f"Puzzle not found: {puzzle_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Puzzle not found: {puzzle_id}",
        )

    puzzle_data = _puzzle_storage[puzzle_id]["puzzle"]
    return PuzzleResponse(**puzzle_data)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[PuzzleResponse],
    summary="List all puzzles",
    description="Get a list of all generated puzzles",
)
async def list_puzzles() -> list[PuzzleResponse]:
    """
    List all generated puzzles.

    Returns:
        List of PuzzleResponse objects
    """
    logger.info(f"Listing all puzzles (count: {len(_puzzle_storage)})")

    puzzles = []
    for puzzle_data in _puzzle_storage.values():
        puzzles.append(PuzzleResponse(**puzzle_data["puzzle"]))

    # Sort by creation time (newest first)
    puzzles.sort(key=lambda p: p.created_at, reverse=True)

    return puzzles


@router.post(
    "/{puzzle_id}/solve",
    status_code=status.HTTP_200_OK,
    response_model=SolveResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Puzzle not found"},
        500: {"model": ErrorResponse, "description": "Solve failed"},
    },
    summary="Solve entire puzzle with AI",
    description="Use AI to solve the entire crossword puzzle",
)
async def solve_puzzle(
    puzzle_id: str,
    request: SolvePuzzleRequest,
    solver: SolverDep,
) -> SolveResponse:
    """
    Solve the entire puzzle using AI.

    This endpoint uses AI to solve all words in the puzzle. The solution
    is based on the clues and any existing intersections.

    Args:
        puzzle_id: Unique puzzle identifier
        request: Solve request with options
        solver: Puzzle solver dependency

    Returns:
        SolveResponse with the complete solution

    Raises:
        HTTPException: If puzzle not found or solve fails
    """
    logger.info(f"Solving puzzle: {puzzle_id}")

    if puzzle_id not in _puzzle_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Puzzle not found: {puzzle_id}",
        )

    try:
        puzzle_data = _puzzle_storage[puzzle_id]
        grid_dict = puzzle_data["grid_dict"]

        # Use AI solver to solve the puzzle
        cells_data, confidence, reasoning = await solver.solve_puzzle(
            grid_dict=grid_dict,
            use_hints=request.use_hints
        )

        # Convert to CellResponse objects
        updated_cells = [
            CellResponse(**cell_data) for cell_data in cells_data
        ]

        logger.info(
            f"Puzzle solved: {puzzle_id}, confidence={confidence:.2f}, "
            f"cells={len(updated_cells)}"
        )

        return SolveResponse(
            success=True,
            answer="Complete puzzle solution",
            confidence=confidence,
            reasoning=reasoning,
            updated_cells=updated_cells,
        )

    except Exception as e:
        logger.error(f"Error solving puzzle: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to solve puzzle: {str(e)}",
        ) from e


@router.post(
    "/{puzzle_id}/solve-word",
    status_code=status.HTTP_200_OK,
    response_model=SolveResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Puzzle or word not found"},
        500: {"model": ErrorResponse, "description": "Solve failed"},
    },
    summary="Solve a specific word with AI",
    description="Use AI to solve a specific word in the puzzle",
)
async def solve_word(
    puzzle_id: str,
    request: SolveWordRequest,
    solver: SolverDep,
) -> SolveResponse:
    """
    Solve a specific word using AI.

    This endpoint uses AI to solve a single word based on its clue
    and any intersecting letters.

    Args:
        puzzle_id: Unique puzzle identifier
        request: Solve word request with clue number and direction
        solver: Puzzle solver dependency

    Returns:
        SolveResponse with the word solution

    Raises:
        HTTPException: If puzzle or word not found
    """
    logger.info(
        f"Solving word in puzzle {puzzle_id}: "
        f"clue={request.clue_number}, direction={request.direction}"
    )

    if puzzle_id not in _puzzle_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Puzzle not found: {puzzle_id}",
        )

    try:
        puzzle_data = _puzzle_storage[puzzle_id]
        grid_dict = puzzle_data["grid_dict"]

        # Find the word
        target_word = None
        for word_data in grid_dict.get("words", []):
            if (word_data["number"] == request.clue_number and
                word_data["direction"] == request.direction):
                target_word = word_data
                break

        if not target_word:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Word not found: clue {request.clue_number} {request.direction}",
            )

        # Extract clue and length
        clue = target_word["clue"]
        length = len(target_word["text"])

        # Build pattern from intersections if requested
        pattern = None
        intersections = None

        if request.use_intersections:
            # TODO: Extract actual intersections from grid
            # For now, we'll use None to let the solver work without constraints
            pass

        # Use AI solver to solve the word
        answer, confidence, reasoning = await solver.solve_word(
            clue=clue,
            length=length,
            pattern=pattern,
            intersections=intersections
        )

        # Create updated cells for this word
        updated_cells = []
        start_row = target_word["start_row"]
        start_col = target_word["start_col"]
        direction = target_word["direction"]

        for i, letter in enumerate(answer):
            if direction == "across":
                row, col = start_row, start_col + i
            else:
                row, col = start_row + i, start_col

            updated_cells.append(
                CellResponse(
                    row=row,
                    col=col,
                    value=letter,
                    is_blocked=False,
                    number=target_word["number"] if i == 0 else None,
                )
            )

        logger.info(
            f"Word solved: {answer}, confidence={confidence:.2f}"
        )

        return SolveResponse(
            success=True,
            answer=answer,
            confidence=confidence,
            reasoning=reasoning,
            updated_cells=updated_cells,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error solving word: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to solve word: {str(e)}",
        ) from e


@router.post(
    "/{puzzle_id}/hint",
    status_code=status.HTTP_200_OK,
    response_model=HintResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Puzzle or word not found"},
        500: {"model": ErrorResponse, "description": "Hint generation failed"},
    },
    summary="Get a hint for a specific word",
    description="Get an AI-generated hint to help solve a specific word",
)
async def get_hint(
    puzzle_id: str,
    request: HintRequest,
    solver: SolverDep,
) -> HintResponse:
    """
    Get a hint for a specific word.

    This endpoint provides different types of hints:
    - letter: Reveal a single letter
    - definition: Provide an alternative definition
    - synonym: Provide a synonym or related word

    Args:
        puzzle_id: Unique puzzle identifier
        request: Hint request with clue number and hint type
        solver: Puzzle solver dependency

    Returns:
        HintResponse with the hint

    Raises:
        HTTPException: If puzzle or word not found
    """
    logger.info(
        f"Getting hint for puzzle {puzzle_id}: "
        f"clue={request.clue_number}, direction={request.direction}, "
        f"type={request.hint_type}"
    )

    if puzzle_id not in _puzzle_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Puzzle not found: {puzzle_id}",
        )

    try:
        puzzle_data = _puzzle_storage[puzzle_id]
        grid_dict = puzzle_data["grid_dict"]

        # Find the word
        target_word = None
        for word_data in grid_dict.get("words", []):
            if (word_data["number"] == request.clue_number and
                word_data["direction"] == request.direction):
                target_word = word_data
                break

        if not target_word:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Word not found: clue {request.clue_number} {request.direction}",
            )

        clue = target_word["clue"]
        answer = target_word["text"]

        # Use AI solver to generate hint
        hint_text, revealed_letter, position = await solver.generate_hint(
            clue=clue,
            answer=answer,
            hint_type=request.hint_type
        )

        logger.info(
            f"Hint generated for word: {answer}, type={request.hint_type}"
        )

        return HintResponse(
            success=True,
            hint=hint_text,
            hint_type=request.hint_type,
            revealed_letter=revealed_letter,
            position=position,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating hint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate hint: {str(e)}",
        ) from e


@router.post(
    "/{puzzle_id}/validate",
    status_code=status.HTTP_200_OK,
    response_model=ValidateResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Puzzle not found"},
    },
    summary="Validate user solution",
    description="Check if the user's solution is correct",
)
async def validate_solution(
    puzzle_id: str,
    request: ValidateRequest,
) -> ValidateResponse:
    """
    Validate the user's solution.

    This endpoint compares the user's answers with the correct solution
    and returns detailed validation results.

    Args:
        puzzle_id: Unique puzzle identifier
        request: Validation request with user's cell values

    Returns:
        ValidateResponse with validation results

    Raises:
        HTTPException: If puzzle not found
    """
    logger.info(f"Validating solution for puzzle: {puzzle_id}")

    if puzzle_id not in _puzzle_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Puzzle not found: {puzzle_id}",
        )

    puzzle_data = _puzzle_storage[puzzle_id]
    grid_dict = puzzle_data["grid_dict"]

    # Create a map of correct answers
    correct_cells = {}
    for cell_data in grid_dict.get("cells", []):
        if cell_data.get("value"):
            key = (cell_data["row"], cell_data["col"])
            correct_cells[key] = cell_data["value"]

    # Validate user's cells
    errors = []
    correct_count = 0
    total_count = len(correct_cells)

    # Create a map of user's answers
    user_cells = {}
    for cell in request.cells:
        if cell.value:
            key = (cell.row, cell.col)
            user_cells[key] = cell.value.upper()

    # Check each cell
    for (row, col), expected in correct_cells.items():
        actual = user_cells.get((row, col))

        if actual is None:
            # Cell not filled
            continue
        elif actual == expected:
            correct_count += 1
        else:
            # Incorrect value
            errors.append(
                ValidationError(
                    row=row,
                    col=col,
                    expected=expected,
                    actual=actual,
                    message=f"Expected '{expected}', got '{actual}'",
                )
            )

    is_valid = len(errors) == 0
    is_complete = len(user_cells) == total_count
    accuracy = correct_count / total_count if total_count > 0 else 0.0

    logger.info(
        f"Validation complete: valid={is_valid}, complete={is_complete}, "
        f"accuracy={accuracy:.2%}"
    )

    return ValidateResponse(
        is_valid=is_valid,
        is_complete=is_complete,
        errors=errors,
        correct_count=correct_count,
        total_count=total_count,
        accuracy=accuracy,
    )


@router.delete(
    "/{puzzle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "Puzzle not found"},
    },
    summary="Delete a puzzle",
    description="Delete a puzzle from storage",
)
async def delete_puzzle(puzzle_id: str) -> None:
    """
    Delete a puzzle.

    Args:
        puzzle_id: Unique puzzle identifier

    Raises:
        HTTPException: If puzzle not found
    """
    logger.info(f"Deleting puzzle: {puzzle_id}")

    if puzzle_id not in _puzzle_storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Puzzle not found: {puzzle_id}",
        )

    del _puzzle_storage[puzzle_id]
    logger.info(f"Puzzle deleted: {puzzle_id}")
