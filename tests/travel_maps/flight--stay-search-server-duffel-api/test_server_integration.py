"""
Integration tests for the FastMCP server with actual database operations.
"""

import json
import pytest
import sys
import os
from pathlib import Path

# Add the project root to Python path to import server modules
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

class TestServerIntegration:
    """Integration tests for server functionality."""
    
    @pytest.fixture
    def database_path(self):
        """Path to the generated database JSON."""
        return project_root / "generated" / "travel_maps" / "flight--stay-search-server-duffel-api" / "flight__stay_search_server_duffel_api_database.json"
    
    @pytest.fixture
    def server_module_path(self):
        """Path to the server module."""
        return project_root / "generated" / "travel_maps" / "flight--stay-search-server-duffel-api" / "flight__stay_search_server_duffel_api_server.py"
    
    def test_server_module_exists(self, server_module_path):
        """Test that the server module file exists."""
        assert server_module_path.exists(), f"Server module not found at {server_module_path}"
    
    @pytest.mark.skip(reason="fastmcp module not available in test environment")
    def test_server_can_be_imported(self, server_module_path):
        """Test that the server module can be imported."""
        try:
            # Import the server module
            import importlib.util
            spec = importlib.util.spec_from_file_location("flight_stay_search_server", server_module_path)
            server_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(server_module)
            
            # Check that the module has expected attributes
            assert hasattr(server_module, 'database'), "Server module should have 'database' attribute"
            assert hasattr(server_module, 'search_flights'), "Server module should have 'search_flights' function"
            assert hasattr(server_module, 'search_stays'), "Server module should have 'search_stays' function"
            
            print("✓ Server module imported successfully")
            
        except Exception as e:
            pytest.fail(f"Failed to import server module: {e}")
    
    def test_server_database_operations(self, database_path):
        """Test that the server can perform basic database operations."""
        try:
            # Load the database directly
            with open(database_path, 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            # Test flight search simulation
            flights = database.get('flights', [])
            assert isinstance(flights, list), "Flights should be a list"
            
            # Test filtering flights by origin/destination
            test_origin = "CDG"
            test_destination = "LAX"
            matching_flights = [
                flight for flight in flights 
                if flight.get('origin') == test_origin and flight.get('destination') == test_destination
            ]
            
            print(f"✓ Found {len(matching_flights)} flights from {test_origin} to {test_destination}")
            
            # Test offer lookup
            offers = database.get('offers', [])
            assert isinstance(offers, list), "Offers should be a list"
            
            # Test stay search simulation
            stays = database.get('stays', [])
            assert isinstance(stays, list), "Stays should be a list"
            
            test_location = "San Francisco"
            matching_stays = [
                stay for stay in stays
                if stay.get('location') == test_location
            ]
            
            print(f"✓ Found {len(matching_stays)} stays in {test_location}")
            
            # Test review lookup
            reviews = database.get('reviews', [])
            assert isinstance(reviews, list), "Reviews should be a list"
            
            if matching_stays:
                test_stay_id = matching_stays[0]['id']
                stay_reviews = [
                    review for review in reviews
                    if review.get('stay_id') == test_stay_id
                ]
                print(f"✓ Found {len(stay_reviews)} reviews for stay {test_stay_id}")
            
        except Exception as e:
            pytest.fail(f"Failed to perform database operations: {e}")
    
    def test_metadata_tools_correspond_to_database_data(self, database_path):
        """Test that metadata tools can actually work with the database data."""
        try:
            # Load the database
            with open(database_path, 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            # Check that we have data for all expected tool operations
            flights = database.get('flights', [])
            offers = database.get('offers', [])
            stays = database.get('stays', [])
            reviews = database.get('reviews', [])
            
            # Verify we have enough data for meaningful operations
            assert len(flights) >= 10, f"Need at least 10 flights for testing, got {len(flights)}"
            assert len(offers) >= 10, f"Need at least 10 offers for testing, got {len(offers)}"
            assert len(stays) >= 10, f"Need at least 10 stays for testing, got {len(stays)}"
            assert len(reviews) >= 10, f"Need at least 10 reviews for testing, got {len(reviews)}"
            
            # Check data consistency
            if offers:
                # Verify offers reference valid flights
                flight_ids = {flight['id'] for flight in flights}
                offer_flight_ids = {offer['flight_id'] for offer in offers}
                
                # At least some offers should reference valid flights
                valid_offers = offer_flight_ids.intersection(flight_ids)
                assert len(valid_offers) > 0, "No offers reference valid flights"
            
            if reviews:
                # Verify reviews reference valid stays
                stay_ids = {stay['id'] for stay in stays}
                review_stay_ids = {review['stay_id'] for review in reviews}
                
                # At least some reviews should reference valid stays
                valid_reviews = review_stay_ids.intersection(stay_ids)
                assert len(valid_reviews) > 0, "No reviews reference valid stays"
            
            print(f"✓ Database contains sufficient data: {len(flights)} flights, {len(offers)} offers, {len(stays)} stays, {len(reviews)} reviews")
            
        except Exception as e:
            pytest.fail(f"Database data validation failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])