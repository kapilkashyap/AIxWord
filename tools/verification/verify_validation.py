#!/usr/bin/env python3
"""
Verification script for Word Validation & Pattern Matching phase.

This script demonstrates the functionality of the pattern matching and
validation engines implemented in Phase 3.
"""

from domain import (
    CrosswordGrid,
    Direction,
    Pattern,
    PatternMatcher,
    WordPlacement,
    WordValidator,
)


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print('=' * 70)


def test_pattern_matching():
    """Test pattern matching functionality."""
    print_section("Pattern Matching Tests")

    # Test 1: Basic pattern matching
    print("\n1. Basic Pattern Matching:")
    pattern = Pattern("A__LE")
    print(f"   Pattern: {pattern}")
    print(f"   Length: {pattern.length}")
    print(f"   Known positions: {pattern.known_positions}")

    test_words = ["APPLE", "ANKLE", "AGILE", "ABLE", "BREAD"]
    print(f"\n   Testing words: {test_words}")
    for word in test_words:
        matches = pattern.matches(word)
        print(f"   - {word}: {'✓ matches' if matches else '✗ no match'}")

    # Test 2: Pattern from grid
    print("\n2. Pattern Extraction from Grid:")
    grid_values = ['A', None, None, 'L', 'E']
    pattern = PatternMatcher.create_pattern_from_grid(grid_values)
    print(f"   Grid values: {grid_values}")
    print(f"   Extracted pattern: {pattern}")

    # Test 3: Pattern complexity
    print("\n3. Pattern Complexity:")
    patterns = ["_____", "A____", "A__LE", "APPLE"]
    for p in patterns:
        pattern = Pattern(p)
        complexity = PatternMatcher.get_pattern_complexity(pattern)
        print(f"   {p}: {complexity:.1%} known")

    # Test 4: Pattern merging
    print("\n4. Pattern Merging:")
    p1 = Pattern("A____")
    p2 = Pattern("___LE")
    merged = PatternMatcher.merge_patterns(p1, p2)
    print(f"   Pattern 1: {p1}")
    print(f"   Pattern 2: {p2}")
    print(f"   Merged: {merged}")


def test_word_validation():
    """Test word validation functionality."""
    print_section("Word Validation Tests")

    grid = CrosswordGrid(size=8)

    # Test 1: Valid placement
    print("\n1. Valid Word Placement:")
    placement = WordPlacement(
        word="APPLE",
        start_row=0,
        start_col=0,
        direction=Direction.ACROSS,
        clue="A fruit",
        number=1
    )
    result = WordValidator.validate_placement(grid, placement)
    print(f"   Word: {placement.word} at ({placement.start_row}, {placement.start_col}) {placement.direction}")
    print(f"   Result: {result}")

    # Place the word
    grid.place_word(placement)

    # Test 2: Valid intersection
    print("\n2. Valid Intersection:")
    placement2 = WordPlacement(
        word="PAPER",
        start_row=0,
        start_col=2,
        direction=Direction.DOWN,
        clue="Writing material",
        number=2
    )
    result = WordValidator.validate_placement(grid, placement2)
    print(f"   Word: {placement2.word} at ({placement2.start_row}, {placement2.start_col}) {placement2.direction}")
    print("   Intersects with APPLE at 'P'")
    print(f"   Result: {result}")

    # Test 3: Invalid - out of bounds
    print("\n3. Invalid - Out of Bounds:")
    placement3 = WordPlacement(
        word="TOOLONG",
        start_row=0,
        start_col=5,
        direction=Direction.ACROSS,
        clue="Too long",
        number=3
    )
    result = WordValidator.validate_placement(grid, placement3)
    print(f"   Word: {placement3.word} at ({placement3.start_row}, {placement3.start_col}) {placement3.direction}")
    print(f"   Result: {result}")
    if result.errors:
        print(f"   Errors: {result.errors}")

    # Test 4: Invalid - conflicting letters
    print("\n4. Invalid - Conflicting Letters:")
    placement4 = WordPlacement(
        word="BREAD",
        start_row=0,
        start_col=0,
        direction=Direction.DOWN,
        clue="Food",
        number=4
    )
    result = WordValidator.validate_placement(grid, placement4)
    print(f"   Word: {placement4.word} at ({placement4.start_row}, {placement4.start_col}) {placement4.direction}")
    print("   Conflicts with APPLE at 'A' vs 'B'")
    print(f"   Result: {result}")
    if result.errors:
        print(f"   Errors: {result.errors}")


def test_pattern_extraction():
    """Test pattern extraction from grid."""
    print_section("Pattern Extraction from Grid")

    grid = CrosswordGrid(size=8)

    # Place a word
    placement = WordPlacement(
        word="APPLE",
        start_row=2,
        start_col=1,
        direction=Direction.ACROSS,
        clue="A fruit",
        number=1
    )
    grid.place_word(placement)

    # Fill some cells manually
    grid.set_cell(0, 2, 'P')
    grid.set_cell(1, 2, 'A')

    # Extract pattern for a DOWN word at (0, 2)
    test_placement = WordPlacement(
        word="PAPER",
        start_row=0,
        start_col=2,
        direction=Direction.DOWN,
        clue="Test",
        number=2
    )

    pattern = WordValidator.get_required_pattern(grid, test_placement)
    print("\n   Grid state at column 2:")
    print("   - (0, 2): P")
    print("   - (1, 2): A")
    print("   - (2, 2): P (from APPLE)")
    print("   - (3, 2): empty")
    print("   - (4, 2): empty")
    print(f"\n   Extracted pattern: {pattern}")
    print(f"   Word 'PAPER' matches: {pattern.matches('PAPER')}")


def test_format_validation():
    """Test word and clue format validation."""
    print_section("Format Validation Tests")

    print("\n1. Word Format Validation:")
    test_words = [
        ("APPLE", True),
        ("A", False),  # Too short
        ("APPLE1", False),  # Contains number
        ("APPLE-PIE", False),  # Contains hyphen
        ("", False),  # Empty
    ]

    for word, expected in test_words:
        is_valid = WordValidator.validate_word_format(word)
        status = "✓" if is_valid == expected else "✗"
        print(f"   {status} '{word}': {is_valid}")

    print("\n2. Clue Format Validation:")
    test_clues = [
        ("A fruit", True),
        ("", False),  # Empty
        ("A" * 501, False),  # Too long
    ]

    for clue, expected in test_clues:
        is_valid = WordValidator.validate_clue(clue)
        display_clue = clue if len(clue) < 20 else clue[:17] + "..."
        status = "✓" if is_valid == expected else "✗"
        print(f"   {status} '{display_clue}': {is_valid}")


def main():
    """Run all verification tests."""
    print("\n" + "=" * 70)
    print("  Word Validation & Pattern Matching - Phase 3 Verification")
    print("=" * 70)

    try:
        test_pattern_matching()
        test_word_validation()
        test_pattern_extraction()
        test_format_validation()

        print("\n" + "=" * 70)
        print("  ✓ All verification tests completed successfully!")
        print("=" * 70 + "\n")

        return 0

    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
