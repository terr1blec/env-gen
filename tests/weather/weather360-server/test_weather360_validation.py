"""
Validation tests for Weather360 FastMCP server without importing server module.

These tests validate:
1. Database structure and DATA CONTRACT compliance
2. Metadata structure and alignment with expected API
3. JSON schema validation
"""

import json
import pytest
from pathlib import Path


class TestWeather360Validation:
    """Validation test suite for Weather360 FastMCP server."""
    
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
    
    def test_database_file_exists(self, database_path):
        """Test that the database file exists."""
        assert database_path.exists(), f"Database file not found: {database_path}"
        assert database_path.is_file(), f"Database path is not a file: {database_path}"
    
    def test_metadata_file_exists(self, metadata_path):
        """Test that the metadata file exists."""
        assert metadata_path.exists(), f"Metadata file not found: {metadata_path}"
        assert metadata_path.is_file(), f"Metadata path is not a file: {metadata_path}"
    
    def test_database_json_valid(self, database_path):
        """Test that the database file contains valid JSON."""
        try:
            with open(database_path, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Database JSON is invalid: {e}")
    
    def test_metadata_json_valid(self, metadata_path):
        """Test that the metadata file contains valid JSON."""
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Metadata JSON is invalid: {e}")
    
    def test_database_has_weather_data_key(self, database_data):
        """Test that the database has the required 'weather_data' key."""
        assert "weather_data" in database_data, "Database missing required 'weather_data' key"
    
    def test_weather_data_is_list(self, database_data):
        """Test that weather_data is a list."""
        assert isinstance(database_data["weather_data"], list), "'weather_data' must be a list"
    
    def test_database_has_records(self, database_data):
        """Test that the database contains weather records."""
        assert len(database_data["weather_data"]) > 0, "Database has no weather records"
    
    def test_database_data_contract(self, database_data):
        """Test DATA CONTRACT compliance for all weather records."""
        required_fields = {
            "latitude", "longitude", "temperature", "humidity", 
            "wind_speed", "description", "timestamp"
        }
        
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
            
            # Check value ranges (basic sanity checks)
            assert -90 <= record["latitude"] <= 90, f"Record {i} latitude out of range: {record['latitude']}"
            assert -180 <= record["longitude"] <= 180, f"Record {i} longitude out of range: {record['longitude']}"
            assert -100 <= record["temperature"] <= 100, f"Record {i} temperature out of range: {record['temperature']}"
            assert 0 <= record["humidity"] <= 100, f"Record {i} humidity out of range: {record['humidity']}"
            assert record["wind_speed"] >= 0, f"Record {i} wind_speed negative: {record['wind_speed']}"
    
    def test_metadata_has_required_fields(self, metadata):
        """Test that metadata has all required top-level fields."""
        assert "name" in metadata, "Metadata missing 'name' field"
        assert "description" in metadata, "Metadata missing 'description' field"
        assert "tools" in metadata, "Metadata missing 'tools' field"
    
    def test_metadata_server_name(self, metadata):
        """Test that metadata name matches expected server name."""
        assert metadata["name"] == "Weather360 Server", f"Server name mismatch: {metadata['name']}"
    
    def test_metadata_tools_is_list(self, metadata):
        """Test that tools is a list."""
        assert isinstance(metadata["tools"], list), "'tools' must be a list"
    
    def test_metadata_has_tools(self, metadata):
        """Test that metadata defines at least one tool."""
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
    
    def test_get_live_weather_tool_exists(self, metadata):
        """Test that get_live_weather tool exists in metadata."""
        tool_names = [tool["name"] for tool in metadata["tools"]]
        assert "get_live_weather" in tool_names, "get_live_weather tool not found in metadata"
    
    def test_get_live_weather_input_schema(self, metadata):
        """Test the input schema for get_live_weather tool."""
        # Find the get_live_weather tool
        weather_tool = None
        for tool in metadata["tools"]:
            if tool["name"] == "get_live_weather":
                weather_tool = tool
                break
        
        assert weather_tool is not None, "get_live_weather tool not found in metadata"
        
        input_schema = weather_tool["input_schema"]
        
        # Check required fields
        assert "latitude" in input_schema["properties"], "get_live_weather missing latitude input"
        assert "longitude" in input_schema["properties"], "get_live_weather missing longitude input"
        assert "latitude" in input_schema["required"], "get_live_weather latitude not marked as required"
        assert "longitude" in input_schema["required"], "get_live_weather longitude not marked as required"
        
        # Check input field descriptions
        latitude_prop = input_schema["properties"]["latitude"]
        longitude_prop = input_schema["properties"]["longitude"]
        
        assert "description" in latitude_prop, "latitude missing description"
        assert "description" in longitude_prop, "longitude missing description"
        assert latitude_prop["type"] == "number", "latitude must be number type"
        assert longitude_prop["type"] == "number", "longitude must be number type"
    
    def test_get_live_weather_output_schema(self, metadata):
        """Test the output schema for get_live_weather tool."""
        # Find the get_live_weather tool
        weather_tool = None
        for tool in metadata["tools"]:
            if tool["name"] == "get_live_weather":
                weather_tool = tool
                break
        
        assert weather_tool is not None, "get_live_weather tool not found in metadata"
        
        output_schema = weather_tool["output_schema"]
        
        # Check expected output fields
        expected_output_fields = {"temperature", "humidity", "wind_speed", "description", "timestamp"}
        actual_output_fields = set(output_schema["properties"].keys())
        assert expected_output_fields == actual_output_fields, f"Output fields mismatch: expected {expected_output_fields}, got {actual_output_fields}"
        
        # Check output field types and descriptions
        for field in expected_output_fields:
            assert field in output_schema["properties"], f"Output field {field} missing from schema"
            field_prop = output_schema["properties"][field]
            assert "description" in field_prop, f"Output field {field} missing description"
            
            # Check type consistency
            if field in ["temperature", "humidity", "wind_speed"]:
                assert field_prop["type"] == "number", f"Output field {field} must be number type"
            elif field in ["description", "timestamp"]:
                assert field_prop["type"] == "string", f"Output field {field} must be string type"
    
    def test_metadata_database_alignment(self, metadata, database_data):
        """Test that metadata output schema aligns with database structure."""
        # Find the get_live_weather tool
        weather_tool = None
        for tool in metadata["tools"]:
            if tool["name"] == "get_live_weather":
                weather_tool = tool
                break
        
        assert weather_tool is not None, "get_live_weather tool not found"
        
        # Get output schema fields
        output_fields = set(weather_tool["output_schema"]["properties"].keys())
        
        # Get database record fields (excluding coordinates)
        first_record = database_data["weather_data"][0]
        database_output_fields = set(first_record.keys()) - {"latitude", "longitude"}
        
        # Output schema should match database fields (excluding inputs)
        assert output_fields == database_output_fields, f"Output schema fields {output_fields} don't match database fields {database_output_fields}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])