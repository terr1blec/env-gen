"""
Test script for SNCF API Server
"""

import sys
import os

# Add the server module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "generated", "travel_maps", "sncf-api-server"))

from sncf_api_server_server import (
    plan_journey_by_city_names,
    check_disruptions,
    get_station_schedule,
    get_station_details
)

def test_plan_journey():
    """Test journey planning functionality"""
    print("Testing plan_journey_by_city_names...")
    result = plan_journey_by_city_names("Paris", "Lille")
    print(f"Found {len(result['journeys'])} journeys from Paris to Lille")
    
    # Test with date filter
    result_with_date = plan_journey_by_city_names("Paris", "Lille", "2024-01-15")
    print(f"Found {len(result_with_date['journeys'])} journeys on 2024-01-15")
    
    return len(result['journeys']) > 0

def test_check_disruptions():
    """Test disruption checking functionality"""
    print("\nTesting check_disruptions...")
    result = check_disruptions()
    print(f"Found {len(result['disruptions'])} total disruptions")
    
    # Test with station filter
    result_with_station = check_disruptions(station="station_001")
    print(f"Found {len(result_with_station['disruptions'])} disruptions affecting station_001")
    
    return len(result['disruptions']) > 0

def test_get_station_schedule():
    """Test station schedule functionality"""
    print("\nTesting get_station_schedule...")
    result = get_station_schedule("station_001")
    print(f"Found schedule for station {result['station_id']}")
    print(f"Departures: {len(result['departures'])}")
    print(f"Arrivals: {len(result['arrivals'])}")
    
    return result['station_id'] == "station_001"

def test_get_station_details():
    """Test station details functionality"""
    print("\nTesting get_station_details...")
    
    # Test existing station
    result = get_station_details("station_001")
    print(f"Found station: {result['name']} in {result['city']}")
    
    # Test non-existent station
    result_not_found = get_station_details("station_999")
    print(f"Non-existent station result: {result_not_found.get('error', 'No error')}")
    
    return result['id'] == "station_001" and 'error' in result_not_found

def main():
    """Run all tests"""
    print("Running SNCF API Server tests...\n")
    
    tests = [
        test_plan_journey,
        test_check_disruptions,
        test_get_station_schedule,
        test_get_station_details
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✓ Test passed")
            else:
                print("✗ Test failed")
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())