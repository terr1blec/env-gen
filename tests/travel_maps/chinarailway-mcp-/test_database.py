"""
Test script for China Railway MCP Database
"""

import sys
import os
import json

# Add the generated module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'travel_maps', 'chinarailway-mcp-'))

from chinarailway_mcp__database import generate_database, update_database


def test_database_generation():
    """Test that database generation works correctly"""
    print("Testing database generation...")
    
    # Test with seed for deterministic results
    database = generate_database(seed=42, count=10)
    
    # Check structure
    assert "train_tickets" in database
    assert isinstance(database["train_tickets"], list)
    assert len(database["train_tickets"]) == 10
    
    # Check first ticket structure
    ticket = database["train_tickets"][0]
    required_fields = ["train_number", "departure_station", "arrival_station", 
                      "departure_time", "arrival_time", "duration", "date"]
    
    for field in required_fields:
        assert field in ticket, f"Missing required field: {field}"
    
    # Check nested structures
    assert "seats_available" in ticket
    assert "prices" in ticket
    
    seat_fields = ["business_class", "first_class", "second_class", "hard_seat"]
    for field in seat_fields:
        assert field in ticket["seats_available"]
        assert field in ticket["prices"]
    
    print("✓ Database generation test passed")


def test_deterministic_generation():
    """Test that generation is deterministic with same seed"""
    print("Testing deterministic generation...")
    
    db1 = generate_database(seed=123, count=5)
    db2 = generate_database(seed=123, count=5)
    
    # Should be identical with same seed
    assert db1["train_tickets"][0]["train_number"] == db2["train_tickets"][0]["train_number"]
    assert db1["train_tickets"][0]["departure_station"] == db2["train_tickets"][0]["departure_station"]
    
    print("✓ Deterministic generation test passed")


def test_data_quality():
    """Test that generated data is realistic"""
    print("Testing data quality...")
    
    database = generate_database(seed=42, count=20)
    
    for ticket in database["train_tickets"]:
        # Check train number format
        assert ticket["train_number"][0] in ["G", "D", "C"]
        assert ticket["train_number"][1:].isdigit()
        
        # Check stations are different
        assert ticket["departure_station"] != ticket["arrival_station"]
        
        # Check time format
        assert ":" in ticket["departure_time"]
        assert ":" in ticket["arrival_time"]
        assert ":" in ticket["duration"]
        
        # Check date format
        assert len(ticket["date"].split("-")) == 3
        
        # Check seat availability is reasonable
        for seat_type, count in ticket["seats_available"].items():
            assert 0 <= count <= 50, f"Unreasonable seat count: {count} for {seat_type}"
        
        # Check prices are reasonable
        for seat_type, price in ticket["prices"].items():
            assert price > 0, f"Invalid price: {price} for {seat_type}"
    
    print("✓ Data quality test passed")


if __name__ == "__main__":
    test_database_generation()
    test_deterministic_generation()
    test_data_quality()
    print("\nAll tests passed! ✓")