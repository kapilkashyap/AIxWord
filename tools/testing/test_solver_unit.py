#!/usr/bin/env python3
"""
Unit tests for the PuzzleSolver service.

This script tests the solver service in isolation without requiring
the full FastAPI application or OpenAI API key.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir.parent))


def test_solver_initialization():
    """Test solver can be initialized."""
    print("Test 1: Solver Initialization")
    print("-" * 70)

    from backend.api.services.solver import PuzzleSolver

    # Mock LLM client
    mock_client = Mock()
    solver = PuzzleSolver(llm_client=mock_client)

    assert solver is not None, "Solver should be initialized"
    assert solver.llm_client is mock_client, "Solver should use provided client"

    print("✓ Solver initialized successfully")
    print("✓ Solver uses provided LLM client")
    return True


def test_solver_singleton():
    """Test solver singleton pattern."""
    print("\nTest 2: Solver Singleton Pattern")
    print("-" * 70)

    from backend.api.services.solver import get_solver

    # Mock the global instance
    with patch('backend.api.services.solver._solver_instance', None):
        solver1 = get_solver()
        solver2 = get_solver()

        assert solver1 is solver2, "get_solver should return same instance"

    print("✓ Singleton pattern working correctly")
    return True


def test_solver_methods_exist():
    """Test solver has required methods."""
    print("\nTest 3: Solver Methods")
    print("-" * 70)

    from backend.api.services.solver import PuzzleSolver

    mock_client = Mock()
    solver = PuzzleSolver(llm_client=mock_client)

    required_methods = [
        'solve_word',
        'solve_puzzle',
        'generate_hint',
        '_build_solve_word_prompt',
        '_matches_pattern',
    ]

    for method in required_methods:
        assert hasattr(solver, method), f"Solver should have {method} method"
        print(f"✓ Solver has {method} method")

    return True


def test_pattern_matching():
    """Test pattern matching logic."""
    print("\nTest 4: Pattern Matching")
    print("-" * 70)

    from backend.api.services.solver import PuzzleSolver

    mock_client = Mock()
    solver = PuzzleSolver(llm_client=mock_client)

    # Test exact match
    assert solver._matches_pattern("ATOM", "ATOM"), "Should match exact pattern"
    print("✓ Exact pattern match works")

    # Test wildcard match
    assert solver._matches_pattern("ATOM", "A__M"), "Should match wildcard pattern"
    print("✓ Wildcard pattern match works")

    # Test mismatch
    assert not solver._matches_pattern("ATOM", "B__M"), "Should not match different pattern"
    print("✓ Pattern mismatch detection works")

    # Test length mismatch
    assert not solver._matches_pattern("ATOM", "A__"), "Should not match different length"
    print("✓ Length mismatch detection works")

    return True


def test_prompt_building():
    """Test prompt building for word solving."""
    print("\nTest 5: Prompt Building")
    print("-" * 70)

    from backend.api.services.solver import PuzzleSolver

    mock_client = Mock()
    solver = PuzzleSolver(llm_client=mock_client)

    # Test basic prompt
    prompt = solver._build_solve_word_prompt("Test clue", 4, None)
    assert "Test clue" in prompt, "Prompt should contain clue"
    assert "4 letters" in prompt, "Prompt should contain length"
    print("✓ Basic prompt building works")

    # Test prompt with pattern
    prompt = solver._build_solve_word_prompt("Test clue", 4, "A__T")
    assert "A__T" in prompt, "Prompt should contain pattern"
    print("✓ Prompt with pattern works")

    return True


def test_dependencies():
    """Test dependency injection setup."""
    print("\nTest 6: Dependency Injection")
    print("-" * 70)

    from backend.api.dependencies import SolverDep, get_puzzle_solver

    # Test dependency function exists
    assert callable(get_puzzle_solver), "get_puzzle_solver should be callable"
    print("✓ get_puzzle_solver function exists")

    # Test type annotation exists
    assert SolverDep is not None, "SolverDep should be defined"
    print("✓ SolverDep type annotation exists")

    return True


def test_service_exports():
    """Test service package exports."""
    print("\nTest 7: Service Package Exports")
    print("-" * 70)

    from backend.api.services import PuzzleSolver

    assert PuzzleSolver is not None, "PuzzleSolver should be exported"
    print("✓ PuzzleSolver exported from services package")

    return True


def main():
    """Run all unit tests."""
    print("\n" + "=" * 70)
    print("PUZZLE SOLVER UNIT TESTS")
    print("=" * 70 + "\n")

    tests = [
        ("Solver Initialization", test_solver_initialization),
        ("Solver Singleton", test_solver_singleton),
        ("Solver Methods", test_solver_methods_exist),
        ("Pattern Matching", test_pattern_matching),
        ("Prompt Building", test_prompt_building),
        ("Dependencies", test_dependencies),
        ("Service Exports", test_service_exports),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL UNIT TESTS PASSED")
        print("=" * 70)
        print("\nThe PuzzleSolver service is working correctly!")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
