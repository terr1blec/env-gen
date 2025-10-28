"""
Automated tests for Weather360 FastMCP server.

These tests validate that:
1. The server can load the offline database correctly
2. The metadata JSON aligns with the server's public API
3. The DATA CONTRACT keys exist and are consumed correctly
4. The server tools work as expected
"""

import json
import pytest
import sys
import os
from pathlib import Path

# Add the generated module to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "generated" / "weather" / "weather360-server"))

from weather360_server_server import load_database, get_live_weather


class TestWeather360Server:
    """Test suite for Weather360 FastMCP server."""
    
    @pytest.fixture
    def database_path(self):
        """Return the path to the database JSON file."""
        return Path(__file__).parent.parent.parent.parent / "generated" / "weather" / "weather360-server" / "weather360_server_database.json"
    
    @pytest.fixture
    def metadata_path(self):
        """Return the path to the metadata JSON file."""
        return Path(__file__).parent.parent.parent.parent / "generated" / "weather" / "weather360-server" / "weather360_server_metadata.json"
    
    @pytest.fixture
    def database_data(self, database_path):
        """Load and return the database content."""
        with open(database_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @pytest.fixture
    def metadata(self, metadata_path):
        """Load and return the metadata content."""
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_database_exists(self, database_path):
        """Test that the database file exists."""
        assert database_path.exists(), f"Database file not found: {database_path}"
        assert database_path.is_file(), f"Database path is not a file: {database_path}"
    
    def test_metadata_exists(self, metadata_path):
        """Test that the metadata file exists."""
        assert metadata_path.exists(), f"Metadata file not found: {metadata_path}"
        assert metadata_path.is_file(), f"Metadata path is not a file: {metadata_path}"
    
    def test_database_structure(self, database_data):
        """Test that the database has the correct structure."""
        # Check top-level keys
        assert "weather_data" in database_data, "Database missing 'weather_data' key"
        
        # Check weather_data is a list
        assert isinstance(database_data["weather_data"], list), "'weather_data' must be a list"
        
        # Check there are records
        assert len(database_data["weather_data"]) > 0, "Database has no weather records"
        
        # Define required fields for DATA CONTRACT
        required_fields = {
            "latitude", "longitude", "temperature", "humidity", 
            "wind_speed", "description", "timestamp"
        }
        
        # Validate each record
        for i, record in enumerate(database_data["weather_data"]):
            # Check all required fields exist
            missing_fields = required_fields - set(record.keys())
            assert not missing_fields, f"Record {i} missing required fields: {missing_fields}"
            
            # Check field types
            assert isinstance(record["latitude"], (int, float)), f"Record {i} latitude must be numeric"
            assert isinstance(record["longitude"], (int, float)), f"Record {i} longitude must be numeric"
            assert isinstance(record["temperature"], (int, float)), f"Record {i} temperature must be numeric"
            assert isinstance(record["humidity"], (int, float)), f"Record {i} humidity must be numeric"
            assert isinstance(record["wind_speed"], (int, float)), f"Record {i} wind_speed must be numeric"
            assert isinstance(record["description"], str), f"Record {i} description must be string"
            assert isinstance(record["timestamp"], str), f"Record {i} timestamp must be string"
    
    def test_metadata_structure(self, metadata):
        """Test that the metadata has the correct structure."""
        # Check top-level fields
        assert "name" in metadata, "Metadata missing 'name' field"
        assert "description" in metadata, "Metadata missing 'description' field"
        assert "tools" in metadata, "Metadata missing 'tools' field"
        
        # Check name matches expected server name
        assert metadata["name"] == "Weather360 Server", f"Server name mismatch: {metadata['name']}"
        
        # Check tools is a list
        assert isinstance(metadata["tools"], list), "'tools' must be a list"
        
        # Check there is at least one tool
        assert len(metadata["tools"]) > 0, "Metadata has no tools defined"
    
    def test_tool_schema_structure(self, metadata):
        """Test that each tool follows the required schema."""
        for tool in metadata["tools"]:
            # Check required tool fields
            assert "name" in tool, "Tool missing 'name' field"
            assert "description" in tool, f"Tool {tool.get('name', 'unknown')} missing 'description' field"
            assert "input_schema" in tool, f"Tool {tool.get('name', 'unknown')} missing 'input_schema' field"
            assert "output_schema" in tool, f"Tool {tool.get('name', 'unknown')} missing 'output_schema' field"
            
            # Check input schema structure
            input_schema = tool["input_schema"]
            assert "type" in input_schema, f"Tool {tool['name']} input_schema missing 'type' field"
            assert input_schema["type"] == "object", f"Tool {tool['name']} input_schema type must be 'object'"
            assert "properties" in input_schema, f"Tool {tool['name']} input_schema missing 'properties' field"
            
            # Check output schema structure
            output_schema = tool["output_schema"]
            assert "type" in output_schema, f"Tool {tool['name']} output_schema missing 'type' field"
            assert output_schema["type"] == "object", f"Tool {tool['name']} output_schema type must be 'object'"
            assert "properties" in output_schema, f"Tool {tool['name']} output_schema missing 'properties' field"
    
    def test_get_live_weather_tool_schema(self, metadata):
        """Test the specific schema for get_live_weather tool."""
        # Find the get_live_weather tool
        weather_tool = None
        for tool in metadata["tools"]:
            if tool["name"] == "get_live_weather":
                weather_tool = tool
                break
        
        assert weather_tool is not None, "get_live_weather tool not found in metadata"
        
        # Check input schema
        input_schema = weather_tool["input_schema"]
        assert "latitude" in input_schema["properties"], "get_live_weather missing latitude input"
        assert "longitude" in input_schema["properties"], "get_live_weather missing longitude input"
        assert "latitude" in input_schema["required"], "get_live_weather latitude not marked as required"
        assert "longitude" in input_schema["required"], "get_live_weather longitude not marked as required"
        
        # Check output schema
        output_schema = weather_tool["output_schema"]
        expected_output_fields = {"temperature", "humidity", "wind_speed", "description", "timestamp"}
        actual_output_fields = set(output_schema["properties"].keys())
        assert expected_output_fields == actual_output_fields, f"Output fields mismatch: expected {expected_output_fields}, got {actual_output_fields}"
    
    def test_load_database_function(self, database_path):
        """Test that the load_database function works correctly."""
        # Temporarily change working directory to where the database is located
        original_cwd = os.getcwd()
        try:
            os.chdir(database_path.parent)
            
            # Test loading database
            database = load_database()
            
            # Verify structure
            assert "weather_data" in database
            assert isinstance(database["weather_data"], list)
            assert len(database["weather_data"]) > 0
            
            # Verify first record has all required fields
            first_record = database["weather_data"][0]
            required_fields = {"latitude", "longitude", "temperature", "humidity", 
                              "wind_speed", "description", "timestamp"}
            assert required_fields.issubset(set(first_record.keys()))
            
        finally:
            os.chdir(original_cwd)
    
    def test_get_live_weather_function_exact_match(self, database_data):
        """Test get_live_weather function with exact coordinate match."""
        # Get coordinates from first record in database
        first_record = database_data["weather_data"][0]
        latitude = first_record["latitude"]
        longitude = first_record["longitude"]
        
        # Temporarily change working directory to where the database is located
        original_cwd = os.getcwd()
        try:
            os.chdir(Path(__file__).parent.parent.parent.parent / "generated" / "weather" / "weather360-server")
            
            # Test function with exact coordinates
            result = get_live_weather(latitude, longitude)
            
            # Verify result structure
            expected_fields = {"temperature", "humidity", "wind_speed", "description", "timestamp"}
            assert set(result.keys()) == expected_fields
            
            # Verify values match the database record
            assert result["temperature"] == first_record["temperature"]
            assert result["humidity"] == first_record["humidity"]
            assert result["wind_speed"] == first_record["wind_speed"]
            assert result["description"] == first_record["description"]
            assert result["timestamp"] == first_record["timestamp"]
            
        finally:
            os.chdir(original_cwd)
    
    def test_get_live_weather_function_closest_match(self, database_data):
        """Test get_live_weather function with closest coordinate match."""
        # Use coordinates that don't exactly match any record
        test_latitude = 40.7
        test_longitude = -74.0
        
        # Temporarily change working directory to where the database is located
        original_cwd = os.getcwd()
        try:
            os.chdir(Path(__file__).parent.parent.parent.parent / "generated" / "weather" / "weather360-server")
            
            # Test function with non-exact coordinates
            result = get_live_weather(test_latitude, test_longitude)
            
            # Verify result structure
            expected_fields = {"temperature", "humidity", "wind_speed", "description", "timestamp"}
            assert set(result.keys()) == expected_fields
            
            # Verify all fields have appropriate types
            assert isinstance(result["temperature"], (int, float))
            assert isinstance(result["humidity"], (int, float))
            assert isinstance(result["wind_speed"], (int, float))
            assert isinstance(result["description"], str)
            assert isinstance(result["timestamp"], str)
            
        finally:
            os.chdir(original_cwd)
    
    def test_get_live_weather_function_invalid_coordinates(self):
        """Test get_live_weather function with invalid coordinates."""
        # Use coordinates that are way out of range
        invalid_latitude = 1000.0
        invalid_longitude = 2000.0
        
        # Temporarily change working directory to where the database is located
        original_cwd = os.getcwd()
        try:
            os.chdir(Path(__file__).parent.parent.parent.parent / "generated" / "weather" / "weather360-server")
            
            # Test function with invalid coordinates - should still find closest match
            result = get_live_weather(invalid_latitude, invalid_longitude)
            
            # Should still return valid weather data (closest match)
            expected_fields = {"temperature", "humidity", "wind_speed", "description", "timestamp"}
            assert set(result.keys()) == expected_fields
            
        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])