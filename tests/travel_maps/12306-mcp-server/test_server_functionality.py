"""
Test server functionality by importing and testing the server module directly.
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

# Import the server module using importlib since the filename starts with a number
import importlib.util
spec = importlib.util.spec_from_file_location("server_module", generated_path / "12306_mcp_server_server.py")
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)

# Paths to generated files
DATABASE_PATH = generated_path / "12306_mcp_server_database.json"
METADATA_PATH = generated_path / "12306_mcp_server_metadata.json"


def test_server_has_required_functions():
    """Test that the server module has the required functions."""
    assert hasattr(server_module, 'load_database'), "Server module should have load_database function"
    assert hasattr(server_module, 'search'), "Server module should have search function"
    assert hasattr(server_module, 'mcp'), "Server module should have mcp FastMCP instance"


def test_load_database_function():
    """Test that the load_database function works correctly."""
    database = server_module.load_database()
    
    # Verify the loaded database has expected structure
    assert database is not None, "Database loading should return non-None value"
    assert isinstance(database, dict), "Database should be a dictionary"
    
    expected_keys = ['train_tickets']
    for key in expected_keys:
        assert key in database, f"Loaded database missing key: {key}"
        assert isinstance(database[key], list), f"Loaded database key {key} should be a list"
        assert len(database[key]) > 0, f"Loaded database key {key} should not be empty"


def test_search_function_basic():
    """Test basic search functionality."""
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


def test_search_function_no_results():
    """Test search function with parameters that should return no results."""
    # Use parameters that likely won't match any tickets
    result = server_module.search("Nonexistent Station", "Another Nonexistent", "2099-01-01")
    
    # Verify result structure
    assert 'train_tickets' in result, "Search result missing 'train_tickets'"
    assert 'search_parameters' in result, "Search result missing 'search_parameters'"
    
    # Should return empty list for no matches
    assert result['train_tickets'] == [], "Search should return empty list for no matches"
    assert result['search_parameters']['total_results'] == 0, "Total results should be 0 for no matches"


def test_metadata_matches_server():
    """Test that the metadata matches what the server provides."""
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Check that the server has the tools defined in metadata
    expected_tools = {tool['name'] for tool in metadata['tools']}
    
    for tool_name in expected_tools:
        assert hasattr(server_module, tool_name), f"Server missing tool function: {tool_name}"


def test_ticket_data_structure():
    """Test that train ticket data has the expected structure."""
    database = server_module.load_database()
    train_tickets = database['train_tickets']
    
    # Check a few tickets to ensure they have required fields
    for ticket in train_tickets[:3]:  # Check first 3 tickets
        required_fields = [
            'train_number', 'departure_station', 'arrival_station',
            'departure_time', 'arrival_time', 'duration', 'date',
            'seat_types', 'prices', 'available_seats'
        ]
        
        for field in required_fields:
            assert field in ticket, f"Ticket missing required field: {field}"
            
        # Check nested structures
        assert isinstance(ticket['seat_types'], dict), "seat_types should be a dictionary"
        assert isinstance(ticket['prices'], dict), "prices should be a dictionary"
        assert isinstance(ticket['available_seats'], dict), "available_seats should be a dictionary"


def test_fastmcp_integration():
    """Test that the FastMCP integration is properly set up."""
    # Check that the mcp instance exists and has expected attributes
    mcp = server_module.mcp
    assert mcp is not None, "FastMCP instance should not be None"
    
    # Check that tools are registered (this is a basic check)
    # The actual tool registration would be verified through the search function tests