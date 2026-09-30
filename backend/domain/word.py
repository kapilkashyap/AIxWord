"""
Word domain model for crossword puzzle system.

This module provides the Word class which represents a word placed or to be placed
on the crossword grid, with methods for pattern matching, intersection detection,
and grid interaction.
"""

from typing import TYPE_CHECKING, Optional

from .models import Direction, WordPlacement

if TYPE_CHECKING:
    from .grid import CrosswordGrid


class Word:
    """
    Represents a word in the crossword puzzle.

    This class encapsulates a word with its position, direction, and clue,
    providing methods for grid interaction and validation.

    Attributes:
        text: The word text (uppercase letters)
        start_row: Starting row position (0-indexed)
        start_col: Starting column position (0-indexed)
        direction: Direction of word placement (ACROSS or DOWN)
        clue: Clue text for this word
        number: Clue number for reference
    """

    def __init__(
        self,
        text: str,
        start_row: int,
        start_col: int,
        direction: Direction,
        clue: str = "",
        number: int = 0,
    ):
        """
        Initialize a Word instance.

        Args:
            text: The word text (will be normalized to uppercase)
            start_row: Starting row position (0-indexed)
            start_col: Starting column position (0-indexed)
            direction: Direction of word placement
            clue: Clue text for this word (optional)
            number: Clue number for reference (optional)

        Raises:
            ValueError: If word text is invalid or positions are negative
        """
        if not text:
            raise ValueError("Word text cannot be empty")
        if not isinstance(text, str):
            raise ValueError(f"Word text must be a string, got {type(text)}")

        self.text = text.upper()
        if not self.text.isalpha():
            raise ValueError(f"Word must contain only letters, got '{text}'")

        if start_row < 0:
            raise ValueError(f"start_row must be non-negative, got {start_row}")
        if start_col < 0:
            raise ValueError(f"start_col must be non-negative, got {start_col}")

        self.start_row = start_row
        self.start_col = start_col
        self.direction = direction
        self.clue = clue
        self.number = number

    @property
    def length(self) -> int:
        """Get the length of the word."""
        return len(self.text)

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

    def get_pattern(self, grid: "CrosswordGrid") -> str:
        """
        Get the current pattern of this word on the grid.

        The pattern shows known letters and underscores for empty cells.
        For example, if the word is "APPLE" and only 'A' and 'E' are filled,
        the pattern might be "A__LE".

        Args:
            grid: The crossword grid to read from

        Returns:
            Pattern string with letters and underscores
        """
        pattern = []
        for row, col in self.get_cells():
            cell = grid.get_cell(row, col)
            if cell.value is not None:
                pattern.append(cell.value)
            else:
                pattern.append("_")
        return "".join(pattern)

    def is_complete(self, grid: "CrosswordGrid") -> bool:
        """
        Check if this word is fully filled on the grid.

        Args:
            grid: The crossword grid to check

        Returns:
            True if all cells of this word have values, False otherwise
        """
        for row, col in self.get_cells():
            cell = grid.get_cell(row, col)
            if cell.value is None:
                return False
        return True

    def intersects_with(self, other: "Word") -> Optional[tuple[int, int]]:
        """
        Find the intersection point with another word.

        Two words intersect if they share exactly one cell and have different
        directions (one ACROSS, one DOWN).

        Args:
            other: Another Word instance to check intersection with

        Returns:
            Tuple of (row, col) if words intersect, None otherwise
        """
        # Words must have different directions to intersect
        if self.direction == other.direction:
            return None

        # Get all cells for both words
        self_cells = set(self.get_cells())
        other_cells = set(other.get_cells())

        # Find intersection
        intersection = self_cells & other_cells

        # Valid intersection is exactly one cell
        if len(intersection) == 1:
            return list(intersection)[0]

        return None

    def get_letter_at_position(self, row: int, col: int) -> Optional[str]:
        """
        Get the letter at a specific position if this word occupies that cell.

        Args:
            row: Row position to check
            col: Column position to check

        Returns:
            Letter at that position, or None if word doesn't occupy that cell
        """
        cells = self.get_cells()
        if (row, col) not in cells:
            return None

        # Find index of this cell in the word
        index = cells.index((row, col))
        return self.text[index]

    def to_placement(self) -> WordPlacement:
        """
        Convert this Word to a WordPlacement object.

        Returns:
            WordPlacement instance with this word's data
        """
        return WordPlacement(
            word=self.text,
            start_row=self.start_row,
            start_col=self.start_col,
            direction=self.direction,
            clue=self.clue,
            number=self.number,
        )

    def __repr__(self) -> str:
        """Return string representation of the word."""
        return (
            f"Word(text='{self.text}', "
            f"start=({self.start_row}, {self.start_col}), "
            f"direction={self.direction}, "
            f"number={self.number})"
        )

    def __eq__(self, other: object) -> bool:
        """Check equality with another Word."""
        if not isinstance(other, Word):
            return NotImplemented
        return (
            self.text == other.text
            and self.start_row == other.start_row
            and self.start_col == other.start_col
            and self.direction == other.direction
        )

    def __hash__(self) -> int:
        """Return hash of the word for use in sets/dicts."""
        return hash((self.text, self.start_row, self.start_col, self.direction))
