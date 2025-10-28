"""
Automated Validation Runner for 12306 MCP Server

This script runs all validation checks and provides a comprehensive report.
"""

import subprocess
import sys
import os


def run_validation_script():
    """Run the main validation script"""
    print("Running comprehensive validation...")
    
    validation_script = os.path.join(os.path.dirname(__file__), "validation_check.py")
    
    try:
        result = subprocess.run([sys.executable, validation_script], 
                              capture_output=True, text=True, timeout=30)
        
        print("Validation output:")
        print("-" * 60)
        print(result.stdout)
        
        if result.stderr:
            print("Validation errors:")
            print("-" * 60)
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Validation timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        return False


def run_server_tests():
    """Run server unit tests"""
    print("\nRunning server unit tests...")
    
    test_script = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "tests", "travel_maps", "12306-mcp-server", "test_server.py"
    )
    
    try:
        result = subprocess.run([sys.executable, "-m", "unittest", test_script], 
                              capture_output=True, text=True, timeout=30)
        
        print("Server test output:")
        print("-" * 60)
        print(result.stdout)
        
        if result.stderr:
            print("Server test errors:")
            print("-" * 60)
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Server tests timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Server tests failed with error: {e}")
        return False


def run_dataset_tests():
    """Run dataset unit tests"""
    print("\nRunning dataset unit tests...")
    
    test_script = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "tests", "travel_maps", "12306-mcp-server", "test_dataset.py"
    )
    
    try:
        result = subprocess.run([sys.executable, "-m", "unittest", test_script], 
                              capture_output=True, text=True, timeout=30)
        
        print("Dataset test output:")
        print("-" * 60)
        print(result.stdout)
        
        if result.stderr:
            print("Dataset test errors:")
            print("-" * 60)
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Dataset tests timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Dataset tests failed with error: {e}")
        return False


def run_server_usage_example():
    """Run server usage examples"""
    print("\nRunning server usage examples...")
    
    usage_script = os.path.join(os.path.dirname(__file__), "server_usage_example.py")
    
    try:
        result = subprocess.run([sys.executable, usage_script], 
                              capture_output=True, text=True, timeout=30)
        
        print("Server usage output:")
        print("-" * 60)
        print(result.stdout)
        
        if result.stderr:
            print("Server usage errors:")
            print("-" * 60)
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Server usage examples timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Server usage examples failed with error: {e}")
        return False


def check_file_existence():
    """Check that all required files exist"""
    print("\nChecking required files...")
    
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..")
    required_files = [
        "generated/travel_maps/12306-mcp-server/12306_mcp_server_server.py",
        "generated/travel_maps/12306-mcp-server/12306_mcp_server_dataset.py",
        "generated/travel_maps/12306-mcp-server/12306_mcp_server_dataset.json",
        "generated/travel_maps/12306-mcp-server/12306_mcp_server_metadata.json",
        "tests/travel_maps/12306-mcp-server/test_server.py",
        "tests/travel_maps/12306-mcp-server/test_dataset.py",
        "transcripts/travel_maps/12306-mcp-server/server_usage_example.py",
        "transcripts/travel_maps/12306-mcp-server/validation_check.py",
        "transcripts/travel_maps/12306-mcp-server/run_validation.py"
    ]
    
    all_exist = True
    for relative_path in required_files:
        full_path = os.path.join(base_dir, relative_path)
        if os.path.exists(full_path):
            print(f"✓ {relative_path}")
        else:
            print(f"✗ {relative_path} (MISSING)")
            all_exist = False
    
    return all_exist


def main():
    """Run all validation and testing"""
    print("=" * 70)
    print("12306 MCP Server - Automated Validation Runner")
    print("=" * 70)
    
    results = []
    
    # Run all checks
    results.append(("File Existence", check_file_existence()))
    results.append(("Comprehensive Validation", run_validation_script()))
    results.append(("Server Unit Tests", run_server_tests()))
    results.append(("Dataset Unit Tests", run_dataset_tests()))
    results.append(("Server Usage Examples", run_server_usage_example()))
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION RUNNER SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:30} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL VALIDATIONS AND TESTS PASSED!")
        print("The 12306 MCP Server is fully implemented and compliant.")
    else:
        print("❌ SOME VALIDATIONS OR TESTS FAILED!")
        print("Please review the failed checks above.")
    print("=" * 70)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)