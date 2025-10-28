"""
Integration tests for the complete EdgeOne Geo Location Server system.

Tests the integration between database generation and server functionality.
"""

import json
import os
import sys
import tempfile
import unittest

# Add the generated module path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'travel_maps', 'edgeone-geo-location-server'))

from edgeone_geo_location_server_database import generate_geolocation_database, write_database
from edgeone_geo_location_server_server import get_geolocation, load_geolocation_database


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.database_path = os.path.join(self.temp_dir, 'test_database.json')
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_full_system_integration(self):
        """Test the complete system from database generation to server response."""
        # Generate database
        write_database(self.database_path, count=5, seed=42)
        
        # Verify database file exists
        self.assertTrue(os.path.exists(self.database_path))
        
        # Load and verify database
        with open(self.database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        self.assertIn('geolocation_data', database)
        self.assertIsInstance(database['geolocation_data'], list)
        self.assertEqual(len(database['geolocation_data']), 5)
        
        # Test server functionality with the generated database
        with unittest.mock.patch('edgeone_geo_location_server_server.load_geolocation_database') as mock_load:
            mock_load.return_value = database['geolocation_data']
            
            # Reset global state for test
            import edgeone_geo_location_server_server
            edgeone_geo_location_server_server.current_record_index = 0
            
            # Test multiple calls to verify round-robin behavior
            results = []
            for _ in range(3):
                result = get_geolocation()
                results.append(result)
            
            # Verify all results have correct structure
            required_fields = [
                'ip', 'country', 'country_code', 'region', 'region_name', 
                'city', 'zip', 'lat', 'lon', 'timezone', 'isp', 'org', 'as'
            ]
            
            for result in results:
                for field in required_fields:
                    self.assertIn(field, result)
            
            # Verify round-robin behavior
            ips = [result['ip'] for result in results]
            self.assertEqual(len(set(ips)), 2, "Should have different IPs in round-robin")
    
    def test_geographic_consistency_in_generated_data(self):
        """Test that generated data maintains geographic consistency."""
        # Generate database
        database = generate_geolocation_database(count=10, seed=42)
        records = database['geolocation_data']
        
        # Test specific geographic consistency cases
        for record in records:
            country = record['country']
            city = record['city']
            region = record['region']
            lat = record['lat']
            lon = record['lon']
            
            # Test city-region-country consistency
            if country == "United States":
                if city == "Houston":
                    self.assertEqual(region, "TX", "Houston should be in Texas")
                elif city == "Chicago":
                    self.assertEqual(region, "IL", "Chicago should be in Illinois")
                elif city == "New York":
                    self.assertEqual(region, "NY", "New York should be in New York")
                
                # Test US coordinates
                self.assertGreaterEqual(lat, 25.0)
                self.assertLessEqual(lat, 49.0)
                self.assertGreaterEqual(lon, -125.0)
                self.assertLessEqual(lon, -67.0)
            
            elif country == "United Kingdom":
                if city == "Glasgow":
                    self.assertEqual(region, "SCT", "Glasgow should be in Scotland")
                elif city == "London":
                    self.assertEqual(region, "ENG", "London should be in England")
                elif city == "Cardiff":
                    self.assertEqual(region, "WLS", "Cardiff should be in Wales")
                
                # Test UK coordinates
                self.assertGreaterEqual(lat, 50.0)
                self.assertLessEqual(lat, 59.0)
                self.assertGreaterEqual(lon, -8.0)
                self.assertLessEqual(lon, 2.0)
            
            elif country == "Germany":
                if city == "Munich":
                    self.assertEqual(region, "BY", "Munich should be in Bavaria")
                elif city == "Berlin":
                    self.assertEqual(region, "BE", "Berlin should be in Berlin")
                elif city == "Hamburg":
                    self.assertEqual(region, "HH", "Hamburg should be in Hamburg")
                
                # Test Germany coordinates
                self.assertGreaterEqual(lat, 47.0)
                self.assertLessEqual(lat, 55.0)
                self.assertGreaterEqual(lon, 5.0)
                self.assertLessEqual(lon, 15.0)
            
            elif country == "Australia":
                # Test Australia coordinates (should be in southern hemisphere)
                self.assertGreaterEqual(lat, -45.0)
                self.assertLessEqual(lat, -10.0)
                self.assertGreaterEqual(lon, 110.0)
                self.assertLessEqual(lon, 155.0)
            
            elif country == "Canada":
                # Test Canada coordinates (should be in northern hemisphere)
                self.assertGreaterEqual(lat, 42.0)
                self.assertLessEqual(lat, 70.0)
                self.assertGreaterEqual(lon, -140.0)
                self.assertLessEqual(lon, -52.0)
            
            elif country == "Japan":
                # Test Japan coordinates (should be in East Asia)
                self.assertGreaterEqual(lat, 24.0)
                self.assertLessEqual(lat, 45.0)
                self.assertGreaterEqual(lon, 122.0)
                self.assertLessEqual(lon, 153.0)
    
    def test_data_quality_metrics(self):
        """Test various data quality metrics."""
        database = generate_geolocation_database(count=20, seed=42)
        records = database['geolocation_data']
        
        # Test IP address uniqueness
        ips = [record['ip'] for record in records]
        unique_ips = set(ips)
        self.assertEqual(len(ips), len(unique_ips), "IP addresses should be unique")
        
        # Test coordinate uniqueness
        coordinates = [(record['lat'], record['lon']) for record in records]
        unique_coordinates = set(coordinates)
        self.assertEqual(len(coordinates), len(unique_coordinates), "Coordinates should be unique")
        
        # Test country diversity
        countries = [record['country'] for record in records]
        unique_countries = set(countries)
        self.assertGreaterEqual(len(unique_countries), 5, "Should have good country diversity")
        
        # Test ISP diversity
        isps = [record['isp'] for record in records]
        unique_isps = set(isps)
        self.assertGreaterEqual(len(unique_isps), 3, "Should have good ISP diversity")
    
    def test_error_handling_and_resilience(self):
        """Test system resilience and error handling."""
        # Test with corrupted database file
        with open(self.database_path, 'w', encoding='utf-8') as f:
            f.write('{"corrupted": "data"')  # Invalid JSON
        
        # Server should handle this gracefully
        with unittest.mock.patch('edgeone_geo_location_server_server.load_geolocation_database', 
                               side_effect=json.JSONDecodeError("Expecting property name", "doc", 1)):
            result = get_geolocation()
            
            # Should return default data
            self.assertEqual(result['ip'], "127.0.0.1")
            self.assertEqual(result['country'], "Unknown")
        
        # Test with empty database
        with open(self.database_path, 'w', encoding='utf-8') as f:
            json.dump({"geolocation_data": []}, f)
        
        with unittest.mock.patch('edgeone_geo_location_server_server.load_geolocation_database') as mock_load:
            mock_load.return_value = []
            result = get_geolocation()
            
            # Should return default data
            self.assertEqual(result['ip'], "127.0.0.1")
            self.assertEqual(result['country'], "Unknown")


if __name__ == '__main__':
    unittest.main()