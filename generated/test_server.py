#!/usr/bin/env python3
"""
Test script for Google Maps MCP Server
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from google_maps_server import (
    maps_geocode,
    maps_reverse_geocode,
    maps_search_places,
    maps_place_details,
    maps_distance_matrix,
    maps_elevation,
    maps_directions
)

def test_geocoding():
    """Test address geocoding functionality"""
    print("Testing maps_geocode...")
    result = maps_geocode("1600 Amphitheatre Parkway, Mountain View, CA")
    print(f"Geocoding result: {result}")
    assert "results" in result
    assert "status" in result
    print("✓ Geocoding test passed\n")

def test_reverse_geocoding():
    """Test reverse geocoding functionality"""
    print("Testing maps_reverse_geocode...")
    result = maps_reverse_geocode("37.7749", "-122.4194")
    print(f"Reverse geocoding result: {result}")
    assert "results" in result
    assert "status" in result
    print("✓ Reverse geocoding test passed\n")

def test_place_search():
    """Test place search functionality"""
    print("Testing maps_search_places...")
    result = maps_search_places("cafe")
    print(f"Place search result: {result}")
    assert "results" in result
    assert "status" in result
    print("✓ Place search test passed\n")

def test_place_details():
    """Test place details functionality"""
    print("Testing maps_place_details...")
    result = maps_place_details("mock_place_id_100000")
    print(f"Place details result: {result}")
    assert "result" in result
    assert "status" in result
    print("✓ Place details test passed\n")

def test_distance_matrix():
    """Test distance matrix functionality"""
    print("Testing maps_distance_matrix...")
    result = maps_distance_matrix("San Francisco, CA", "Los Angeles, CA")
    print(f"Distance matrix result: {result}")
    assert "rows" in result
    assert "status" in result
    print("✓ Distance matrix test passed\n")

def test_elevation():
    """Test elevation functionality"""
    print("Testing maps_elevation...")
    result = maps_elevation("37.7749,-122.4194")
    print(f"Elevation result: {result}")
    assert "results" in result
    assert "status" in result
    print("✓ Elevation test passed\n")

def test_directions():
    """Test directions functionality"""
    print("Testing maps_directions...")
    result = maps_directions("San Francisco, CA", "Los Angeles, CA")
    print(f"Directions result: {result}")
    assert "routes" in result
    assert "status" in result
    print("✓ Directions test passed\n")

def main():
    """Run all tests"""
    print("Running Google Maps MCP Server Tests...\n")
    
    try:
        test_geocoding()
        test_reverse_geocoding()
        test_place_search()
        test_place_details()
        test_distance_matrix()
        test_elevation()
        test_directions()
        
        print("🎉 All tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()