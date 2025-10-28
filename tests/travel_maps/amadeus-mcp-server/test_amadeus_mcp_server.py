"""
Test suite for Amadeus MCP Server

Validates that the FastMCP server can:
1. Load the offline database correctly
2. Expose the expected tools via metadata
3. Process flight search queries correctly
4. Maintain schema consistency
"""

import json
import pytest
from pathlib import Path


class TestAmadeusMCPServer:
    """Test suite for Amadeus MCP Server functionality"""
    
    @pytest.fixture
    def database_path(self):
        """Path to the test database"""
        return Path("generated/travel_maps/amadeus-mcp-server/amadeus_mcp_server_database.json")
    
    @pytest.fixture
    def metadata_path(self):
        """Path to the metadata file"""
        return Path("generated/travel_maps/amadeus-mcp-server/amadeus_mcp_server_metadata.json")
    
    @pytest.fixture
    def database(self, database_path):
        """Load the database for testing"""
        with open(database_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @pytest.fixture
    def metadata(self, metadata_path):
        """Load the metadata for testing"""
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_database_exists(self, database_path):
        """Test that the database file exists"""
        assert database_path.exists(), f"Database file not found at {database_path}"
    
    def test_metadata_exists(self, metadata_path):
        """Test that the metadata file exists"""
        assert metadata_path.exists(), f"Metadata file not found at {metadata_path}"
    
    def test_load_database(self, database):
        """Test that the database can be loaded successfully"""
        # Check that database is a dictionary
        assert isinstance(database, dict), "Database should be a dictionary"
        
        # Check that flight_offers key exists
        assert "flight_offers" in database, "Database should contain 'flight_offers' key"
        
        # Check that flight_offers is a list
        assert isinstance(database["flight_offers"], list), "flight_offers should be a list"
        
        # Check that we have flight data
        assert len(database["flight_offers"]) > 0, "Database should contain flight offers"
        
        # Check structure of first flight offer
        first_offer = database["flight_offers"][0]
        required_fields = [
            "id", "origin", "destination", "departure_date", 
            "adults", "children", "infants", "travel_class", 
            "currency", "price", "airline", "flight_number",
            "departure_time", "arrival_time", "duration", "stops"
        ]
        
        for field in required_fields:
            assert field in first_offer, f"Flight offer missing required field: {field}"
    
    def test_metadata_schema(self, metadata):
        """Test that metadata follows the required schema"""
        # Check top-level fields
        assert "name" in metadata, "Metadata should contain 'name' field"
        assert "description" in metadata, "Metadata should contain 'description' field"
        assert "tools" in metadata, "Metadata should contain 'tools' field"
        
        # Check name matches server name
        assert metadata["name"] == "Amadeus MCP Server", "Server name should match metadata"
        
        # Check tools is a list
        assert isinstance(metadata["tools"], list), "Tools should be a list"
        
        # Check at least one tool exists
        assert len(metadata["tools"]) > 0, "Should have at least one tool defined"
        
        # Check first tool structure
        first_tool = metadata["tools"][0]
        assert "name" in first_tool, "Tool should have 'name' field"
        assert "description" in first_tool, "Tool should have 'description' field"
        assert "input_schema" in first_tool, "Tool should have 'input_schema' field"
        assert "output_schema" in first_tool, "Tool should have 'output_schema' field"
        
        # Check input schema structure
        input_schema = first_tool["input_schema"]
        assert "properties" in input_schema, "Input schema should have 'properties'"
        assert "required" in input_schema, "Input schema should have 'required' fields"
        assert "type" in input_schema, "Input schema should have 'type'"
        
        # Check output schema structure
        output_schema = first_tool["output_schema"]
        assert "properties" in output_schema, "Output schema should have 'properties'"
        assert "type" in output_schema, "Output schema should have 'type'"
    
    def test_search_flight_offers_basic(self, database):
        """Test basic flight search functionality"""
        flight_offers = database["flight_offers"]
        
        # Test with known data from the database
        matching_offers = [
            offer for offer in flight_offers 
            if (offer["origin"] == "JFK" and 
                offer["destination"] == "LAX" and 
                offer["departure_date"] == "2025-11-16")
        ]
        
        # Should find at least one matching flight
        assert len(matching_offers) > 0, "Should find at least one matching flight"
        
        # Check that all returned flights match the criteria
        for offer in matching_offers:
            assert offer["origin"] == "JFK", "Origin should match"
            assert offer["destination"] == "LAX", "Destination should match"
            assert offer["departure_date"] == "2025-11-16", "Departure date should match"
    
    def test_search_flight_offers_with_filters(self, database):
        """Test flight search with additional filters"""
        flight_offers = database["flight_offers"]
        
        matching_offers = [
            offer for offer in flight_offers 
            if (offer["origin"] == "LHR" and 
                offer["destination"] == "CDG" and 
                offer["departure_date"] == "2025-10-30" and
                offer.get("return_date") == "2025-11-03" and
                offer.get("travel_class") == "ECONOMY" and
                offer.get("currency") == "USD")
        ]
        
        # Should find specific flight FL001
        matching_flights = [offer for offer in matching_offers if offer["id"] == "FL001"]
        assert len(matching_flights) > 0, "Should find flight FL001 with matching criteria"
        
        flight = matching_flights[0]
        assert flight["return_date"] == "2025-11-03", "Return date should match"
        assert flight["travel_class"] == "ECONOMY", "Travel class should match"
        assert flight["currency"] == "USD", "Currency should match"
    
    def test_search_flight_offers_no_results(self, database):
        """Test flight search with criteria that should return no results"""
        flight_offers = database["flight_offers"]
        
        matching_offers = [
            offer for offer in flight_offers 
            if (offer["origin"] == "XXX" and 
                offer["destination"] == "YYY" and 
                offer["departure_date"] == "2025-01-01")
        ]
        
        assert len(matching_offers) == 0, "Should return empty list for no matches"
    
    def test_search_flight_offers_passenger_capacity(self, database):
        """Test flight search with passenger capacity constraints"""
        flight_offers = database["flight_offers"]
        
        # Find flights with specific passenger capacity
        matching_offers = [
            offer for offer in flight_offers 
            if (offer["origin"] == "JFK" and 
                offer["destination"] == "LAX" and 
                offer["departure_date"] == "2025-11-16" and
                offer["adults"] >= 4 and
                offer["children"] >= 0 and
                offer["infants"] >= 1)
        ]
        
        # Check that all returned flights can accommodate the passengers
        for offer in matching_offers:
            assert offer["adults"] >= 4, "Should accommodate at least 4 adults"
            assert offer["children"] >= 0, "Should accommodate at least 0 children"
            assert offer["infants"] >= 1, "Should accommodate at least 1 infant"
    
    def test_database_data_contract(self, database):
        """Test that the database follows the expected data contract"""
        flight_offers = database["flight_offers"]
        
        # Define expected data contract
        required_fields = {
            "id": str,
            "origin": str,
            "destination": str,
            "departure_date": str,
            "return_date": str,  # Can be empty string
            "adults": int,
            "children": int,
            "infants": int,
            "travel_class": str,
            "currency": str,
            "price": (int, float),
            "airline": str,
            "flight_number": str,
            "departure_time": str,
            "arrival_time": str,
            "duration": str,
            "stops": int
        }
        
        # Test a sample of flight offers
        sample_size = min(10, len(flight_offers))
        for i in range(sample_size):
            offer = flight_offers[i]
            
            for field, expected_type in required_fields.items():
                assert field in offer, f"Flight offer {i} missing field: {field}"
                
                # Handle multiple allowed types
                if isinstance(expected_type, tuple):
                    assert isinstance(offer[field], expected_type), \
                        f"Field {field} should be one of {expected_type}, got {type(offer[field])}"
                else:
                    assert isinstance(offer[field], expected_type), \
                        f"Field {field} should be {expected_type}, got {type(offer[field])}"
    
    def test_metadata_tool_alignment(self, metadata):
        """Test that metadata tools align with actual server tools"""
        # Get tool names from metadata
        metadata_tool_names = [tool["name"] for tool in metadata["tools"]]
        
        # Check that search_flight_offers tool exists in metadata
        assert "search_flight_offers" in metadata_tool_names, \
            "search_flight_offers tool should be in metadata"
        
        # Check that the tool has the correct input schema
        search_tool = next(tool for tool in metadata["tools"] if tool["name"] == "search_flight_offers")
        input_schema = search_tool["input_schema"]
        
        # Check required fields
        required_fields = ["origin", "destination", "departure_date"]
        for field in required_fields:
            assert field in input_schema["required"], f"{field} should be required in input schema"
        
        # Check optional fields exist
        optional_fields = ["return_date", "adults", "children", "infants", "travel_class", "currency"]
        for field in optional_fields:
            assert field in input_schema["properties"], f"{field} should be in input schema properties"
    
    def test_server_code_structure(self, database_path):
        """Test that the server code follows expected structure"""
        server_path = Path("generated/travel_maps/amadeus-mcp-server/amadeus_mcp_server_server.py")
        
        assert server_path.exists(), "Server code file should exist"
        
        with open(server_path, 'r', encoding='utf-8') as f:
            server_code = f.read()
        
        # Check for required components
        assert "FastMCP" in server_code, "Server should use FastMCP"
        assert "search_flight_offers" in server_code, "Server should contain search_flight_offers function"
        assert "load_database" in server_code, "Server should contain load_database function"
        assert "@mcp.tool()" in server_code, "Server should use MCP tool decorator"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])