"""
Test suite for Naver Maps Directions Server

Validates that the FastMCP server can load the offline database and satisfy schema behaviors.
Tests the DATA CONTRACT keys and ensures metadata JSON aligns with the server's public API.
"""

import json
import os
import sys
import pytest
from pathlib import Path

# Paths to test files
DATABASE_PATH = Path(__file__).parent.parent.parent.parent / 'generated' / 'travel_maps' / 'naver-maps-directions-server' / 'naver_maps_directions_server_database.json'
METADATA_PATH = Path(__file__).parent.parent.parent.parent / 'generated' / 'travel_maps' / 'naver-maps-directions-server' / 'naver_maps_directions_server_metadata.json'


def load_database():
    """Load the database from JSON file with fallback to empty structure."""
    try:
        with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load database from {DATABASE_PATH}: {e}")
        # Return empty structure matching DATA CONTRACT
        return {
            "directions": [],
            "geocoding": [],
            "reverse_geocoding": [],
            "static_maps": []
        }


class TestDatabaseLoading:
    """Test database loading functionality"""
    
    def test_load_database_exists(self):
        """Test that database file exists and can be loaded"""
        assert DATABASE_PATH.exists(), f"Database file not found at {DATABASE_PATH}"
        
        database = load_database()
        assert isinstance(database, dict), "Database should be a dictionary"
        
        # Check DATA CONTRACT keys
        required_keys = ["directions", "geocoding", "reverse_geocoding", "static_maps"]
        for key in required_keys:
            assert key in database, f"Missing required key in database: {key}"
            assert isinstance(database[key], list), f"Database key {key} should be a list"
    
    def test_database_content_structure(self):
        """Test that database content follows expected structure"""
        database = load_database()
        
        # Test directions structure
        for direction in database["directions"]:
            assert "id" in direction, "Direction missing 'id' field"
            assert "start" in direction, "Direction missing 'start' field"
            assert "goal" in direction, "Direction missing 'goal' field"
            assert "route_info" in direction, "Direction missing 'route_info' field"
            
            route_info = direction["route_info"]
            assert "distance" in route_info, "Route info missing 'distance' field"
            assert "duration" in route_info, "Route info missing 'duration' field"
            assert "steps" in route_info, "Route info missing 'steps' field"
        
        # Test geocoding structure
        for geocode in database["geocoding"]:
            assert "id" in geocode, "Geocode missing 'id' field"
            assert "address" in geocode, "Geocode missing 'address' field"
            assert "coordinates" in geocode, "Geocode missing 'coordinates' field"
            
            coordinates = geocode["coordinates"]
            assert "lat" in coordinates, "Coordinates missing 'lat' field"
            assert "lng" in coordinates, "Coordinates missing 'lng' field"
        
        # Test reverse geocoding structure
        for reverse_geocode in database["reverse_geocoding"]:
            assert "id" in reverse_geocode, "Reverse geocode missing 'id' field"
            assert "lat" in reverse_geocode, "Reverse geocode missing 'lat' field"
            assert "lng" in reverse_geocode, "Reverse geocode missing 'lng' field"
            assert "address" in reverse_geocode, "Reverse geocode missing 'address' field"
        
        # Test static maps structure
        for static_map in database["static_maps"]:
            assert "id" in static_map, "Static map missing 'id' field"
            assert "center" in static_map, "Static map missing 'center' field"
            assert "image_data" in static_map, "Static map missing 'image_data' field"
    
    def test_database_has_records(self):
        """Test that database has actual records"""
        database = load_database()
        
        assert len(database["directions"]) > 0, "Directions should have records"
        assert len(database["geocoding"]) > 0, "Geocoding should have records"
        assert len(database["reverse_geocoding"]) > 0, "Reverse geocoding should have records"
        assert len(database["static_maps"]) > 0, "Static maps should have records"


class TestServerLogic:
    """Test server logic by simulating function behavior"""
    
    def test_directions_logic(self):
        """Test directions lookup logic"""
        database = load_database()
        
        # Test finding a route
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
        
        assert found_route is not None, "Should find a route for Gangnam Station to Myeongdong"
        assert "route_info" in found_route, "Found route should have route_info"
    
    def test_geocode_logic(self):
        """Test geocoding logic"""
        database = load_database()
        
        # Test finding an address
        address = "서울특별시 강남구 강남대로 396"
        
        found_geocode = None
        for geocode in database["geocoding"]:
            if address.lower() in geocode.get("address", "").lower():
                found_geocode = geocode
                break
        
        assert found_geocode is not None, "Should find geocode for address"
        assert "coordinates" in found_geocode, "Found geocode should have coordinates"
    
    def test_reverse_geocode_logic(self):
        """Test reverse geocoding logic"""
        database = load_database()
        
        # Test finding coordinates
        lat = "37.4979"
        lng = "127.0276"
        
        found_reverse_geocode = None
        for reverse_geocode in database["reverse_geocoding"]:
            if (reverse_geocode.get("lat") == lat and 
                reverse_geocode.get("lng") == lng):
                found_reverse_geocode = reverse_geocode
                break
        
        assert found_reverse_geocode is not None, "Should find reverse geocode for coordinates"
        assert "address" in found_reverse_geocode, "Found reverse geocode should have address"
    
    def test_static_map_logic(self):
        """Test static map logic"""
        database = load_database()
        
        # Test finding a static map
        center = "37.4979,127.0276"
        
        found_static_map = None
        for static_map in database["static_maps"]:
            if static_map.get("center") == center:
                found_static_map = static_map
                break
        
        assert found_static_map is not None, "Should find static map for center coordinates"
        assert "image_data" in found_static_map, "Found static map should have image_data"


class TestMetadataValidation:
    """Test metadata JSON structure and alignment with server"""
    
    def test_metadata_file_exists(self):
        """Test that metadata file exists"""
        assert METADATA_PATH.exists(), f"Metadata file not found at {METADATA_PATH}"
    
    def test_metadata_structure(self):
        """Test metadata JSON structure"""
        with open(METADATA_PATH, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Check top-level fields
        assert "name" in metadata, "Metadata missing 'name' field"
        assert "description" in metadata, "Metadata missing 'description' field"
        assert "tools" in metadata, "Metadata missing 'tools' field"
        
        # Check name matches server name
        assert metadata["name"] == "Naver Maps Directions Server", "Server name mismatch"
        
        # Check tools structure
        tools = metadata["tools"]
        assert isinstance(tools, list), "Tools should be a list"
        assert len(tools) > 0, "Tools list should not be empty"
        
        # Check each tool follows required schema
        tool_names = [tool["name"] for tool in tools]
        expected_tools = ["naver_directions", "naver_geocode", "naver_reverse_geocode", "naver_static_map"]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Missing expected tool: {expected_tool}"
        
        for tool in tools:
            assert "name" in tool, "Tool missing 'name' field"
            assert "description" in tool, "Tool missing 'description' field"
            assert "input_schema" in tool, "Tool missing 'input_schema' field"
            assert "output_schema" in tool, "Tool missing 'output_schema' field"
            
            # Check input schema structure
            input_schema = tool["input_schema"]
            assert "type" in input_schema, "Input schema missing 'type' field"
            assert input_schema["type"] == "object", "Input schema type should be 'object'"
            assert "properties" in input_schema, "Input schema missing 'properties' field"
            
            # Check output schema structure
            output_schema = tool["output_schema"]
            assert "type" in output_schema, "Output schema missing 'type' field"
            assert output_schema["type"] == "object", "Output schema type should be 'object'"
            assert "properties" in output_schema, "Output schema missing 'properties' field"
    
    def test_metadata_tool_schemas(self):
        """Test that tool schemas have proper input/output definitions"""
        with open(METADATA_PATH, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        tools = metadata["tools"]
        
        # Test naver_directions schema
        directions_tool = next(tool for tool in tools if tool["name"] == "naver_directions")
        
        # Check input schema
        input_props = directions_tool["input_schema"]["properties"]
        assert "start" in input_props, "Directions input missing 'start'"
        assert "goal" in input_props, "Directions input missing 'goal'"
        assert "option" in input_props, "Directions input missing 'option'"
        assert "waypoints" in input_props, "Directions input missing 'waypoints'"
        
        # Check required fields
        required_fields = directions_tool["input_schema"]["required"]
        assert "start" in required_fields, "'start' should be required"
        assert "goal" in required_fields, "'goal' should be required"
        
        # Check output schema
        output_props = directions_tool["output_schema"]["properties"]
        assert "route_id" in output_props, "Directions output missing 'route_id'"
        assert "route_info" in output_props, "Directions output missing 'route_info'"
        assert "error" in output_props, "Directions output missing 'error'"
        
        # Test naver_geocode schema
        geocode_tool = next(tool for tool in tools if tool["name"] == "naver_geocode")
        
        input_props = geocode_tool["input_schema"]["properties"]
        assert "address" in input_props, "Geocode input missing 'address'"
        
        required_fields = geocode_tool["input_schema"]["required"]
        assert "address" in required_fields, "'address' should be required"
        
        output_props = geocode_tool["output_schema"]["properties"]
        assert "geocode_id" in output_props, "Geocode output missing 'geocode_id'"
        assert "coordinates" in output_props, "Geocode output missing 'coordinates'"
        assert "error" in output_props, "Geocode output missing 'error'"
        
        # Test naver_reverse_geocode schema
        reverse_geocode_tool = next(tool for tool in tools if tool["name"] == "naver_reverse_geocode")
        
        input_props = reverse_geocode_tool["input_schema"]["properties"]
        assert "lat" in input_props, "Reverse geocode input missing 'lat'"
        assert "lng" in input_props, "Reverse geocode input missing 'lng'"
        
        required_fields = reverse_geocode_tool["input_schema"]["required"]
        assert "lat" in required_fields, "'lat' should be required"
        assert "lng" in required_fields, "'lng' should be required"
        
        output_props = reverse_geocode_tool["output_schema"]["properties"]
        assert "reverse_geocode_id" in output_props, "Reverse geocode output missing 'reverse_geocode_id'"
        assert "address" in output_props, "Reverse geocode output missing 'address'"
        assert "error" in output_props, "Reverse geocode output missing 'error'"
        
        # Test naver_static_map schema
        static_map_tool = next(tool for tool in tools if tool["name"] == "naver_static_map")
        
        input_props = static_map_tool["input_schema"]["properties"]
        assert "center" in input_props, "Static map input missing 'center'"
        assert "h" in input_props, "Static map input missing 'h'"
        assert "w" in input_props, "Static map input missing 'w'"
        assert "level" in input_props, "Static map input missing 'level'"
        assert "format" in input_props, "Static map input missing 'format'"
        
        required_fields = static_map_tool["input_schema"]["required"]
        assert "center" in required_fields, "'center' should be required"
        
        output_props = static_map_tool["output_schema"]["properties"]
        assert "map_id" in output_props, "Static map output missing 'map_id'"
        assert "image_data" in output_props, "Static map output missing 'image_data'"
        assert "error" in output_props, "Static map output missing 'error'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])