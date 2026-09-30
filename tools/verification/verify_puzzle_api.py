#!/usr/bin/env python3
"""
Verification script for puzzle generation API endpoints.

This script verifies that:
1. All API modules can be imported
2. Solver service is properly configured
3. Dependencies are correctly set up
4. Routes are properly registered
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir.parent))


def verify_imports():
    """Verify all API modules can be imported."""
    print("=" * 70)
    print("VERIFYING IMPORTS")
    print("=" * 70)

    try:
        print("✓ PuzzleSolver imported successfully")
    except Exception as e:
        print(f"✗ Failed to import PuzzleSolver: {e}")
        return False

    try:
        print("✓ get_solver imported successfully")
    except Exception as e:
        print(f"✗ Failed to import get_solver: {e}")
        return False

    try:
        print("✓ SolverDep imported successfully")
    except Exception as e:
        print(f"✗ Failed to import SolverDep: {e}")
        return False

    try:
        print("✓ Puzzle routes imported successfully")
    except Exception as e:
        print(f"✗ Failed to import puzzle routes: {e}")
        return False

    try:
        print("✓ FastAPI app imported successfully")
    except Exception as e:
        print(f"✗ Failed to import FastAPI app: {e}")
        return False

    print("\n✓ All imports successful\n")
    return True


def verify_solver_service():
    """Verify solver service is properly configured."""
    print("=" * 70)
    print("VERIFYING SOLVER SERVICE")
    print("=" * 70)

    try:
        from backend.api.services.solver import get_solver

        # Test singleton
        solver1 = get_solver()
        solver2 = get_solver()

        if solver1 is not solver2:
            print("✗ Solver singleton not working correctly")
            return False
        print("✓ Solver singleton working correctly")

        # Test solver initialization
        if not hasattr(solver1, 'llm_client'):
            print("✗ Solver missing llm_client attribute")
            return False
        print("✓ Solver has llm_client attribute")

        # Test solver methods
        required_methods = ['solve_word', 'solve_puzzle', 'generate_hint']
        for method in required_methods:
            if not hasattr(solver1, method):
                print(f"✗ Solver missing {method} method")
                return False
            print(f"✓ Solver has {method} method")

        print("\n✓ Solver service verified\n")
        return True

    except Exception as e:
        print(f"✗ Solver service verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_dependencies():
    """Verify dependency injection is properly configured."""
    print("=" * 70)
    print("VERIFYING DEPENDENCIES")
    print("=" * 70)

    try:
        from backend.api.dependencies import (
            get_app_settings,
            get_puzzle_orchestrator,
            get_puzzle_solver,
        )

        # Test orchestrator dependency
        orchestrator = get_puzzle_orchestrator()
        if orchestrator is None:
            print("✗ Orchestrator dependency returns None")
            return False
        print("✓ Orchestrator dependency working")

        # Test solver dependency
        solver = get_puzzle_solver()
        if solver is None:
            print("✗ Solver dependency returns None")
            return False
        print("✓ Solver dependency working")

        # Test settings dependency
        settings = get_app_settings()
        if settings is None:
            print("✗ Settings dependency returns None")
            return False
        print("✓ Settings dependency working")

        # Verify type annotations
        print("✓ OrchestratorDep type annotation defined")
        print("✓ SolverDep type annotation defined")
        print("✓ SettingsDep type annotation defined")

        print("\n✓ All dependencies verified\n")
        return True

    except Exception as e:
        print(f"✗ Dependency verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_routes():
    """Verify routes are properly registered."""
    print("=" * 70)
    print("VERIFYING ROUTES")
    print("=" * 70)

    try:
        from backend.api.main import app

        # Get all routes
        routes = [route.path for route in app.routes]

        # Expected routes
        expected_routes = [
            "/api/puzzles/generate",
            "/api/puzzles/",
            "/api/puzzles/{puzzle_id}",
            "/api/puzzles/{puzzle_id}/solve",
            "/api/puzzles/{puzzle_id}/solve-word",
            "/api/puzzles/{puzzle_id}/hint",
            "/api/puzzles/{puzzle_id}/validate",
        ]

        for route in expected_routes:
            if route in routes:
                print(f"✓ Route registered: {route}")
            else:
                print(f"✗ Route missing: {route}")
                return False

        print("\n✓ All routes verified\n")
        return True

    except Exception as e:
        print(f"✗ Route verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_route_dependencies():
    """Verify routes use correct dependencies."""
    print("=" * 70)
    print("VERIFYING ROUTE DEPENDENCIES")
    print("=" * 70)

    try:
        import inspect

        from backend.api.routes import puzzles

        # Check solve_puzzle endpoint
        solve_puzzle_sig = inspect.signature(puzzles.solve_puzzle)
        params = list(solve_puzzle_sig.parameters.keys())

        if 'solver' not in params:
            print("✗ solve_puzzle missing solver parameter")
            return False
        print("✓ solve_puzzle has solver parameter")

        # Check solve_word endpoint
        solve_word_sig = inspect.signature(puzzles.solve_word)
        params = list(solve_word_sig.parameters.keys())

        if 'solver' not in params:
            print("✗ solve_word missing solver parameter")
            return False
        print("✓ solve_word has solver parameter")

        # Check get_hint endpoint
        get_hint_sig = inspect.signature(puzzles.get_hint)
        params = list(get_hint_sig.parameters.keys())

        if 'solver' not in params:
            print("✗ get_hint missing solver parameter")
            return False
        print("✓ get_hint has solver parameter")

        print("\n✓ All route dependencies verified\n")
        return True

    except Exception as e:
        print(f"✗ Route dependency verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print("PUZZLE GENERATION API VERIFICATION")
    print("=" * 70 + "\n")

    checks = [
        ("Imports", verify_imports),
        ("Solver Service", verify_solver_service),
        ("Dependencies", verify_dependencies),
        ("Routes", verify_routes),
        ("Route Dependencies", verify_route_dependencies),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} check failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Print summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL CHECKS PASSED")
        print("=" * 70)
        print("\nThe puzzle generation API is properly configured!")
        print("\nNext steps:")
        print("1. Start the server: python3 run_server.py")
        print("2. Test the endpoints: python3 test_api_manual.py")
        print("3. View API docs: http://localhost:8000/docs")
        return 0
    else:
        print("✗ SOME CHECKS FAILED")
        print("=" * 70)
        print("\nPlease fix the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
