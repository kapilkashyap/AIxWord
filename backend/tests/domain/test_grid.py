"""
Tests for CrosswordGrid engine.

This module contains comprehensive tests for the grid engine including:
- Grid initialization and basic operations
- Word placement and removal
- Collision detection
- Intersection detection
- Fill rate calculation
- Grid serialization/deserialization
- Grid cloning
- Number assignment
"""

import pytest

from backend.domain import CrosswordGrid, Direction, Word, WordPlacement


class TestGridInitialization:
    """Tests for grid initialization."""

    def test_default_grid_size(self):
        """Test grid initializes with default 8x8 size."""
        grid = CrosswordGrid()
        assert grid.size == 8
        assert len(grid.cells) == 8
        assert all(len(row) == 8 for row in grid.cells)

    def test_custom_grid_size(self):
        """Test grid initializes with custom size."""
        grid = CrosswordGrid(size=10)
        assert grid.size == 10
        assert len(grid.cells) == 10
        assert all(len(row) == 10 for row in grid.cells)

    def test_minimum_grid_size(self):
        """Test grid accepts minimum size of 3."""
        grid = CrosswordGrid(size=3)
        assert grid.size == 3

    def test_grid_size_too_small(self):
        """Test grid rejects size less than 3."""
        with pytest.raises(ValueError, match="at least 3"):
            CrosswordGrid(size=2)

    def test_grid_size_too_large(self):
        """Test grid rejects size greater than 50."""
        with pytest.raises(ValueError, match="at most 50"):
            CrosswordGrid(size=51)

    def test_empty_grid_initialization(self):
        """Test all cells are empty on initialization."""
        grid = CrosswordGrid()
        for row in range(grid.size):
            for col in range(grid.size):
                cell = grid.get_cell(row, col)
                assert cell.value is None
                assert not cell.is_blocked
                assert cell.number is None

    def test_cell_positions(self):
        """Test cells have correct row and column positions."""
        grid = CrosswordGrid(size=5)
        for row in range(5):
            for col in range(5):
                cell = grid.get_cell(row, col)
                assert cell.row == row
                assert cell.col == col

    def test_empty_words_list(self):
        """Test words list is empty on initialization."""
        grid = CrosswordGrid()
        assert grid.words == []


class TestCellAccess:
    """Tests for cell access and manipulation."""

    def test_get_cell_valid_position(self):
        """Test getting cell at valid position."""
        grid = CrosswordGrid()
        cell = grid.get_cell(3, 4)
        assert cell.row == 3
        assert cell.col == 4

    def test_get_cell_out_of_bounds(self):
        """Test getting cell at invalid position raises IndexError."""
        grid = CrosswordGrid(size=8)
        with pytest.raises(IndexError):
            grid.get_cell(8, 0)
        with pytest.raises(IndexError):
            grid.get_cell(0, 8)
        with pytest.raises(IndexError):
            grid.get_cell(-1, 0)

    def test_set_cell_value(self):
        """Test setting cell value."""
        grid = CrosswordGrid()
        grid.set_cell(2, 3, "A")
        cell = grid.get_cell(2, 3)
        assert cell.value == "A"

    def test_set_cell_normalizes_to_uppercase(self):
        """Test cell value is normalized to uppercase."""
        grid = CrosswordGrid()
        grid.set_cell(0, 0, "a")
        assert grid.get_cell(0, 0).value == "A"

    def test_set_cell_clear_value(self):
        """Test clearing cell value with None."""
        grid = CrosswordGrid()
        grid.set_cell(1, 1, "B")
        grid.set_cell(1, 1, None)
        assert grid.get_cell(1, 1).value is None

    def test_set_cell_invalid_value(self):
        """Test setting invalid cell value raises ValueError."""
        grid = CrosswordGrid()
        with pytest.raises(ValueError):
            grid.set_cell(0, 0, "AB")  # Too long
        with pytest.raises(ValueError):
            grid.set_cell(0, 0, "1")  # Not a letter
        with pytest.raises(ValueError):
            grid.set_cell(0, 0, "")  # Empty string

    def test_is_valid_position(self):
        """Test position validation."""
        grid = CrosswordGrid(size=8)
        assert grid.is_valid_position(0, 0)
        assert grid.is_valid_position(7, 7)
        assert grid.is_valid_position(3, 4)
        assert not grid.is_valid_position(-1, 0)
        assert not grid.is_valid_position(0, -1)
        assert not grid.is_valid_position(8, 0)
        assert not grid.is_valid_position(0, 8)


class TestWordPlacement:
    """Tests for word placement on grid."""

    def test_place_word_horizontal(self):
        """Test placing a horizontal word."""
        grid = CrosswordGrid()
        placement = WordPlacement(
            word="HELLO",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="A greeting",
            number=1,
        )
        result = grid.place_word(placement)
        assert result is True
        assert len(grid.words) == 1

        # Check cells are filled
        assert grid.get_cell(2, 1).value == "H"
        assert grid.get_cell(2, 2).value == "E"
        assert grid.get_cell(2, 3).value == "L"
        assert grid.get_cell(2, 4).value == "L"
        assert grid.get_cell(2, 5).value == "O"

    def test_place_word_vertical(self):
        """Test placing a vertical word."""
        grid = CrosswordGrid()
        placement = WordPlacement(
            word="WORLD",
            start_row=1,
            start_col=3,
            direction=Direction.DOWN,
            clue="The Earth",
            number=1,
        )
        result = grid.place_word(placement)
        assert result is True
        assert len(grid.words) == 1

        # Check cells are filled
        assert grid.get_cell(1, 3).value == "W"
        assert grid.get_cell(2, 3).value == "O"
        assert grid.get_cell(3, 3).value == "R"
        assert grid.get_cell(4, 3).value == "L"
        assert grid.get_cell(5, 3).value == "D"

    def test_place_word_out_of_bounds(self):
        """Test placing word that goes out of bounds fails."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="TOOLONG",
            start_row=0,
            start_col=5,  # Would end at column 11
            direction=Direction.ACROSS,
            clue="Too long",
            number=1,
        )
        result = grid.place_word(placement)
        assert result is False
        assert len(grid.words) == 0

    def test_place_word_at_boundary(self):
        """Test placing word at grid boundary."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="FITS",
            start_row=0,
            start_col=4,  # Ends at column 7 (last column)
            direction=Direction.ACROSS,
            clue="Just fits",
            number=1,
        )
        result = grid.place_word(placement)
        assert result is True

    def test_place_intersecting_words(self):
        """Test placing two words that intersect."""
        grid = CrosswordGrid()

        # Place first word: HELLO (horizontal)
        placement1 = WordPlacement(
            word="HELLO",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="Greeting",
            number=1,
        )
        grid.place_word(placement1)

        # Place second word: EARLY (vertical, intersecting at 'L')
        # EARLY: E(0,3), A(1,3), R(2,3), L(3,3), Y(4,3)
        # HELLO: H(2,1), E(2,2), L(2,3), L(2,4), O(2,5)
        # They don't intersect! Let's use a word that shares 'L' at position (2,3)
        # We need a word with 'L' at index 2: like "ABLE" -> A(0,3), B(1,3), L(2,3), E(3,3)
        placement2 = WordPlacement(
            word="ABLE",
            start_row=0,
            start_col=3,
            direction=Direction.DOWN,
            clue="Capable",
            number=2,
        )
        result = grid.place_word(placement2)
        assert result is True
        assert len(grid.words) == 2

        # Check intersection cell
        assert grid.get_cell(2, 3).value == "L"

    def test_place_word_conflicting_letter(self):
        """Test placing word with conflicting letter fails."""
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

        # Try to place word with conflicting letter at intersection
        placement2 = WordPlacement(
            word="WRONG",
            start_row=0,
            start_col=3,
            direction=Direction.DOWN,
            clue="Incorrect",
            number=2,
        )
        result = grid.place_word(placement2)
        assert result is False  # 'O' conflicts with 'L'
        assert len(grid.words) == 1


class TestWordRemoval:
    """Tests for word removal from grid."""

    def test_remove_word(self):
        """Test removing a word from grid."""
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
        grid.remove_word(word)

        assert len(grid.words) == 0
        # Check cells are cleared
        for col in range(1, 6):
            assert grid.get_cell(2, col).value is None

    def test_remove_word_preserves_intersections(self):
        """Test removing word preserves shared cells."""
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

        # Remove first word
        word1 = grid.words[0]
        grid.remove_word(word1)

        # Intersection cell should still have value from second word
        assert grid.get_cell(2, 3).value == "L"
        # Other cells from first word should be cleared
        assert grid.get_cell(2, 1).value is None
        assert grid.get_cell(2, 2).value is None

    def test_remove_nonexistent_word(self):
        """Test removing word not in grid does nothing."""
        grid = CrosswordGrid()
        word = Word("HELLO", 0, 0, Direction.ACROSS)
        grid.remove_word(word)  # Should not raise error
        assert len(grid.words) == 0


class TestWordRetrieval:
    """Tests for finding words on grid."""

    def test_get_word_at_position(self):
        """Test finding word at specific position."""
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

        word = grid.get_word_at(2, 3, Direction.ACROSS)
        assert word is not None
        assert word.text == "HELLO"

    def test_get_word_at_wrong_direction(self):
        """Test finding word with wrong direction returns None."""
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

        word = grid.get_word_at(2, 3, Direction.DOWN)
        assert word is None

    def test_get_word_at_empty_position(self):
        """Test finding word at empty position returns None."""
        grid = CrosswordGrid()
        word = grid.get_word_at(2, 3, Direction.ACROSS)
        assert word is None

    def test_get_intersecting_words(self):
        """Test finding intersecting words."""
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

        word1 = grid.words[0]
        intersecting = grid.get_intersecting_words(word1)

        assert len(intersecting) == 1
        assert intersecting[0].text == "ABLE"


class TestFillRate:
    """Tests for fill rate calculation."""

    def test_empty_grid_fill_rate(self):
        """Test fill rate of empty grid is 0."""
        grid = CrosswordGrid()
        assert grid.get_fill_rate() == 0.0

    def test_partial_fill_rate(self):
        """Test fill rate calculation with partial grid."""
        grid = CrosswordGrid(size=4)
        placement = WordPlacement(
            word="HI",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Greeting",
            number=1,
        )
        grid.place_word(placement)

        # 2 cells filled out of 16 total
        assert grid.get_fill_rate() == 2 / 16

    def test_full_grid_fill_rate(self):
        """Test fill rate of completely filled grid."""
        grid = CrosswordGrid(size=3)

        # Fill all cells
        for row in range(3):
            for col in range(3):
                grid.set_cell(row, col, "A")

        assert grid.get_fill_rate() == 1.0

    def test_fill_rate_ignores_blocked_cells(self):
        """Test fill rate calculation ignores blocked cells."""
        grid = CrosswordGrid(size=4)

        # Block some cells
        grid.cells[0][0].is_blocked = True
        grid.cells[0][1].is_blocked = True

        # Fill some non-blocked cells
        grid.set_cell(1, 0, "A")
        grid.set_cell(1, 1, "B")

        # 2 filled out of 14 non-blocked cells
        assert grid.get_fill_rate() == 2 / 14


class TestNumberAssignment:
    """Tests for clue number assignment."""

    def test_assign_numbers_single_word(self):
        """Test number assignment for single word."""
        grid = CrosswordGrid()
        placement = WordPlacement(
            word="HELLO",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="Greeting",
            number=99,  # Will be reassigned
        )
        grid.place_word(placement)
        grid.assign_numbers()

        assert grid.get_cell(2, 1).number == 1
        assert grid.words[0].number == 1

    def test_assign_numbers_multiple_words(self):
        """Test number assignment in reading order."""
        grid = CrosswordGrid()

        # Place words in non-reading order
        placement1 = WordPlacement(
            word="WORLD",
            start_row=3,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Earth",
            number=99,
        )
        grid.place_word(placement1)

        placement2 = WordPlacement(
            word="HELLO",
            start_row=1,
            start_col=2,
            direction=Direction.ACROSS,
            clue="Greeting",
            number=88,
        )
        grid.place_word(placement2)

        grid.assign_numbers()

        # Numbers should be assigned in reading order
        assert grid.get_cell(1, 2).number == 1  # HELLO (row 1)
        assert grid.get_cell(3, 0).number == 2  # WORLD (row 3)

    def test_assign_numbers_same_position(self):
        """Test words starting at same position share number."""
        grid = CrosswordGrid()

        # Place two words starting at same position
        placement1 = WordPlacement(
            word="HELLO",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="Greeting",
            number=99,
        )
        grid.place_word(placement1)

        placement2 = WordPlacement(
            word="HELP",
            start_row=2,
            start_col=1,
            direction=Direction.DOWN,
            clue="Assist",
            number=88,
        )
        grid.place_word(placement2)

        grid.assign_numbers()

        # Both words should have same number
        assert grid.words[0].number == 1
        assert grid.words[1].number == 1


class TestGridSerialization:
    """Tests for grid serialization and deserialization."""

    def test_to_dict_empty_grid(self):
        """Test serializing empty grid."""
        grid = CrosswordGrid(size=4)
        data = grid.to_dict()

        assert data["size"] == 4
        assert len(data["cells"]) == 4
        assert len(data["words"]) == 0

    def test_to_dict_with_words(self):
        """Test serializing grid with words."""
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

        data = grid.to_dict()

        assert data["size"] == 8
        assert len(data["words"]) == 1
        assert data["words"][0]["text"] == "HELLO"
        assert data["words"][0]["direction"] == "across"

    def test_from_dict_empty_grid(self):
        """Test deserializing empty grid."""
        original = CrosswordGrid(size=5)
        data = original.to_dict()
        restored = CrosswordGrid.from_dict(data)

        assert restored.size == 5
        assert len(restored.words) == 0

    def test_from_dict_with_words(self):
        """Test deserializing grid with words."""
        original = CrosswordGrid()
        placement = WordPlacement(
            word="HELLO",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="Greeting",
            number=1,
        )
        original.place_word(placement)

        data = original.to_dict()
        restored = CrosswordGrid.from_dict(data)

        assert restored.size == original.size
        assert len(restored.words) == 1
        assert restored.words[0].text == "HELLO"
        assert restored.get_cell(2, 1).value == "H"

    def test_serialization_roundtrip(self):
        """Test complete serialization roundtrip."""
        original = CrosswordGrid()

        # Place multiple words
        placement1 = WordPlacement(
            word="HELLO",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="Greeting",
            number=1,
        )
        original.place_word(placement1)

        placement2 = WordPlacement(
            word="WORLD",
            start_row=0,
            start_col=3,
            direction=Direction.DOWN,
            clue="Earth",
            number=2,
        )
        original.place_word(placement2)

        # Serialize and deserialize
        data = original.to_dict()
        restored = CrosswordGrid.from_dict(data)

        # Verify state is preserved
        assert restored.size == original.size
        assert len(restored.words) == len(original.words)
        assert restored.get_fill_rate() == original.get_fill_rate()


class TestGridCloning:
    """Tests for grid cloning."""

    def test_clone_empty_grid(self):
        """Test cloning empty grid."""
        original = CrosswordGrid(size=6)
        clone = original.clone()

        assert clone.size == original.size
        assert clone is not original
        assert clone.cells is not original.cells

    def test_clone_with_words(self):
        """Test cloning grid with words."""
        original = CrosswordGrid()
        placement = WordPlacement(
            word="HELLO",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="Greeting",
            number=1,
        )
        original.place_word(placement)

        clone = original.clone()

        assert len(clone.words) == 1
        assert clone.words[0].text == "HELLO"
        assert clone.get_cell(2, 1).value == "H"

    def test_clone_independence(self):
        """Test cloned grid is independent of original."""
        original = CrosswordGrid()
        placement = WordPlacement(
            word="HELLO",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="Greeting",
            number=1,
        )
        original.place_word(placement)

        clone = original.clone()

        # Modify clone
        clone.set_cell(0, 0, "X")

        # Original should be unchanged
        assert original.get_cell(0, 0).value is None
        assert clone.get_cell(0, 0).value == "X"


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_single_letter_word(self):
        """Test placing single-letter word."""
        grid = CrosswordGrid()
        placement = WordPlacement(
            word="I",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="First person pronoun",
            number=1,
        )
        result = grid.place_word(placement)
        assert result is True
        assert grid.get_cell(0, 0).value == "I"

    def test_full_row_word(self):
        """Test placing word that fills entire row."""
        grid = CrosswordGrid(size=5)
        placement = WordPlacement(
            word="ABCDE",
            start_row=2,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Full row",
            number=1,
        )
        result = grid.place_word(placement)
        assert result is True
        for col in range(5):
            assert grid.get_cell(2, col).value is not None

    def test_multiple_words_same_direction(self):
        """Test placing multiple words in same direction."""
        grid = CrosswordGrid()

        placement1 = WordPlacement(
            word="HELLO",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Greeting",
            number=1,
        )
        grid.place_word(placement1)

        placement2 = WordPlacement(
            word="WORLD",
            start_row=2,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Earth",
            number=2,
        )
        grid.place_word(placement2)

        assert len(grid.words) == 2
