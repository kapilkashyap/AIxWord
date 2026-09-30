"""
Core domain models for AIxWord crossword puzzle system.

This module defines the fundamental data structures used throughout the application:
- Direction: Enum for word orientation (ACROSS, DOWN)
- Cell: Individual grid cell with position and state
- WordPlacement: Specification for placing a word on the grid
- Clue: Crossword clue with metadata
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Direction(str, Enum):
    """
    Direction enum for word placement in crossword grid.

    ACROSS: Horizontal word placement (left to right)
    DOWN: Vertical word placement (top to bottom)
    """
    ACROSS = "across"
    DOWN = "down"

    def __str__(self) -> str:
        """Return string representation of direction."""
        return self.value

    @property
    def opposite(self) -> "Direction":
        """Get the opposite direction."""
        return Direction.DOWN if self == Direction.ACROSS else Direction.ACROSS


@dataclass
class Cell:
    """
    Represents a single cell in the crossword grid.

    Attributes:
        row: Row position (0-indexed from top)
        col: Column position (0-indexed from left)
        value: Letter in the cell (None if empty, uppercase A-Z)
        is_blocked: Whether this cell is a black square (blocked)
        number: Clue number if this cell starts a word (None otherwise)
    """
    row: int
    col: int
    value: Optional[str] = None
    is_blocked: bool = False
    number: Optional[int] = None

    def __post_init__(self):
        """Validate cell data after initialization."""
        if self.value is not None:
            if not isinstance(self.value, str):
                raise ValueError(f"Cell value must be a string, got {type(self.value)}")
            if len(self.value) != 1:
                raise ValueError(f"Cell value must be a single character, got '{self.value}'")
            # Normalize to uppercase
            self.value = self.value.upper()
            if not self.value.isalpha():
                raise ValueError(f"Cell value must be a letter, got '{self.value}'")

    @property
    def is_empty(self) -> bool:
        """Check if cell is empty (no value and not blocked)."""
        return self.value is None and not self.is_blocked

    @property
    def is_filled(self) -> bool:
        """Check if cell has a letter value."""
        return self.value is not None

    def clone(self) -> "Cell":
        """Create a deep copy of this cell."""
        return Cell(
            row=self.row,
            col=self.col,
            value=self.value,
            is_blocked=self.is_blocked,
            number=self.number,
        )

    def to_dict(self) -> dict:
        """Convert cell to dictionary for serialization."""
        return {
            "row": self.row,
            "col": self.col,
            "value": self.value,
            "is_blocked": self.is_blocked,
            "number": self.number,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Cell":
        """Create cell from dictionary."""
        return cls(
            row=data["row"],
            col=data["col"],
            value=data.get("value"),
            is_blocked=data.get("is_blocked", False),
            number=data.get("number"),
        )


@dataclass
class WordPlacement:
    """
    Specification for placing a word on the crossword grid.

    Attributes:
        word: The word to place (uppercase letters)
        start_row: Starting row position (0-indexed)
        start_col: Starting column position (0-indexed)
        direction: Direction of word placement (ACROSS or DOWN)
        clue: Clue text for this word
        number: Clue number for reference
    """
    word: str
    start_row: int
    start_col: int
    direction: Direction
    clue: str
    number: int

    def __post_init__(self):
        """Validate word placement data after initialization."""
        if not isinstance(self.word, str):
            raise ValueError(f"Word must be a string, got {type(self.word)}")
        if not self.word:
            raise ValueError("Word cannot be empty")
        # Normalize to uppercase
        self.word = self.word.upper()
        if not self.word.isalpha():
            raise ValueError(f"Word must contain only letters, got '{self.word}'")
        if self.start_row < 0:
            raise ValueError(f"start_row must be non-negative, got {self.start_row}")
        if self.start_col < 0:
            raise ValueError(f"start_col must be non-negative, got {self.start_col}")
        if self.number < 1:
            raise ValueError(f"Clue number must be positive, got {self.number}")
        if not isinstance(self.direction, Direction):
            raise ValueError(f"direction must be Direction enum, got {type(self.direction)}")

    @property
    def length(self) -> int:
        """Get the length of the word."""
        return len(self.word)

    @property
    def end_row(self) -> int:
        """Get the ending row position (inclusive)."""
        if self.direction == Direction.DOWN:
            return self.start_row + self.length - 1
        return self.start_row

    @property
    def end_col(self) -> int:
        """Get the ending column position (inclusive)."""
        if self.direction == Direction.ACROSS:
            return self.start_col + self.length - 1
        return self.start_col

    def get_cells(self) -> list[tuple[int, int]]:
        """
        Get list of (row, col) tuples for all cells occupied by this word.

        Returns:
            List of (row, col) tuples in order from start to end
        """
        cells = []
        for i in range(self.length):
            if self.direction == Direction.ACROSS:
                cells.append((self.start_row, self.start_col + i))
            else:  # DOWN
                cells.append((self.start_row + i, self.start_col))
        return cells

    def to_dict(self) -> dict:
        """Convert word placement to dictionary for serialization."""
        return {
            "word": self.word,
            "start_row": self.start_row,
            "start_col": self.start_col,
            "direction": self.direction.value,
            "clue": self.clue,
            "number": self.number,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WordPlacement":
        """Create word placement from dictionary."""
        return cls(
            word=data["word"],
            start_row=data["start_row"],
            start_col=data["start_col"],
            direction=Direction(data["direction"]),
            clue=data["clue"],
            number=data["number"],
        )


@dataclass
class Clue:
    """
    Represents a crossword clue with its metadata.

    Attributes:
        number: Clue number for reference
        direction: Direction of the answer (ACROSS or DOWN)
        text: The clue text
        answer: The answer word (uppercase letters)
        start_row: Starting row position of answer
        start_col: Starting column position of answer
        length: Length of the answer word
    """
    number: int
    direction: Direction
    text: str
    answer: str
    start_row: int
    start_col: int
    length: int

    def __post_init__(self):
        """Validate clue data after initialization."""
        if self.number < 1:
            raise ValueError(f"Clue number must be positive, got {self.number}")
        if not isinstance(self.direction, Direction):
            raise ValueError(f"direction must be Direction enum, got {type(self.direction)}")
        if not self.text:
            raise ValueError("Clue text cannot be empty")
        if not self.answer:
            raise ValueError("Answer cannot be empty")
        # Normalize answer to uppercase
        self.answer = self.answer.upper()
        if not self.answer.isalpha():
            raise ValueError(f"Answer must contain only letters, got '{self.answer}'")
        if self.length != len(self.answer):
            raise ValueError(f"Length {self.length} does not match answer length {len(self.answer)}")
        if self.start_row < 0:
            raise ValueError(f"start_row must be non-negative, got {self.start_row}")
        if self.start_col < 0:
            raise ValueError(f"start_col must be non-negative, got {self.start_col}")

    def to_word_placement(self) -> WordPlacement:
        """Convert clue to WordPlacement for grid operations."""
        return WordPlacement(
            word=self.answer,
            start_row=self.start_row,
            start_col=self.start_col,
            direction=self.direction,
            clue=self.text,
            number=self.number,
        )

    def to_dict(self) -> dict:
        """Convert clue to dictionary for serialization."""
        return {
            "number": self.number,
            "direction": self.direction.value,
            "text": self.text,
            "answer": self.answer,
            "start_row": self.start_row,
            "start_col": self.start_col,
            "length": self.length,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Clue":
        """Create clue from dictionary."""
        return cls(
            number=data["number"],
            direction=Direction(data["direction"]),
            text=data["text"],
            answer=data["answer"],
            start_row=data["start_row"],
            start_col=data["start_col"],
            length=data["length"],
        )
