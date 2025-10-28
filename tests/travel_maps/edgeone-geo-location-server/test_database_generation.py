"""
Unit tests for EdgeOne Geo Location Server database generation.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add the generated module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'travel_maps', 'edgeone-geo-location-server'))

from edgeone_geo_location_server_database import (
    generate_realistic_geolocation_data,
    validate_data_contract,
    main
)


class TestDatabaseGeneration(unittest.TestCase):
    """Test cases for database generation functionality."""
    
    def test_generate_realistic_geolocation_data(self):
        """Test that realistic geolocation data is generated correctly."""
        
        # Generate data
        data = generate_realistic_geolocation_data()
        
        # Check basic structure
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Check each record has required fields
        required_fields = {
            "ip", "country", "country_code", "region", "region_name", 
            "city", "zip", "lat", "lon", "timezone", "isp", "org", "as"
        }
        
        for record in data:
            self.assertEqual(set(record.keys()), required_fields)
    
    def test_geographic_consistency(self):
        """Test that geographic data is consistent and realistic."""
        
        data = generate_realistic_geolocation_data()
        
        # Test specific geographic consistency
        for record in data:
            country = record["country"]
            city = record["city"]
            lat = record["lat"]
            lon = record["lon"]
            
            # Test realistic coordinate ranges
            self.assertGreaterEqual(lat, -90)
            self.assertLessEqual(lat, 90)
            self.assertGreaterEqual(lon, -180)
            self.assertLessEqual(lon, 180)
            
            # Test specific geographic consistency
            if country == "United States" and city == "Houston":
                self.assertEqual(record["region"], "TX")
                self.assertEqual(record["region_name"], "Texas")
                # Houston coordinates should be around 29.7, -95.3
                self.assertAlmostEqual(lat, 29.7604, places=1)
                self.assertAlmostEqual(lon, -95.3698, places=1)
            
            elif country == "United Kingdom" and city == "Glasgow":
                self.assertEqual(record["region"], "SCT")
                self.assertEqual(record["region_name"], "Scotland")
                # Glasgow coordinates should be around 55.8, -4.2
                self.assertAlmostEqual(lat, 55.8642, places=1)
                self.assertAlmostEqual(lon, -4.2518, places=1)
            
            elif country == "Australia" and city == "Sydney":
                # Australia should have southern hemisphere latitude
                self.assertLess(lat, 0)
                # Sydney coordinates should be around -33.8, 151.2
                self.assertAlmostEqual(lat, -33.8688, places=1)
                self.assertAlmostEqual(lon, 151.2093, places=1)
            
            elif country == "Canada" and city == "Toronto":
                # Canada should have northern hemisphere latitude
                self.assertGreater(lat, 0)
                # Toronto coordinates should be around 43.6, -79.3
                self.assertAlmostEqual(lat, 43.6532, places=1)
                self.assertAlmostEqual(lon, -79.3832, places=1)
    
    def test_validate_data_contract(self):
        """Test DATA CONTRACT validation."""
        
        # Valid data should pass
        valid_data = generate_realistic_geolocation_data()
        self.assertTrue(validate_data_contract(valid_data))
        
        # Invalid data should fail
        invalid_data = [{"ip": "192.168.1.1"}]  # Missing required fields
        self.assertFalse(validate_data_contract(invalid_data))
        
        # Data with wrong types should fail
        wrong_type_data = [{
            "ip": "192.168.1.1",
            "country": "United States",
            "country_code": "US",
            "region": "CA",
            "region_name": "California",
            "city": "San Francisco",
            "zip": "94102",
            "lat": "37.7749",  # String instead of number
            "lon": -122.4194,
            "timezone": "America/Los_Angeles",
            "isp": "Comcast",
            "org": "Comcast Cable",
            "as": "AS7922"
        }]
        self.assertFalse(validate_data_contract(wrong_type_data))
    
    def test_main_function(self):
        """Test the main database generation function."""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the output path
            test_output_path = os.path.join(temp_dir, "test_database.json")
            
            with patch('edgeone_geo_location_server_database.open', 
                      unittest.mock.mock_open()) as mock_file, \
                 patch('edgeone_geo_location_server_database.print') as mock_print:
                
                # Mock the output path
                with patch('edgeone_geo_location_server_database.output_path', test_output_path):
                    main()
                
                # Check that file was written
                mock_file.assert_called()
                mock_print.assert_called()


if __name__ == "__main__":
    unittest.main()