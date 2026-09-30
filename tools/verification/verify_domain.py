#!/usr/bin/env python3
"""
Verification script for domain models and grid engine.

This script verifies that the domain models work correctly without requiring
all project dependencies to be installed.
"""

from domain import Cell, Clue, CrosswordGrid, Direction, Word, WordPlacement


def test_basic_functionality():
    """Test basic domain functionality."""
    print("Testing AIxWord Domain Models...")
    print("=" * 60)

    # Test 1: Create a grid
    print("\n1. Creating 8x8 grid...")
    grid = CrosswordGrid(size=8)
    print(f"   ✓ Grid created: {grid}")
    assert grid.size == 8
    assert len(grid.words) == 0

    # Test 2: Place a horizontal word
    print("\n2. Placing horizontal word 'HELLO'...")
    placement1 = WordPlacement(
        word="HELLO",
        start_row=2,
        start_col=1,
        direction=Direction.ACROSS,
        clue="A greeting",
        number=1,
    )
    result = grid.place_word(placement1)
    print(f"   ✓ Word placed: {result}")
    assert result is True
    assert len(grid.words) == 1
    assert grid.get_cell(2, 1).value == "H"

    # Test 3: Place a vertical word that intersects
    # HELLO: H(2,1) E(2,2) L(2,3) L(2,4) O(2,5)
    # OLDER: O(0,4) L(1,4) D(2,4) E(3,4) R(4,4)
    # At (2,4): HELLO has 'L', OLDER has 'D' - no match!
    # Let's use ALLOW: A(0,4) L(1,4) L(2,4) O(3,4) W(4,4)
    # At (2,4): HELLO has 'L', ALLOW has 'L' - match!
    print("\n3. Placing vertical word 'ALLOW' (intersecting at 'L')...")
    placement2 = WordPlacement(
        word="ALLOW",
        start_row=0,
        start_col=4,
        direction=Direction.DOWN,
        clue="Permit",
        number=2,
    )
    result = grid.place_word(placement2)
    print(f"   ✓ Word placed: {result}")
    assert result is True
    assert len(grid.words) == 2

    # Test 4: Check intersection
    print("\n4. Checking word intersection...")
    word1 = grid.words[0]
    word2 = grid.words[1]
    intersection = word1.intersects_with(word2)
    print(f"   ✓ Intersection at: {intersection}")
    assert intersection == (2, 4)
    assert grid.get_cell(2, 4).value == "L"

    # Test 5: Check fill rate
    print("\n5. Checking grid fill rate...")
    fill_rate = grid.get_fill_rate()
    print(f"   ✓ Fill rate: {fill_rate:.2%}")
    assert fill_rate > 0

    # Test 6: Assign numbers
    print("\n6. Assigning clue numbers...")
    grid.assign_numbers()
    print("   ✓ Numbers assigned")
    assert grid.get_cell(0, 4).number == 1
    assert grid.get_cell(2, 1).number == 2

    # Test 7: Test pattern matching
    print("\n7. Testing pattern matching...")
    word3 = Word("WORLD", 0, 3, Direction.DOWN)
    pattern = word3.get_pattern(grid)
    print(f"   ✓ Pattern for 'WORLD': {pattern}")
    # WORLD at col 3: (0,3) (1,3) (2,3) (3,3) (4,3)
    # HELLO has 'L' at (2,3)
    assert pattern == "__L__"  # 'L' from HELLO at position 2

    # Test 8: Test serialization
    print("\n8. Testing grid serialization...")
    data = grid.to_dict()
    restored = CrosswordGrid.from_dict(data)
    print("   ✓ Grid serialized and restored")
    assert restored.size == grid.size
    assert len(restored.words) == len(grid.words)

    # Test 9: Test cloning
    print("\n9. Testing grid cloning...")
    clone = grid.clone()
    clone.set_cell(0, 0, "X")
    print("   ✓ Grid cloned (original unchanged)")
    assert grid.get_cell(0, 0).value is None
    assert clone.get_cell(0, 0).value == "X"

    # Test 10: Test word removal
    print("\n10. Testing word removal...")
    initial_count = len(grid.words)
    grid.remove_word(word1)
    print(f"   ✓ Word removed (words: {initial_count} → {len(grid.words)})")
    assert len(grid.words) == initial_count - 1

    print("\n" + "=" * 60)
    print("✓ All domain model tests passed!")
    print("=" * 60)


def test_cell_model():
    """Test Cell model."""
    print("\nTesting Cell model...")

    cell = Cell(row=0, col=0, value="A")
    assert cell.value == "A"
    assert cell.is_filled
    assert not cell.is_empty

    cell2 = Cell(row=1, col=1)
    assert cell2.value is None
    assert not cell2.is_filled
    assert cell2.is_empty

    print("   ✓ Cell model works correctly")


def test_direction_enum():
    """Test Direction enum."""
    print("\nTesting Direction enum...")

    assert Direction.ACROSS.value == "across"
    assert Direction.DOWN.value == "down"
    assert Direction.ACROSS.opposite == Direction.DOWN
    assert Direction.DOWN.opposite == Direction.ACROSS

    print("   ✓ Direction enum works correctly")


def test_clue_model():
    """Test Clue model."""
    print("\nTesting Clue model...")

    clue = Clue(
        number=1,
        direction=Direction.ACROSS,
        text="A greeting",
        answer="HELLO",
        start_row=0,
        start_col=0,
        length=5,
    )

    assert clue.answer == "HELLO"
    assert clue.length == 5

    placement = clue.to_word_placement()
    assert placement.word == "HELLO"
    assert placement.clue == "A greeting"

    print("   ✓ Clue model works correctly")


if __name__ == "__main__":
    try:
        test_direction_enum()
        test_cell_model()
        test_clue_model()
        test_basic_functionality()
        print("\n🎉 All verification tests passed successfully!")
        exit(0)
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
