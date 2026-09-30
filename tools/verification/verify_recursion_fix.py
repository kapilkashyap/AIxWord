#!/usr/bin/env python3
"""
Verification script for recursion limit fix.

This script verifies that the dynamic recursion limit calculation
is working correctly in the workflow.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))


def test_recursion_limit_calculation():
    """Test the recursion limit calculation logic."""
    print("Testing recursion limit calculation...")
    print("=" * 60)
    
    test_cases = [
        (1, 100, "Minimum enforced"),
        (10, 100, "Minimum enforced"),
        (25, 120, "Default UI value"),
        (50, 240, "Default UI value"),
        (75, 360, "High value"),
        (100, 480, "Maximum UI value"),
    ]
    
    all_passed = True
    
    for max_iter, expected_limit, description in test_cases:
        # This is the same calculation used in workflow.py
        calculated_limit = max(100, int(max_iter * 4 * 1.2))
        
        status = "✅ PASS" if calculated_limit == expected_limit else "❌ FAIL"
        if calculated_limit != expected_limit:
            all_passed = False
            
        print(
            f"{status} | max_iterations={max_iter:3d} → "
            f"recursion_limit={calculated_limit:3d} "
            f"(expected: {expected_limit:3d}) | {description}"
        )
    
    print("=" * 60)
    
    if all_passed:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


def verify_workflow_code():
    """Verify that the workflow.py file has the dynamic calculation."""
    print("\nVerifying workflow.py implementation...")
    print("=" * 60)
    
    workflow_file = backend_dir / "agents" / "workflow.py"
    
    if not workflow_file.exists():
        print(f"❌ FAIL: {workflow_file} not found")
        return 1
    
    content = workflow_file.read_text()
    
    # Check for the dynamic calculation
    checks = [
        ("recursion_limit = max(100, int(max_iterations * 4 * 1.2))", 
         "Dynamic calculation present"),
        ("config={\"recursion_limit\": recursion_limit}", 
         "Using calculated recursion_limit"),
        ("max_iterations={max_iterations}", 
         "Logging max_iterations"),
        ("calculated recursion_limit={recursion_limit}", 
         "Logging calculated recursion_limit"),
    ]
    
    all_passed = True
    
    for check_string, description in checks:
        if check_string in content:
            print(f"✅ PASS | {description}")
        else:
            print(f"❌ FAIL | {description} - NOT FOUND")
            all_passed = False
    
    # Check that hardcoded 100 is NOT present
    if 'config={"recursion_limit": 100}' in content:
        print("❌ FAIL | Hardcoded recursion_limit=100 still present!")
        all_passed = False
    else:
        print("✅ PASS | Hardcoded recursion_limit=100 removed")
    
    print("=" * 60)
    
    if all_passed:
        print("✅ Workflow implementation verified!")
        return 0
    else:
        print("❌ Workflow implementation has issues!")
        return 1


def main():
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("RECURSION LIMIT FIX VERIFICATION")
    print("=" * 60 + "\n")
    
    # Run calculation tests
    calc_result = test_recursion_limit_calculation()
    
    # Verify workflow code
    code_result = verify_workflow_code()
    
    # Overall result
    print("\n" + "=" * 60)
    if calc_result == 0 and code_result == 0:
        print("✅ ALL VERIFICATIONS PASSED!")
        print("=" * 60)
        print("\nThe recursion limit fix is correctly implemented.")
        print("\nNext steps:")
        print("1. Restart the backend server:")
        print("   cd backend && source venv/bin/activate && uvicorn main:app --reload")
        print("2. Try generating a puzzle with different max_iterations values")
        print("3. Check the logs for: 'calculated recursion_limit=...'")
        return 0
    else:
        print("❌ SOME VERIFICATIONS FAILED!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
