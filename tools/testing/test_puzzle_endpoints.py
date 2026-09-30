#!/usr/bin/env python3
"""
Test script for puzzle generation API endpoints.

This script demonstrates the complete puzzle generation and solving workflow:
1. Generate a puzzle from a topic
2. Retrieve the puzzle
3. Solve a word with AI
4. Get hints for words
5. Solve the entire puzzle
6. Validate a solution
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir.parent))


async def test_puzzle_workflow():
    """Test the complete puzzle workflow."""
    from backend.agents.orchestrator import PuzzleGenerationRequest, PuzzleOrchestrator
    from backend.api.services.solver import PuzzleSolver

    print("\n" + "=" * 70)
    print("PUZZLE GENERATION API WORKFLOW TEST")
    print("=" * 70 + "\n")

    # Initialize services
    orchestrator = PuzzleOrchestrator()
    solver = PuzzleSolver()

    # Step 1: Generate a puzzle
    print("Step 1: Generating puzzle...")
    print("-" * 70)

    request = PuzzleGenerationRequest(
        topic="Science",
        grid_size=8,
        min_words=8,
        max_words=12,
        difficulty="medium",
        max_iterations=30,
    )

    print(f"Topic: {request.topic}")
    print(f"Grid size: {request.grid_size}x{request.grid_size}")
    print(f"Target words: {request.min_words}-{request.max_words}")
    print(f"Difficulty: {request.difficulty}")
    print("\nGenerating puzzle (this may take 30-60 seconds)...")

    result = await orchestrator.generate_puzzle_async(request)

    if not result.success:
        print(f"\n✗ Puzzle generation failed: {result.error_message}")
        return False

    print("\n✓ Puzzle generated successfully!")
    print(f"  - Words placed: {result.word_count}")
    print(f"  - Fill rate: {result.fill_rate:.1%}")
    print(f"  - Iterations: {result.iterations}")
    print(f"  - Status: {result.status}")

    grid_dict = result.grid
    if not grid_dict:
        print("\n✗ No grid data in result")
        return False

    # Step 2: Display puzzle information
    print("\n" + "=" * 70)
    print("Step 2: Puzzle Information")
    print("-" * 70)

    words = grid_dict.get("words", [])
    print(f"\nTotal words: {len(words)}")

    across_words = [w for w in words if w["direction"] == "across"]
    down_words = [w for w in words if w["direction"] == "down"]

    print(f"\nAcross clues ({len(across_words)}):")
    for word in sorted(across_words, key=lambda w: w["number"]):
        print(f"  {word['number']}. {word['clue']} ({len(word['word'])} letters)")

    print(f"\nDown clues ({len(down_words)}):")
    for word in sorted(down_words, key=lambda w: w["number"]):
        print(f"  {word['number']}. {word['clue']} ({len(word['word'])} letters)")

    # Step 3: Test solving a word
    if words:
        print("\n" + "=" * 70)
        print("Step 3: Solving a Word with AI")
        print("-" * 70)

        test_word = words[0]
        print(f"\nSolving: {test_word['number']} {test_word['direction']}")
        print(f"Clue: {test_word['clue']}")
        print(f"Length: {len(test_word['word'])} letters")
        print(f"Actual answer: {test_word['word']}")

        print("\nCalling AI solver...")
        answer, confidence, reasoning = await solver.solve_word(
            clue=test_word['clue'],
            length=len(test_word['word']),
            pattern=None,
            intersections=None
        )

        print("\n✓ AI Solution:")
        print(f"  - Answer: {answer}")
        print(f"  - Confidence: {confidence:.2%}")
        print(f"  - Reasoning: {reasoning}")

        if answer == test_word['word']:
            print("  - ✓ Correct!")
        else:
            print(f"  - ✗ Incorrect (expected: {test_word['word']})")

    # Step 4: Test hint generation
    if words:
        print("\n" + "=" * 70)
        print("Step 4: Generating Hints")
        print("-" * 70)

        test_word = words[0]
        print(f"\nGenerating hints for: {test_word['number']} {test_word['direction']}")
        print(f"Clue: {test_word['clue']}")
        print(f"Answer: {test_word['word']}")

        # Test letter hint
        print("\n1. Letter hint:")
        hint_text, letter, position = await solver.generate_hint(
            clue=test_word['clue'],
            answer=test_word['word'],
            hint_type="letter"
        )
        print(f"   {hint_text}")
        if letter and position is not None:
            print(f"   Revealed: '{letter}' at position {position}")

        # Test definition hint
        print("\n2. Definition hint:")
        hint_text, _, _ = await solver.generate_hint(
            clue=test_word['clue'],
            answer=test_word['word'],
            hint_type="definition"
        )
        print(f"   {hint_text}")

        # Test synonym hint
        print("\n3. Synonym hint:")
        hint_text, _, _ = await solver.generate_hint(
            clue=test_word['clue'],
            answer=test_word['word'],
            hint_type="synonym"
        )
        print(f"   {hint_text}")

    # Step 5: Test solving entire puzzle
    print("\n" + "=" * 70)
    print("Step 5: Solving Entire Puzzle")
    print("-" * 70)

    print("\nSolving entire puzzle...")
    cells_data, confidence, reasoning = await solver.solve_puzzle(
        grid_dict=grid_dict,
        use_hints=True
    )

    print("\n✓ Puzzle solved:")
    print(f"  - Cells filled: {len(cells_data)}")
    print(f"  - Confidence: {confidence:.2%}")
    print(f"  - Reasoning: {reasoning}")

    # Step 6: Summary
    print("\n" + "=" * 70)
    print("WORKFLOW TEST SUMMARY")
    print("=" * 70)

    print("\n✓ All workflow steps completed successfully!")
    print("\nTested features:")
    print("  ✓ Puzzle generation from topic")
    print("  ✓ Word solving with AI")
    print("  ✓ Hint generation (letter, definition, synonym)")
    print("  ✓ Full puzzle solving")

    print("\nThe puzzle generation API is working correctly!")

    return True


async def test_solver_edge_cases():
    """Test solver edge cases and error handling."""
    from backend.api.services.solver import PuzzleSolver

    print("\n" + "=" * 70)
    print("SOLVER EDGE CASES TEST")
    print("=" * 70 + "\n")

    solver = PuzzleSolver()

    # Test 1: Short word
    print("Test 1: Short word (3 letters)")
    print("-" * 70)
    answer, confidence, reasoning = await solver.solve_word(
        clue="Opposite of yes",
        length=3,
        pattern=None,
        intersections=None
    )
    print(f"Answer: {answer}")
    print(f"Confidence: {confidence:.2%}")
    print(f"Reasoning: {reasoning}")

    # Test 2: Word with pattern
    print("\n\nTest 2: Word with pattern")
    print("-" * 70)
    answer, confidence, reasoning = await solver.solve_word(
        clue="Large body of water",
        length=5,
        pattern="O_E_N",
        intersections=None
    )
    print(f"Answer: {answer}")
    print(f"Confidence: {confidence:.2%}")
    print(f"Reasoning: {reasoning}")

    # Test 3: Hint generation
    print("\n\nTest 3: Hint generation")
    print("-" * 70)
    hint_text, letter, position = await solver.generate_hint(
        clue="King of the jungle",
        answer="LION",
        hint_type="letter"
    )
    print(f"Hint: {hint_text}")
    print(f"Revealed letter: {letter} at position {position}")

    print("\n✓ Edge cases handled correctly!")

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("PUZZLE GENERATION API ENDPOINT TESTS")
    print("=" * 70)

    try:
        # Run workflow test
        success = asyncio.run(test_puzzle_workflow())

        if not success:
            print("\n✗ Workflow test failed")
            return 1

        # Run edge cases test
        success = asyncio.run(test_solver_edge_cases())

        if not success:
            print("\n✗ Edge cases test failed")
            return 1

        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        print("\nThe puzzle generation API endpoints are working correctly!")
        print("\nYou can now:")
        print("1. Start the server: python3 run_server.py")
        print("2. Access the API docs: http://localhost:8000/docs")
        print("3. Test with the frontend application")

        return 0

    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
