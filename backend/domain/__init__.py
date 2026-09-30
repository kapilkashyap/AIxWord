"""
Domain models and business logic for AIxWord.

This package contains the core domain models, grid engine, and business logic
for crossword puzzle generation and solving.
"""

from .grid import CrosswordGrid
from .models import Cell, Clue, Direction, WordPlacement
from .pattern import Pattern, PatternMatcher
from .validator import ValidationResult, WordValidator
from .word import Word

__all__ = [
    # Enums
    "Direction",
    # Core models
    "Cell",
    "WordPlacement",
    "Clue",
    # Domain classes
    "Word",
    "CrosswordGrid",
    # Pattern matching
    "Pattern",
    "PatternMatcher",
    # Validation
    "ValidationResult",
    "WordValidator",
]
