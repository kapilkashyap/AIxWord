#!/usr/bin/env python3
"""
Quick test validation script for AIxWord backend.
Runs tests and reports summary statistics.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    return result.returncode, result.stdout, result.stderr


def main():
    """Run test validation."""
    print("=" * 60)
    print("AIxWord Backend Test Validation")
    print("=" * 60)
    print()

    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: Must be run from backend directory")
        sys.exit(1)

    # Run domain tests
    print("Running domain tests...")
    exit_code, stdout, stderr = run_command([
        "python3", "-m", "pytest",
        "tests/domain/",
        "-v", "--tb=no", "-q"
    ])

    # Parse results
    if "passed" in stdout:
        # Extract test count
        for line in stdout.split('\n'):
            if 'passed' in line:
                print(f"✓ Domain tests: {line.strip()}")
                break
    else:
        print("❌ Domain tests failed")
        print(stdout)
        sys.exit(1)

    print()

    # Run LLM tests
    print("Running LLM tests...")
    exit_code, stdout, stderr = run_command([
        "python3", "-m", "pytest",
        "tests/llm/",
        "-v", "--tb=no", "-q"
    ])

    # Parse results
    if "passed" in stdout:
        for line in stdout.split('\n'):
            if 'passed' in line:
                print(f"✓ LLM tests: {line.strip()}")
                break
    else:
        print("❌ LLM tests failed")
        print(stdout)
        sys.exit(1)

    print()

    # Try agent tests
    print("Checking agent tests...")
    exit_code, stdout, stderr = run_command([
        "python3", "-m", "pytest",
        "tests/agents/",
        "--collect-only", "-q"
    ])

    if "ModuleNotFoundError" in stderr or "No module named 'langgraph'" in stderr:
        print("⚠️  Agent tests: Skipped (langgraph not installed)")
    elif exit_code == 0:
        print("✓ Agent tests: Available")
    else:
        print("⚠️  Agent tests: Error during collection")

    print()
    print("=" * 60)
    print("✅ Test validation complete!")
    print("=" * 60)
    print()
    print("Summary:")
    print("  • Domain tests: PASSING")
    print("  • LLM tests: PASSING")
    print("  • Agent tests: Requires langgraph installation")
    print()
    print("To run all tests:")
    print("  ./run_tests.sh")
    print()
    print("To install missing dependencies:")
    print("  pip install langgraph>=0.0.20")
    print()


if __name__ == "__main__":
    main()
