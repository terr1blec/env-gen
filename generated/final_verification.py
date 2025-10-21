#!/usr/bin/env python3
"""
Final verification of Google Calendar MCP Server implementation
"""

import subprocess
import sys
import os

def run_validation():
    """Run the validation script."""
    validation_script = os.path.join(os.path.dirname(__file__), "validate_server.py")
    
    try:
        print("Running final validation...")
        print("-" * 50)
        
        result = subprocess.run([sys.executable, validation_script], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("✅ Final validation: PASSED")
            return True
        else:
            print("❌ Final validation: FAILED")
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False

def check_file_structure():
    """Verify that all required files exist."""
    print("\n📁 Checking file structure...")
    
    required_files = [
        "google_calendar_server.py",
        "google_calendar_dataset.py", 
        "google_calendar_dataset.json",
        "google_calendar_README.md",
        "test_google_calendar_server.py",
        "run_tests.py",
        "validate_server.py"
    ]
    
    all_exist = True
    for file in required_files:
        file_path = os.path.join(os.path.dirname(__file__), file)
        if os.path.exists(file_path):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (MISSING)")
            all_exist = False
    
    return all_exist

def main():
    """Run final verification."""
    print("🔍 Google Calendar MCP Server - Final Verification")
    print("=" * 60)
    
    # Check file structure
    structure_ok = check_file_structure()
    
    # Run validation
    validation_ok = run_validation()
    
    print("\n" + "=" * 60)
    
    if structure_ok and validation_ok:
        print("🎉 SUCCESS: Google Calendar MCP Server is fully implemented!")
        print("\n📋 Implementation Summary:")
        print("   ✅ FastMCP server module created")
        print("   ✅ All 5 required tools implemented")
        print("   ✅ Offline dataset integration")
        print("   ✅ Comprehensive error handling")
        print("   ✅ Test suite and validation scripts")
        print("   ✅ Documentation and README")
        print("\n🚀 Ready for use with MCP clients!")
        return True
    else:
        print("❌ Some issues were found. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)