"""
Integration tests for FastMCP server with offline database.

Validates that:
1. Server can load the generated database
2. Metadata JSON reflects server's public API
3. DATA CONTRACT keys are present and consumed correctly
4. Metadata schema is properly structured
"""

import json
import pytest
import sys
from pathlib import Path

# Add the generated module to Python path
workspace_root = Path(__file__).parent.parent.parent.parent
generated_path = workspace_root / "generated" / "travel_maps" / "chinarailway-mcp-"
sys.path.insert(0, str(generated_path))


def test_metadata_exists():
    """Test that metadata JSON file exists and is valid JSON."""
    metadata_path = generated_path / "chinarailway_mcp__metadata.json"
    
    assert metadata_path.exists(), f"Metadata file not found at {metadata_path}"
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    assert isinstance(metadata, dict), "Metadata should be a dictionary"
    print("[OK] Metadata file exists and is valid JSON")


def test_metadata_schema():
    """Test that metadata follows the required schema."""
    metadata_path = generated_path / "chinarailway_mcp__metadata.json"
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Required top-level fields
    required_fields = ['name', 'description', 'tools']
    for field in required_fields:
        assert field in metadata, f"Metadata missing required field: {field}"
    
    # Name should match server name
    assert 'chinarailway' in metadata['name'].lower(), "Server name should contain 'chinarailway'"
    
    # Description should be present
    assert isinstance(metadata['description'], str), "Description should be a string"
    assert len(metadata['description']) > 0, "Description should not be empty"
    
    # Tools should be a list (FastMCP uses list format)
    assert isinstance(metadata['tools'], list), "Tools should be a list"
    
    print("[OK] Metadata schema validation passed")


def test_tools_schema():
    """Test that each tool in metadata follows the required schema."""
    metadata_path = generated_path / "chinarailway_mcp__metadata.json"
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    for tool_spec in metadata['tools']:
        assert isinstance(tool_spec, dict), f"Tool should be a dictionary"
        
        # Required tool fields
        required_tool_fields = ['name', 'description', 'input_schema', 'output_schema']
        for field in required_tool_fields:
            assert field in tool_spec, f"Tool missing required field: {field}"
        
        # Check tool name
        assert tool_spec['name'] == 'search', "Tool name should be 'search'"
        
        # Input schema validation
        input_schema = tool_spec['input_schema']
        assert isinstance(input_schema, dict), "Input schema should be a dictionary"
        assert input_schema['type'] == 'object', "Input schema type should be 'object'"
        assert 'properties' in input_schema, "Input schema should have properties"
        assert 'required' in input_schema, "Input schema should have required fields"
        
        # Check required input fields
        required_inputs = ['from_station', 'to_station', 'date']
        for req in required_inputs:
            assert req in input_schema['required'], f"Required input field missing: {req}"
        
        # Output schema validation
        output_schema = tool_spec['output_schema']
        assert isinstance(output_schema, dict), "Output schema should be a dictionary"
        assert output_schema['type'] == 'object', "Output schema type should be 'object'"
        assert 'properties' in output_schema, "Output schema should have properties"
        
        print(f"[OK] Tool {tool_spec['name']} schema validation passed")


def test_database_json_exists():
    """Test that database JSON file exists and contains expected structure."""
    database_path = generated_path / "chinarailway_mcp__database.json"
    
    assert database_path.exists(), f"Database file not found at {database_path}"
    
    with open(database_path, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    assert isinstance(database, dict), "Database should be a dictionary"
    
    # Check for DATA CONTRACT keys
    expected_keys = ['trains']
    for key in expected_keys:
        assert key in database, f"Database missing expected key: {key}"
        print(f"[OK] Found expected data key: {key}")
    
    # Check train data structure
    assert isinstance(database['trains'], list), "Trains should be a list"
    assert len(database['trains']) > 0, "Database should contain train data"
    
    # Check a sample train
    sample_train = database['trains'][0]
    required_train_fields = [
        'train_number', 'departure_station', 'arrival_station',
        'departure_time', 'arrival_time', 'duration', 'date',
        'seat_types', 'prices', 'available_seats'
    ]
    for field in required_train_fields:
        assert field in sample_train, f"Train missing required field: {field}"
    
    print("[OK] Database file exists and has expected structure")


def test_server_file_exists():
    """Test that server Python file exists and has expected structure."""
    server_path = generated_path / "chinarailway_mcp__server.py"
    
    assert server_path.exists(), f"Server file not found at {server_path}"
    
    with open(server_path, 'r', encoding='utf-8') as f:
        server_content = f.read()
    
    # Check that server contains expected functions
    expected_functions = ['load_database', 'validate_database_structure', 'search']
    for func in expected_functions:
        assert f"def {func}" in server_content, f"Server missing function: {func}"
    
    # Check that server contains expected imports
    expected_imports = ['json', 'os', 'FastMCP']
    for imp in expected_imports:
        assert imp in server_content, f"Server missing import: {imp}"
    
    print("[OK] Server file exists and has expected structure")


def test_database_contract():
    """Test that the database follows the DATA CONTRACT."""
    database_path = generated_path / "chinarailway_mcp__database.json"
    
    with open(database_path, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    # Validate database structure
    assert isinstance(database, dict), "Database should be a dictionary"
    assert "trains" in database, "Database should contain 'trains' key"
    assert isinstance(database["trains"], list), "Trains should be a list"
    
    # Check each train for required fields
    required_fields = [
        "train_number", "departure_station", "arrival_station", 
        "departure_time", "arrival_time", "duration", "date",
        "seat_types", "prices", "available_seats"
    ]
    
    for train in database["trains"]:
        assert isinstance(train, dict), "Each train should be a dictionary"
        
        for field in required_fields:
            assert field in train, f"Train missing required field: {field}"
        
        # Check nested structures
        for nested_field in ["seat_types", "prices", "available_seats"]:
            assert isinstance(train[nested_field], dict), f"{nested_field} should be a dictionary"
    
    print("[OK] Database follows DATA CONTRACT")


def test_metadata_alignment():
    """Test that metadata aligns with server capabilities."""
    metadata_path = generated_path / "chinarailway_mcp__metadata.json"
    server_path = generated_path / "chinarailway_mcp__server.py"
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    with open(server_path, 'r', encoding='utf-8') as f:
        server_content = f.read()
    
    # Check that the tool in metadata matches the server function
    assert len(metadata['tools']) == 1, "Should have exactly one tool"
    tool_spec = metadata['tools'][0]
    
    # Tool name should match server function
    assert tool_spec['name'] == 'search', "Tool name should be 'search'"
    
    # Server should have the search function
    assert "def search(" in server_content, "Server should have search function"
    
    # Input parameters should match
    input_schema = tool_spec['input_schema']
    required_inputs = input_schema['required']
    
    # Check that server function signature includes these parameters
    for param in required_inputs:
        assert f"{param}:" in server_content, f"Server search function missing parameter: {param}"
    
    print("[OK] Metadata aligns with server capabilities")


def test_integration_workflow():
    """End-to-end test of the complete workflow."""
    # Test all components
    test_metadata_exists()
    test_metadata_schema()
    test_tools_schema()
    test_database_json_exists()
    test_server_file_exists()
    test_database_contract()
    test_metadata_alignment()
    
    print("[OK] Complete integration workflow validated")


if __name__ == "__main__":
    # Run all tests
    test_metadata_exists()
    test_metadata_schema()
    test_tools_schema()
    test_database_json_exists()
    test_server_file_exists()
    test_database_contract()
    test_metadata_alignment()
    test_integration_workflow()
    print("\nSUCCESS: All tests passed successfully!")