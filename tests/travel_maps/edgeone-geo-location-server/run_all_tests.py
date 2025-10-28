#!/usr/bin/env python3
"""
Test runner for all EdgeOne Geo Location Server tests.

Runs all unit tests and integration tests for the complete system.
"""

import os
import sys
import unittest
import subprocess


def run_tests():
    """Run all tests and return results."""
    # Add the current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = current_dir
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


def run_database_generation_test():
    """Run database generation to verify it works correctly."""
    print("\n" + "="*60)
    print("RUNNING DATABASE GENERATION TEST")
    print("="*60)
    
    try:
        # Import and run database generation
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'travel_maps', 'edgeone-geo-location-server'))
        
        from edgeone_geo_location_server_database import generate_geolocation_database
        
        # Generate test database
        database = generate_geolocation_database(count=10, seed=42)
        
        # Basic validation
        assert 'geolocation_data' in database
        assert isinstance(database['geolocation_data'], list)
        assert len(database['geolocation_data']) == 10
        
        # Check geographic consistency
        for record in database['geolocation_data']:
            # Check required fields
            required_fields = ['ip', 'country', 'country_code', 'region', 'region_name', 
                             'city', 'zip', 'lat', 'lon', 'timezone', 'isp', 'org', 'as']
            for field in required_fields:
                assert field in record, f"Missing field: {field}"
            
            # Check geographic consistency
            country = record['country']
            city = record['city']
            region = record['region']
            
            if country == "United States":
                if city == "Houston":
                    assert region == "TX", "Houston should be in Texas"
                elif city == "Chicago":
                    assert region == "IL", "Chicago should be in Illinois"
            elif country == "United Kingdom":
                if city == "Glasgow":
                    assert region == "SCT", "Glasgow should be in Scotland"
        
        print("✅ Database generation test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Database generation test FAILED: {e}")
        return False


def run_server_functionality_test():
    """Run basic server functionality test."""
    print("\n" + "="*60)
    print("RUNNING SERVER FUNCTIONALITY TEST")
    print("="*60)
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'travel_maps', 'edgeone-geo-location-server'))
        
        from edgeone_geo_location_server_server import get_geolocation
        
        # Mock the database loading
        import edgeone_geo_location_server_server
        original_load = edgeone_geo_location_server_server.load_geolocation_database
        
        def mock_load():
            return [
                {
                    "ip": "192.168.1.1",
                    "country": "United States",
                    "country_code": "US",
                    "region": "CA",
                    "region_name": "CA State",
                    "city": "San Francisco",
                    "zip": "94102",
                    "lat": 37.7749,
                    "lon": -122.4194,
                    "timezone": "America/Los_Angeles",
                    "isp": "Comcast",
                    "org": "Comcast Cable",
                    "as": "AS7922"
                }
            ]
        
        edgeone_geo_location_server_server.load_geolocation_database = mock_load
        
        # Reset global state
        edgeone_geo_location_server_server.current_record_index = 0
        
        # Test the function
        result = get_geolocation()
        
        # Verify result structure
        required_fields = ['ip', 'country', 'country_code', 'region', 'region_name', 
                         'city', 'zip', 'lat', 'lon', 'timezone', 'isp', 'org', 'as']
        for field in required_fields:
            assert field in result, f"Missing field in result: {field}"
        
        # Restore original function
        edgeone_geo_location_server_server.load_geolocation_database = original_load
        
        print("✅ Server functionality test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Server functionality test FAILED: {e}")
        return False


def main():
    """Main test runner function."""
    print("EdgeOne Geo Location Server - Comprehensive Test Suite")
    print("="*60)
    
    # Run individual component tests
    db_test_passed = run_database_generation_test()
    server_test_passed = run_server_functionality_test()
    
    # Run all unit tests
    print("\n" + "="*60)
    print("RUNNING ALL UNIT TESTS")
    print("="*60)
    
    test_result = run_tests()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total_tests = test_result.testsRun
    failed_tests = len(test_result.failures) + len(test_result.errors)
    
    print(f"Database Generation Test: {'PASSED' if db_test_passed else 'FAILED'}")
    print(f"Server Functionality Test: {'PASSED' if server_test_passed else 'FAILED'}")
    print(f"Unit Tests Run: {total_tests}")
    print(f"Unit Tests Failed: {failed_tests}")
    
    if db_test_passed and server_test_passed and failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())