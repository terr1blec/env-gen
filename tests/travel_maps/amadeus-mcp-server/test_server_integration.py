"""
Integration tests for Amadeus MCP Server functionality.
"""

import sys
import os
from pathlib import Path

# Add the server module to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "generated" / "travel_maps" / "amadeus-mcp-server"))

from amadeus_mcp_server_server import search_flight_offers, load_database


def test_load_database():
    """Test that the database loads correctly."""
    database = load_database()
    
    assert database is not None, "Database should not be None"
    assert "flight_offers" in database, "Database should contain flight_offers key"
    assert isinstance(database["flight_offers"], list), "flight_offers should be a list"
    
    print(f"✓ Database loaded successfully with {len(database['flight_offers'])} flight offers")


def test_search_exact_match():
    """Test searching for flights with exact matches."""
    # Test a known route from the database
    result = search_flight_offers(
        origin="JFK",
        destination="LAX", 
        departure_date="2025-11-17"
    )
    
    assert "flight_offers" in result, "Result should contain flight_offers key"
    assert isinstance(result["flight_offers"], list), "flight_offers should be a list"
    
    # Check that we found the specific flight
    matching_flights = [f for f in result["flight_offers"] if f.get("flight_number") == "AM158"]
    assert len(matching_flights) > 0, "Should find flight AM158 from JFK to LAX on 2025-11-17"
    
    print(f"✓ Found {len(result['flight_offers'])} flights for JFK->LAX on 2025-11-17")


def test_search_with_return_date():
    """Test searching for round-trip flights."""
    result = search_flight_offers(
        origin="LHR",
        destination="CDG",
        departure_date="2025-10-30",
        return_date="2025-11-03"
    )
    
    assert "flight_offers" in result, "Result should contain flight_offers key"
    
    # Check that we found flights with matching return date
    matching_flights = [f for f in result["flight_offers"] if f.get("return_date") == "2025-11-03"]
    assert len(matching_flights) > 0, "Should find flights with return date 2025-11-03"
    
    print(f"✓ Found {len(matching_flights)} round-trip flights for LHR->CDG")


def test_search_with_travel_class():
    """Test searching for flights by travel class."""
    result = search_flight_offers(
        origin="LAX",
        destination="LHR",
        departure_date="2025-11-09",
        travel_class="BUSINESS"
    )
    
    assert "flight_offers" in result, "Result should contain flight_offers key"
    
    # Check that all returned flights match the requested class
    for flight in result["flight_offers"]:
        assert flight.get("travel_class") == "BUSINESS", "All flights should be BUSINESS class"
    
    print(f"✓ Found {len(result['flight_offers'])} BUSINESS class flights for LAX->LHR")


def test_search_no_results():
    """Test searching for non-existent flights."""
    result = search_flight_offers(
        origin="JFK",
        destination="CDG",
        departure_date="2025-12-31"  # Date that doesn't exist in database
    )
    
    assert "flight_offers" in result, "Result should contain flight_offers key"
    assert len(result["flight_offers"]) == 0, "Should find no flights for non-existent date"
    
    print("✓ Correctly returned empty results for non-existent flight")


def test_search_with_passengers():
    """Test searching for flights with passenger requirements."""
    result = search_flight_offers(
        origin="LAX",
        destination="CDG",
        departure_date="2025-11-27",
        adults=4,
        children=1,
        infants=0
    )
    
    assert "flight_offers" in result, "Result should contain flight_offers key"
    
    # Check that flights have sufficient capacity
    for flight in result["flight_offers"]:
        assert flight.get("adults", 0) >= 4, "Flight should have at least 4 adult capacity"
        assert flight.get("children", 0) >= 1, "Flight should have at least 1 child capacity"
    
    print(f"✓ Found {len(result['flight_offers'])} flights with sufficient passenger capacity")


if __name__ == "__main__":
    print("Running Amadeus MCP Server integration tests...")
    
    try:
        test_load_database()
        test_search_exact_match()
        test_search_with_return_date()
        test_search_with_travel_class()
        test_search_no_results()
        test_search_with_passengers()
        
        print("\n✅ All integration tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)