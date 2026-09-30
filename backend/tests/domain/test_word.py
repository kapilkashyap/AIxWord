"""
Tests for Word domain model.

This module contains comprehensive tests for the Word class including:
- Word creation and validation
- Cell position calculation
- Pattern extraction from grid
- Word completion checking
- Intersection detection
- Conversion to WordPlacement
"""

import pytest

from backend.domain import CrosswordGrid, Direction, Word, WordPlacement


class TestWordCreation:
    """Tests for Word initialization and validation."""

    def test_create_word_basic(self):
        """Test creating a basic word."""
        word = Word(
            text="HELLO",
            start_row=2,
            start_col=3,
            direction=Direction.ACROSS,
        )
        assert word.text == "HELLO"
        assert word.start_row == 2
        assert word.start_col == 3
        assert word.direction == Direction.ACROSS

    def test_create_word_with_clue(self):
        """Test creating word with clue and number."""
        word = Word(
            text="WORLD",
            start_row=0,
            start_col=0,
            direction=Direction.DOWN,
            clue="The Earth",
            number=5,
        )
        assert word.clue == "The Earth"
        assert word.number == 5

    def test_word_text_normalized_to_uppercase(self):
        """Test word text is normalized to uppercase."""
        word = Word("hello", 0, 0, Direction.ACROSS)
        assert word.text == "HELLO"

    def test_word_empty_text_raises_error(self):
        """Test creating word with empty text raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Word("", 0, 0, Direction.ACROSS)

    def test_word_non_alpha_text_raises_error(self):
        """Test creating word with non-alphabetic text raises ValueError."""
        with pytest.raises(ValueError, match="only letters"):
            Word("HELLO123", 0, 0, Direction.ACROSS)
        with pytest.raises(ValueError, match="only letters"):
            Word("HELLO-WORLD", 0, 0, Direction.ACROSS)

    def test_word_negative_start_row_raises_error(self):
        """Test creating word with negative start_row raises ValueError."""
        with pytest.raises(ValueError, match="non-negative"):
            Word("HELLO", -1, 0, Direction.ACROSS)

    def test_word_negative_start_col_raises_error(self):
        """Test creating word with negative start_col raises ValueError."""
        with pytest.raises(ValueError, match="non-negative"):
            Word("HELLO", 0, -1, Direction.ACROSS)

    def test_word_invalid_type_raises_error(self):
        """Test creating word with invalid text type raises ValueError."""
        with pytest.raises(ValueError, match="must be a string"):
            Word(123, 0, 0, Direction.ACROSS)


class TestWordProperties:
    """Tests for Word properties."""

    def test_word_length(self):
        """Test word length property."""
        word = Word("HELLO", 0, 0, Direction.ACROSS)
        assert word.length == 5

    def test_word_length_single_letter(self):
        """Test length of single-letter word."""
        word = Word("I", 0, 0, Direction.ACROSS)
        assert word.length == 1

    def test_end_row_across(self):
        """Test end_row for ACROSS word."""
        word = Word("HELLO", 3, 2, Direction.ACROSS)
        assert word.end_row == 3  # Same as start_row

    def test_end_row_down(self):
        """Test end_row for DOWN word."""
        word = Word("HELLO", 3, 2, Direction.DOWN)
        assert word.end_row == 7  # start_row + length - 1

    def test_end_col_across(self):
        """Test end_col for ACROSS word."""
        word = Word("HELLO", 3, 2, Direction.ACROSS)
        assert word.end_col == 6  # start_col + length - 1

    def test_end_col_down(self):
        """Test end_col for DOWN word."""
        word = Word("HELLO", 3, 2, Direction.DOWN)
        assert word.end_col == 2  # Same as start_col


class TestGetCells:
    """Tests for get_cells method."""

    def test_get_cells_across(self):
        """Test getting cells for ACROSS word."""
        word = Word("HELLO", 2, 1, Direction.ACROSS)
        cells = word.get_cells()

        expected = [(2, 1), (2, 2), (2, 3), (2, 4), (2, 5)]
        assert cells == expected

    def test_get_cells_down(self):
        """Test getting cells for DOWN word."""
        word = Word("WORLD", 1, 3, Direction.DOWN)
        cells = word.get_cells()

        expected = [(1, 3), (2, 3), (3, 3), (4, 3), (5, 3)]
        assert cells == expected

    def test_get_cells_single_letter(self):
        """Test getting cells for single-letter word."""
        word = Word("I", 0, 0, Direction.ACROSS)
        cells = word.get_cells()

        assert cells == [(0, 0)]

    def test_get_cells_order(self):
        """Test cells are returned in order from start to end."""
        word = Word("ABC", 0, 0, Direction.ACROSS)
        cells = word.get_cells()

        # Cells should be in order
        assert cells[0] == (0, 0)
        assert cells[1] == (0, 1)
        assert cells[2] == (0, 2)


class TestGetPattern:
    """Tests for get_pattern method."""

    def test_get_pattern_empty_grid(self):
        """Test getting pattern from empty grid."""
        grid = CrosswordGrid()
        word = Word("HELLO", 2, 1, Direction.ACROSS)
        pattern = word.get_pattern(grid)

        assert pattern == "_____"

    def test_get_pattern_partial_fill(self):
        """Test getting pattern with partial fill."""
        grid = CrosswordGrid()
        word = Word("HELLO", 2, 1, Direction.ACROSS)

        # Fill some cells
        grid.set_cell(2, 1, "H")
        grid.set_cell(2, 5, "O")

        pattern = word.get_pattern(grid)
        assert pattern == "H___O"

    def test_get_pattern_complete_fill(self):
        """Test getting pattern with complete fill."""
        grid = CrosswordGrid()
        placement = WordPlacement(
            word="HELLO",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="Greeting",
            number=1,
        )
        grid.place_word(placement)

        word = grid.words[0]
        pattern = word.get_pattern(grid)
        assert pattern == "HELLO"

    def test_get_pattern_vertical_word(self):
        """Test getting pattern for vertical word."""
        grid = CrosswordGrid()
        word = Word("WORLD", 1, 3, Direction.DOWN)

        # Fill some cells
        grid.set_cell(1, 3, "W")
        grid.set_cell(3, 3, "R")
        grid.set_cell(5, 3, "D")

        pattern = word.get_pattern(grid)
        assert pattern == "W_R_D"


class TestIsComplete:
    """Tests for is_complete method."""

    def test_is_complete_empty_grid(self):
        """Test word is not complete on empty grid."""
        grid = CrosswordGrid()
        word = Word("HELLO", 2, 1, Direction.ACROSS)

        assert not word.is_complete(grid)

    def test_is_complete_partial_fill(self):
        """Test word is not complete with partial fill."""
        grid = CrosswordGrid()
        word = Word("HELLO", 2, 1, Direction.ACROSS)

        # Fill some but not all cells
        grid.set_cell(2, 1, "H")
        grid.set_cell(2, 2, "E")

        assert not word.is_complete(grid)

    def test_is_complete_full_fill(self):
        """Test word is complete when all cells filled."""
        grid = CrosswordGrid()
        placement = WordPlacement(
            word="HELLO",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="Greeting",
            number=1,
        )
        grid.place_word(placement)

        word = grid.words[0]
        assert word.is_complete(grid)

    def test_is_complete_single_letter(self):
        """Test single-letter word completion."""
        grid = CrosswordGrid()
        word = Word("I", 0, 0, Direction.ACROSS)

        assert not word.is_complete(grid)

        grid.set_cell(0, 0, "I")
        assert word.is_complete(grid)


class TestIntersectsWith:
    """Tests for intersects_with method."""

    def test_intersects_with_perpendicular_words(self):
        """Test intersection of perpendicular words."""
        word1 = Word("HELLO", 2, 1, Direction.ACROSS)
        word2 = Word("WORLD", 0, 3, Direction.DOWN)

        intersection = word1.intersects_with(word2)
        assert intersection == (2, 3)  # They intersect at 'L'

    def test_intersects_with_no_intersection(self):
        """Test words that don't intersect."""
        word1 = Word("HELLO", 2, 1, Direction.ACROSS)
        word2 = Word("WORLD", 5, 5, Direction.DOWN)

        intersection = word1.intersects_with(word2)
        assert intersection is None

    def test_intersects_with_same_direction(self):
        """Test words with same direction don't intersect."""
        word1 = Word("HELLO", 2, 1, Direction.ACROSS)
        word2 = Word("WORLD", 2, 1, Direction.ACROSS)

        intersection = word1.intersects_with(word2)
        assert intersection is None

    def test_intersects_with_parallel_words(self):
        """Test parallel words don't intersect."""
        word1 = Word("HELLO", 2, 1, Direction.ACROSS)
        word2 = Word("WORLD", 4, 1, Direction.ACROSS)

        intersection = word1.intersects_with(word2)
        assert intersection is None

    def test_intersects_with_touching_but_not_crossing(self):
        """Test words that touch but don't cross."""
        word1 = Word("HELLO", 2, 1, Direction.ACROSS)
        word2 = Word("WORLD", 3, 3, Direction.DOWN)  # Starts below word1

        intersection = word1.intersects_with(word2)
        assert intersection is None

    def test_intersects_with_multiple_overlaps(self):
        """Test words with multiple overlapping cells don't count as intersection."""
        # This shouldn't happen in valid crosswords, but test the logic
        word1 = Word("HELLO", 2, 1, Direction.ACROSS)
        word2 = Word("HELLO", 2, 1, Direction.ACROSS)

        intersection = word1.intersects_with(word2)
        assert intersection is None  # Same direction


class TestGetLetterAtPosition:
    """Tests for get_letter_at_position method."""

    def test_get_letter_at_position_valid(self):
        """Test getting letter at valid position."""
        word = Word("HELLO", 2, 1, Direction.ACROSS)

        assert word.get_letter_at_position(2, 1) == "H"
        assert word.get_letter_at_position(2, 2) == "E"
        assert word.get_letter_at_position(2, 3) == "L"
        assert word.get_letter_at_position(2, 4) == "L"
        assert word.get_letter_at_position(2, 5) == "O"

    def test_get_letter_at_position_invalid(self):
        """Test getting letter at position not occupied by word."""
        word = Word("HELLO", 2, 1, Direction.ACROSS)

        assert word.get_letter_at_position(2, 0) is None
        assert word.get_letter_at_position(2, 6) is None
        assert word.get_letter_at_position(3, 3) is None

    def test_get_letter_at_position_vertical(self):
        """Test getting letter for vertical word."""
        word = Word("WORLD", 1, 3, Direction.DOWN)

        assert word.get_letter_at_position(1, 3) == "W"
        assert word.get_letter_at_position(2, 3) == "O"
        assert word.get_letter_at_position(3, 3) == "R"
        assert word.get_letter_at_position(4, 3) == "L"
        assert word.get_letter_at_position(5, 3) == "D"


class TestToPlacement:
    """Tests for to_placement method."""

    def test_to_placement_basic(self):
        """Test converting word to placement."""
        word = Word(
            text="HELLO",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="Greeting",
            number=5,
        )

        placement = word.to_placement()

        assert placement.word == "HELLO"
        assert placement.start_row == 2
        assert placement.start_col == 1
        assert placement.direction == Direction.ACROSS
        assert placement.clue == "Greeting"
        assert placement.number == 5

    def test_to_placement_without_clue(self):
        """Test converting word without clue to placement."""
        word = Word("HELLO", 0, 0, Direction.ACROSS, number=1)
        placement = word.to_placement()

        assert placement.word == "HELLO"
        assert placement.clue == ""
        assert placement.number == 1


class TestWordEquality:
    """Tests for word equality and hashing."""

    def test_word_equality_same_words(self):
        """Test two identical words are equal."""
        word1 = Word("HELLO", 2, 1, Direction.ACROSS)
        word2 = Word("HELLO", 2, 1, Direction.ACROSS)

        assert word1 == word2

    def test_word_equality_different_text(self):
        """Test words with different text are not equal."""
        word1 = Word("HELLO", 2, 1, Direction.ACROSS)
        word2 = Word("WORLD", 2, 1, Direction.ACROSS)

        assert word1 != word2

    def test_word_equality_different_position(self):
        """Test words at different positions are not equal."""
        word1 = Word("HELLO", 2, 1, Direction.ACROSS)
        word2 = Word("HELLO", 3, 1, Direction.ACROSS)

        assert word1 != word2

    def test_word_equality_different_direction(self):
        """Test words with different directions are not equal."""
        word1 = Word("HELLO", 2, 1, Direction.ACROSS)
        word2 = Word("HELLO", 2, 1, Direction.DOWN)

        assert word1 != word2

    def test_word_equality_ignores_clue(self):
        """Test equality ignores clue and number."""
        word1 = Word("HELLO", 2, 1, Direction.ACROSS, clue="Hi", number=1)
        word2 = Word("HELLO", 2, 1, Direction.ACROSS, clue="Greeting", number=2)

        assert word1 == word2

    def test_word_hash(self):
        """Test word can be hashed for use in sets/dicts."""
        word1 = Word("HELLO", 2, 1, Direction.ACROSS)
        word2 = Word("HELLO", 2, 1, Direction.ACROSS)
        word3 = Word("WORLD", 2, 1, Direction.ACROSS)

        word_set = {word1, word2, word3}
        assert len(word_set) == 2  # word1 and word2 are same

    def test_word_equality_with_non_word(self):
        """Test word equality with non-Word object."""
        word = Word("HELLO", 2, 1, Direction.ACROSS)

        assert word != "HELLO"
        assert word != 123
        assert word is not None


class TestWordRepresentation:
    """Tests for word string representation."""

    def test_word_repr(self):
        """Test word string representation."""
        word = Word("HELLO", 2, 1, Direction.ACROSS, number=5)
        repr_str = repr(word)

        assert "HELLO" in repr_str
        assert "2" in repr_str
        assert "1" in repr_str
        assert "across" in repr_str
        assert "5" in repr_str


class TestWordIntegration:
    """Integration tests for Word with CrosswordGrid."""

    def test_word_on_grid_pattern_matching(self):
        """Test word pattern matching on actual grid."""
        grid = CrosswordGrid()

        # Place first word
        placement1 = WordPlacement(
            word="HELLO",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="Greeting",
            number=1,
        )
        grid.place_word(placement1)

        # Create second word that will intersect
        word2 = Word("WORLD", 0, 3, Direction.DOWN)

        # Check pattern before placing
        pattern = word2.get_pattern(grid)
        assert pattern == "__L__"  # 'L' from HELLO at position (2, 3)

    def test_word_intersection_on_grid(self):
        """Test word intersection detection on actual grid."""
        grid = CrosswordGrid()

        # Place two intersecting words
        placement1 = WordPlacement(
            word="HELLO",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="Greeting",
            number=1,
        )
        grid.place_word(placement1)

        placement2 = WordPlacement(
            word="ABLE",
            start_row=0,
            start_col=3,
            direction=Direction.DOWN,
            clue="Capable",
            number=2,
        )
        grid.place_word(placement2)

        # Check intersection
        word1 = grid.words[0]
        word2 = grid.words[1]

        intersection = word1.intersects_with(word2)
        assert intersection == (2, 3)

        # Verify letters match at intersection
        assert word1.get_letter_at_position(2, 3) == "L"
        assert word2.get_letter_at_position(2, 3) == "L"
