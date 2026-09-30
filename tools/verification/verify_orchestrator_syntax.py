"""
Quick syntax verification for orchestrator module.

This script verifies that the orchestrator module has correct syntax
and can be imported without runtime errors (with mocked dependencies).
"""

import os
import sys

# Set dummy API key to avoid config errors
os.environ['OPENAI_API_KEY'] = 'sk-test-dummy-key-for-verification'

# Add parent directory to path for backend imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

print("=" * 60)
print("Orchestrator Syntax Verification")
print("=" * 60)

try:
    print("\n1. Importing orchestrator module...")
    from backend.agents.orchestrator import (
        PuzzleGenerationRequest,
        PuzzleGenerationResult,
        PuzzleOrchestrator,
        create_orchestrator,
        get_orchestrator,
    )
    print("   ✓ Import successful")

    print("\n2. Verifying PuzzleGenerationRequest...")
    request = PuzzleGenerationRequest(topic="Science")
    assert request.topic == "Science"
    assert request.grid_size == 8
    print("   ✓ PuzzleGenerationRequest works")

    print("\n3. Verifying PuzzleGenerationResult...")
    result = PuzzleGenerationResult(
        success=True,
        status="completed",
        word_count=10,
        fill_rate=0.75,
        iterations=15,
    )
    assert result.success is True
    assert result.word_count == 10
    print("   ✓ PuzzleGenerationResult works")

    print("\n4. Verifying PuzzleOrchestrator initialization...")
    # This will create default agents with LLM clients
    orchestrator = PuzzleOrchestrator()
    assert orchestrator is not None
    assert orchestrator.planner_agent is not None
    assert orchestrator.word_generator_agent is not None
    assert orchestrator.workflow is not None
    print("   ✓ PuzzleOrchestrator initialization works")

    print("\n5. Verifying singleton pattern...")
    orch1 = get_orchestrator()
    orch2 = get_orchestrator()
    assert orch1 is orch2
    print("   ✓ Singleton pattern works")

    print("\n6. Verifying create_orchestrator...")
    new_orch = create_orchestrator()
    assert new_orch is not None
    assert new_orch is not orch1  # Should be different instance
    print("   ✓ create_orchestrator works")

    print("\n7. Verifying request validation...")
    valid_request = PuzzleGenerationRequest(topic="Test", grid_size=8)
    is_valid, error = orchestrator.validate_request(valid_request)
    assert is_valid is True
    assert error is None
    print("   ✓ Request validation works")

    print("\n" + "=" * 60)
    print("✓ All syntax verification checks passed!")
    print("=" * 60)
    sys.exit(0)

except Exception as e:
    print(f"\n✗ Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
