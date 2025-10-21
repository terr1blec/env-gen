#!/usr/bin/env python3
"""
Run Google Calendar Server Tests

This script runs the test suite for the Google Calendar MCP server.
"""

import subprocess
import sys
import os

def run_tests():
    """Run the Google Calendar server tests."""
    test_script = os.path.join(os.path.dirname(__file__), "test_google_calendar_server.py")
    
    try:
        print("Running Google Calendar MCP Server tests...")
        print("-" * 50)
        
        result = subprocess.run([sys.executable, test_script], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ Tests failed with return code: {result.returncode}")
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False
    
    return result.returncode == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)