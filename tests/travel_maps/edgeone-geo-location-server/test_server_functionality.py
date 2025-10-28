"""
Unit tests for EdgeOne Geo Location Server functionality.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

# Add the generated module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'travel_maps', 'edgeone-geo-location-server'))

from edgeone_geo_location_server_server import GeoLocationDatabase


class TestGeoLocationDatabase(unittest.TestCase):
    """Test cases for GeoLocationDatabase class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_database_path = os.path.join(self.temp_dir.name, "test_database.json")
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def create_test_database(self, data):
        """Create a test database file."""
        database = {"geolocation_data": data}
        with open(self.test_database_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2)
    
    def test_load_database_valid(self):
        """Test loading a valid database."""
        
        test_data = [
            {
                "ip": "192.168.1.1",
                "country": "United States",
                "country_code": "US",
                "region": "CA",
                "region_name": "California",
                "city": "San Francisco",
                "zip": "94102",
                "lat": 37.7749,
                "lon": -122.4194,
                "timezone": "America/Los_Angeles",
                "isp": "Comcast",
                "org": "Comcast Cable",
                "as": "AS7922"
            }
        ]
        
        self.create_test_database(test_data)
        
        with patch('edgeone_geo_location_server_server.os.path.join', 
                  return_value=self.test_database_path):
            database = GeoLocationDatabase()
            
            self.assertEqual(len(database.data), 1)
            self.assertEqual(database.data[0]["city"], "San Francisco")
    
    def test_load_database_invalid_structure(self):
        """Test loading database with invalid structure."""
        
        # Create invalid database (missing geolocation_data key)
        invalid_database = {"wrong_key": []}
        with open(self.test_database_path, 'w', encoding='utf-8') as f:
            json.dump(invalid_database, f, indent=2)
        
        with patch('edgeone_geo_location_server_server.os.path.join', 
                  return_value=self.test_database_path):
            database = GeoLocationDatabase()
            
            # Should fall back to default data
            self.assertGreater(len(database.data), 0)
            self.assertEqual(database.data[0]["city"], "San Francisco")
    
    def test_load_database_file_not_found(self):
        """Test behavior when database file doesn't exist."""
        
        with patch('edgeone_geo_location_server_server.os.path.exists', return_value=False):
            database = GeoLocationDatabase()
            
            # Should fall back to default data
            self.assertGreater(len(database.data), 0)
            self.assertEqual(database.data[0]["city"], "San Francisco")
    
    def test_get_random_location(self):
        """Test random location selection."""
        
        test_data = [
            {
                "ip": "192.168.1.1",
                "country": "United States",
                "country_code": "US",
                "region": "CA",
                "region_name": "California",
                "city": "San Francisco",
                "zip": "94102",
                "lat": 37.7749,
                "lon": -122.4194,
                "timezone": "America/Los_Angeles",
                "isp": "Comcast",
                "org": "Comcast Cable",
                "as": "AS7922"
            },
            {
                "ip": "192.168.1.2",
                "country": "United Kingdom",
                "country_code": "GB",
                "region": "LND",
                "region_name": "London",
                "city": "London",
                "zip": "SW1A 1AA",
                "lat": 51.5074,
                "lon": -0.1278,
                "timezone": "Europe/London",
                "isp": "BT",
                "org": "British Telecom",
                "as": "AS2856"
            }
        ]
        
        self.create_test_database(test_data)
        
        with patch('edgeone_geo_location_server_server.os.path.join', 
                  return_value=self.test_database_path):
            database = GeoLocationDatabase()
            
            # Test multiple random selections
            locations = set()
            for _ in range(10):
                location = database.get_random_location()
                self.assertIsNotNone(location)
                locations.add(location["city"])
            
            # Should eventually get both cities (random selection)
            self.assertEqual(len(locations), 2)
    
    def test_get_location_by_ip_prefix(self):
        """Test IP prefix-based location selection."""
        
        test_data = [
            {
                "ip": "192.168.1.1",
                "country": "United States",
                "country_code": "US",
                "region": "CA",
                "region_name": "California",
                "city": "San Francisco",
                "zip": "94102",
                "lat": 37.7749,
                "lon": -122.4194,
                "timezone": "America/Los_Angeles",
                "isp": "Comcast",
                "org": "Comcast Cable",
                "as": "AS7922"
            },
            {
                "ip": "10.0.0.1",
                "country": "United Kingdom",
                "country_code": "GB",
                "region": "LND",
                "region_name": "London",
                "city": "London",
                "zip": "SW1A 1AA",
                "lat": 51.5074,
                "lon": -0.1278,
                "timezone": "Europe/London",
                "isp": "BT",
                "org": "British Telecom",
                "as": "AS2856"
            }
        ]
        
        self.create_test_database(test_data)
        
        with patch('edgeone_geo_location_server_server.os.path.join', 
                  return_value=self.test_database_path):
            database = GeoLocationDatabase()
            
            # Test IP prefix matching
            location = database.get_location_by_ip_prefix("192")
            self.assertIsNotNone(location)
            self.assertEqual(location["city"], "San Francisco")
            
            # Test no matching prefix (should return random)
            location = database.get_location_by_ip_prefix("172")
            self.assertIsNotNone(location)
    
    def test_empty_database(self):
        """Test behavior with empty database."""
        
        self.create_test_database([])
        
        with patch('edgeone_geo_location_server_server.os.path.join', 
                  return_value=self.test_database_path):
            database = GeoLocationDatabase()
            
            # Should fall back to default data
            self.assertGreater(len(database.data), 0)


class TestServerIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests for the server functionality."""
    
    async def test_tool_listing(self):
        """Test that tools are listed correctly."""
        
        from edgeone_geo_location_server_server import handle_list_tools
        
        tools = await handle_list_tools()
        
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0].name, "get_geolocation")
        self.assertEqual(tools[0].description, "Get the user's geolocation information")
    
    async def test_tool_execution(self):
        """Test tool execution with mocked database."""
        
        from edgeone_geo_location_server_server import handle_call_tool
        
        # Mock the global database
        mock_database = MagicMock()
        mock_database.get_location_by_ip_prefix.return_value = {
            "ip": "192.168.1.1",
            "country": "United States",
            "country_code": "US",
            "region": "CA",
            "region_name": "California",
            "city": "San Francisco",
            "zip": "94102",
            "lat": 37.7749,
            "lon": -122.4194,
            "timezone": "America/Los_Angeles",
            "isp": "Comcast",
            "org": "Comcast Cable",
            "as": "AS7922"
        }
        
        with patch('edgeone_geo_location_server_server.database', mock_database):
            result = await handle_call_tool("get_geolocation", {})
            
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].type, "text")
            self.assertIn("Geolocation Information", result[0].text)
            self.assertIn("San Francisco", result[0].text)
    
    async def test_unknown_tool(self):
        """Test behavior with unknown tool."""
        
        from edgeone_geo_location_server_server import handle_call_tool
        
        with self.assertRaises(ValueError):
            await handle_call_tool("unknown_tool", {})


if __name__ == "__main__":
    unittest.main()