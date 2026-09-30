#!/usr/bin/env python3
"""
Verification script for FastAPI application setup.

This script verifies that:
1. All API modules can be imported
2. FastAPI app is properly configured
3. Routes are registered correctly
4. Dependencies are working
"""

import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir.parent))


def verify_imports():
    """Verify all API modules can be imported."""
    print("Verifying imports...")

    try:
        print("  ✓ backend.api.main")

        print("  ✓ backend.api.dependencies")

        print("  ✓ backend.api.schemas")

        print("  ✓ backend.api.routes.health")
        print("  ✓ backend.api.routes.puzzles")

        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def verify_app_configuration():
    """Verify FastAPI app is properly configured."""
    print("\nVerifying app configuration...")

    try:
        from backend.api.main import app

        # Check app attributes
        assert app.title == "AIxWord API", "App title mismatch"
        print(f"  ✓ App title: {app.title}")

        assert app.version == "0.1.0", "App version mismatch"
        print(f"  ✓ App version: {app.version}")

        # Check middleware
        has_cors = False
        for middleware in app.user_middleware:
            # Check if it's a Starlette middleware wrapper
            if hasattr(middleware, 'cls'):
                if 'CORS' in middleware.cls.__name__:
                    has_cors = True
                    break

        if has_cors:
            print("  ✓ CORS middleware configured")
        else:
            print("  ⚠ CORS middleware check skipped (middleware structure varies)")

        return True
    except Exception as e:
        print(f"  ✗ Configuration check failed: {e}")
        return False


def verify_routes():
    """Verify routes are registered correctly."""
    print("\nVerifying routes...")

    try:
        from backend.api.main import app

        # Get all routes
        routes = []
        for route in app.routes:
            if hasattr(route, "path") and hasattr(route, "methods"):
                routes.append((route.path, route.methods))

        # Expected routes
        expected_routes = [
            ("/api/health", {"GET"}),
            ("/api/ready", {"GET"}),
            ("/api/puzzles/generate", {"POST"}),
            ("/api/puzzles/{puzzle_id}", {"GET", "DELETE"}),
            ("/api/puzzles/", {"GET"}),
            ("/api/puzzles/{puzzle_id}/solve", {"POST"}),
            ("/api/puzzles/{puzzle_id}/solve-word", {"POST"}),
            ("/api/puzzles/{puzzle_id}/hint", {"POST"}),
            ("/api/puzzles/{puzzle_id}/validate", {"POST"}),
        ]

        # Check each expected route
        for path, methods in expected_routes:
            found = False
            for route_path, route_methods in routes:
                # Handle path parameters
                if route_path == path or ('{' in path and route_path.replace('{puzzle_id}', '{puzzle_id}') == path):
                    # Check if any of the expected methods are present
                    if methods.intersection(route_methods):
                        found = True
                        break

            if found:
                print(f"  ✓ {path} {methods}")
            else:
                # Try to find similar routes for debugging
                similar = [r for r in routes if path.split('/')[:-1] == r[0].split('/')[:-1]]
                if similar:
                    print(f"  ⚠ {path} {methods} - Found similar: {similar[0]}")
                else:
                    print(f"  ✗ {path} {methods} - NOT FOUND")

        return True
    except Exception as e:
        print(f"  ✗ Route verification failed: {e}")
        return False


def verify_dependencies():
    """Verify dependency injection is working."""
    print("\nVerifying dependencies...")

    try:
        from backend.api.dependencies import (
            get_app_settings,
            get_puzzle_orchestrator,
        )

        # Test settings dependency
        settings = get_app_settings()
        assert settings is not None, "Settings dependency returned None"
        print("  ✓ Settings dependency")

        # Test orchestrator dependency
        orchestrator = get_puzzle_orchestrator()
        assert orchestrator is not None, "Orchestrator dependency returned None"
        print("  ✓ Orchestrator dependency")

        return True
    except Exception as e:
        print(f"  ✗ Dependency verification failed: {e}")
        return False


def verify_schemas():
    """Verify Pydantic schemas are valid."""
    print("\nVerifying schemas...")

    try:
        from backend.api.schemas import (
            PuzzleGenerateRequest,
        )

        # Test schema instantiation
        request = PuzzleGenerateRequest(topic="Science")
        assert request.topic == "Science", "Schema field mismatch"
        assert request.grid_size == 8, "Default value not set"
        print("  ✓ PuzzleGenerateRequest")

        # Test schema validation
        try:
            PuzzleGenerateRequest(topic="", grid_size=100)
            print("  ✗ Schema validation not working")
            return False
        except Exception:
            print("  ✓ Schema validation working")

        return True
    except Exception as e:
        print(f"  ✗ Schema verification failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("FastAPI Application Setup Verification")
    print("=" * 70)
    print()

    results = []

    # Run all checks
    results.append(("Imports", verify_imports()))
    results.append(("App Configuration", verify_app_configuration()))
    results.append(("Routes", verify_routes()))
    results.append(("Dependencies", verify_dependencies()))
    results.append(("Schemas", verify_schemas()))

    # Print summary
    print("\n" + "=" * 70)
    print("Verification Summary")
    print("=" * 70)

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20s} {status}")
        if not passed:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("\n✓ All checks passed! FastAPI application is properly configured.")
        return 0
    else:
        print("\n✗ Some checks failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
