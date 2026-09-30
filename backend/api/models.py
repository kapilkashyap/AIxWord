"""
API data models for puzzle storage and management.

This module defines the data models used for storing and managing puzzles
in the application. Currently uses in-memory storage, but designed to be
easily replaceable with database models (SQLAlchemy, etc.) in the future.

The models here are separate from Pydantic schemas (schemas.py) which are
used for API request/response validation. These models represent the internal
storage format.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.domain import CrosswordGrid


class PuzzleMetadata(BaseModel):
    """
    Metadata for a stored puzzle.

    Attributes:
        id: Unique puzzle identifier (UUID)
        topic: Topic used for generation
        grid_size: Size of the grid (NxN)
        difficulty: Difficulty level
        word_count: Number of words placed
        fill_rate: Grid fill rate (0.0 to 1.0)
        iterations: Number of iterations used
        created_at: Timestamp when puzzle was created
        status: Generation status (completed, failed, in_progress)
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    grid_size: int
    difficulty: str
    word_count: int = 0
    fill_rate: float = 0.0
    iterations: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "in_progress"

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StoredPuzzle(BaseModel):
    """
    Complete puzzle storage model.

    This model represents a puzzle as stored in the application's storage layer.
    It combines metadata with the actual grid data and clues.

    Attributes:
        metadata: Puzzle metadata
        grid_data: Serialized grid data (from CrosswordGrid.to_dict())
        clues: List of clues (across and down)
        solution: Complete solution grid (for validation)
        user_progress: User's current progress (cells filled)
    """
    metadata: PuzzleMetadata
    grid_data: Dict[str, Any]
    clues: List[Dict[str, Any]] = Field(default_factory=list)
    solution: Optional[Dict[str, Any]] = None
    user_progress: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert puzzle to dictionary for API responses.

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {
            "id": self.metadata.id,
            "topic": self.metadata.topic,
            "grid_size": self.metadata.grid_size,
            "difficulty": self.metadata.difficulty,
            "word_count": self.metadata.word_count,
            "fill_rate": self.metadata.fill_rate,
            "iterations": self.metadata.iterations,
            "created_at": self.metadata.created_at.isoformat(),
            "status": self.metadata.status,
            "grid": self.grid_data,
            "clues": self.clues,
        }

    @classmethod
    def from_grid(
        cls,
        grid: CrosswordGrid,
        topic: str,
        difficulty: str,
        iterations: int,
        puzzle_id: Optional[str] = None,
    ) -> "StoredPuzzle":
        """
        Create a StoredPuzzle from a CrosswordGrid.

        Args:
            grid: The crossword grid to store
            topic: Topic used for generation
            difficulty: Difficulty level
            iterations: Number of iterations used
            puzzle_id: Optional puzzle ID (generates new UUID if not provided)

        Returns:
            StoredPuzzle instance
        """
        # Extract clues from grid
        clues = []
        for clue in grid.clues:
            clues.append({
                "number": clue.number,
                "direction": clue.direction.value,
                "text": clue.text,
                "answer": clue.answer,
                "row": clue.row,
                "col": clue.col,
                "length": clue.length,
            })

        # Create metadata
        metadata = PuzzleMetadata(
            id=puzzle_id or str(uuid.uuid4()),
            topic=topic,
            grid_size=grid.size,
            difficulty=difficulty,
            word_count=len(grid.placements),
            fill_rate=grid.fill_rate,
            iterations=iterations,
            status="completed",
        )

        # Serialize grid
        grid_data = grid.to_dict()

        # Store solution separately
        solution = {
            "cells": [
                {
                    "row": cell.row,
                    "col": cell.col,
                    "value": cell.value,
                }
                for row in grid.cells
                for cell in row
                if cell.value is not None
            ]
        }

        return cls(
            metadata=metadata,
            grid_data=grid_data,
            clues=clues,
            solution=solution,
        )


class PuzzleStore:
    """
    In-memory storage for puzzles.

    This class provides a simple in-memory storage mechanism for puzzles.
    It's designed to be easily replaceable with a database-backed store
    in the future.

    Thread-safety: This implementation is NOT thread-safe. For production
    use with multiple workers, replace with a proper database or add locking.
    """

    def __init__(self):
        """Initialize empty puzzle store."""
        self._puzzles: Dict[str, StoredPuzzle] = {}

    def save(self, puzzle: StoredPuzzle) -> str:
        """
        Save a puzzle to the store.

        Args:
            puzzle: Puzzle to save

        Returns:
            Puzzle ID
        """
        puzzle_id = puzzle.metadata.id
        self._puzzles[puzzle_id] = puzzle
        return puzzle_id

    def get(self, puzzle_id: str) -> Optional[StoredPuzzle]:
        """
        Retrieve a puzzle by ID.

        Args:
            puzzle_id: Puzzle ID to retrieve

        Returns:
            StoredPuzzle if found, None otherwise
        """
        return self._puzzles.get(puzzle_id)

    def list_all(self) -> List[StoredPuzzle]:
        """
        List all stored puzzles.

        Returns:
            List of all puzzles, sorted by creation time (newest first)
        """
        puzzles = list(self._puzzles.values())
        puzzles.sort(key=lambda p: p.metadata.created_at, reverse=True)
        return puzzles

    def delete(self, puzzle_id: str) -> bool:
        """
        Delete a puzzle by ID.

        Args:
            puzzle_id: Puzzle ID to delete

        Returns:
            True if puzzle was deleted, False if not found
        """
        if puzzle_id in self._puzzles:
            del self._puzzles[puzzle_id]
            return True
        return False

    def update_progress(
        self,
        puzzle_id: str,
        user_progress: Dict[str, Any]
    ) -> bool:
        """
        Update user progress for a puzzle.

        Args:
            puzzle_id: Puzzle ID
            user_progress: User's current progress data

        Returns:
            True if updated, False if puzzle not found
        """
        puzzle = self._puzzles.get(puzzle_id)
        if puzzle:
            puzzle.user_progress = user_progress
            return True
        return False

    def clear(self) -> None:
        """Clear all puzzles from the store."""
        self._puzzles.clear()

    def count(self) -> int:
        """
        Get the total number of stored puzzles.

        Returns:
            Number of puzzles in store
        """
        return len(self._puzzles)


# Singleton instance for in-memory storage
_puzzle_store: Optional[PuzzleStore] = None


def get_puzzle_store() -> PuzzleStore:
    """
    Get the singleton puzzle store instance.

    This function ensures only one PuzzleStore instance exists throughout
    the application lifecycle.

    Returns:
        PuzzleStore singleton instance
    """
    global _puzzle_store
    if _puzzle_store is None:
        _puzzle_store = PuzzleStore()
    return _puzzle_store


def reset_puzzle_store() -> None:
    """
    Reset the puzzle store (useful for testing).

    This function clears the singleton instance, forcing a new one to be
    created on the next call to get_puzzle_store().
    """
    global _puzzle_store
    if _puzzle_store is not None:
        _puzzle_store.clear()
    _puzzle_store = None
