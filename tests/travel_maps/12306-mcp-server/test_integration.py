"""
Integration tests that validate the FastMCP server works with the offline database
without requiring the fastmcp module to be installed.
"""

import json
import pytest
from pathlib import Path

# Paths to generated files
project_root = Path(__file__).parent.parent.parent.parent
generated_path = project_root / "generated" / "travel_maps" / "12306-mcp-server"
DATABASE_PATH = generated_path / "12306_mcp_server_database.json"
METADATA_PATH = generated_path / "12306_mcp_server_metadata.json"
SERVER_PATH = generated_path / "12306_mcp_server_server.py"


def test_database_data_contract():
    """Test that the database satisfies the DATA CONTRACT requirements."""
    with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    # Check DATA CONTRACT: train_tickets must exist and be a non-empty list
    assert 'train_tickets' in database, "DATA CONTRACT: Database must have 'train_tickets' key"
    train_tickets = database['train_tickets']
    assert isinstance(train_tickets, list), "DATA CONTRACT: 'train_tickets' must be a list"
    assert len(train_tickets) > 0, "DATA CONTRACT: 'train_tickets' must not be empty"
    
    # Check DATA CONTRACT: Each ticket must have required fields
    required_fields = [
        'train_number', 'departure_station', 'arrival_station',
        'departure_time', 'arrival_time', 'duration', 'date',
        'seat_types', 'prices', 'available_seats'
    ]
    
    for ticket in train_tickets:
        for field in required_fields:
            assert field in ticket, f"DATA CONTRACT: Ticket missing required field: {field}"
        
        # Check nested structures
        assert isinstance(ticket['seat_types'], dict), "DATA CONTRACT: seat_types must be a dictionary"
        assert isinstance(ticket['prices'], dict), "DATA CONTRACT: prices must be a dictionary"
        assert isinstance(ticket['available_seats'], dict), "DATA CONTRACT: available_seats must be a dictionary"
        
        # Check that prices and available_seats have consistent keys
        seat_keys = set(ticket['seat_types'].keys())
        price_keys = set(ticket['prices'].keys())
        seat_availability_keys = set(ticket['available_seats'].keys())
        
        assert seat_keys == price_keys == seat_availability_keys, \
            "DATA CONTRACT: seat_types, prices, and available_seats must have consistent keys"


def test_metadata_schema():
    """Test that metadata follows the required schema for FastMCP servers."""
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
    
    # Check each tool definition
    for tool_def in tools:
        # Required tool fields
        assert 'name' in tool_def, "Tool missing 'name' field"
        assert 'description' in tool_def, f"Tool {tool_def.get('name', 'unknown')} missing 'description' field"
        assert 'input_schema' in tool_def, f"Tool {tool_def.get('name', 'unknown')} missing 'input_schema' field"
        
        # Check input schema structure
        input_schema = tool_def['input_schema']
        assert 'type' in input_schema, f"Tool {tool_def.get('name', 'unknown')} input_schema missing 'type' field"
        assert input_schema['type'] == 'object', f"Tool {tool_def.get('name', 'unknown')} input_schema type should be 'object'"
        
        # Check properties exist
        assert 'properties' in input_schema, f"Tool {tool_def.get('name', 'unknown')} input_schema missing 'properties'"
        assert isinstance(input_schema['properties'], dict), f"Tool {tool_def.get('name', 'unknown')} input_schema properties should be a dictionary"
        
        # Check required fields are defined
        assert 'required' in input_schema, f"Tool {tool_def.get('name', 'unknown')} input_schema missing 'required' field"
        assert isinstance(input_schema['required'], list), f"Tool {tool_def.get('name', 'unknown')} required fields should be a list"
        
        # Check output schema if present
        if 'output_schema' in tool_def:
            output_schema = tool_def['output_schema']
            assert 'type' in output_schema, f"Tool {tool_def.get('name', 'unknown')} output_schema missing 'type' field"


def test_server_implementation():
    """Test that the server implementation follows expected patterns."""
    with open(SERVER_PATH, 'r', encoding='utf-8') as f:
        server_code = f.read()
    
    # Check for required imports
    assert "import json" in server_code, "Server should import json"
    assert "from fastmcp import FastMCP" in server_code, "Server should import FastMCP"
    
    # Check for required functions
    assert "def load_database()" in server_code, "Server should have load_database function"
    assert "def search(" in server_code, "Server should have search function"
    
    # Check for FastMCP initialization
    assert "mcp = FastMCP" in server_code, "Server should initialize FastMCP instance"
    
    # Check for tool decorator
    assert "@mcp.tool()" in server_code, "Server should use @mcp.tool() decorator"


def test_database_server_integration():
    """Test that database and server are properly integrated."""
    with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    with open(SERVER_PATH, 'r', encoding='utf-8') as f:
        server_code = f.read()
    
    # Check that server code references the database file
    assert "12306_mcp_server_database.json" in server_code, "Server should reference the database file"
    
    # Check that database has data that can be consumed by the server
    train_tickets = database['train_tickets']
    assert len(train_tickets) > 0, "Database should have tickets for server to consume"
    
    # Verify that tickets have the structure expected by the search function
    for ticket in train_tickets[:5]:  # Check first 5 tickets
        # These fields are used in the search function
        assert 'departure_station' in ticket, "Ticket missing departure_station for search"
        assert 'arrival_station' in ticket, "Ticket missing arrival_station for search"
        assert 'date' in ticket, "Ticket missing date for search"


def test_metadata_tool_alignment():
    """Test that metadata tools align with server implementation."""
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    with open(SERVER_PATH, 'r', encoding='utf-8') as f:
        server_code = f.read()
    
    # Check that each tool in metadata exists in the server
    for tool_def in metadata['tools']:
        tool_name = tool_def['name']
        assert f"def {tool_name}(" in server_code, f"Server missing implementation for tool: {tool_name}"
        
        # Check that tool parameters in metadata match server function
        input_schema = tool_def['input_schema']
        required_params = input_schema.get('required', [])
        
        # Verify that the server function has these parameters
        for param in required_params:
            assert param in server_code, f"Server function {tool_name} missing parameter: {param}"


def test_search_tool_schema():
    """Test that the search tool schema is properly defined."""
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Find the search tool
    search_tool = None
    for tool in metadata['tools']:
        if tool['name'] == 'search':
            search_tool = tool
            break
    
    assert search_tool is not None, "Metadata should contain a 'search' tool"
    
    # Check search tool input schema
    input_schema = search_tool['input_schema']
    assert input_schema['type'] == 'object', "Search input schema type should be 'object'"
    
    # Check required parameters
    required_params = input_schema.get('required', [])
    expected_params = ['departure_station', 'arrival_station', 'date']
    for param in expected_params:
        assert param in required_params, f"Search tool missing required parameter: {param}"
    
    # Check parameter properties
    properties = input_schema.get('properties', {})
    for param in expected_params:
        assert param in properties, f"Search tool missing property definition for: {param}"
        assert 'type' in properties[param], f"Search tool parameter {param} missing type"
        assert 'description' in properties[param], f"Search tool parameter {param} missing description"


def test_server_name_consistency():
    """Test that server name is consistent across all artifacts."""
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    with open(SERVER_PATH, 'r', encoding='utf-8') as f:
        server_code = f.read()
    
    # Check metadata name
    metadata_name = metadata['name']
    assert metadata_name == "12306 MCP Server", f"Metadata name should be '12306 MCP Server', got '{metadata_name}'"
    
    # Check server code references the name
    assert "12306 MCP Server" in server_code, "Server code should contain the server name"
    assert "name=\"12306 MCP Server\"" in server_code, "Server should set name in FastMCP initialization"