"""
Basic tests to verify the generated files exist and are valid.
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


def test_files_exist():
    """Test that all required files exist."""
    assert DATABASE_PATH.exists(), f"Database file not found at {DATABASE_PATH}"
    assert METADATA_PATH.exists(), f"Metadata file not found at {METADATA_PATH}"
    assert SERVER_PATH.exists(), f"Server file not found at {SERVER_PATH}"


def test_database_valid():
    """Test that the database file contains valid JSON and expected structure."""
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


def test_metadata_valid():
    """Test that the metadata file follows the required schema."""
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
    
    # Check first tool
    tool_def = tools[0]
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


def test_server_file_readable():
    """Test that the server file can be read and contains expected content."""
    with open(SERVER_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for expected content
    assert "12306 MCP Server" in content, "Server file should contain server name"
    assert "search" in content, "Server file should contain search function"
    assert "load_database" in content, "Server file should contain load_database function"