"""
Word validation engine for crossword puzzle placement.

This module provides comprehensive validation for word placements on the crossword
grid, including bounds checking, conflict detection, intersection validation, and
pattern extraction.
"""

from dataclasses import dataclass, field

from .grid import CrosswordGrid
from .models import Direction, WordPlacement
from .pattern import Pattern, PatternMatcher


@dataclass
class ValidationResult:
    """
    Result of a word placement validation.

    Attributes:
        is_valid: Whether the placement is valid
        errors: List of validation errors (empty if valid)
        warnings: List of warnings (non-blocking issues)
    """
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, error: str) -> None:
        """
        Add an error to the result.

        Args:
            error: Error message to add
        """
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """
        Add a warning to the result.

        Args:
            warning: Warning message to add
        """
        self.warnings.append(warning)

    def __str__(self) -> str:
        """Return string representation of validation result."""
        if self.is_valid:
            status = "VALID"
            if self.warnings:
                status += f" (with {len(self.warnings)} warning(s))"
            return status
        else:
            return f"INVALID: {', '.join(self.errors)}"

    def __repr__(self) -> str:
        """Return detailed representation of validation result."""
        return (
            f"ValidationResult(is_valid={self.is_valid}, "
            f"errors={len(self.errors)}, warnings={len(self.warnings)})"
        )


class WordValidator:
    """
    Validator for word placements on crossword grids.

    This class provides comprehensive validation including:
    - Bounds checking (word fits within grid)
    - Conflict detection (no letter mismatches)
    - Intersection validation (proper crossings)
    - Format validation (word and clue format)
    - Pattern extraction (current grid state)
    """

    @staticmethod
    def validate_placement(
        grid: CrosswordGrid,
        placement: WordPlacement
    ) -> ValidationResult:
        """
        Perform comprehensive validation of a word placement.

        This checks all validation rules:
        - Bounds (word fits in grid)
        - Conflicts (no letter mismatches)
        - Intersections (valid crossings)
        - Format (valid word and clue)

        Args:
            grid: Crossword grid to validate against
            placement: Word placement to validate

        Returns:
            ValidationResult with validation status and messages
        """
        result = ValidationResult(is_valid=True)

        # Validate word format
        if not WordValidator.validate_word_format(placement.word):
            result.add_error(f"Invalid word format: '{placement.word}'")

        # Validate clue format
        if not WordValidator.validate_clue(placement.clue):
            result.add_warning("Clue is empty or invalid")

        # Check bounds
        if not WordValidator.check_bounds(grid, placement):
            result.add_error(
                f"Word extends beyond grid bounds: "
                f"({placement.start_row}, {placement.start_col}) "
                f"length {placement.length} {placement.direction}"
            )
            # If out of bounds, other checks are meaningless
            return result

        # Check for conflicts
        conflicts = WordValidator.check_conflicts(grid, placement)
        for conflict in conflicts:
            result.add_error(conflict)

        # Check intersections
        intersection_result = WordValidator.check_intersections(grid, placement)
        result.errors.extend(intersection_result.errors)
        result.warnings.extend(intersection_result.warnings)
        if not intersection_result.is_valid:
            result.is_valid = False

        return result

    @staticmethod
    def check_bounds(grid: CrosswordGrid, placement: WordPlacement) -> bool:
        """
        Check if a word placement fits within grid bounds.

        Args:
            grid: Crossword grid
            placement: Word placement to check

        Returns:
            True if word fits within bounds, False otherwise
        """
        # Check starting position
        if not grid.is_valid_position(placement.start_row, placement.start_col):
            return False

        # Check ending position
        if placement.direction == Direction.ACROSS:
            end_col = placement.start_col + placement.length - 1
            return grid.is_valid_position(placement.start_row, end_col)
        else:  # DOWN
            end_row = placement.start_row + placement.length - 1
            return grid.is_valid_position(end_row, placement.start_col)

    @staticmethod
    def check_conflicts(
        grid: CrosswordGrid,
        placement: WordPlacement
    ) -> list[str]:
        """
        Find conflicting cells for a word placement.

        A conflict occurs when:
        - A cell is blocked (black square)
        - A cell has a different letter than required

        Args:
            grid: Crossword grid
            placement: Word placement to check

        Returns:
            List of conflict error messages (empty if no conflicts)
        """
        conflicts = []
        cells = placement.get_cells()

        for i, (row, col) in enumerate(cells):
            cell = grid.get_cell(row, col)
            required_letter = placement.word[i]

            # Check if cell is blocked
            if cell.is_blocked:
                conflicts.append(
                    f"Cell ({row}, {col}) is blocked but required for word"
                )
                continue

            # Check if cell has conflicting letter
            if cell.value is not None and cell.value != required_letter:
                conflicts.append(
                    f"Conflict at cell ({row}, {col}): has '{cell.value}' but word requires '{required_letter}'"
                )

        return conflicts

    @staticmethod
    def check_intersections(
        grid: CrosswordGrid,
        placement: WordPlacement
    ) -> ValidationResult:
        """
        Validate intersections with existing words.

        This checks that:
        - Intersections occur at matching letters
        - Parallel words don't touch (crossword rule)
        - Words don't overlap improperly

        Args:
            grid: Crossword grid
            placement: Word placement to check

        Returns:
            ValidationResult for intersection validation
        """
        result = ValidationResult(is_valid=True)

        # Get cells occupied by this placement
        placement_cells = set(placement.get_cells())

        # Check each existing word
        for word in grid.words:
            word_cells = set(word.get_cells())
            intersection = placement_cells & word_cells

            if not intersection:
                # No intersection - check for parallel adjacency
                if word.direction == placement.direction:
                    # Same direction - check if they're adjacent (invalid)
                    if WordValidator._are_parallel_adjacent(placement, word):
                        result.add_warning(
                            f"Word is adjacent to parallel word at "
                            f"({word.start_row}, {word.start_col})"
                        )
                continue

            # Words intersect
            if word.direction == placement.direction:
                # Same direction - this is an overlap, not a valid intersection
                result.add_error(
                    f"Word overlaps with existing {word.direction} word at "
                    f"({word.start_row}, {word.start_col})"
                )
                continue

            # Different directions - validate intersection point
            if len(intersection) > 1:
                result.add_error(
                    f"Word intersects existing word at multiple points: {intersection}"
                )
                continue

            # Single intersection point - check letters match
            row, col = list(intersection)[0]

            # Find position in each word
            placement_idx = placement.get_cells().index((row, col))
            word_idx = word.get_cells().index((row, col))

            placement_letter = placement.word[placement_idx]
            word_letter = word.text[word_idx]

            if placement_letter != word_letter:
                result.add_error(
                    f"Intersection at ({row}, {col}) has conflicting letters: "
                    f"'{placement_letter}' vs '{word_letter}'"
                )

        return result

    @staticmethod
    def _are_parallel_adjacent(
        placement: WordPlacement,
        word
    ) -> bool:
        """
        Check if two parallel words are adjacent (touching).

        Args:
            placement: Word placement to check
            word: Existing word to check against

        Returns:
            True if words are parallel and adjacent, False otherwise
        """
        if placement.direction != word.direction:
            return False

        if placement.direction == Direction.ACROSS:
            # Same row or adjacent rows
            if abs(placement.start_row - word.start_row) <= 1:
                # Check column overlap
                p_start, p_end = placement.start_col, placement.end_col
                w_start, w_end = word.start_col, word.end_col
                return not (p_end < w_start or p_start > w_end)
        else:  # DOWN
            # Same column or adjacent columns
            if abs(placement.start_col - word.start_col) <= 1:
                # Check row overlap
                p_start, p_end = placement.start_row, placement.end_row
                w_start, w_end = word.start_row, word.end_row
                return not (p_end < w_start or p_start > w_end)

        return False

    @staticmethod
    def validate_word_format(word: str) -> bool:
        """
        Validate word format.

        A valid word:
        - Is not empty
        - Contains only letters (A-Z, case-insensitive)
        - Has length >= 2 (typical crossword minimum)

        Args:
            word: Word to validate

        Returns:
            True if word format is valid, False otherwise
        """
        if not word:
            return False

        if not isinstance(word, str):
            return False

        if len(word) < 2:
            return False

        return word.isalpha()

    @staticmethod
    def validate_clue(clue: str) -> bool:
        """
        Validate clue format.

        A valid clue:
        - Is not empty
        - Is a string
        - Has reasonable length (> 0, < 500 characters)

        Args:
            clue: Clue to validate

        Returns:
            True if clue format is valid, False otherwise
        """
        if not clue:
            return False

        if not isinstance(clue, str):
            return False

        # Clue should have reasonable length
        if len(clue) > 500:
            return False

        return True

    @staticmethod
    def get_required_pattern(
        grid: CrosswordGrid,
        placement: WordPlacement
    ) -> Pattern:
        """
        Extract the current pattern for a word placement from the grid.

        This creates a pattern showing which letters are already filled
        in the cells where the word would be placed.

        Args:
            grid: Crossword grid
            placement: Word placement to extract pattern for

        Returns:
            Pattern object representing current grid state

        Raises:
            IndexError: If placement is out of bounds
        """
        cells = placement.get_cells()
        grid_values = []

        for row, col in cells:
            cell = grid.get_cell(row, col)
            grid_values.append(cell.value)

        return PatternMatcher.create_pattern_from_grid(grid_values)

    @staticmethod
    def validate_against_pattern(
        word: str,
        pattern: Pattern
    ) -> ValidationResult:
        """
        Validate that a word matches a required pattern.

        Args:
            word: Word to validate
            pattern: Required pattern

        Returns:
            ValidationResult indicating if word matches pattern
        """
        result = ValidationResult(is_valid=True)

        if not pattern.matches(word):
            result.add_error(
                f"Word '{word}' does not match required pattern '{pattern}'"
            )

            # Add detailed mismatch information
            if len(word) != pattern.length:
                result.add_error(
                    f"Length mismatch: word has {len(word)} letters, "
                    f"pattern requires {pattern.length}"
                )
            else:
                for i, (word_char, pattern_char) in enumerate(zip(word, pattern.pattern)):
                    if pattern_char != '_' and word_char.upper() != pattern_char:
                        result.add_error(
                            f"Position {i}: word has '{word_char}', "
                            f"pattern requires '{pattern_char}'"
                        )

        return result

    @staticmethod
    def can_place_word(
        grid: CrosswordGrid,
        placement: WordPlacement
    ) -> bool:
        """
        Quick check if a word can be placed (without detailed errors).

        This is a convenience method that returns a simple boolean.
        For detailed validation results, use validate_placement().

        Args:
            grid: Crossword grid
            placement: Word placement to check

        Returns:
            True if word can be placed, False otherwise
        """
        result = WordValidator.validate_placement(grid, placement)
        return result.is_valid
