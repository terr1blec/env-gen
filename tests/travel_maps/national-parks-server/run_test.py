#!/usr/bin/env python3
"""
Run the database generation test.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from test_database_generation import test_database_generation

if __name__ == "__main__":
    try:
        test_database_generation()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)