#!/usr/bin/env python3
"""
Test script to verify the database generation works correctly.
"""

import sys
import os

# Add the generated module path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'travel_maps', 'national-parks-server'))

from national_parks_server_database import generate_database, get_database_path

def test_database_generation():
    """Test that database generation works correctly."""
    print("Testing database generation...")
    
    # Generate database with seed for reproducibility
    database = generate_database(seed=42)
    
    # Verify all required top-level keys are present
    required_keys = ["parks", "park_details", "alerts", "visitor_centers", "campgrounds", "events"]
    for key in required_keys:
        assert key in database, f"Missing required key: {key}"
        assert isinstance(database[key], list), f"{key} should be a list"
        print(f"✓ {key}: {len(database[key])} items")
    
    # Verify park count
    assert len(database["parks"]) == 15, f"Expected 15 parks, got {len(database['parks'])}"
    
    # Verify database path resolution
    db_path = get_database_path()
    print(f"✓ Database path: {db_path}")
    assert os.path.isabs(db_path), "Database path should be absolute"
    
    print("\n✅ All database generation tests passed!")
    return True

if __name__ == "__main__":
    test_database_generation()