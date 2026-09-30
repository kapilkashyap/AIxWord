"""
Puzzle management service layer.

This module provides business logic for puzzle management operations,
acting as an intermediary between API routes and storage/domain layers.
It handles:
- Puzzle creation and storage
- Puzzle retrieval and listing
- Puzzle validation
- Puzzle deletion

This service layer decouples the API routes from direct storage access,
making it easier to swap storage implementations (e.g., from in-memory
to database) in the future.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

from backend.agents.orchestrator import (
    PuzzleGenerationRequest,
    PuzzleGenerationResult,
    PuzzleOrchestrator,
)

from .models import PuzzleMetadata, PuzzleStore, StoredPuzzle, get_puzzle_store
from .schemas import (
    CellResponse,
    ClueResponse,
    PuzzleResponse,
    ValidateResponse,
    ValidationError,
)

logger = logging.getLogger(__name__)


class PuzzleService:
    """
    Service layer for puzzle management operations.

    This class provides high-level business logic for puzzle operations,
    coordinating between the orchestrator, storage, and domain layers.
    """

    def __init__(
        self,
        orchestrator: Optional[PuzzleOrchestrator] = None,
        store: Optional[PuzzleStore] = None,
    ):
        """
        Initialize the puzzle service.

        Args:
            orchestrator: Puzzle orchestrator instance (uses singleton if not provided)
            store: Puzzle store instance (uses singleton if not provided)
        """
        from .dependencies import get_puzzle_orchestrator

        self.orchestrator = orchestrator or get_puzzle_orchestrator()
        self.store = store or get_puzzle_store()
        logger.info("PuzzleService initialized")

    async def generate_and_store_puzzle(
        self,
        request: PuzzleGenerationRequest,
        puzzle_id: Optional[str] = None,
    ) -> tuple[bool, Optional[StoredPuzzle], Optional[str]]:
        """
        Generate a puzzle and store it.

        This method orchestrates puzzle generation and storage:
        1. Generates puzzle using the orchestrator
        2. Converts result to StoredPuzzle
        3. Saves to storage
        4. Returns result

        Args:
            request: Puzzle generation request
            puzzle_id: Optional puzzle ID (generates new UUID if not provided)

        Returns:
            Tuple of (success, stored_puzzle, error_message)
        """
        logger.info(f"Generating and storing puzzle: topic='{request.topic}'")

        try:
            # Generate puzzle
            result: PuzzleGenerationResult = await self.orchestrator.generate_puzzle_async(
                request
            )

            if not result.success:
                logger.warning(f"Puzzle generation failed: {result.error_message}")
                return False, None, result.error_message

            # Convert result to StoredPuzzle
            # The result.grid is a dictionary representation of CrosswordGrid
            grid_dict = result.grid

            if not grid_dict:
                logger.error("Generated puzzle has no grid data")
                return False, None, "Generated puzzle has no grid data"

            # Create metadata
            metadata = PuzzleMetadata(
                id=puzzle_id or str(uuid.uuid4()),
                topic=request.topic,
                grid_size=request.grid_size,
                difficulty=request.difficulty,
                word_count=result.word_count,
                fill_rate=result.fill_rate,
                iterations=result.iterations,
                status="completed",
            )

            # Extract clues from grid
            clues = []
            for word_data in grid_dict.get("words", []):
                clues.append({
                    "number": word_data["number"],
                    "direction": word_data["direction"],
                    "text": word_data["clue"],
                    "answer": word_data["word"],
                    "row": word_data["start_row"],
                    "col": word_data["start_col"],
                    "length": len(word_data["word"]),
                })

            # Store solution separately
            solution = {
                "cells": [
                    {
                        "row": cell_data["row"],
                        "col": cell_data["col"],
                        "value": cell_data.get("value"),
                    }
                    for cell_data in grid_dict.get("cells", [])
                    if cell_data.get("value") is not None
                ]
            }

            # Create stored puzzle
            stored_puzzle = StoredPuzzle(
                metadata=metadata,
                grid_data=grid_dict,
                clues=clues,
                solution=solution,
            )

            # Save to store
            puzzle_id = self.store.save(stored_puzzle)

            logger.info(
                f"Puzzle generated and stored: id={puzzle_id}, "
                f"words={result.word_count}, fill_rate={result.fill_rate:.2%}"
            )

            return True, stored_puzzle, None

        except Exception as e:
            logger.error(f"Error generating and storing puzzle: {e}", exc_info=True)
            return False, None, f"Unexpected error: {str(e)}"

    def get_puzzle(self, puzzle_id: str) -> Optional[StoredPuzzle]:
        """
        Retrieve a puzzle by ID.

        Args:
            puzzle_id: Unique puzzle identifier

        Returns:
            StoredPuzzle if found, None otherwise
        """
        logger.info(f"Retrieving puzzle: {puzzle_id}")
        return self.store.get(puzzle_id)

    def list_puzzles(self) -> list[StoredPuzzle]:
        """
        List all stored puzzles.

        Returns:
            List of all puzzles, sorted by creation time (newest first)
        """
        logger.info("Listing all puzzles")
        return self.store.list_all()

    def delete_puzzle(self, puzzle_id: str) -> bool:
        """
        Delete a puzzle by ID.

        Args:
            puzzle_id: Unique puzzle identifier

        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting puzzle: {puzzle_id}")
        return self.store.delete(puzzle_id)

    def validate_solution(
        self,
        puzzle_id: str,
        user_cells: list[CellResponse]
    ) -> Optional[ValidateResponse]:
        """
        Validate a user's solution against the stored puzzle.

        Args:
            puzzle_id: Unique puzzle identifier
            user_cells: User's cell values

        Returns:
            ValidateResponse if puzzle found, None otherwise
        """
        logger.info(f"Validating solution for puzzle: {puzzle_id}")

        # Get puzzle
        puzzle = self.store.get(puzzle_id)
        if not puzzle:
            logger.warning(f"Puzzle not found for validation: {puzzle_id}")
            return None

        # Get correct solution
        solution = puzzle.solution
        if not solution:
            logger.warning(f"No solution stored for puzzle: {puzzle_id}")
            return None

        # Create a map of correct answers
        correct_cells = {}
        for cell_data in solution.get("cells", []):
            if cell_data.get("value"):
                key = (cell_data["row"], cell_data["col"])
                correct_cells[key] = cell_data["value"]

        # Create a map of user's answers
        user_cells_map = {}
        for cell in user_cells:
            if cell.value:
                key = (cell.row, cell.col)
                user_cells_map[key] = cell.value.upper()

        # Validate each cell
        errors = []
        correct_count = 0
        total_count = len(correct_cells)

        for (row, col), expected in correct_cells.items():
            actual = user_cells_map.get((row, col))

            if actual is None:
                # Cell not filled - not an error, just incomplete
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
        is_complete = len(user_cells_map) == total_count
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

    def convert_to_response(
        self,
        puzzle: StoredPuzzle,
        include_answers: bool = True
    ) -> PuzzleResponse:
        """
        Convert a StoredPuzzle to a PuzzleResponse.

        Args:
            puzzle: Stored puzzle to convert
            include_answers: Whether to include answers in clues

        Returns:
            PuzzleResponse for API response
        """
        # Convert cells
        cells = []
        for cell_data in puzzle.grid_data.get("cells", []):
            cells.append(
                CellResponse(
                    row=cell_data["row"],
                    col=cell_data["col"],
                    value=cell_data.get("value") if include_answers else None,
                    is_blocked=cell_data.get("is_blocked", False),
                    number=cell_data.get("number"),
                )
            )

        # Convert clues
        clues_across = []
        clues_down = []

        for clue_data in puzzle.clues:
            clue = ClueResponse(
                number=clue_data["number"],
                direction=clue_data["direction"],
                text=clue_data["text"],
                answer=clue_data["answer"] if include_answers else None,
                start_row=clue_data["row"],
                start_col=clue_data["col"],
                length=clue_data["length"],
            )

            if clue_data["direction"] == "across":
                clues_across.append(clue)
            else:
                clues_down.append(clue)

        # Sort by clue number
        clues_across.sort(key=lambda c: c.number)
        clues_down.sort(key=lambda c: c.number)

        return PuzzleResponse(
            puzzle_id=puzzle.metadata.id,
            topic=puzzle.metadata.topic,
            grid_size=puzzle.metadata.grid_size,
            cells=cells,
            clues_across=clues_across,
            clues_down=clues_down,
            word_count=puzzle.metadata.word_count,
            fill_rate=puzzle.metadata.fill_rate,
            difficulty=puzzle.metadata.difficulty,
            created_at=puzzle.metadata.created_at.isoformat(),
            metadata={
                "iterations": puzzle.metadata.iterations,
                "status": puzzle.metadata.status,
            },
        )

    def update_user_progress(
        self,
        puzzle_id: str,
        user_cells: list[CellResponse]
    ) -> bool:
        """
        Update user's progress for a puzzle.

        Args:
            puzzle_id: Unique puzzle identifier
            user_cells: User's current cell values

        Returns:
            True if updated, False if puzzle not found
        """
        logger.info(f"Updating user progress for puzzle: {puzzle_id}")

        # Convert cells to dict format
        progress = {
            "cells": [
                {
                    "row": cell.row,
                    "col": cell.col,
                    "value": cell.value,
                }
                for cell in user_cells
                if cell.value is not None
            ],
            "updated_at": datetime.utcnow().isoformat(),
        }

        return self.store.update_progress(puzzle_id, progress)


# Singleton instance for convenience
_service_instance: Optional[PuzzleService] = None


def get_puzzle_service() -> PuzzleService:
    """
    Get the singleton puzzle service instance.

    Returns:
        PuzzleService instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = PuzzleService()
    return _service_instance


def reset_puzzle_service() -> None:
    """
    Reset the puzzle service (useful for testing).

    This function clears the singleton instance, forcing a new one to be
    created on the next call to get_puzzle_service().
    """
    global _service_instance
    _service_instance = None
