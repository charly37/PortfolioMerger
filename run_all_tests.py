#!/usr/bin/env python3
"""
Global test runner for PortfolioMerger
Runs all end-to-end tests in the Tests folder
"""

import subprocess
import os
import sys
from pathlib import Path

def find_test_files(tests_dir):
    """Find all test_e2e.py files in the Tests directory"""
    test_files = []
    tests_path = Path(tests_dir)
    
    if not tests_path.exists():
        print(f"Error: Tests directory '{tests_dir}' does not exist")
        return test_files
    
    # Search for test_e2e.py files recursively
    for test_file in tests_path.rglob('test_e2e.py'):
        test_files.append(test_file.resolve())
    
    return sorted(test_files)

def run_test(test_file, tests_base_dir):
    """Run a single test file and return True if it passes"""
    test_dir = test_file.parent
    test_name = test_dir.relative_to(tests_base_dir)
    
    print(f"\n{'='*70}")
    print(f"Running Test: {test_name}")
    print(f"Location: {test_file}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            ['python3', str(test_file)],
            cwd=str(test_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"✗ Test timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"✗ Error running test: {e}")
        return False

def main():
    """Main test runner"""
    print("\n" + "="*70)
    print("PortfolioMerger - Global Test Runner")
    print("="*70)
    
    # Find all test files
    tests_dir = './Tests'
    test_files = find_test_files(tests_dir)
    
    if not test_files:
        print(f"\n✗ No test files found in '{tests_dir}'")
        print("   Looking for: test_e2e.py")
        sys.exit(1)
    
    tests_base_path = Path(tests_dir).resolve()
    
    print(f"\nFound {len(test_files)} test(s):")
    for test_file in test_files:
        test_name = test_file.parent.relative_to(tests_base_path)
        print(f"  - {test_name}")
    
    # Run all tests
    results = {}
    for test_file in test_files:
        test_name = test_file.parent.relative_to(tests_base_path)
        success = run_test(test_file, tests_base_path)
        results[str(test_name)] = success
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for success in results.values() if success)
    failed = len(results) - passed
    
    for test_name, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {status:<12} {test_name}")
    
    print(f"\nTotal: {len(results)} test(s)")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    print("="*70)
    
    if failed > 0:
        print("✗ SOME TESTS FAILED")
        sys.exit(1)
    else:
        print("✓ ALL TESTS PASSED")
        sys.exit(0)

if __name__ == "__main__":
    main()
