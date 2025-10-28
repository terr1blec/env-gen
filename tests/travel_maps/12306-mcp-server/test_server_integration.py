"""
Integration tests for FastMCP server with offline database.
Validates that the server can load the database and expose the correct tools.
"""

import json
import pytest
import sys
import os
from pathlib import Path

# Add the generated directory to Python path to import the server module
project_root = Path(__file__).parent.parent.parent.parent
generated_path = project_root / "generated" / "travel_maps" / "12306-mcp-server"
sys.path.insert(0, str(generated_path))

# Import the server module
try:
    # Import the server module using importlib since the filename starts with a number
    import importlib.util
    spec = importlib.util.spec_from_file_location("server_module", generated_path / "12306_mcp_server_server.py")
    server_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server_module)
except ImportError as e:
    pytest.skip(f"Server module not available: {e}", allow_module_level=True)

# Paths to generated files
DATABASE_PATH = generated_path / "12306_mcp_server_database.json"
METADATA_PATH = generated_path / "12306_mcp_server_metadata.json"


def test_database_exists_and_valid():
    """Test that the database file exists and contains valid JSON."""
    assert DATABASE_PATH.exists(), f"Database file not found at {DATABASE_PATH}"
    
    with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    # Check that database has the expected structure
    assert isinstance(database, dict), "Database should be a dictionary"
    assert len(database) > 0, "Database should not be empty"
    
    # Check for expected data contract keys
    expected_keys = ['train_tickets']
    for key in expected_keys:
        assert key in database, f"Database missing expected key: {key}"
        assert isinstance(database[key], list), f"Database key {key} should be a list"
        assert len(database[key]) > 0, f"Database key {key} should not be empty"


def test_metadata_exists_and_valid():
    """Test that the metadata file exists and follows the required schema."""
    assert METADATA_PATH.exists(), f"Metadata file not found at {METADATA_PATH}"
    
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Check top-level required fields
    assert 'name' in metadata, "Metadata missing 'name' field"
    assert 'description' in metadata, "Metadata missing 'description' field"
    assert 'tools' in metadata, "Metadata missing 'tools' field"
    
    # Validate name matches expected server name
    expected_name = "12306 MCP Server"
    assert metadata['name'] == expected_name, f"Expected name '{expected_name}', got '{metadata['name']}'"
    
    # Validate tools structure
    tools = metadata['tools']
    assert isinstance(tools, list), "Tools should be a list"
    assert len(tools) > 0, "Tools list should not be empty"
    
    for tool_def in tools:
        assert 'name' in tool_def, f"Tool missing 'name' field"
        assert 'description' in tool_def, f"Tool {tool_def.get('name', 'unknown')} missing 'description' field"
        assert 'input_schema' in tool_def, f"Tool {tool_def.get('name', 'unknown')} missing 'input_schema' field"
        
        # Check input schema structure
        input_schema = tool_def['input_schema']
        assert 'type' in input_schema, f"Tool {tool_def.get('name', 'unknown')} input_schema missing 'type' field"
        assert input_schema['type'] == 'object', f"Tool {tool_def.get('name', 'unknown')} input_schema type should be 'object'"
        
        if 'properties' in input_schema:
            assert isinstance(input_schema['properties'], dict), f"Tool {tool_def.get('name', 'unknown')} input_schema properties should be a dictionary"


def test_server_can_load_database():
    """Test that the server module can load and use the database."""
    # Test the load_database function
    assert hasattr(server_module, 'load_database'), "Server module should have load_database function"
    
    # Try to load the database
    try:
        database = server_module.load_database()
        assert database is not None, "Database loading should return non-None value"
        
        # Verify the loaded database has expected structure
        expected_keys = ['train_tickets']
        for key in expected_keys:
            assert key in database, f"Loaded database missing key: {key}"
            assert isinstance(database[key], list), f"Loaded database key {key} should be a list"
            assert len(database[key]) > 0, f"Loaded database key {key} should not be empty"
            
    except Exception as e:
        pytest.fail(f"Failed to load database: {e}")


def test_server_exposes_expected_tools():
    """Test that the server exposes the tools defined in metadata."""
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    expected_tools = {tool['name'] for tool in metadata['tools']}
    
    # Check if server module has the expected tools
    # Since this is a FastMCP server, tools are registered via decorators
    # We'll check if the tool functions exist
    for tool_name in expected_tools:
        assert hasattr(server_module, tool_name), f"Server missing tool function: {tool_name}"


def test_search_tool_functionality():
    """Test that the search tool works correctly with the database."""
    # Load database to get test data
    database = server_module.load_database()
    train_tickets = database['train_tickets']
    
    if len(train_tickets) > 0:
        # Test with actual data from database
        test_ticket = train_tickets[0]
        departure_station = test_ticket['departure_station']
        arrival_station = test_ticket['arrival_station']
        date = test_ticket['date']
        
        # Test the search function
        result = server_module.search(departure_station, arrival_station, date)
        
        # Verify result structure
        assert 'train_tickets' in result, "Search result missing 'train_tickets'"
        assert 'search_parameters' in result, "Search result missing 'search_parameters'"
        
        # Verify search parameters
        search_params = result['search_parameters']
        assert search_params['departure_station'] == departure_station
        assert search_params['arrival_station'] == arrival_station
        assert search_params['date'] == date
        
        # Should find at least the test ticket
        assert len(result['train_tickets']) >= 1, "Search should find at least one matching ticket"


def test_metadata_tool_schemas():
    """Test that tool schemas in metadata are properly defined."""
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    for tool_def in metadata['tools']:
        input_schema = tool_def['input_schema']
        
        # Check required fields in input schema
        assert 'type' in input_schema, f"Input schema for {tool_def['name']} missing 'type'"
        assert input_schema['type'] == 'object', f"Input schema type should be 'object' for {tool_def['name']}"
        
        # Check properties exist
        assert 'properties' in input_schema, f"Input schema for {tool_def['name']} missing 'properties'"
        assert isinstance(input_schema['properties'], dict), f"Properties should be a dictionary for {tool_def['name']}"
        
        # Check required fields are defined
        if 'required' in input_schema:
            assert isinstance(input_schema['required'], list), f"Required fields should be a list for {tool_def['name']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])