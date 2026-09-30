"""
Tests for word validation engine.

This module contains comprehensive tests for the WordValidator class, including:
- Validation result handling
- Bounds checking
- Conflict detection
- Intersection validation
- Format validation
- Pattern extraction
- Edge cases and error handling
"""


from backend.domain import CrosswordGrid, Direction, WordPlacement
from backend.domain.pattern import Pattern
from backend.domain.validator import ValidationResult, WordValidator


class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_valid_result_initialization(self):
        """Test creating a valid result."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_invalid_result_initialization(self):
        """Test creating an invalid result."""
        result = ValidationResult(is_valid=False, errors=["Error 1"])
        assert result.is_valid is False
        assert result.errors == ["Error 1"]

    def test_add_error(self):
        """Test adding error to result."""
        result = ValidationResult(is_valid=True)
        result.add_error("Test error")

        assert result.is_valid is False
        assert "Test error" in result.errors

    def test_add_warning(self):
        """Test adding warning to result."""
        result = ValidationResult(is_valid=True)
        result.add_warning("Test warning")

        assert result.is_valid is True  # Warnings don't invalidate
        assert "Test warning" in result.warnings

    def test_multiple_errors(self):
        """Test adding multiple errors."""
        result = ValidationResult(is_valid=True)
        result.add_error("Error 1")
        result.add_error("Error 2")

        assert result.is_valid is False
        assert len(result.errors) == 2

    def test_string_representation_valid(self):
        """Test string representation of valid result."""
        result = ValidationResult(is_valid=True)
        assert "VALID" in str(result)

    def test_string_representation_invalid(self):
        """Test string representation of invalid result."""
        result = ValidationResult(is_valid=False, errors=["Error 1"])
        assert "INVALID" in str(result)
        assert "Error 1" in str(result)


class TestBoundsChecking:
    """Tests for bounds checking validation."""

    def test_word_within_bounds_across(self):
        """Test ACROSS word within bounds."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )

        assert WordValidator.check_bounds(grid, placement) is True

    def test_word_within_bounds_down(self):
        """Test DOWN word within bounds."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=0,
            direction=Direction.DOWN,
            clue="A fruit",
            number=1
        )

        assert WordValidator.check_bounds(grid, placement) is True

    def test_word_at_edge_across(self):
        """Test ACROSS word at right edge."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=3,  # Ends at column 7 (last column)
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )

        assert WordValidator.check_bounds(grid, placement) is True

    def test_word_at_edge_down(self):
        """Test DOWN word at bottom edge."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="APPLE",
            start_row=3,  # Ends at row 7 (last row)
            start_col=0,
            direction=Direction.DOWN,
            clue="A fruit",
            number=1
        )

        assert WordValidator.check_bounds(grid, placement) is True

    def test_word_exceeds_bounds_across(self):
        """Test ACROSS word exceeds right boundary."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=4,  # Would end at column 8 (out of bounds)
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )

        assert WordValidator.check_bounds(grid, placement) is False

    def test_word_exceeds_bounds_down(self):
        """Test DOWN word exceeds bottom boundary."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="APPLE",
            start_row=4,  # Would end at row 8 (out of bounds)
            start_col=0,
            direction=Direction.DOWN,
            clue="A fruit",
            number=1
        )

        assert WordValidator.check_bounds(grid, placement) is False

    def test_word_starts_out_of_bounds(self):
        """Test word starting position out of bounds."""
        grid = CrosswordGrid(size=8)
        # WordPlacement validates start_row >= 0, so we test with grid.is_valid_position
        assert grid.is_valid_position(-1, 0) is False
        assert grid.is_valid_position(0, -1) is False
        assert grid.is_valid_position(8, 0) is False
        assert grid.is_valid_position(0, 8) is False


class TestConflictDetection:
    """Tests for conflict detection."""

    def test_no_conflicts_empty_grid(self):
        """Test no conflicts on empty grid."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )

        conflicts = WordValidator.check_conflicts(grid, placement)
        assert conflicts == []

    def test_no_conflicts_matching_letters(self):
        """Test no conflicts when letters match."""
        grid = CrosswordGrid(size=8)

        # Place first word
        first = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )
        grid.place_word(first)

        # Try to place intersecting word with matching letter
        second = WordPlacement(
            word="APRIL",
            start_row=0,
            start_col=0,
            direction=Direction.DOWN,
            clue="A month",
            number=1
        )

        conflicts = WordValidator.check_conflicts(grid, second)
        assert conflicts == []

    def test_conflict_different_letter(self):
        """Test conflict when letters don't match."""
        grid = CrosswordGrid(size=8)

        # Place first word
        first = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )
        grid.place_word(first)

        # Try to place word with conflicting letter
        second = WordPlacement(
            word="BREAD",
            start_row=0,
            start_col=0,
            direction=Direction.DOWN,
            clue="Food",
            number=1
        )

        conflicts = WordValidator.check_conflicts(grid, second)
        assert len(conflicts) > 0
        assert "has 'A' but word requires 'B'" in conflicts[0]

    def test_conflict_blocked_cell(self):
        """Test conflict with blocked cell."""
        grid = CrosswordGrid(size=8)

        # Block a cell
        grid.cells[0][0].is_blocked = True

        # Try to place word over blocked cell
        placement = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )

        conflicts = WordValidator.check_conflicts(grid, placement)
        assert len(conflicts) > 0
        assert "blocked" in conflicts[0].lower()


class TestIntersectionValidation:
    """Tests for intersection validation."""

    def test_valid_intersection(self):
        """Test valid intersection with matching letters."""
        grid = CrosswordGrid(size=8)

        # Place first word: APPLE across at (2,1)
        # A at (2,1), P at (2,2), P at (2,3), L at (2,4), E at (2,5)
        first = WordPlacement(
            word="APPLE",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )
        grid.place_word(first)

        # Place second word: PAPER down at (0,2) - intersects at 'P'
        # P at (0,2), A at (1,2), P at (2,2), E at (3,2), R at (4,2)
        second = WordPlacement(
            word="PAPER",
            start_row=0,
            start_col=2,
            direction=Direction.DOWN,
            clue="Writing material",
            number=2
        )

        result = WordValidator.check_intersections(grid, second)
        assert result.is_valid is True

    def test_invalid_intersection_conflicting_letters(self):
        """Test invalid intersection with conflicting letters."""
        grid = CrosswordGrid(size=8)

        # Place first word: APPLE across
        first = WordPlacement(
            word="APPLE",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )
        grid.place_word(first)

        # Try to place word with conflicting intersection
        second = WordPlacement(
            word="BREAD",
            start_row=0,
            start_col=2,
            direction=Direction.DOWN,
            clue="Food",
            number=2
        )

        result = WordValidator.check_intersections(grid, second)
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_parallel_words_overlap(self):
        """Test parallel words overlapping is invalid."""
        grid = CrosswordGrid(size=8)

        # Place first word: APPLE across
        first = WordPlacement(
            word="APPLE",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )
        grid.place_word(first)

        # Try to place overlapping parallel word
        second = WordPlacement(
            word="BREAD",
            start_row=2,
            start_col=3,
            direction=Direction.ACROSS,
            clue="Food",
            number=2
        )

        result = WordValidator.check_intersections(grid, second)
        assert result.is_valid is False

    def test_multiple_intersections_invalid(self):
        """Test multiple intersection points is invalid."""
        grid = CrosswordGrid(size=8)

        # Place first word: ABCD across at (2,1)
        # A at (2,1), B at (2,2), C at (2,3), D at (2,4)
        first = WordPlacement(
            word="ABCD",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="Test",
            number=1
        )
        grid.place_word(first)

        # Try to place overlapping parallel word (same direction, overlapping cells)
        # This would share cells (2,2) and (2,3)
        second = WordPlacement(
            word="BCDE",
            start_row=2,
            start_col=2,
            direction=Direction.ACROSS,
            clue="Test",
            number=2
        )

        result = WordValidator.check_intersections(grid, second)
        # This should be invalid due to parallel overlap
        assert result.is_valid is False


class TestFormatValidation:
    """Tests for word and clue format validation."""

    def test_valid_word_format(self):
        """Test valid word format."""
        assert WordValidator.validate_word_format("APPLE") is True
        assert WordValidator.validate_word_format("apple") is True
        assert WordValidator.validate_word_format("ApPlE") is True

    def test_invalid_word_empty(self):
        """Test empty word is invalid."""
        assert WordValidator.validate_word_format("") is False

    def test_invalid_word_too_short(self):
        """Test single letter word is invalid."""
        assert WordValidator.validate_word_format("A") is False

    def test_invalid_word_with_numbers(self):
        """Test word with numbers is invalid."""
        assert WordValidator.validate_word_format("APPLE1") is False
        assert WordValidator.validate_word_format("1APPLE") is False

    def test_invalid_word_with_spaces(self):
        """Test word with spaces is invalid."""
        assert WordValidator.validate_word_format("AP PLE") is False

    def test_invalid_word_with_special_chars(self):
        """Test word with special characters is invalid."""
        assert WordValidator.validate_word_format("APPLE-PIE") is False
        assert WordValidator.validate_word_format("APPLE'S") is False

    def test_invalid_word_non_string(self):
        """Test non-string word is invalid."""
        assert WordValidator.validate_word_format(123) is False  # type: ignore
        assert WordValidator.validate_word_format(None) is False  # type: ignore

    def test_valid_clue_format(self):
        """Test valid clue format."""
        assert WordValidator.validate_clue("A fruit") is True
        assert WordValidator.validate_clue("Red fruit that grows on trees") is True

    def test_invalid_clue_empty(self):
        """Test empty clue is invalid."""
        assert WordValidator.validate_clue("") is False

    def test_invalid_clue_too_long(self):
        """Test very long clue is invalid."""
        long_clue = "A" * 501
        assert WordValidator.validate_clue(long_clue) is False

    def test_invalid_clue_non_string(self):
        """Test non-string clue is invalid."""
        assert WordValidator.validate_clue(123) is False  # type: ignore
        assert WordValidator.validate_clue(None) is False  # type: ignore


class TestPatternExtraction:
    """Tests for pattern extraction from grid."""

    def test_extract_pattern_empty_grid(self):
        """Test extracting pattern from empty grid."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )

        pattern = WordValidator.get_required_pattern(grid, placement)
        assert pattern.pattern == "_____"

    def test_extract_pattern_partially_filled(self):
        """Test extracting pattern from partially filled grid."""
        grid = CrosswordGrid(size=8)

        # Fill some cells
        grid.set_cell(0, 0, 'A')
        grid.set_cell(0, 3, 'L')
        grid.set_cell(0, 4, 'E')

        placement = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )

        pattern = WordValidator.get_required_pattern(grid, placement)
        assert pattern.pattern == "A__LE"

    def test_extract_pattern_fully_filled(self):
        """Test extracting pattern from fully filled grid."""
        grid = CrosswordGrid(size=8)

        # Place a word
        first = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )
        grid.place_word(first)

        pattern = WordValidator.get_required_pattern(grid, first)
        assert pattern.pattern == "APPLE"

    def test_extract_pattern_down_direction(self):
        """Test extracting pattern for DOWN word."""
        grid = CrosswordGrid(size=8)

        # Fill some cells vertically
        grid.set_cell(0, 0, 'A')
        grid.set_cell(2, 0, 'R')

        placement = WordPlacement(
            word="APRIL",
            start_row=0,
            start_col=0,
            direction=Direction.DOWN,
            clue="A month",
            number=1
        )

        pattern = WordValidator.get_required_pattern(grid, placement)
        assert pattern.pattern == "A_R__"


class TestValidateAgainstPattern:
    """Tests for validating words against patterns."""

    def test_word_matches_pattern(self):
        """Test word that matches pattern."""
        pattern = Pattern("A__LE")
        result = WordValidator.validate_against_pattern("APPLE", pattern)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_word_doesnt_match_pattern(self):
        """Test word that doesn't match pattern."""
        pattern = Pattern("A__LE")
        result = WordValidator.validate_against_pattern("BREAD", pattern)

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_word_wrong_length(self):
        """Test word with wrong length."""
        pattern = Pattern("A__LE")
        result = WordValidator.validate_against_pattern("ABLE", pattern)

        assert result.is_valid is False
        assert any("length" in error.lower() for error in result.errors)

    def test_word_wrong_letter_at_position(self):
        """Test word with wrong letter at specific position."""
        pattern = Pattern("A__LE")
        result = WordValidator.validate_against_pattern("BPPLE", pattern)

        assert result.is_valid is False
        assert any("position 0" in error.lower() for error in result.errors)


class TestComprehensiveValidation:
    """Tests for comprehensive validation."""

    def test_validate_placement_valid(self):
        """Test comprehensive validation for valid placement."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )

        result = WordValidator.validate_placement(grid, placement)
        assert result.is_valid is True

    def test_validate_placement_out_of_bounds(self):
        """Test validation catches out of bounds."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=5,  # Would extend beyond grid
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )

        result = WordValidator.validate_placement(grid, placement)
        assert result.is_valid is False
        assert any("bounds" in error.lower() for error in result.errors)

    def test_validate_placement_with_conflicts(self):
        """Test validation catches conflicts."""
        grid = CrosswordGrid(size=8)

        # Place first word
        first = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )
        grid.place_word(first)

        # Try to place conflicting word
        second = WordPlacement(
            word="BREAD",
            start_row=0,
            start_col=0,
            direction=Direction.DOWN,
            clue="Food",
            number=2
        )

        result = WordValidator.validate_placement(grid, second)
        assert result.is_valid is False

    def test_validate_placement_invalid_word_format(self):
        """Test validation catches invalid word format."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="A",  # Too short
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Letter",
            number=1
        )

        result = WordValidator.validate_placement(grid, placement)
        assert result.is_valid is False
        assert any("format" in error.lower() for error in result.errors)

    def test_validate_placement_empty_clue_warning(self):
        """Test validation warns about empty clue."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="",  # Empty clue
            number=1
        )

        result = WordValidator.validate_placement(grid, placement)
        # Should have warning but might still be valid
        assert len(result.warnings) > 0


class TestCanPlaceWord:
    """Tests for can_place_word convenience method."""

    def test_can_place_word_true(self):
        """Test can_place_word returns True for valid placement."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )

        assert WordValidator.can_place_word(grid, placement) is True

    def test_can_place_word_false(self):
        """Test can_place_word returns False for invalid placement."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=5,  # Out of bounds
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )

        assert WordValidator.can_place_word(grid, placement) is False


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_corner_placement_top_left(self):
        """Test word placement at top-left corner."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="APPLE",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )

        result = WordValidator.validate_placement(grid, placement)
        assert result.is_valid is True

    def test_corner_placement_bottom_right(self):
        """Test word placement at bottom-right corner."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="APPLE",
            start_row=7,
            start_col=3,  # Ends at column 7
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )

        result = WordValidator.validate_placement(grid, placement)
        assert result.is_valid is True

    def test_full_grid_word_across(self):
        """Test word spanning entire grid width."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="ABCDEFGH",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Test",
            number=1
        )

        result = WordValidator.validate_placement(grid, placement)
        assert result.is_valid is True

    def test_full_grid_word_down(self):
        """Test word spanning entire grid height."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="ABCDEFGH",
            start_row=0,
            start_col=0,
            direction=Direction.DOWN,
            clue="Test",
            number=1
        )

        result = WordValidator.validate_placement(grid, placement)
        assert result.is_valid is True

    def test_minimum_word_length(self):
        """Test minimum valid word length (2 letters)."""
        grid = CrosswordGrid(size=8)
        placement = WordPlacement(
            word="AB",
            start_row=0,
            start_col=0,
            direction=Direction.ACROSS,
            clue="Test",
            number=1
        )

        result = WordValidator.validate_placement(grid, placement)
        assert result.is_valid is True

    def test_complex_intersection_scenario(self):
        """Test complex scenario with multiple intersections."""
        grid = CrosswordGrid(size=8)

        # Place first word: APPLE across
        first = WordPlacement(
            word="APPLE",
            start_row=2,
            start_col=1,
            direction=Direction.ACROSS,
            clue="A fruit",
            number=1
        )
        grid.place_word(first)

        # Place second word: APRIL down (intersects at first P)
        second = WordPlacement(
            word="APRIL",
            start_row=0,
            start_col=2,
            direction=Direction.DOWN,
            clue="A month",
            number=2
        )
        grid.place_word(second)

        # Try to place third word that intersects both
        third = WordPlacement(
            word="PAPER",
            start_row=2,
            start_col=2,
            direction=Direction.DOWN,
            clue="Writing material",
            number=3
        )

        result = WordValidator.validate_placement(grid, third)
        # Should be valid as it matches the 'P' at (2, 2)
        assert result.is_valid is True
