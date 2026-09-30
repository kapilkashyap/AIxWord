"""
API services for AIxWord application.

This package contains service layer implementations for:
- Puzzle solving with AI
- Hint generation
- Solution validation
"""

from .solver import PuzzleSolver

__all__ = ["PuzzleSolver"]
