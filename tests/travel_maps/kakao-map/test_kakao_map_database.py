"""
Tests for Kakao Map database generation and validation.
"""

import json
import os
import sys
import unittest
from pathlib import Path

# Add the generated module to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "generated" / "travel_maps" / "kakao-map"))

from kakao_map_database import (
    generate_kakao_map_database,
    validate_database_structure,
    update_database
)


class TestKakaoMapDatabase(unittest.TestCase):
    """Test cases for Kakao Map database functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_database_path = "test_database.json"
        
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_database_path):
            os.remove(self.test_database_path)
    
    def test_generate_database_structure(self):
        """Test that generated database has correct structure."""
        database = generate_kakao_map_database(seed=42, place_count=10)
        
        # Check top-level structure
        self.assertIn("places", database)
        self.assertIsInstance(database["places"], list)
        self.assertEqual(len(database["places"]), 10)
        
        # Check each place structure
        for place in database["places"]:
            self.assertIsInstance(place, dict)
            required_fields = ["id", "name", "location", "type", "description", "rating", "price_range", "tags", "coordinates"]
            for field in required_fields:
                self.assertIn(field, place)
            
            # Check coordinates structure
            self.assertIsInstance(place["coordinates"], dict)
            self.assertIn("latitude", place["coordinates"])
            self.assertIn("longitude", place["coordinates"])
            self.assertIsInstance(place["coordinates"]["latitude"], (int, float))
            self.assertIsInstance(place["coordinates"]["longitude"], (int, float))
    
    def test_generate_database_unique_names(self):
        """Test that generated database has unique place names."""
        database = generate_kakao_map_database(seed=42, place_count=20)
        
        names = [place["name"] for place in database["places"]]
        unique_names = set(names)
        
        self.assertEqual(len(names), len(unique_names), f"Found duplicate names: {names}")
    
    def test_validate_database_structure_valid(self):
        """Test that valid database structure passes validation."""
        valid_database = {
            "places": [
                {
                    "id": "place_001",
                    "name": "Test Place",
                    "location": "Seoul",
                    "type": "restaurant",
                    "description": "Test description",
                    "rating": 4.5,
                    "price_range": "₩₩",
                    "tags": ["test", "local"],
                    "coordinates": {
                        "latitude": 37.5,
                        "longitude": 127.0
                    }
                }
            ]
        }
        
        self.assertTrue(validate_database_structure(valid_database))
    
    def test_validate_database_structure_invalid(self):
        """Test that invalid database structure fails validation."""
        # Missing places key
        invalid_database1 = {}
        self.assertFalse(validate_database_structure(invalid_database1))
        
        # Places is not a list
        invalid_database2 = {"places": "not_a_list"}
        self.assertFalse(validate_database_structure(invalid_database2))
        
        # Missing required field
        invalid_database3 = {
            "places": [
                {
                    "id": "place_001",
                    "name": "Test Place",
                    # Missing location
                    "type": "restaurant",
                    "description": "Test description",
                    "rating": 4.5,
                    "price_range": "₩₩",
                    "tags": ["test", "local"],
                    "coordinates": {
                        "latitude": 37.5,
                        "longitude": 127.0
                    }
                }
            ]
        }
        self.assertFalse(validate_database_structure(invalid_database3))
        
        # Invalid coordinates structure
        invalid_database4 = {
            "places": [
                {
                    "id": "place_001",
                    "name": "Test Place",
                    "location": "Seoul",
                    "type": "restaurant",
                    "description": "Test description",
                    "rating": 4.5,
                    "price_range": "₩₩",
                    "tags": ["test", "local"],
                    "coordinates": "not_a_dict"
                }
            ]
        }
        self.assertFalse(validate_database_structure(invalid_database4))
    
    def test_deterministic_generation(self):
        """Test that database generation is deterministic with same seed."""
        database1 = generate_kakao_map_database(seed=123, place_count=5)
        database2 = generate_kakao_map_database(seed=123, place_count=5)
        
        # Should have same structure and names
        self.assertEqual(len(database1["places"]), len(database2["places"]))
        names1 = [place["name"] for place in database1["places"]]
        names2 = [place["name"] for place in database2["places"]]
        self.assertEqual(names1, names2)
    
    def test_update_database(self):
        """Test updating an existing database."""
        # Create initial database
        initial_database = {
            "places": [
                {
                    "id": "place_001",
                    "name": "Original Place",
                    "location": "Seoul",
                    "type": "restaurant",
                    "description": "Original description",
                    "rating": 4.0,
                    "price_range": "₩₩",
                    "tags": ["original"],
                    "coordinates": {
                        "latitude": 37.5,
                        "longitude": 127.0
                    }
                }
            ]
        }
        
        # Save initial database
        with open(self.test_database_path, 'w', encoding='utf-8') as f:
            json.dump(initial_database, f, indent=2)
        
        # Create updates
        updates = {
            "places": [
                {
                    "id": "place_001",  # Update existing
                    "name": "Updated Place",
                    "location": "Seoul",
                    "type": "restaurant",
                    "description": "Updated description",
                    "rating": 4.5,
                    "price_range": "₩₩₩",
                    "tags": ["updated"],
                    "coordinates": {
                        "latitude": 37.6,
                        "longitude": 127.1
                    }
                },
                {
                    "id": "place_002",  # Add new
                    "name": "New Place",
                    "location": "Busan",
                    "type": "cafe",
                    "description": "New description",
                    "rating": 4.8,
                    "price_range": "₩",
                    "tags": ["new"],
                    "coordinates": {
                        "latitude": 35.1,
                        "longitude": 129.0
                    }
                }
            ]
        }
        
        # Update database
        updated_database = update_database(updates, self.test_database_path)
        
        # Verify updates
        self.assertEqual(len(updated_database["places"]), 2)
        
        # Check updated place
        updated_place = next(p for p in updated_database["places"] if p["id"] == "place_001")
        self.assertEqual(updated_place["name"], "Updated Place")
        self.assertEqual(updated_place["rating"], 4.5)
        
        # Check new place
        new_place = next(p for p in updated_database["places"] if p["id"] == "place_002")
        self.assertEqual(new_place["name"], "New Place")
    
    def test_update_database_validation(self):
        """Test that update_database validates inputs."""
        # Create initial database
        initial_database = {
            "places": [
                {
                    "id": "place_001",
                    "name": "Test Place",
                    "location": "Seoul",
                    "type": "restaurant",
                    "description": "Test description",
                    "rating": 4.5,
                    "price_range": "₩₩",
                    "tags": ["test"],
                    "coordinates": {
                        "latitude": 37.5,
                        "longitude": 127.0
                    }
                }
            ]
        }
        
        # Save initial database
        with open(self.test_database_path, 'w', encoding='utf-8') as f:
            json.dump(initial_database, f, indent=2)
        
        # Test invalid updates
        invalid_updates = {
            "places": [
                {
                    "id": "place_002",
                    "name": "Invalid Place",
                    # Missing location
                    "type": "restaurant",
                    "description": "Invalid description",
                    "rating": 4.5,
                    "price_range": "₩₩",
                    "tags": ["invalid"],
                    "coordinates": {
                        "latitude": 37.5,
                        "longitude": 127.0
                    }
                }
            ]
        }
        
        with self.assertRaises(ValueError):
            update_database(invalid_updates, self.test_database_path)


if __name__ == "__main__":
    unittest.main()