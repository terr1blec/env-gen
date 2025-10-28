"""
Unit tests for edgeone-geo-location-server implementation.

Tests the get_geolocation tool functionality and data structure compliance.
"""

import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the generated module path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'travel_maps', 'edgeone-geo-location-server'))

from edgeone_geo_location_server_server import get_geolocation


class TestEdgeOneGeoLocationServer(unittest.TestCase):
    """Test cases for the edgeone-geo-location-server implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Load the test dataset
        dataset_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', 
            'generated', 'travel_maps', 'edgeone-geo-location-server',
            'edgeone_geo_location_server_dataset.json'
        )
        with open(dataset_path, 'r', encoding='utf-8') as f:
            self.test_data = json.load(f)
    
    def test_get_geolocation_returns_valid_structure(self):
        """Test that get_geolocation returns a valid geolocation structure."""
        result = get_geolocation()
        
        # Check that result is a dictionary
        self.assertIsInstance(result, dict)
        
        # Check all required fields are present
        required_fields = [
            'ip', 'country', 'country_code', 'region', 'region_name', 
            'city', 'zip', 'lat', 'lon', 'timezone', 'isp', 'org', 'as'
        ]
        for field in required_fields:
            self.assertIn(field, result, f"Missing required field: {field}")
    
    def test_get_geolocation_field_types(self):
        """Test that all fields have the correct data types."""
        result = get_geolocation()
        
        # Check field types
        self.assertIsInstance(result['ip'], str)
        self.assertIsInstance(result['country'], str)
        self.assertIsInstance(result['country_code'], str)
        self.assertIsInstance(result['region'], str)
        self.assertIsInstance(result['region_name'], str)
        self.assertIsInstance(result['city'], str)
        self.assertIsInstance(result['zip'], str)
        self.assertIsInstance(result['lat'], (int, float))
        self.assertIsInstance(result['lon'], (int, float))
        self.assertIsInstance(result['timezone'], str)
        self.assertIsInstance(result['isp'], str)
        self.assertIsInstance(result['org'], str)
        self.assertIsInstance(result['as'], str)
    
    def test_get_geolocation_returns_data_from_dataset(self):
        """Test that returned data comes from the generated dataset."""
        result = get_geolocation()
        
        # Check that the result matches one of the dataset entries
        dataset_locations = self.test_data['geolocation_data']
        
        # Find matching location in dataset
        matching_location = None
        for location in dataset_locations:
            if all(location.get(field) == result.get(field) for field in ['ip', 'country', 'city']):
                matching_location = location
                break
        
        self.assertIsNotNone(matching_location, "Returned location not found in dataset")
    
    def test_get_geolocation_round_robin_behavior(self):
        """Test that consecutive calls return different locations (round-robin)."""
        # Call multiple times and collect results
        results = []
        for _ in range(3):
            results.append(get_geolocation())
        
        # Check that we got different IP addresses (indicating different locations)
        ips = [result['ip'] for result in results]
        unique_ips = set(ips)
        
        # Should have at least 2 different IPs in 3 calls (due to round-robin)
        self.assertGreaterEqual(len(unique_ips), 2, "Round-robin not working - got same IPs repeatedly")
    
    def test_get_geolocation_no_parameters(self):
        """Test that get_geolocation accepts no parameters."""
        # This should not raise any errors
        result = get_geolocation()
        self.assertIsNotNone(result)
    
    def test_dataset_structure_compliance(self):
        """Test that the dataset follows the DATA CONTRACT structure."""
        # Check top-level key
        self.assertIn('geolocation_data', self.test_data)
        
        # Check that geolocation_data is a list
        self.assertIsInstance(self.test_data['geolocation_data'], list)
        
        # Check each location in the dataset
        for location in self.test_data['geolocation_data']:
            self.assertIsInstance(location, dict)
            
            # Check all required fields
            required_fields = [
                'ip', 'country', 'country_code', 'region', 'region_name', 
                'city', 'zip', 'lat', 'lon', 'timezone', 'isp', 'org', 'as'
            ]
            for field in required_fields:
                self.assertIn(field, location, f"Dataset location missing field: {field}")
    
    def test_dataset_field_types(self):
        """Test that all dataset fields have correct types."""
        for location in self.test_data['geolocation_data']:
            self.assertIsInstance(location['ip'], str)
            self.assertIsInstance(location['country'], str)
            self.assertIsInstance(location['country_code'], str)
            self.assertIsInstance(location['region'], str)
            self.assertIsInstance(location['region_name'], str)
            self.assertIsInstance(location['city'], str)
            self.assertIsInstance(location['zip'], str)
            self.assertIsInstance(location['lat'], (int, float))
            self.assertIsInstance(location['lon'], (int, float))
            self.assertIsInstance(location['timezone'], str)
            self.assertIsInstance(location['isp'], str)
            self.assertIsInstance(location['org'], str)
            self.assertIsInstance(location['as'], str)


if __name__ == '__main__':
    unittest.main()