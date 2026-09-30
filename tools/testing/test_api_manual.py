#!/usr/bin/env python3
"""
Manual API test script.

This script performs a simple end-to-end test of the API without starting the server.
It uses FastAPI's TestClient to simulate HTTP requests.
"""

import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir.parent))


def test_api():
    """Test the API endpoints."""
    from fastapi.testclient import TestClient

    from backend.api.main import app

    print("=" * 70)
    print("Manual API Test")
    print("=" * 70)
    print()

    client = TestClient(app)

    # Test 1: Health check
    print("Test 1: Health check")
    response = client.get("/api/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "healthy", f"Expected healthy status, got {data['status']}"
    print(f"  ✓ Health check passed: {data['status']}")
    print()

    # Test 2: Ready check
    print("Test 2: Ready check")
    response = client.get("/api/ready")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "ready", f"Expected ready status, got {data['status']}"
    print(f"  ✓ Ready check passed: {data['status']}")
    print()

    # Test 3: List puzzles (should be empty)
    print("Test 3: List puzzles (empty)")
    response = client.get("/api/puzzles/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    print(f"  ✓ List puzzles passed: {len(data)} puzzles")
    print()

    # Test 4: Get non-existent puzzle (should 404)
    print("Test 4: Get non-existent puzzle")
    response = client.get("/api/puzzles/non-existent-id")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    print("  ✓ 404 for non-existent puzzle")
    print()

    # Test 5: Validate request schema
    print("Test 5: Validate request schema")
    from backend.api.schemas import PuzzleGenerateRequest

    request = PuzzleGenerateRequest(topic="Science")
    assert request.topic == "Science"
    assert request.grid_size == 8
    assert request.difficulty == "medium"
    print("  ✓ Request schema validation passed")
    print()

    # Test 6: Invalid request (empty topic)
    print("Test 6: Invalid request validation")
    try:
        PuzzleGenerateRequest(topic="")
        print("  ✗ Should have raised validation error")
        return False
    except Exception:
        print("  ✓ Validation error raised for empty topic")
    print()

    print("=" * 70)
    print("✓ All manual tests passed!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    try:
        success = test_api()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
