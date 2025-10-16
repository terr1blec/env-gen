"""
Tests for Google Maps MCP Server
"""

import sys
import os
import json

# Add the generated directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'generated'))

from generated.google_maps_server import (
    maps_geocode,
    maps_reverse_geocode,
    maps_search_places,
    maps_place_details,
    maps_distance_matrix,
    maps_elevation,
    maps_directions
)


def test_maps_geocode():
    """Test geocoding functionality."""
    result = maps_geocode("1600 Amphitheatre Parkway, Mountain View, CA")
    assert "latitude" in result
    assert "longitude" in result
    assert "formatted_address" in result
    assert result["status"] in ["OK", "ZERO_RESULTS"]
    print("✓ maps_geocode test passed")


def test_maps_reverse_geocode():
    """Test reverse geocoding functionality."""
    result = maps_reverse_geocode("37.4220656", "-122.0840897")
    assert "formatted_address" in result
    assert "status" in result
    print("✓ maps_reverse_geocode test passed")


def test_maps_search_places():
    """Test place search functionality."""
    result = maps_search_places("Googleplex")
    assert "results" in result
    assert "status" in result
    assert isinstance(result["results"], list)
    print("✓ maps_search_places test passed")


def test_maps_place_details():
    """Test place details functionality."""
    result = maps_place_details("ChIJN1t_tDeuEmsRUsoyG83frY4")
    assert "result" in result
    assert "status" in result
    assert isinstance(result["result"], dict)
    print("✓ maps_place_details test passed")


def test_maps_distance_matrix():
    """Test distance matrix functionality."""
    result = maps_distance_matrix()
    assert "rows" in result
    assert "status" in result
    assert isinstance(result["rows"], list)
    print("✓ maps_distance_matrix test passed")


def test_maps_elevation():
    """Test elevation functionality."""
    result = maps_elevation("37.4220656,-122.0840897|40.748817,-73.985428")
    assert "results" in result
    assert "status" in result
    assert isinstance(result["results"], list)
    print("✓ maps_elevation test passed")


def test_maps_directions():
    """Test directions functionality."""
    result = maps_directions("Googleplex, Mountain View", "San Francisco Airport")
    assert "routes" in result
    assert "status" in result
    assert isinstance(result["routes"], list)
    print("✓ maps_directions test passed")


def run_all_tests():
    """Run all tests."""
    print("Running Google Maps MCP Server Tests...")
    print("=" * 50)
    
    test_maps_geocode()
    test_maps_reverse_geocode()
    test_maps_search_places()
    test_maps_place_details()
    test_maps_distance_matrix()
    test_maps_elevation()
    test_maps_directions()
    
    print("=" * 50)
    print("All tests passed! ✓")


if __name__ == "__main__":
    run_all_tests()