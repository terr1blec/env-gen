"""
Test module for EdgeOne Geo Location Server database generation.
"""

import json
import sys
import os

# Add the generated module path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'travel_maps', 'edgeone-geo-location-server'))

from edgeone_geo_location_server_database import generate_geolocation_database


def test_database_structure():
    """Test that generated database matches DATA CONTRACT structure."""
    database = generate_geolocation_database(count=5, seed=123)
    
    # Check top-level key
    assert "geolocation_data" in database, "Missing 'geolocation_data' key"
    
    # Check that geolocation_data is a list
    assert isinstance(database["geolocation_data"], list), "geolocation_data should be a list"
    
    # Check each record has required fields
    required_fields = {
        "ip": str,
        "country": str,
        "country_code": str,
        "region": str,
        "region_name": str,
        "city": str,
        "zip": str,
        "lat": (int, float),
        "lon": (int, float),
        "timezone": str,
        "isp": str,
        "org": str,
        "as": str
    }
    
    for record in database["geolocation_data"]:
        for field, expected_type in required_fields.items():
            assert field in record, f"Missing field: {field}"
            assert isinstance(record[field], expected_type), f"Field {field} has wrong type: {type(record[field])}"
    
    print("✓ Database structure test passed")


def test_deterministic_generation():
    """Test that generation is deterministic with the same seed."""
    db1 = generate_geolocation_database(count=3, seed=42)
    db2 = generate_geolocation_database(count=3, seed=42)
    
    assert db1 == db2, "Databases with same seed should be identical"
    
    # Test different seeds produce different results
    db3 = generate_geolocation_database(count=3, seed=43)
    assert db1 != db3, "Databases with different seeds should be different"
    
    print("✓ Deterministic generation test passed")


def test_record_count():
    """Test that the correct number of records are generated."""
    for count in [1, 5, 10]:
        database = generate_geolocation_database(count=count, seed=42)
        assert len(database["geolocation_data"]) == count, f"Expected {count} records, got {len(database['geolocation_data'])}"
    
    print("✓ Record count test passed")


def test_data_quality():
    """Test that generated data has reasonable values."""
    database = generate_geolocation_database(count=10, seed=42)
    
    for record in database["geolocation_data"]:
        # Check IP format
        ip_parts = record["ip"].split(".")
        assert len(ip_parts) == 4, f"Invalid IP format: {record['ip']}"
        for part in ip_parts:
            assert 0 <= int(part) <= 255, f"Invalid IP octet: {part}"
        
        # Check coordinates are within valid ranges
        assert -90 <= record["lat"] <= 90, f"Invalid latitude: {record['lat']}"
        assert -180 <= record["lon"] <= 180, f"Invalid longitude: {record['lon']}"
        
        # Check country code is 2 characters
        assert len(record["country_code"]) == 2, f"Invalid country code: {record['country_code']}"
    
    print("✓ Data quality test passed")


if __name__ == "__main__":
    test_database_structure()
    test_deterministic_generation()
    test_record_count()
    test_data_quality()
    print("\n✅ All database tests passed!")