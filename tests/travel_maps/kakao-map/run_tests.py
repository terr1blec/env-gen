#!/usr/bin/env python3
"""
Run all Kakao Map tests.
"""

import sys
import unittest
import os

# Add the generated module to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "generated", "travel_maps", "kakao-map"))

def run_all_tests():
    """Run all test suites."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("Running Kakao Map tests...")
    print("=" * 50)
    
    success = run_all_tests()
    
    print("=" * 50)
    if success:
        print("✅ All tests PASSED")
        sys.exit(0)
    else:
        print("❌ Some tests FAILED")
        sys.exit(1)