#!/usr/bin/env python3
"""
AIxWord - Automated Test Verification Script

This script runs all tests and verifies the application is working correctly.
It provides detailed output and exit codes for CI/CD integration.
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, Tuple, List


class Colors:
    """ANSI color codes for terminal output."""
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")


def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}✓{Colors.NC} {text}")


def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}✗{Colors.NC} {text}")


def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.NC} {text}")


def print_info(text: str) -> None:
    """Print an info message."""
    print(f"{Colors.BLUE}ℹ{Colors.NC} {text}")


def run_command(cmd: List[str], cwd: Path = None) -> Tuple[int, str, str]:
    """
    Run a shell command and return exit code, stdout, and stderr.
    
    Args:
        cmd: Command to run as list of strings
        cwd: Working directory for command
        
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out after 5 minutes"
    except Exception as e:
        return 1, "", str(e)


def check_backend_tests() -> Dict[str, any]:
    """
    Run backend tests and return results.
    
    Returns:
        Dictionary with test results
    """
    print_header("Backend Tests (pytest)")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print_error("Backend directory not found")
        return {"success": False, "passed": 0, "failed": 0, "skipped": 0}
    
    # Check if virtual environment exists
    venv_dir = backend_dir / "venv"
    if not venv_dir.exists():
        print_warning("Virtual environment not found. Using system Python.")
    
    print_info("Running backend test suite...")
    
    # Run pytest (will use system Python if venv not found)
    cmd = ["python3", "-m", "pytest", "tests/", "-v", "--tb=short", "--no-cov", "-q"]
    exit_code, stdout, stderr = run_command(cmd, cwd=backend_dir)
    
    # Parse results
    passed = 0
    failed = 0
    skipped = 0
    
    for line in stdout.split('\n'):
        if ' passed' in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == 'passed':
                    try:
                        passed = int(parts[i-1])
                    except (ValueError, IndexError):
                        pass
        if ' failed' in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == 'failed':
                    try:
                        failed = int(parts[i-1])
                    except (ValueError, IndexError):
                        pass
        if ' skipped' in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == 'skipped':
                    try:
                        skipped = int(parts[i-1])
                    except (ValueError, IndexError):
                        pass
    
    # Print results
    print(f"\nBackend Test Results:")
    print(f"  Passed:  {Colors.GREEN}{passed}{Colors.NC}")
    if failed > 0:
        print(f"  Failed:  {Colors.RED}{failed}{Colors.NC}")
    else:
        print(f"  Failed:  {failed}")
    if skipped > 0:
        print(f"  Skipped: {Colors.YELLOW}{skipped}{Colors.NC}")
    
    success = exit_code == 0 and failed == 0
    if success:
        print_success("Backend tests PASSED")
    else:
        print_error("Backend tests FAILED")
    
    return {
        "success": success,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "exit_code": exit_code
    }


def check_frontend_tests() -> Dict[str, any]:
    """
    Run frontend tests and return results.
    
    Returns:
        Dictionary with test results
    """
    print_header("Frontend Tests (vitest)")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print_error("Frontend directory not found")
        return {"success": False, "passed": 0, "failed": 0, "skipped": 0}
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print_warning("Node modules not found. Run 'npm install' first.")
        return {"success": False, "passed": 0, "failed": 0, "skipped": 0}
    
    print_info("Running frontend test suite...")
    
    # Run vitest
    cmd = ["npm", "test", "--", "--run"]
    exit_code, stdout, stderr = run_command(cmd, cwd=frontend_dir)
    
    # Parse results
    passed = 0
    failed = 0
    skipped = 0
    
    for line in stdout.split('\n'):
        if ' passed' in line and 'Tests' in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == 'passed':
                    try:
                        passed = int(parts[i-1])
                    except (ValueError, IndexError):
                        pass
        if ' failed' in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == 'failed':
                    try:
                        failed = int(parts[i-1])
                    except (ValueError, IndexError):
                        pass
        if ' skipped' in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == 'skipped':
                    try:
                        skipped = int(parts[i-1])
                    except (ValueError, IndexError):
                        pass
    
    # Print results
    print(f"\nFrontend Test Results:")
    print(f"  Passed:  {Colors.GREEN}{passed}{Colors.NC}")
    if failed > 0:
        print(f"  Failed:  {Colors.RED}{failed}{Colors.NC}")
    else:
        print(f"  Failed:  {failed}")
    if skipped > 0:
        print(f"  Skipped: {Colors.YELLOW}{skipped}{Colors.NC}")
    
    success = exit_code == 0 and failed == 0
    if success:
        print_success("Frontend tests PASSED")
    else:
        print_error("Frontend tests FAILED")
    
    return {
        "success": success,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "exit_code": exit_code
    }


def check_project_structure() -> bool:
    """
    Verify project structure is correct.
    
    Returns:
        True if structure is valid, False otherwise
    """
    print_header("Project Structure Verification")
    
    required_dirs = [
        "backend",
        "backend/domain",
        "backend/agents",
        "backend/api",
        "backend/tests",
        "frontend",
        "frontend/src",
        "frontend/src/components",
        "frontend/src/hooks",
        "docs"
    ]
    
    required_files = [
        "README.md",
        "backend/main.py",
        "backend/pyproject.toml",
        "frontend/package.json",
        "frontend/vite.config.ts"
    ]
    
    all_valid = True
    
    # Check directories
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print_success(f"Directory exists: {dir_path}")
        else:
            print_error(f"Directory missing: {dir_path}")
            all_valid = False
    
    # Check files
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"File exists: {file_path}")
        else:
            print_error(f"File missing: {file_path}")
            all_valid = False
    
    return all_valid


def main() -> int:
    """
    Main verification function.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print(f"{Colors.BLUE}")
    print("""
   ___    ____     _       __               __
  /   |  /  _/  __| |     / /___  _________/ /
 / /| |  / /   / /| | /| / / __ \/ ___/ __  / 
/ ___ |_/ /   / /_| |/ |/ / /_/ / /  / /_/ /  
/_/  |_/___/  \____|__/|__/\____/_/   \__,_/   
                                                
    Automated Test Verification
    """)
    print(f"{Colors.NC}")
    
    print_info("Starting comprehensive test verification...")
    print_info("This will verify project structure and run all tests\n")
    
    # Check project structure
    structure_valid = check_project_structure()
    
    if not structure_valid:
        print_error("\nProject structure is invalid. Please fix the issues above.")
        return 1
    
    # Run backend tests
    backend_results = check_backend_tests()
    
    # Run frontend tests
    frontend_results = check_frontend_tests()
    
    # Print summary
    print_header("Overall Summary")
    
    total_passed = backend_results["passed"] + frontend_results["passed"]
    total_failed = backend_results["failed"] + frontend_results["failed"]
    total_skipped = backend_results["skipped"] + frontend_results["skipped"]
    total_tests = total_passed + total_failed + total_skipped
    
    print(f"Total Tests:  {total_tests}")
    print(f"Passed:       {Colors.GREEN}{total_passed}{Colors.NC}")
    if total_failed > 0:
        print(f"Failed:       {Colors.RED}{total_failed}{Colors.NC}")
    else:
        print(f"Failed:       {total_failed}")
    if total_skipped > 0:
        print(f"Skipped:      {Colors.YELLOW}{total_skipped}{Colors.NC}")
    
    if total_tests > 0:
        success_rate = (total_passed * 100) // total_tests
        print(f"\nSuccess Rate: {Colors.BLUE}{success_rate}%{Colors.NC}")
    
    # Final verdict
    print_header("Final Verdict")
    
    all_passed = backend_results["success"] and frontend_results["success"]
    
    if all_passed:
        print(f"{Colors.GREEN}✓ ALL TESTS PASSED!{Colors.NC}")
        print(f"{Colors.GREEN}  The application is fully tested and ready for use.{Colors.NC}\n")
        print_info("Next steps:")
        print("  1. Start the backend: cd backend && python run_server.py")
        print("  2. Start the frontend: cd frontend && npm run dev")
        print("  3. Open http://localhost:5173 in your browser\n")
        return 0
    else:
        print(f"{Colors.RED}✗ TESTS FAILED{Colors.NC}")
        print(f"{Colors.RED}  {total_failed} test(s) failed. Please review the output above.{Colors.NC}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
