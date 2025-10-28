"""
Unit tests for the edgeone-geo-location-server dataset generator.

Tests the dataset generation functionality and data structure compliance.
"""

import json
import os
import sys
import unittest

# Add the generated module path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'travel_maps', 'edgeone-geo-location-server'))

from edgeone_geo_location_server_dataset import GeolocationDatasetGenerator, generate_dataset


class TestDatasetGenerator(unittest.TestCase):
    """Test cases for the dataset generator implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Load the test dataset from JSON
        dataset_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', 
            'generated', 'travel_maps', 'edgeone-geo-location-server',
            'edgeone_geo_location_server_dataset.json'
        )
        with open(dataset_path, 'r', encoding='utf-8') as f:
            self.json_data = json.load(f)
    
    def test_generator_initialization(self):
        """Test that the generator initializes correctly."""
        generator = GeolocationDatasetGenerator(seed=42)
        locations = generator.get_all_locations()
        
        self.assertIsInstance(locations, list)
        self.assertGreater(len(locations), 0)
    
    def test_deterministic_generation(self):
        """Test that the same seed produces identical results."""
        generator1 = GeolocationDatasetGenerator(seed=123)
        generator2 = GeolocationDatasetGenerator(seed=123)
        
        locations1 = generator1.get_all_locations()
        locations2 = generator2.get_all_locations()
        
        # Should have same number of locations
        self.assertEqual(len(locations1), len(locations2))
        
        # Should have identical data
        for loc1, loc2 in zip(locations1, locations2):
            self.assertEqual(loc1, loc2)
    
    def test_different_seeds_produce_different_data(self):
        """Test that different seeds produce different coordinate variations."""
        generator1 = GeolocationDatasetGenerator(seed=1)
        generator2 = GeolocationDatasetGenerator(seed=2)
        
        locations1 = generator1.get_all_locations()
        locations2 = generator2.get_all_locations()
        
        # Should have same number of locations
        self.assertEqual(len(locations1), len(locations2))
        
        # Coordinates should be different (due to random variations)
        different_coords = False
        for loc1, loc2 in zip(locations1, locations2):
            if loc1['lat'] != loc2['lat'] or loc1['lon'] != loc2['lon']:
                different_coords = True
                break
        
        self.assertTrue(different_coords, "Different seeds should produce different coordinate variations")
    
    def test_get_all_locations(self):
        """Test that get_all_locations returns all generated locations."""
        generator = GeolocationDatasetGenerator(seed=42)
        locations = generator.get_all_locations()
        
        self.assertIsInstance(locations, list)
        self.assertEqual(len(locations), 8)  # Should have 8 locations
        
        # All locations should be dictionaries
        for location in locations:
            self.assertIsInstance(location, dict)
    
    def test_get_random_location(self):
        """Test that get_random_location returns a valid location."""
        generator = GeolocationDatasetGenerator(seed=42)
        
        # Test multiple random selections
        for _ in range(5):
            location = generator.get_random_location()
            self.assertIsInstance(location, dict)
            self._validate_location_structure(location)
    
    def test_get_location_by_index(self):
        """Test that get_location_by_index returns correct locations."""
        generator = GeolocationDatasetGenerator(seed=42)
        
        # Test valid indices
        for i in range(8):
            location = generator.get_location_by_index(i)
            self.assertIsInstance(location, dict)
            self._validate_location_structure(location)
        
        # Test invalid indices
        self.assertIsNone(generator.get_location_by_index(-1))
        self.assertIsNone(generator.get_location_by_index(10))
    
    def test_generate_dataset_function(self):
        """Test the generate_dataset function."""
        data = generate_dataset(seed=42)
        
        self.assertIsInstance(data, dict)
        self.assertIn('geolocation_data', data)
        self.assertIsInstance(data['geolocation_data'], list)
        self.assertEqual(len(data['geolocation_data']), 8)
    
    def test_json_dataset_structure(self):
        """Test that the JSON dataset has the correct structure."""
        # Check top-level structure
        self.assertIn('geolocation_data', self.json_data)
        self.assertIsInstance(self.json_data['geolocation_data'], list)
        
        # Check that we have the expected number of locations
        self.assertEqual(len(self.json_data['geolocation_data']), 8)
    
    def test_json_dataset_required_fields(self):
        """Test that all JSON dataset locations have all required fields."""
        for location in self.json_data['geolocation_data']:
            self._validate_location_structure(location)
    
    def test_json_dataset_field_types(self):
        """Test that all JSON dataset fields have correct types."""
        for location in self.json_data['geolocation_data']:
            self._validate_field_types(location)
    
    def test_json_dataset_realistic_values(self):
        """Test that the dataset contains realistic values."""
        for location in self.json_data['geolocation_data']:
            # Check IP address format
            self.assertTrue(self._is_valid_ip_format(location['ip']))
            
            # Check coordinate ranges
            self.assertGreaterEqual(location['lat'], -90)
            self.assertLessEqual(location['lat'], 90)
            self.assertGreaterEqual(location['lon'], -180)
            self.assertLessEqual(location['lon'], 180)
            
            # Check country code format
            self.assertEqual(len(location['country_code']), 2)
            self.assertTrue(location['country_code'].isalpha())
    
    def _validate_location_structure(self, location):
        """Validate that a location has all required fields."""
        required_fields = [
            'ip', 'country', 'country_code', 'region', 'region_name', 
            'city', 'zip', 'lat', 'lon', 'timezone', 'isp', 'org', 'as'
        ]
        for field in required_fields:
            self.assertIn(field, location, f"Location missing field: {field}")
            self.assertIsNotNone(location[field], f"Location field {field} is None")
    
    def _validate_field_types(self, location):
        """Validate that all location fields have correct types."""
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
    
    def _is_valid_ip_format(self, ip):
        """Check if an IP address has a valid format."""
        # Simple format check - should contain dots and numbers
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        for part in parts:
            if not part.isdigit():
                return False
            num = int(part)
            if num < 0 or num > 255:
                return False
        
        return True


if __name__ == '__main__':
    unittest.main()