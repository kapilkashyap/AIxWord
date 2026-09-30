"""
Storage utilities and helpers for puzzle management.

This module provides utility functions and helpers for working with
puzzle storage, including:
- Storage initialization and configuration
- Data conversion utilities
- Storage health checks
- Backup and restore utilities (for future use)

Note: Currently uses in-memory storage. This module is designed to make
it easy to migrate to database storage in the future by centralizing
storage-related utilities.
"""

import logging
from datetime import datetime
from typing import Any, Optional

from .models import PuzzleStore, StoredPuzzle, get_puzzle_store

logger = logging.getLogger(__name__)


class StorageManager:
    """
    Manager for puzzle storage operations.

    This class provides high-level utilities for managing puzzle storage,
    including initialization, health checks, and maintenance operations.
    """

    def __init__(self, store: Optional[PuzzleStore] = None):
        """
        Initialize the storage manager.

        Args:
            store: Puzzle store instance (uses singleton if not provided)
        """
        self.store = store or get_puzzle_store()
        logger.info("StorageManager initialized")

    def get_storage_info(self) -> dict[str, Any]:
        """
        Get information about the storage system.

        Returns:
            Dictionary with storage information
        """
        return {
            "type": "in-memory",
            "puzzle_count": self.store.count(),
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def health_check(self) -> tuple[bool, str]:
        """
        Perform a health check on the storage system.

        Returns:
            Tuple of (is_healthy, message)
        """
        try:
            # Check if store is accessible
            count = self.store.count()

            # For in-memory storage, we just check if we can access it
            return True, f"Storage healthy: {count} puzzles stored"

        except Exception as e:
            logger.error(f"Storage health check failed: {e}", exc_info=True)
            return False, f"Storage unhealthy: {str(e)}"

    def clear_storage(self) -> int:
        """
        Clear all puzzles from storage.

        Warning: This operation is irreversible for in-memory storage!

        Returns:
            Number of puzzles cleared
        """
        count = self.store.count()
        logger.warning(f"Clearing storage: {count} puzzles will be deleted")
        self.store.clear()
        return count

    def get_storage_statistics(self) -> dict[str, Any]:
        """
        Get detailed statistics about stored puzzles.

        Returns:
            Dictionary with storage statistics
        """
        puzzles = self.store.list_all()

        if not puzzles:
            return {
                "total_puzzles": 0,
                "topics": {},
                "difficulties": {},
                "grid_sizes": {},
                "average_fill_rate": 0.0,
                "average_word_count": 0.0,
            }

        # Collect statistics
        topics = {}
        difficulties = {}
        grid_sizes = {}
        total_fill_rate = 0.0
        total_word_count = 0

        for puzzle in puzzles:
            # Count by topic
            topic = puzzle.metadata.topic
            topics[topic] = topics.get(topic, 0) + 1

            # Count by difficulty
            difficulty = puzzle.metadata.difficulty
            difficulties[difficulty] = difficulties.get(difficulty, 0) + 1

            # Count by grid size
            grid_size = puzzle.metadata.grid_size
            grid_sizes[grid_size] = grid_sizes.get(grid_size, 0) + 1

            # Accumulate metrics
            total_fill_rate += puzzle.metadata.fill_rate
            total_word_count += puzzle.metadata.word_count

        count = len(puzzles)

        return {
            "total_puzzles": count,
            "topics": topics,
            "difficulties": difficulties,
            "grid_sizes": grid_sizes,
            "average_fill_rate": total_fill_rate / count,
            "average_word_count": total_word_count / count,
        }

    def find_puzzles_by_topic(self, topic: str) -> list[StoredPuzzle]:
        """
        Find all puzzles for a given topic.

        Args:
            topic: Topic to search for (case-insensitive)

        Returns:
            List of puzzles matching the topic
        """
        all_puzzles = self.store.list_all()
        topic_lower = topic.lower()

        matching = [
            puzzle for puzzle in all_puzzles
            if puzzle.metadata.topic.lower() == topic_lower
        ]

        logger.info(f"Found {len(matching)} puzzles for topic '{topic}'")
        return matching

    def find_puzzles_by_difficulty(self, difficulty: str) -> list[StoredPuzzle]:
        """
        Find all puzzles for a given difficulty level.

        Args:
            difficulty: Difficulty level to search for

        Returns:
            List of puzzles matching the difficulty
        """
        all_puzzles = self.store.list_all()

        matching = [
            puzzle for puzzle in all_puzzles
            if puzzle.metadata.difficulty == difficulty
        ]

        logger.info(f"Found {len(matching)} puzzles with difficulty '{difficulty}'")
        return matching

    def get_recent_puzzles(self, limit: int = 10) -> list[StoredPuzzle]:
        """
        Get the most recently created puzzles.

        Args:
            limit: Maximum number of puzzles to return

        Returns:
            List of recent puzzles (newest first)
        """
        all_puzzles = self.store.list_all()
        return all_puzzles[:limit]

    def export_puzzle(self, puzzle_id: str) -> Optional[dict[str, Any]]:
        """
        Export a puzzle to a dictionary format.

        This can be used for backup, sharing, or migration purposes.

        Args:
            puzzle_id: Unique puzzle identifier

        Returns:
            Dictionary representation of the puzzle, or None if not found
        """
        puzzle = self.store.get(puzzle_id)
        if not puzzle:
            logger.warning(f"Puzzle not found for export: {puzzle_id}")
            return None

        return {
            "metadata": {
                "id": puzzle.metadata.id,
                "topic": puzzle.metadata.topic,
                "grid_size": puzzle.metadata.grid_size,
                "difficulty": puzzle.metadata.difficulty,
                "word_count": puzzle.metadata.word_count,
                "fill_rate": puzzle.metadata.fill_rate,
                "iterations": puzzle.metadata.iterations,
                "created_at": puzzle.metadata.created_at.isoformat(),
                "status": puzzle.metadata.status,
            },
            "grid_data": puzzle.grid_data,
            "clues": puzzle.clues,
            "solution": puzzle.solution,
            "user_progress": puzzle.user_progress,
        }

    def import_puzzle(self, puzzle_data: dict[str, Any]) -> Optional[str]:
        """
        Import a puzzle from a dictionary format.

        This can be used for restore or migration purposes.

        Args:
            puzzle_data: Dictionary representation of the puzzle

        Returns:
            Puzzle ID if successful, None if failed
        """
        try:
            from .models import PuzzleMetadata

            # Extract metadata
            metadata_dict = puzzle_data.get("metadata", {})
            metadata = PuzzleMetadata(
                id=metadata_dict.get("id"),
                topic=metadata_dict.get("topic"),
                grid_size=metadata_dict.get("grid_size"),
                difficulty=metadata_dict.get("difficulty"),
                word_count=metadata_dict.get("word_count", 0),
                fill_rate=metadata_dict.get("fill_rate", 0.0),
                iterations=metadata_dict.get("iterations", 0),
                status=metadata_dict.get("status", "completed"),
            )

            # Create stored puzzle
            puzzle = StoredPuzzle(
                metadata=metadata,
                grid_data=puzzle_data.get("grid_data", {}),
                clues=puzzle_data.get("clues", []),
                solution=puzzle_data.get("solution"),
                user_progress=puzzle_data.get("user_progress"),
            )

            # Save to store
            puzzle_id = self.store.save(puzzle)
            logger.info(f"Puzzle imported successfully: {puzzle_id}")

            return puzzle_id

        except Exception as e:
            logger.error(f"Error importing puzzle: {e}", exc_info=True)
            return None


# Singleton instance for convenience
_storage_manager: Optional[StorageManager] = None


def get_storage_manager() -> StorageManager:
    """
    Get the singleton storage manager instance.

    Returns:
        StorageManager instance
    """
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageManager()
    return _storage_manager


def reset_storage_manager() -> None:
    """
    Reset the storage manager (useful for testing).

    This function clears the singleton instance, forcing a new one to be
    created on the next call to get_storage_manager().
    """
    global _storage_manager
    _storage_manager = None


def initialize_storage() -> tuple[bool, str]:
    """
    Initialize the storage system.

    This function performs any necessary setup for the storage system.
    For in-memory storage, this is mostly a no-op, but it provides a
    hook for future database initialization.

    Returns:
        Tuple of (success, message)
    """
    try:
        # Get or create storage manager
        manager = get_storage_manager()

        # Perform health check
        is_healthy, message = manager.health_check()

        if is_healthy:
            logger.info("Storage initialized successfully")
            return True, "Storage initialized successfully"
        else:
            logger.error(f"Storage initialization failed: {message}")
            return False, f"Storage initialization failed: {message}"

    except Exception as e:
        logger.error(f"Error initializing storage: {e}", exc_info=True)
        return False, f"Error initializing storage: {str(e)}"


def cleanup_storage() -> tuple[bool, str]:
    """
    Clean up the storage system.

    This function performs any necessary cleanup for the storage system.
    For in-memory storage, this clears all data.

    Warning: This operation is irreversible for in-memory storage!

    Returns:
        Tuple of (success, message)
    """
    try:
        manager = get_storage_manager()
        count = manager.clear_storage()

        message = f"Storage cleaned up: {count} puzzles cleared"
        logger.info(message)

        return True, message

    except Exception as e:
        logger.error(f"Error cleaning up storage: {e}", exc_info=True)
        return False, f"Error cleaning up storage: {str(e)}"
