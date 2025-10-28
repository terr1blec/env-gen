"""
Unit tests for Amadeus MCP Server database generation and validation.
"""

import json
import pytest
from pathlib import Path

# Database path - use forward slashes for cross-platform compatibility
DATABASE_PATH = Path("generated/travel_maps/amadeus-mcp-server/amadeus_mcp_server_database.json")


def test_database_exists():
    """Test that the database file exists."""
    assert DATABASE_PATH.exists(), f"Database file not found at {DATABASE_PATH}"


def test_database_structure():
    """Test that the database has the correct structure."""
    with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    # Check top-level key
    assert "flight_offers" in database, "Database missing 'flight_offers' key"
    
    # Check that flight_offers is an array
    assert isinstance(database["flight_offers"], list), "flight_offers should be a list"
    
    # Check that we have the expected number of records
    assert len(database["flight_offers"]) == 150, f"Expected 150 flight offers, got {len(database['flight_offers'])}"


def test_flight_offer_required_fields():
    """Test that each flight offer has all required fields."""
    with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    required_fields = ["id", "origin", "destination", "departure_date", "price", "airline"]
    
    for i, offer in enumerate(database["flight_offers"]):
        for field in required_fields:
            assert field in offer, f"Flight offer {i} missing required field: {field}"
            assert offer[field] is not None, f"Flight offer {i} has null value for required field: {field}"


def test_flight_offer_data_types():
    """Test that flight offer fields have correct data types."""
    with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    for i, offer in enumerate(database["flight_offers"]):
        # Check string fields
        string_fields = ["id", "origin", "destination", "departure_date", "travel_class", 
                        "currency", "airline", "flight_number", "departure_time", 
                        "arrival_time", "duration"]
        
        for field in string_fields:
            if field in offer and offer[field] is not None:
                assert isinstance(offer[field], str), f"Flight offer {i} field {field} should be string"
        
        # Check numeric fields
        if "price" in offer:
            assert isinstance(offer["price"], (int, float)), f"Flight offer {i} price should be numeric"
        
        if "adults" in offer:
            assert isinstance(offer["adults"], int), f"Flight offer {i} adults should be integer"
        
        if "children" in offer:
            assert isinstance(offer["children"], int), f"Flight offer {i} children should be integer"
        
        if "infants" in offer:
            assert isinstance(offer["infants"], int), f"Flight offer {i} infants should be integer"
        
        if "stops" in offer:
            assert isinstance(offer["stops"], int), f"Flight offer {i} stops should be integer"


def test_airport_codes():
    """Test that origin and destination use valid airport codes."""
    with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    valid_airports = ["JFK", "LAX", "LHR", "CDG", "SFO", "DXB", "FRA", "ORD", "ATL", "DFW"]
    
    for offer in database["flight_offers"]:
        assert offer["origin"] in valid_airports, f"Invalid origin airport: {offer['origin']}"
        assert offer["destination"] in valid_airports, f"Invalid destination airport: {offer['destination']}"


if __name__ == "__main__":
    # Run tests
    test_database_exists()
    test_database_structure()
    test_flight_offer_required_fields()
    test_flight_offer_data_types()
    test_airport_codes()
    print("All database tests passed!")