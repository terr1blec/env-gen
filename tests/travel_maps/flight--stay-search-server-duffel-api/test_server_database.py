"""
Tests for FastMCP server with offline database integration.
Validates that the server can load the generated database and maintain schema consistency.
"""

import json
import pytest
import sys
import os
from pathlib import Path

# Add the project root to Python path to import server modules
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

class TestServerDatabaseIntegration:
    """Test suite for server and database integration."""
    
    @pytest.fixture
    def database_path(self):
        """Path to the generated database JSON."""
        return project_root / "generated" / "travel_maps" / "flight--stay-search-server-duffel-api" / "flight__stay_search_server_duffel_api_database.json"
    
    @pytest.fixture
    def metadata_path(self):
        """Path to the generated metadata JSON."""
        return project_root / "generated" / "travel_maps" / "flight--stay-search-server-duffel-api" / "flight__stay_search_server_duffel_api_metadata.json"
    
    def test_database_file_exists(self, database_path):
        """Test that the database JSON file exists."""
        assert database_path.exists(), f"Database file not found at {database_path}"
        
    def test_metadata_file_exists(self, metadata_path):
        """Test that the metadata JSON file exists."""
        assert metadata_path.exists(), f"Metadata file not found at {metadata_path}"
    
    def test_database_schema_structure(self, database_path):
        """Test that the database has the expected DATA CONTRACT structure."""
        with open(database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        # Check top-level structure
        assert isinstance(database, dict), "Database should be a dictionary"
        
        # Check for required DATA CONTRACT keys based on actual database
        required_keys = [
            'flights', 'offers', 'stays', 'reviews'
        ]
        
        for key in required_keys:
            assert key in database, f"Missing required key in database: {key}"
            assert isinstance(database[key], (dict, list)), f"Database key {key} should be dict or list"
        
        # Validate specific collections have expected structure
        if 'flights' in database:
            flights = database['flights']
            assert isinstance(flights, list), "Flights should be a list"
            if len(flights) > 0:
                flight = flights[0]
                assert 'id' in flight, "Flight should have id"
                assert 'origin' in flight, "Flight should have origin"
                assert 'destination' in flight, "Flight should have destination"
                assert 'departure_date' in flight, "Flight should have departure_date"
        
        if 'offers' in database:
            offers = database['offers']
            assert isinstance(offers, list), "Offers should be a list"
            if len(offers) > 0:
                offer = offers[0]
                assert 'id' in offer, "Offer should have id"
                assert 'flight_id' in offer, "Offer should have flight_id"
                assert 'price' in offer, "Offer should have price"
        
        if 'stays' in database:
            stays = database['stays']
            assert isinstance(stays, list), "Stays should be a list"
            if len(stays) > 0:
                stay = stays[0]
                assert 'id' in stay, "Stay should have id"
                assert 'name' in stay, "Stay should have name"
                assert 'location' in stay, "Stay should have location"
        
        if 'reviews' in database:
            reviews = database['reviews']
            assert isinstance(reviews, list), "Reviews should be a list"
            if len(reviews) > 0:
                review = reviews[0]
                assert 'id' in review, "Review should have id"
                assert 'stay_id' in review, "Review should have stay_id"
                assert 'rating' in review, "Review should have rating"
    
    def test_metadata_schema_structure(self, metadata_path):
        """Test that the metadata follows the required schema."""
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Check top-level required fields
        assert 'name' in metadata, "Metadata missing 'name' field"
        assert 'description' in metadata, "Metadata missing 'description' field"
        assert 'tools' in metadata, "Metadata missing 'tools' field"
        
        # Validate name matches expected server name pattern
        name = metadata['name']
        assert isinstance(name, str), "Name should be a string"
        assert len(name) > 0, "Name should not be empty"
        
        # Validate description
        description = metadata['description']
        assert isinstance(description, str), "Description should be a string"
        assert len(description) > 0, "Description should not be empty"
        
        # Validate tools structure
        tools = metadata['tools']
        assert isinstance(tools, list), "Tools should be a list"
        
        for tool in tools:
            self._validate_tool_schema(tool)
    
    def _validate_tool_schema(self, tool):
        """Validate individual tool schema."""
        assert 'name' in tool, "Tool missing 'name' field"
        assert 'description' in tool, "Tool missing 'description' field"
        
        # Check input schema if present
        if 'input_schema' in tool:
            input_schema = tool['input_schema']
            assert 'type' in input_schema, "Input schema missing 'type' field"
            assert input_schema['type'] == 'object', "Input schema type should be 'object'"
            
            if 'properties' in input_schema:
                assert isinstance(input_schema['properties'], dict), "Input schema properties should be a dictionary"
        
        # Check output schema if present
        if 'output_schema' in tool:
            output_schema = tool['output_schema']
            assert 'type' in output_schema, "Output schema missing 'type' field"
    
    def test_server_can_load_database(self, database_path):
        """Test that the server can successfully load and parse the database."""
        # This test simulates what the server would do when loading the database
        try:
            with open(database_path, 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            # Verify the database contains valid data structures
            assert isinstance(database, dict), "Database should be a dictionary"
            
            # Check that required collections exist and have appropriate data
            for collection_name in ['flights', 'offers', 'stays', 'reviews']:
                if collection_name in database:
                    collection = database[collection_name]
                    assert isinstance(collection, (dict, list)), f"{collection_name} should be dict or list"
                    
                    # If it's a list, check some sample items
                    if isinstance(collection, list) and len(collection) > 0:
                        sample_item = collection[0]
                        assert isinstance(sample_item, dict), f"Items in {collection_name} should be dictionaries"
            
            print(f"✓ Successfully loaded database with {len(database)} top-level keys")
            
        except Exception as e:
            pytest.fail(f"Failed to load database: {e}")
    
    def test_metadata_tools_align_with_server_capabilities(self, metadata_path):
        """Test that metadata tools reflect actual server capabilities."""
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        tools = metadata['tools']
        
        # Expected tool names based on typical flight/stay search server
        expected_tool_patterns = [
            'search_flights', 'search_stays', 'get_offer_details', 
            'get_stay_reviews', 'search_multi_city'
        ]
        
        actual_tool_names = [tool['name'] for tool in tools]
        
        # Check that we have at least some expected tools
        found_expected_tools = any(
            any(pattern in name for pattern in expected_tool_patterns)
            for name in actual_tool_names
        )
        
        assert found_expected_tools, f"No expected tools found. Got: {actual_tool_names}"
        
        print(f"✓ Metadata contains {len(tools)} tools: {actual_tool_names}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])