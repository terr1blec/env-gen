"""
Tests for Kakao Map server functionality.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the generated module to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "generated" / "travel_maps" / "kakao-map"))

from kakao_map_server import kakao_map_place_recommender, load_database


class TestKakaoMapServer(unittest.TestCase):
    """Test cases for Kakao Map server functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_database = {
            "places": [
                {
                    "id": "place_001",
                    "name": "Seoul Restaurant",
                    "location": "Gangnam, Seoul",
                    "type": "restaurant",
                    "description": "Authentic Korean cuisine",
                    "rating": 4.5,
                    "price_range": "₩₩",
                    "tags": ["korean", "traditional", "local"],
                    "coordinates": {
                        "latitude": 37.5,
                        "longitude": 127.0
                    }
                },
                {
                    "id": "place_002",
                    "name": "Busan Cafe",
                    "location": "Haeundae, Busan",
                    "type": "cafe",
                    "description": "Cozy coffee shop",
                    "rating": 4.8,
                    "price_range": "₩",
                    "tags": ["coffee", "dessert", "relaxing"],
                    "coordinates": {
                        "latitude": 35.1,
                        "longitude": 129.0
                    }
                },
                {
                    "id": "place_003",
                    "name": "Jeju Attraction",
                    "location": "Jeju City, Jeju",
                    "type": "attraction",
                    "description": "Beautiful scenic spot",
                    "rating": 4.2,
                    "price_range": "₩",
                    "tags": ["tourist", "scenic", "cultural"],
                    "coordinates": {
                        "latitude": 33.4,
                        "longitude": 126.5
                    }
                },
                {
                    "id": "place_004",
                    "name": "Seoul Shopping",
                    "location": "Myeongdong, Seoul",
                    "type": "shopping",
                    "description": "Premier shopping destination",
                    "rating": 4.7,
                    "price_range": "₩₩₩",
                    "tags": ["shopping", "fashion", "luxury"],
                    "coordinates": {
                        "latitude": 37.6,
                        "longitude": 127.0
                    }
                }
            ]
        }
        
        # Create temporary database file
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_database.json")
        
        with open(self.test_db_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_database, f, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('kakao_map_server.DATABASE_PATH')
    def test_load_database_success(self, mock_db_path):
        """Test successful database loading."""
        mock_db_path.__str__ = lambda x: self.test_db_path
        
        database = load_database()
        
        self.assertIn("places", database)
        self.assertEqual(len(database["places"]), 4)
        self.assertEqual(database["places"][0]["name"], "Seoul Restaurant")
    
    @patch('kakao_map_server.DATABASE_PATH')
    def test_load_database_file_not_found(self, mock_db_path):
        """Test database loading when file doesn't exist."""
        mock_db_path.__str__ = lambda x: "/nonexistent/path/database.json"
        
        with self.assertRaises(FileNotFoundError):
            load_database()
    
    @patch('kakao_map_server.DATABASE_PATH')
    def test_load_database_invalid_json(self, mock_db_path):
        """Test database loading with invalid JSON."""
        # Create invalid JSON file
        invalid_db_path = os.path.join(self.temp_dir, "invalid_database.json")
        with open(invalid_db_path, 'w', encoding='utf-8') as f:
            f.write("invalid json content")
        
        mock_db_path.__str__ = lambda x: invalid_db_path
        
        with self.assertRaises(ValueError):
            load_database()
    
    @patch('kakao_map_server.DATABASE_PATH')
    def test_load_database_invalid_structure(self, mock_db_path):
        """Test database loading with invalid structure."""
        # Create database with invalid structure
        invalid_database = {
            "invalid_key": "invalid_value"
        }
        
        invalid_db_path = os.path.join(self.temp_dir, "invalid_structure_database.json")
        with open(invalid_db_path, 'w', encoding='utf-8') as f:
            json.dump(invalid_database, f, indent=2)
        
        mock_db_path.__str__ = lambda x: invalid_db_path
        
        with self.assertRaises(ValueError):
            load_database()
    
    @patch('kakao_map_server.load_database')
    def test_recommender_location_match(self, mock_load_database):
        """Test recommender with location matching."""
        mock_load_database.return_value = self.test_database
        
        result = kakao_map_place_recommender("Seoul", "restaurant")
        
        self.assertIn("recommendations", result)
        self.assertEqual(len(result["recommendations"]), 2)  # Seoul Restaurant and Seoul Shopping
        
        # Should return Seoul Restaurant first (higher rating)
        self.assertEqual(result["recommendations"][0]["name"], "Seoul Shopping")
        self.assertEqual(result["recommendations"][1]["name"], "Seoul Restaurant")
    
    @patch('kakao_map_server.load_database')
    def test_recommender_preference_match(self, mock_load_database):
        """Test recommender with preference matching."""
        mock_load_database.return_value = self.test_database
        
        result = kakao_map_place_recommender("Busan", "coffee")
        
        self.assertIn("recommendations", result)
        self.assertEqual(len(result["recommendations"]), 1)
        self.assertEqual(result["recommendations"][0]["name"], "Busan Cafe")
    
    @patch('kakao_map_server.load_database')
    def test_recommender_no_matches(self, mock_load_database):
        """Test recommender with no matching places."""
        mock_load_database.return_value = self.test_database
        
        result = kakao_map_place_recommender("Daegu", "restaurant")
        
        self.assertIn("recommendations", result)
        self.assertEqual(len(result["recommendations"]), 0)
    
    @patch('kakao_map_server.load_database')
    def test_recommender_case_insensitive(self, mock_load_database):
        """Test recommender with case-insensitive matching."""
        mock_load_database.return_value = self.test_database
        
        result = kakao_map_place_recommender("seoul", "RESTAURANT")
        
        self.assertIn("recommendations", result)
        self.assertEqual(len(result["recommendations"]), 2)
    
    @patch('kakao_map_server.load_database')
    def test_recommender_tag_matching(self, mock_load_database):
        """Test recommender with tag-based matching."""
        mock_load_database.return_value = self.test_database
        
        result = kakao_map_place_recommender("Seoul", "luxury")
        
        self.assertIn("recommendations", result)
        self.assertEqual(len(result["recommendations"]), 1)
        self.assertEqual(result["recommendations"][0]["name"], "Seoul Shopping")
    
    @patch('kakao_map_server.load_database')
    def test_recommender_rating_sorting(self, mock_load_database):
        """Test that recommendations are sorted by rating."""
        mock_load_database.return_value = self.test_database
        
        result = kakao_map_place_recommender("Seoul", "any")
        
        self.assertIn("recommendations", result)
        
        # Should be sorted by rating descending
        ratings = [place["rating"] for place in result["recommendations"]]
        self.assertEqual(ratings, sorted(ratings, reverse=True))
    
    @patch('kakao_map_server.load_database')
    def test_recommender_limit_to_10(self, mock_load_database):
        """Test that recommendations are limited to 10 results."""
        # Create database with more than 10 Seoul places
        large_database = {
            "places": [
                {
                    "id": f"place_{i:03d}",
                    "name": f"Seoul Place {i}",
                    "location": "Seoul",
                    "type": "restaurant",
                    "description": f"Description {i}",
                    "rating": 4.0 + (i * 0.1),
                    "price_range": "₩₩",
                    "tags": ["korean"],
                    "coordinates": {
                        "latitude": 37.5,
                        "longitude": 127.0
                    }
                }
                for i in range(15)
            ]
        }
        
        mock_load_database.return_value = large_database
        
        result = kakao_map_place_recommender("Seoul", "restaurant")
        
        self.assertIn("recommendations", result)
        self.assertEqual(len(result["recommendations"]), 10)
    
    @patch('kakao_map_server.load_database')
    def test_recommender_database_error(self, mock_load_database):
        """Test recommender behavior when database loading fails."""
        mock_load_database.side_effect = FileNotFoundError("Database not found")
        
        result = kakao_map_place_recommender("Seoul", "restaurant")
        
        self.assertIn("error", result)
        self.assertIn("recommendations", result)
        self.assertEqual(len(result["recommendations"]), 0)


if __name__ == "__main__":
    unittest.main()