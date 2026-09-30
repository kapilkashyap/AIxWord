"""
Pattern matching engine for crossword puzzle word validation.

This module provides pattern matching capabilities for finding words that fit
partially filled crossword slots. Patterns use underscores for unknown letters
and actual letters for known positions (e.g., "A__LE" matches "APPLE", "ANKLE").
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Pattern:
    """
    Represents a word pattern with known and unknown letter positions.

    A pattern is a string where:
    - Letters (A-Z) represent known positions
    - Underscores (_) represent unknown positions

    Example: "A__LE" means:
    - Position 0: must be 'A'
    - Position 1: unknown
    - Position 2: unknown
    - Position 3: must be 'L'
    - Position 4: must be 'E'

    Attributes:
        pattern: Pattern string (e.g., "A__LE")
    """

    pattern: str

    def __post_init__(self):
        """Validate and normalize pattern after initialization."""
        if not self.pattern:
            raise ValueError("Pattern cannot be empty")

        if not isinstance(self.pattern, str):
            raise ValueError(f"Pattern must be a string, got {type(self.pattern)}")

        # Normalize to uppercase
        self.pattern = self.pattern.upper()

        # Validate pattern contains only letters and underscores
        if not all(c.isalpha() or c == '_' for c in self.pattern):
            raise ValueError(
                f"Pattern must contain only letters and underscores, got '{self.pattern}'"
            )

    @property
    def length(self) -> int:
        """Get the length of the pattern."""
        return len(self.pattern)

    @property
    def known_positions(self) -> dict[int, str]:
        """
        Get a dictionary mapping positions to known letters.

        Returns:
            Dictionary where keys are positions (0-indexed) and values are letters
        """
        return {
            i: char
            for i, char in enumerate(self.pattern)
            if char != '_'
        }

    @property
    def unknown_count(self) -> int:
        """Get the number of unknown positions in the pattern."""
        return self.pattern.count('_')

    @property
    def is_complete(self) -> bool:
        """Check if pattern has no unknown positions."""
        return '_' not in self.pattern

    @property
    def is_empty(self) -> bool:
        """Check if pattern has no known positions."""
        return all(c == '_' for c in self.pattern)

    def matches(self, word: str) -> bool:
        """
        Check if a word matches this pattern.

        Args:
            word: Word to check (will be normalized to uppercase)

        Returns:
            True if word matches pattern, False otherwise
        """
        if not word:
            return False

        # Normalize word to uppercase
        word = word.upper()

        # Length must match
        if len(word) != self.length:
            return False

        # Check each known position
        for i, pattern_char in enumerate(self.pattern):
            if pattern_char != '_':
                if word[i] != pattern_char:
                    return False

        return True

    def to_regex(self) -> str:
        """
        Convert pattern to a regular expression string.

        Returns:
            Regex pattern string (e.g., "A..LE" for "A__LE")
        """
        # Replace underscores with . (any character)
        # Escape any special regex characters in letters (though A-Z shouldn't have any)
        regex = self.pattern.replace('_', '.')
        return f"^{regex}$"

    def get_constraints(self) -> list[tuple[int, str]]:
        """
        Get list of position constraints.

        Returns:
            List of (position, letter) tuples for known positions
        """
        return list(self.known_positions.items())

    def get_char_at(self, position: int) -> Optional[str]:
        """
        Get the character at a specific position.

        Args:
            position: Position index (0-based)

        Returns:
            Letter if known, None if unknown ('_')

        Raises:
            IndexError: If position is out of bounds
        """
        if position < 0 or position >= self.length:
            raise IndexError(f"Position {position} out of bounds for pattern of length {self.length}")

        char = self.pattern[position]
        return char if char != '_' else None

    def __str__(self) -> str:
        """Return string representation of pattern."""
        return self.pattern

    def __repr__(self) -> str:
        """Return detailed representation of pattern."""
        return f"Pattern('{self.pattern}')"

    def __eq__(self, other: object) -> bool:
        """Check equality with another Pattern."""
        if not isinstance(other, Pattern):
            return NotImplemented
        return self.pattern == other.pattern

    def __hash__(self) -> int:
        """Return hash of pattern for use in sets/dicts."""
        return hash(self.pattern)


class PatternMatcher:
    """
    Utility class for matching words against patterns.

    This class provides methods for filtering word lists, scoring matches,
    and suggesting words based on patterns.
    """

    @staticmethod
    def find_matches(pattern: Pattern, candidates: list[str]) -> list[str]:
        """
        Filter a list of candidate words by pattern.

        Args:
            pattern: Pattern to match against
            candidates: List of candidate words

        Returns:
            List of words that match the pattern
        """
        matches = []
        for word in candidates:
            if pattern.matches(word):
                matches.append(word.upper())
        return matches

    @staticmethod
    def score_match(word: str, pattern: Pattern) -> float:
        """
        Score how well a word fits a pattern.

        The score is based on:
        - 1.0 if word matches pattern perfectly
        - 0.0 if word doesn't match pattern
        - Partial scores for partial matches (future enhancement)

        Args:
            word: Word to score
            pattern: Pattern to match against

        Returns:
            Score between 0.0 and 1.0
        """
        if pattern.matches(word):
            return 1.0
        return 0.0

    @staticmethod
    def suggest_words(
        pattern: Pattern,
        topic: Optional[str] = None,
        max_suggestions: int = 10
    ) -> list[str]:
        """
        Suggest words that match a pattern.

        This is a placeholder for LLM-based word suggestion.
        In the actual implementation, this would call an LLM to generate
        contextually appropriate words.

        Args:
            pattern: Pattern to match
            topic: Optional topic for context-aware suggestions
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of suggested words (empty in this placeholder)
        """
        # Placeholder - will be implemented with LLM integration
        # For now, return empty list
        return []

    @staticmethod
    def create_pattern_from_grid(
        grid_values: list[Optional[str]]
    ) -> Pattern:
        """
        Create a pattern from a list of grid cell values.

        Args:
            grid_values: List of cell values (None for empty, letter for filled)

        Returns:
            Pattern object representing the grid state

        Raises:
            ValueError: If grid_values is empty or contains invalid values
        """
        if not grid_values:
            raise ValueError("Grid values cannot be empty")

        pattern_str = ""
        for value in grid_values:
            if value is None:
                pattern_str += "_"
            elif isinstance(value, str) and len(value) == 1 and value.isalpha():
                pattern_str += value.upper()
            else:
                raise ValueError(f"Invalid grid value: {value}")

        return Pattern(pattern_str)

    @staticmethod
    def match_with_regex(pattern: Pattern, candidates: list[str]) -> list[str]:
        """
        Filter candidates using compiled regex for better performance.

        This is more efficient than Pattern.matches() for large candidate lists.

        Args:
            pattern: Pattern to match against
            candidates: List of candidate words

        Returns:
            List of words that match the pattern
        """
        regex = re.compile(pattern.to_regex(), re.IGNORECASE)
        matches = []
        for word in candidates:
            if regex.match(word):
                matches.append(word.upper())
        return matches

    @staticmethod
    def get_pattern_complexity(pattern: Pattern) -> float:
        """
        Calculate the complexity of a pattern.

        Complexity is the ratio of known positions to total positions.
        - 0.0: all positions unknown (e.g., "____")
        - 1.0: all positions known (e.g., "WORD")

        Args:
            pattern: Pattern to analyze

        Returns:
            Complexity score between 0.0 and 1.0
        """
        if pattern.length == 0:
            return 0.0

        known_count = len(pattern.known_positions)
        return known_count / pattern.length

    @staticmethod
    def merge_patterns(pattern1: Pattern, pattern2: Pattern) -> Optional[Pattern]:
        """
        Merge two patterns if they are compatible.

        Two patterns are compatible if:
        - They have the same length
        - Known positions don't conflict

        Args:
            pattern1: First pattern
            pattern2: Second pattern

        Returns:
            Merged pattern if compatible, None otherwise
        """
        if pattern1.length != pattern2.length:
            return None

        merged = []
        for i in range(pattern1.length):
            char1 = pattern1.get_char_at(i)
            char2 = pattern2.get_char_at(i)

            if char1 is not None and char2 is not None:
                # Both known - must match
                if char1 != char2:
                    return None
                merged.append(char1)
            elif char1 is not None:
                merged.append(char1)
            elif char2 is not None:
                merged.append(char2)
            else:
                merged.append('_')

        return Pattern(''.join(merged))
