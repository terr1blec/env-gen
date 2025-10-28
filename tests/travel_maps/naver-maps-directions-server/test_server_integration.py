"""
Integration test for Naver Maps Directions Server

Tests that verify the server module structure and basic functionality.
"""

import json
import pytest
from pathlib import Path

# Paths to test files
SERVER_PATH = Path(__file__).parent.parent.parent.parent / 'generated' / 'travel_maps' / 'naver-maps-directions-server' / 'naver_maps_directions_server_server.py'


class TestServerModule:
    """Test server module structure"""
    
    def test_server_file_exists(self):
        """Test that server file exists"""
        assert SERVER_PATH.exists(), f"Server file not found at {SERVER_PATH}"
    
    def test_server_file_content(self):
        """Test that server file contains expected content"""
        with open(SERVER_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key components
        assert "FastMCP" in content, "Server should use FastMCP"
        assert "naver_directions" in content, "Server should contain naver_directions function"
        assert "naver_geocode" in content, "Server should contain naver_geocode function"
        assert "naver_reverse_geocode" in content, "Server should contain naver_reverse_geocode function"
        assert "naver_static_map" in content, "Server should contain naver_static_map function"
        assert "@mcp.tool()" in content, "Server should use mcp.tool decorator"
        assert "load_database" in content, "Server should have load_database function"
    
    def test_server_database_path(self):
        """Test that server references correct database path"""
        with open(SERVER_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that database path is correctly referenced
        assert "naver_maps_directions_server_database.json" in content, "Server should reference correct database file"


class TestServerFunctionality:
    """Test server functionality through simulation"""
    
    def test_simulated_directions(self):
        """Test directions functionality simulation"""
        # This simulates what the server would do
        database_path = Path(__file__).parent.parent.parent.parent / 'generated' / 'travel_maps' / 'naver-maps-directions-server' / 'naver_maps_directions_server_database.json'
        
        with open(database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        # Simulate directions lookup
        start = "Gangnam Station"
        goal = "Myeongdong"
        
        found_route = None
        for direction in database["directions"]:
            if (direction.get("start", "").lower() in start.lower() or 
                start.lower() in direction.get("start", "").lower()) and \
               (direction.get("goal", "").lower() in goal.lower() or 
                goal.lower() in direction.get("goal", "").lower()):
                found_route = direction
                break
        
        assert found_route is not None, "Should find a route"
        assert found_route["start"] == "Gangnam Station", "Route should start from Gangnam Station"
        assert found_route["goal"] == "Myeongdong", "Route should go to Myeongdong"
    
    def test_simulated_geocode(self):
        """Test geocoding functionality simulation"""
        database_path = Path(__file__).parent.parent.parent.parent / 'generated' / 'travel_maps' / 'naver-maps-directions-server' / 'naver_maps_directions_server_database.json'
        
        with open(database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        # Simulate geocoding
        address = "서울특별시 강남구 강남대로 396"
        
        found_geocode = None
        for geocode in database["geocoding"]:
            if address.lower() in geocode.get("address", "").lower():
                found_geocode = geocode
                break
        
        assert found_geocode is not None, "Should find geocode"
        assert found_geocode["address"] == "서울특별시 강남구 강남대로 396", "Address should match"
        assert "37.4979" in found_geocode["coordinates"]["lat"], "Latitude should be correct"
        assert "127.0276" in found_geocode["coordinates"]["lng"], "Longitude should be correct"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])