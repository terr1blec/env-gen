"""
Unit tests for the 12306 MCP Server
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, mock_open

# Add the server module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "generated", "travel_maps", "12306-mcp-server"))

from 12306_mcp_server_server import search, validate_date_format, load_dataset


class Test12306MCPServer(unittest.TestCase):
    """Test cases for the 12306 MCP Server"""

    def setUp(self):
        """Set up test fixtures"""
        # Sample dataset for testing
        self.sample_dataset = {
            "search_results": [
                {
                    "train_number": "G0001",
                    "departure_station": "北京",
                    "arrival_station": "上海",
                    "departure_time": "07:30",
                    "arrival_time": "12:15",
                    "duration": "04:45",
                    "date": "2024-03-15",
                    "seat_types": {
                        "business_class": "商务座",
                        "first_class": "一等座",
                        "second_class": "二等座",
                        "hard_seat": "硬座"
                    },
                    "prices": {
                        "business_class": "¥1298",
                        "first_class": "¥933",
                        "second_class": "¥553",
                        "hard_seat": "¥301"
                    },
                    "available_seats": {
                        "business_class": "12",
                        "first_class": "35",
                        "second_class": "67",
                        "hard_seat": "142"
                    }
                },
                {
                    "train_number": "D0204",
                    "departure_station": "上海",
                    "arrival_station": "北京",
                    "departure_time": "08:45",
                    "arrival_time": "14:30",
                    "duration": "05:45",
                    "date": "2024-03-15",
                    "seat_types": {
                        "business_class": "商务座",
                        "first_class": "一等座",
                        "second_class": "二等座",
                        "hard_seat": "硬座"
                    },
                    "prices": {
                        "business_class": "¥1054",
                        "first_class": "¥746",
                        "second_class": "¥442",
                        "hard_seat": "¥241"
                    },
                    "available_seats": {
                        "business_class": "8",
                        "first_class": "28",
                        "second_class": "89",
                        "hard_seat": "156"
                    }
                }
            ]
        }

    def test_validate_date_format_valid(self):
        """Test valid date formats"""
        valid_dates = ["2024-03-15", "2024-12-31", "2025-01-01"]
        for date in valid_dates:
            with self.subTest(date=date):
                self.assertTrue(validate_date_format(date))

    def test_validate_date_format_invalid(self):
        """Test invalid date formats"""
        invalid_dates = ["2024/03/15", "15-03-2024", "2024-3-15", "2024-03-5", "not-a-date"]
        for date in invalid_dates:
            with self.subTest(date=date):
                self.assertFalse(validate_date_format(date))

    def test_load_dataset_success(self):
        """Test successful dataset loading"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_dataset, f)
            temp_path = f.name
        
        try:
            with patch('12306_mcp_server_server.DATASET_PATH', temp_path):
                dataset = load_dataset()
                self.assertIn("search_results", dataset)
                self.assertEqual(len(dataset["search_results"]), 2)
        finally:
            os.unlink(temp_path)

    def test_load_dataset_file_not_found(self):
        """Test dataset loading when file doesn't exist"""
        with patch('12306_mcp_server_server.DATASET_PATH', "/nonexistent/file.json"):
            with self.assertRaises(FileNotFoundError):
                load_dataset()

    def test_load_dataset_invalid_json(self):
        """Test dataset loading with invalid JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name
        
        try:
            with patch('12306_mcp_server_server.DATASET_PATH', temp_path):
                with self.assertRaises(json.JSONDecodeError):
                    load_dataset()
        finally:
            os.unlink(temp_path)

    def test_load_dataset_missing_key(self):
        """Test dataset loading with missing required key"""
        invalid_dataset = {"wrong_key": []}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_dataset, f)
            temp_path = f.name
        
        try:
            with patch('12306_mcp_server_server.DATASET_PATH', temp_path):
                with self.assertRaises(KeyError):
                    load_dataset()
        finally:
            os.unlink(temp_path)

    def test_search_success(self):
        """Test successful search operation"""
        with patch('12306_mcp_server_server.load_dataset') as mock_load:
            mock_load.return_value = self.sample_dataset
            
            result = search("北京", "上海", "2024-03-15")
            
            self.assertIn("search_results", result)
            self.assertEqual(len(result["search_results"]), 1)
            self.assertEqual(result["search_results"][0]["train_number"], "G0001")

    def test_search_no_results(self):
        """Test search with no matching results"""
        with patch('12306_mcp_server_server.load_dataset') as mock_load:
            mock_load.return_value = self.sample_dataset
            
            result = search("北京", "广州", "2024-03-15")
            
            self.assertIn("search_results", result)
            self.assertEqual(len(result["search_results"]), 0)

    def test_search_invalid_date_format(self):
        """Test search with invalid date format"""
        with self.assertRaises(ValueError) as context:
            search("北京", "上海", "2024/03/15")
        
        self.assertIn("Date must be in YYYY-MM-DD format", str(context.exception))

    def test_search_empty_stations(self):
        """Test search with empty station names"""
        with self.assertRaises(ValueError) as context:
            search("", "上海", "2024-03-15")
        
        self.assertIn("Departure and arrival stations cannot be empty", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            search("北京", "", "2024-03-15")
        
        self.assertIn("Departure and arrival stations cannot be empty", str(context.exception))

    def test_search_dataset_load_error(self):
        """Test search when dataset loading fails"""
        with patch('12306_mcp_server_server.load_dataset') as mock_load:
            mock_load.side_effect = FileNotFoundError("Dataset file not found")
            
            with self.assertRaises(FileNotFoundError):
                search("北京", "上海", "2024-03-15")


if __name__ == "__main__":
    unittest.main()