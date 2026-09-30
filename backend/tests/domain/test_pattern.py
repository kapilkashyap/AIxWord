"""
Tests for pattern matching engine.

This module contains comprehensive tests for the Pattern and PatternMatcher classes,
including:
- Pattern initialization and validation
- Pattern matching with various patterns
- Regex conversion
- Constraint extraction
- Pattern matcher filtering and scoring
- Edge cases and error handling
"""

import pytest

from backend.domain.pattern import Pattern, PatternMatcher


class TestPatternInitialization:
    """Tests for Pattern initialization and validation."""

    def test_simple_pattern(self):
        """Test creating a simple pattern."""
        pattern = Pattern("A__LE")
        assert pattern.pattern == "A__LE"
        assert pattern.length == 5

    def test_pattern_normalization(self):
        """Test pattern is normalized to uppercase."""
        pattern = Pattern("a__le")
        assert pattern.pattern == "A__LE"

    def test_empty_pattern_raises_error(self):
        """Test empty pattern raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Pattern("")

    def test_invalid_characters_raise_error(self):
        """Test pattern with invalid characters raises ValueError."""
        with pytest.raises(ValueError, match="only letters and underscores"):
            Pattern("A-B-C")

        with pytest.raises(ValueError, match="only letters and underscores"):
            Pattern("A1B2C")

        with pytest.raises(ValueError, match="only letters and underscores"):
            Pattern("A B C")

    def test_non_string_pattern_raises_error(self):
        """Test non-string pattern raises ValueError."""
        with pytest.raises(ValueError, match="must be a string"):
            Pattern(123)  # type: ignore


class TestPatternProperties:
    """Tests for Pattern properties."""

    def test_length_property(self):
        """Test length property returns correct value."""
        assert Pattern("ABC").length == 3
        assert Pattern("A__LE").length == 5
        assert Pattern("_________").length == 9

    def test_known_positions(self):
        """Test known_positions returns correct mapping."""
        pattern = Pattern("A__LE")
        known = pattern.known_positions
        assert known == {0: 'A', 3: 'L', 4: 'E'}

    def test_known_positions_empty_pattern(self):
        """Test known_positions for pattern with no known letters."""
        pattern = Pattern("_____")
        assert pattern.known_positions == {}

    def test_known_positions_full_pattern(self):
        """Test known_positions for pattern with all known letters."""
        pattern = Pattern("APPLE")
        assert pattern.known_positions == {0: 'A', 1: 'P', 2: 'P', 3: 'L', 4: 'E'}

    def test_unknown_count(self):
        """Test unknown_count returns correct value."""
        assert Pattern("A__LE").unknown_count == 2
        assert Pattern("APPLE").unknown_count == 0
        assert Pattern("_____").unknown_count == 5

    def test_is_complete(self):
        """Test is_complete property."""
        assert Pattern("APPLE").is_complete is True
        assert Pattern("A__LE").is_complete is False
        assert Pattern("_____").is_complete is False

    def test_is_empty(self):
        """Test is_empty property."""
        assert Pattern("_____").is_empty is True
        assert Pattern("A____").is_empty is False
        assert Pattern("APPLE").is_empty is False


class TestPatternMatching:
    """Tests for pattern matching functionality."""

    def test_exact_match(self):
        """Test pattern matches exact word."""
        pattern = Pattern("APPLE")
        assert pattern.matches("APPLE") is True
        assert pattern.matches("apple") is True  # Case insensitive

    def test_partial_pattern_matches(self):
        """Test pattern with underscores matches multiple words."""
        pattern = Pattern("A__LE")
        assert pattern.matches("APPLE") is True
        assert pattern.matches("ANKLE") is True
        assert pattern.matches("AGILE") is True

    def test_partial_pattern_no_match(self):
        """Test pattern doesn't match incorrect words."""
        pattern = Pattern("A__LE")
        assert pattern.matches("ABLE") is False  # Too short
        assert pattern.matches("APPLES") is False  # Too long
        assert pattern.matches("BPPLE") is False  # Wrong first letter
        assert pattern.matches("APPLA") is False  # Wrong last letter

    def test_empty_pattern_matches_any_word_same_length(self):
        """Test pattern with all underscores matches any word of same length."""
        pattern = Pattern("_____")
        assert pattern.matches("APPLE") is True
        assert pattern.matches("BREAD") is True
        assert pattern.matches("ZEBRA") is True
        assert pattern.matches("ABCD") is False  # Wrong length

    def test_single_letter_pattern(self):
        """Test single letter pattern."""
        pattern = Pattern("A")
        assert pattern.matches("A") is True
        assert pattern.matches("B") is False

        pattern = Pattern("_")
        assert pattern.matches("A") is True
        assert pattern.matches("Z") is True

    def test_matches_with_empty_word(self):
        """Test pattern doesn't match empty word."""
        pattern = Pattern("ABC")
        assert pattern.matches("") is False

    def test_case_insensitive_matching(self):
        """Test matching is case insensitive."""
        pattern = Pattern("A__LE")
        assert pattern.matches("APPLE") is True
        assert pattern.matches("apple") is True
        assert pattern.matches("ApPlE") is True


class TestPatternRegex:
    """Tests for regex conversion."""

    def test_to_regex_simple(self):
        """Test regex conversion for simple pattern."""
        pattern = Pattern("A__LE")
        regex = pattern.to_regex()
        assert regex == "^A..LE$"

    def test_to_regex_full_pattern(self):
        """Test regex conversion for full pattern."""
        pattern = Pattern("APPLE")
        regex = pattern.to_regex()
        assert regex == "^APPLE$"

    def test_to_regex_empty_pattern(self):
        """Test regex conversion for empty pattern."""
        pattern = Pattern("_____")
        regex = pattern.to_regex()
        assert regex == "^.....$"


class TestPatternConstraints:
    """Tests for constraint extraction."""

    def test_get_constraints(self):
        """Test get_constraints returns correct list."""
        pattern = Pattern("A__LE")
        constraints = pattern.get_constraints()
        assert set(constraints) == {(0, 'A'), (3, 'L'), (4, 'E')}

    def test_get_constraints_empty_pattern(self):
        """Test get_constraints for empty pattern."""
        pattern = Pattern("_____")
        assert pattern.get_constraints() == []

    def test_get_constraints_full_pattern(self):
        """Test get_constraints for full pattern."""
        pattern = Pattern("ABC")
        constraints = pattern.get_constraints()
        assert set(constraints) == {(0, 'A'), (1, 'B'), (2, 'C')}


class TestPatternCharAt:
    """Tests for get_char_at method."""

    def test_get_char_at_known_position(self):
        """Test getting character at known position."""
        pattern = Pattern("A__LE")
        assert pattern.get_char_at(0) == 'A'
        assert pattern.get_char_at(3) == 'L'
        assert pattern.get_char_at(4) == 'E'

    def test_get_char_at_unknown_position(self):
        """Test getting character at unknown position returns None."""
        pattern = Pattern("A__LE")
        assert pattern.get_char_at(1) is None
        assert pattern.get_char_at(2) is None

    def test_get_char_at_out_of_bounds(self):
        """Test getting character at invalid position raises IndexError."""
        pattern = Pattern("ABC")
        with pytest.raises(IndexError):
            pattern.get_char_at(-1)
        with pytest.raises(IndexError):
            pattern.get_char_at(3)
        with pytest.raises(IndexError):
            pattern.get_char_at(10)


class TestPatternEquality:
    """Tests for pattern equality and hashing."""

    def test_pattern_equality(self):
        """Test pattern equality comparison."""
        pattern1 = Pattern("A__LE")
        pattern2 = Pattern("A__LE")
        pattern3 = Pattern("A__LX")

        assert pattern1 == pattern2
        assert pattern1 != pattern3

    def test_pattern_hash(self):
        """Test pattern can be used in sets and dicts."""
        pattern1 = Pattern("A__LE")
        pattern2 = Pattern("A__LE")
        pattern3 = Pattern("A__LX")

        pattern_set = {pattern1, pattern2, pattern3}
        assert len(pattern_set) == 2  # pattern1 and pattern2 are same


class TestPatternMatcher:
    """Tests for PatternMatcher class."""

    def test_find_matches_basic(self):
        """Test finding matches in candidate list."""
        pattern = Pattern("A__LE")
        candidates = ["APPLE", "ANKLE", "ABLE", "AGILE", "BREAD"]
        matches = PatternMatcher.find_matches(pattern, candidates)

        assert set(matches) == {"APPLE", "ANKLE", "AGILE"}

    def test_find_matches_empty_candidates(self):
        """Test finding matches with empty candidate list."""
        pattern = Pattern("A__LE")
        matches = PatternMatcher.find_matches(pattern, [])
        assert matches == []

    def test_find_matches_no_matches(self):
        """Test finding matches when no candidates match."""
        pattern = Pattern("XYZ")
        candidates = ["APPLE", "BREAD", "CHAIR"]
        matches = PatternMatcher.find_matches(pattern, candidates)
        assert matches == []

    def test_find_matches_case_normalization(self):
        """Test matches are normalized to uppercase."""
        pattern = Pattern("A__LE")
        candidates = ["apple", "ANKLE", "AgIlE"]
        matches = PatternMatcher.find_matches(pattern, candidates)

        assert all(m.isupper() for m in matches)
        assert set(matches) == {"APPLE", "ANKLE", "AGILE"}


class TestPatternMatcherScoring:
    """Tests for pattern match scoring."""

    def test_score_match_perfect(self):
        """Test scoring for perfect match."""
        pattern = Pattern("A__LE")
        score = PatternMatcher.score_match("APPLE", pattern)
        assert score == 1.0

    def test_score_match_no_match(self):
        """Test scoring for no match."""
        pattern = Pattern("A__LE")
        score = PatternMatcher.score_match("BREAD", pattern)
        assert score == 0.0


class TestPatternMatcherGridPattern:
    """Tests for creating patterns from grid values."""

    def test_create_pattern_from_grid_mixed(self):
        """Test creating pattern from mixed grid values."""
        grid_values = ['A', None, None, 'L', 'E']
        pattern = PatternMatcher.create_pattern_from_grid(grid_values)
        assert pattern.pattern == "A__LE"

    def test_create_pattern_from_grid_all_filled(self):
        """Test creating pattern from all filled grid."""
        grid_values = ['A', 'P', 'P', 'L', 'E']
        pattern = PatternMatcher.create_pattern_from_grid(grid_values)
        assert pattern.pattern == "APPLE"

    def test_create_pattern_from_grid_all_empty(self):
        """Test creating pattern from all empty grid."""
        grid_values = [None, None, None, None, None]
        pattern = PatternMatcher.create_pattern_from_grid(grid_values)
        assert pattern.pattern == "_____"

    def test_create_pattern_from_grid_empty_list(self):
        """Test creating pattern from empty grid raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            PatternMatcher.create_pattern_from_grid([])

    def test_create_pattern_from_grid_invalid_value(self):
        """Test creating pattern with invalid grid value raises error."""
        with pytest.raises(ValueError, match="Invalid grid value"):
            PatternMatcher.create_pattern_from_grid(['A', 'B', 123])

        with pytest.raises(ValueError, match="Invalid grid value"):
            PatternMatcher.create_pattern_from_grid(['A', 'BB', 'C'])

    def test_create_pattern_from_grid_case_normalization(self):
        """Test grid values are normalized to uppercase."""
        grid_values = ['a', None, 'p', None, 'e']
        pattern = PatternMatcher.create_pattern_from_grid(grid_values)
        assert pattern.pattern == "A_P_E"


class TestPatternMatcherRegex:
    """Tests for regex-based matching."""

    def test_match_with_regex(self):
        """Test regex-based matching."""
        pattern = Pattern("A__LE")
        candidates = ["APPLE", "ANKLE", "ABLE", "AGILE", "BREAD"]
        matches = PatternMatcher.match_with_regex(pattern, candidates)

        assert set(matches) == {"APPLE", "ANKLE", "AGILE"}

    def test_match_with_regex_case_insensitive(self):
        """Test regex matching is case insensitive."""
        pattern = Pattern("A__LE")
        candidates = ["apple", "ANKLE", "AgIlE"]
        matches = PatternMatcher.match_with_regex(pattern, candidates)

        assert set(matches) == {"APPLE", "ANKLE", "AGILE"}


class TestPatternComplexity:
    """Tests for pattern complexity calculation."""

    def test_complexity_empty_pattern(self):
        """Test complexity of empty pattern."""
        pattern = Pattern("_____")
        complexity = PatternMatcher.get_pattern_complexity(pattern)
        assert complexity == 0.0

    def test_complexity_full_pattern(self):
        """Test complexity of full pattern."""
        pattern = Pattern("APPLE")
        complexity = PatternMatcher.get_pattern_complexity(pattern)
        assert complexity == 1.0

    def test_complexity_partial_pattern(self):
        """Test complexity of partial pattern."""
        pattern = Pattern("A__LE")
        complexity = PatternMatcher.get_pattern_complexity(pattern)
        assert complexity == 0.6  # 3 known out of 5

    def test_complexity_half_known(self):
        """Test complexity of half-known pattern."""
        pattern = Pattern("A_B_")
        complexity = PatternMatcher.get_pattern_complexity(pattern)
        assert complexity == 0.5  # 2 known out of 4


class TestPatternMerging:
    """Tests for pattern merging."""

    def test_merge_compatible_patterns(self):
        """Test merging compatible patterns."""
        pattern1 = Pattern("A____")
        pattern2 = Pattern("___LE")
        merged = PatternMatcher.merge_patterns(pattern1, pattern2)

        assert merged is not None
        assert merged.pattern == "A__LE"

    def test_merge_overlapping_same_letters(self):
        """Test merging patterns with overlapping same letters."""
        pattern1 = Pattern("A__L_")
        pattern2 = Pattern("___LE")
        merged = PatternMatcher.merge_patterns(pattern1, pattern2)

        assert merged is not None
        assert merged.pattern == "A__LE"

    def test_merge_conflicting_patterns(self):
        """Test merging conflicting patterns returns None."""
        pattern1 = Pattern("A__LE")
        pattern2 = Pattern("B__LE")
        merged = PatternMatcher.merge_patterns(pattern1, pattern2)

        assert merged is None

    def test_merge_different_lengths(self):
        """Test merging patterns of different lengths returns None."""
        pattern1 = Pattern("ABC")
        pattern2 = Pattern("ABCD")
        merged = PatternMatcher.merge_patterns(pattern1, pattern2)

        assert merged is None

    def test_merge_identical_patterns(self):
        """Test merging identical patterns."""
        pattern1 = Pattern("A__LE")
        pattern2 = Pattern("A__LE")
        merged = PatternMatcher.merge_patterns(pattern1, pattern2)

        assert merged is not None
        assert merged.pattern == "A__LE"

    def test_merge_empty_patterns(self):
        """Test merging empty patterns."""
        pattern1 = Pattern("_____")
        pattern2 = Pattern("_____")
        merged = PatternMatcher.merge_patterns(pattern1, pattern2)

        assert merged is not None
        assert merged.pattern == "_____"


class TestPatternEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_single_character_pattern(self):
        """Test single character patterns."""
        pattern = Pattern("A")
        assert pattern.length == 1
        assert pattern.matches("A") is True
        assert pattern.matches("B") is False

        pattern = Pattern("_")
        assert pattern.matches("X") is True

    def test_very_long_pattern(self):
        """Test very long pattern."""
        long_pattern = "A" + "_" * 48 + "Z"  # 50 characters
        pattern = Pattern(long_pattern)
        assert pattern.length == 50
        assert pattern.known_positions == {0: 'A', 49: 'Z'}

    def test_pattern_with_all_same_letter(self):
        """Test pattern with all same letter."""
        pattern = Pattern("AAAA")
        assert pattern.matches("AAAA") is True
        assert pattern.matches("AAAB") is False

    def test_alternating_pattern(self):
        """Test alternating known/unknown pattern."""
        pattern = Pattern("A_B_C_D")
        assert pattern.length == 7
        assert len(pattern.known_positions) == 4
        assert pattern.matches("AXBXCXD") is True
        assert pattern.matches("AZBZCZD") is True
        assert pattern.matches("BXBXCXD") is False
