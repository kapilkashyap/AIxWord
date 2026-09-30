"""
Crossword grid engine for AIxWord puzzle system.

This module provides the CrosswordGrid class which manages the crossword puzzle grid,
including word placement, collision detection, intersection validation, and grid state
management.
"""

from typing import Optional

from .models import Cell, Direction, WordPlacement
from .word import Word


class CrosswordGrid:
    """
    Manages the crossword puzzle grid and word placements.

    The grid is represented as a 2D array of Cell objects. This class provides
    methods for placing words, detecting collisions, validating intersections,
    and managing grid state.

    Attributes:
        size: Grid dimension (NxN square grid)
        cells: 2D list of Cell objects
        words: List of Word objects placed on the grid
    """

    def __init__(self, size: int = 8):
        """
        Initialize an empty crossword grid.

        Args:
            size: Grid dimension (default 8 for 8x8 grid)

        Raises:
            ValueError: If size is less than 3 or greater than 50
        """
        if size < 3:
            raise ValueError(f"Grid size must be at least 3, got {size}")
        if size > 50:
            raise ValueError(f"Grid size must be at most 50, got {size}")

        self.size = size
        self.cells: list[list[Cell]] = []
        self.words: list[Word] = []

        # Initialize empty grid
        for row in range(size):
            row_cells = []
            for col in range(size):
                row_cells.append(Cell(row=row, col=col))
            self.cells.append(row_cells)

    def get_cell(self, row: int, col: int) -> Cell:
        """
        Get the cell at the specified position.

        Args:
            row: Row position (0-indexed)
            col: Column position (0-indexed)

        Returns:
            Cell at the specified position

        Raises:
            IndexError: If position is out of bounds
        """
        if not self.is_valid_position(row, col):
            raise IndexError(f"Position ({row}, {col}) is out of bounds for {self.size}x{self.size} grid")
        return self.cells[row][col]

    def set_cell(self, row: int, col: int, value: Optional[str]) -> None:
        """
        Set the value of a cell at the specified position.

        Args:
            row: Row position (0-indexed)
            col: Column position (0-indexed)
            value: Letter to place in cell (None to clear, uppercase A-Z)

        Raises:
            IndexError: If position is out of bounds
            ValueError: If value is invalid
        """
        if not self.is_valid_position(row, col):
            raise IndexError(f"Position ({row}, {col}) is out of bounds for {self.size}x{self.size} grid")

        cell = self.cells[row][col]
        if value is not None:
            if not isinstance(value, str) or len(value) != 1:
                raise ValueError(f"Cell value must be a single character, got '{value}'")
            value = value.upper()
            if not value.isalpha():
                raise ValueError(f"Cell value must be a letter, got '{value}'")

        cell.value = value

    def is_valid_position(self, row: int, col: int) -> bool:
        """
        Check if a position is within grid bounds.

        Args:
            row: Row position to check
            col: Column position to check

        Returns:
            True if position is valid, False otherwise
        """
        return 0 <= row < self.size and 0 <= col < self.size

    def can_place_word(self, placement: WordPlacement) -> bool:
        """
        Check if a word can be placed at the specified position.

        This checks:
        - All cells are within bounds
        - No blocked cells in the path
        - No conflicting letters (different letter already in cell)
        - Valid intersections with existing words

        Args:
            placement: WordPlacement specification

        Returns:
            True if word can be placed, False otherwise
        """
        cells = placement.get_cells()

        # Check all cells are within bounds
        for row, col in cells:
            if not self.is_valid_position(row, col):
                return False

        # Check each cell for conflicts
        for i, (row, col) in enumerate(cells):
            cell = self.get_cell(row, col)

            # Cannot place on blocked cells
            if cell.is_blocked:
                return False

            # If cell has a value, it must match the word's letter
            if cell.value is not None:
                if cell.value != placement.word[i]:
                    return False

        return True

    def place_word(self, placement: WordPlacement) -> bool:
        """
        Place a word on the grid.

        This method:
        1. Validates the placement is possible
        2. Creates a Word object
        3. Fills the grid cells with the word's letters
        4. Adds the word to the words list

        Args:
            placement: WordPlacement specification

        Returns:
            True if word was placed successfully, False otherwise
        """
        # Check if placement is valid
        if not self.can_place_word(placement):
            return False

        # Create Word object
        word = Word(
            text=placement.word,
            start_row=placement.start_row,
            start_col=placement.start_col,
            direction=placement.direction,
            clue=placement.clue,
            number=placement.number,
        )

        # Place letters on grid
        cells = placement.get_cells()
        for i, (row, col) in enumerate(cells):
            self.set_cell(row, col, placement.word[i])

        # Add word to list
        self.words.append(word)

        return True

    def remove_word(self, word: Word) -> None:
        """
        Remove a word from the grid.

        This method:
        1. Removes the word from the words list
        2. Clears cells that are only used by this word
        3. Keeps cells that are shared with other words

        Args:
            word: Word instance to remove
        """
        if word not in self.words:
            return

        # Remove from words list
        self.words.remove(word)

        # Clear cells that are only used by this word
        for row, col in word.get_cells():
            # Check if any other word uses this cell
            cell_used = False
            for other_word in self.words:
                if (row, col) in other_word.get_cells():
                    cell_used = True
                    break

            # Clear cell if not used by other words
            if not cell_used:
                self.set_cell(row, col, None)

    def get_word_at(self, row: int, col: int, direction: Direction) -> Optional[Word]:
        """
        Find a word at the specified position and direction.

        Args:
            row: Row position
            col: Column position
            direction: Direction to search (ACROSS or DOWN)

        Returns:
            Word instance if found, None otherwise
        """
        for word in self.words:
            if word.direction == direction:
                if (row, col) in word.get_cells():
                    return word
        return None

    def get_intersecting_words(self, word: Word) -> list[Word]:
        """
        Find all words that intersect with the given word.

        Args:
            word: Word instance to check intersections for

        Returns:
            List of Word instances that intersect with the given word
        """
        intersecting = []
        for other_word in self.words:
            if other_word != word:
                if word.intersects_with(other_word) is not None:
                    intersecting.append(other_word)
        return intersecting

    def get_fill_rate(self) -> float:
        """
        Calculate the percentage of non-blocked cells that are filled.

        Returns:
            Fill rate as a float between 0.0 and 1.0
        """
        total_cells = 0
        filled_cells = 0

        for row in range(self.size):
            for col in range(self.size):
                cell = self.get_cell(row, col)
                if not cell.is_blocked:
                    total_cells += 1
                    if cell.is_filled:
                        filled_cells += 1

        if total_cells == 0:
            return 0.0

        return filled_cells / total_cells

    def get_word_count(self) -> int:
        """
        Get the number of words placed on the grid.

        Returns:
            Number of words on the grid
        """
        return len(self.words)

    def assign_numbers(self) -> None:
        """
        Assign clue numbers to word starting positions.

        Numbers are assigned in reading order (left to right, top to bottom).
        A cell gets a number if it starts at least one word (ACROSS or DOWN).
        """
        # Clear existing numbers
        for row in range(self.size):
            for col in range(self.size):
                self.cells[row][col].number = None

        # Find all word starting positions
        word_starts: set[tuple[int, int]] = set()
        for word in self.words:
            word_starts.add((word.start_row, word.start_col))

        # Assign numbers in reading order
        number = 1
        for row in range(self.size):
            for col in range(self.size):
                if (row, col) in word_starts:
                    self.cells[row][col].number = number
                    # Update word numbers
                    for word in self.words:
                        if word.start_row == row and word.start_col == col:
                            word.number = number
                    number += 1

    def clone(self) -> "CrosswordGrid":
        """
        Create a deep copy of this grid.

        Returns:
            New CrosswordGrid instance with copied state
        """
        new_grid = CrosswordGrid(size=self.size)

        # Copy cells
        for row in range(self.size):
            for col in range(self.size):
                new_grid.cells[row][col] = self.cells[row][col].clone()

        # Copy words
        for word in self.words:
            new_word = Word(
                text=word.text,
                start_row=word.start_row,
                start_col=word.start_col,
                direction=word.direction,
                clue=word.clue,
                number=word.number,
            )
            new_grid.words.append(new_word)

        return new_grid

    def to_dict(self) -> dict:
        """
        Serialize grid state to dictionary.

        Returns:
            Dictionary representation of grid state
        """
        return {
            "size": self.size,
            "cells": [
                [cell.to_dict() for cell in row]
                for row in self.cells
            ],
            "words": [
                {
                    "text": word.text,
                    "start_row": word.start_row,
                    "start_col": word.start_col,
                    "direction": word.direction.value,
                    "clue": word.clue,
                    "number": word.number,
                }
                for word in self.words
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CrosswordGrid":
        """
        Deserialize grid state from dictionary.

        Args:
            data: Dictionary representation of grid state

        Returns:
            CrosswordGrid instance with restored state
        """
        grid = cls(size=data["size"])

        # Restore cells
        for row_idx, row_data in enumerate(data["cells"]):
            for col_idx, cell_data in enumerate(row_data):
                grid.cells[row_idx][col_idx] = Cell.from_dict(cell_data)

        # Restore words
        for word_data in data["words"]:
            word = Word(
                text=word_data["text"],
                start_row=word_data["start_row"],
                start_col=word_data["start_col"],
                direction=Direction(word_data["direction"]),
                clue=word_data["clue"],
                number=word_data["number"],
            )
            grid.words.append(word)

        return grid

    def __repr__(self) -> str:
        """Return string representation of the grid."""
        return f"CrosswordGrid(size={self.size}, words={len(self.words)}, fill_rate={self.get_fill_rate():.2%})"
