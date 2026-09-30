#!/usr/bin/env python3
"""
Verification script to check if the backend setup is complete.

This script verifies:
- Directory structure
- Required files exist
- Python files can be imported
- Configuration can be loaded (with dummy values)
"""

import sys
from pathlib import Path


def check_directory_structure():
    """Check if all required directories exist."""
    print("Checking directory structure...")
    required_dirs = [
        "domain",
        "agents",
        "llm",
        "api",
        "tests",
        "tests/domain",
        "tests/agents",
        "tests/llm",
        "tests/api",
    ]

    missing_dirs = []
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists() or not dir_path.is_dir():
            missing_dirs.append(dir_name)
        else:
            print(f"  ✓ {dir_name}/")

    if missing_dirs:
        print(f"\n❌ Missing directories: {', '.join(missing_dirs)}")
        return False

    print("✅ All directories exist\n")
    return True


def check_required_files():
    """Check if all required configuration files exist."""
    print("Checking required files...")
    required_files = [
        "pyproject.toml",
        ".env.example",
        ".python-version",
        "pytest.ini",
        ".gitignore",
        "mypy.ini",
        "config.py",
        "__init__.py",
        "requirements-dev.txt",
    ]

    missing_files = []
    for file_name in required_files:
        file_path = Path(file_name)
        if not file_path.exists() or not file_path.is_file():
            missing_files.append(file_name)
        else:
            print(f"  ✓ {file_name}")

    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False

    print("✅ All required files exist\n")
    return True


def check_python_imports():
    """Check if Python modules can be imported."""
    print("Checking Python imports...")

    # Add parent directory to path to allow imports
    sys.path.insert(0, str(Path(__file__).parent.parent))

    try:
        # Try importing the main package
        import backend
        print(f"  ✓ backend package (version {backend.__version__})")

        # Check if config can be imported (will fail if pydantic not installed)
        try:
            from backend.config import Settings  # noqa: F401
            print("  ✓ backend.config.Settings")
        except ImportError as e:
            print(f"  ⚠️  backend.config.Settings (dependencies not installed: {e})")

        print("✅ Python imports successful\n")
        return True

    except ImportError as e:
        print(f"❌ Failed to import backend package: {e}\n")
        return False


def check_env_example():
    """Check if .env.example has required variables."""
    print("Checking .env.example...")

    required_vars = [
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "GRID_SIZE",
        "MAX_ITERATIONS",
        "MIN_FILL_RATE",
    ]

    env_example = Path(".env.example")
    if not env_example.exists():
        print("❌ .env.example not found\n")
        return False

    content = env_example.read_text()
    missing_vars = []

    for var in required_vars:
        if var not in content:
            missing_vars.append(var)
        else:
            print(f"  ✓ {var}")

    if missing_vars:
        print(f"\n❌ Missing variables in .env.example: {', '.join(missing_vars)}")
        return False

    print("✅ .env.example is complete\n")
    return True


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("AIxWord Backend Setup Verification")
    print("=" * 60)
    print()

    checks = [
        ("Directory Structure", check_directory_structure),
        ("Required Files", check_required_files),
        ("Python Imports", check_python_imports),
        ("Environment Configuration", check_env_example),
    ]

    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}\n")
            results.append((check_name, False))

    print("=" * 60)
    print("Summary")
    print("=" * 60)

    all_passed = True
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check_name}")
        if not result:
            all_passed = False

    print()
    if all_passed:
        print("🎉 All checks passed! Backend setup is complete.")
        print()
        print("Next steps:")
        print("1. Create a virtual environment: python3 -m venv venv")
        print("2. Activate it: source venv/bin/activate")
        print("3. Install dependencies: pip install -e .")
        print("4. Copy .env.example to .env and add your OPENAI_API_KEY")
        return 0
    else:
        print("⚠️  Some checks failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
