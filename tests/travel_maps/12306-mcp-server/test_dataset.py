"""
Unit tests for the 12306 MCP Server dataset
"""

import json
import os
import sys
import unittest

# Add the dataset module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "generated", "travel_maps", "12306-mcp-server"))

# Import the dataset module using importlib to avoid Python module naming issues
import importlib.util
spec = importlib.util.spec_from_file_location("dataset_module", 
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "generated", "travel_maps", "12306-mcp-server", "12306_mcp_server_dataset.py"))
dataset_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dataset_module)


class Test12306MCPDataset(unittest.TestCase):
    """Test cases for the 12306 MCP Server dataset"""

    def setUp(self):
        """Set up test fixtures"""
        self.dataset_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "generated", "travel_maps", "12306-mcp-server", "12306_mcp_server_dataset.json"
        )

    def test_dataset_file_exists(self):
        """Test that the dataset file exists"""
        self.assertTrue(os.path.exists(self.dataset_path), "Dataset file should exist")

    def test_dataset_valid_json(self):
        """Test that the dataset file contains valid JSON"""
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            try:
                dataset = json.load(f)
            except json.JSONDecodeError as e:
                self.fail(f"Dataset file contains invalid JSON: {e}")

    def test_dataset_structure(self):
        """Test that the dataset follows the data contract schema"""
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        # Check top-level keys
        self.assertIn("search_results", dataset, "Dataset must contain 'search_results' key")
        self.assertIsInstance(dataset["search_results"], list, "'search_results' must be a list")
        
        # Check each train entry
        for train in dataset["search_results"]:
            # Required fields
            required_fields = ["train_number", "departure_station", "arrival_station", 
                             "departure_time", "arrival_time", "duration", "date"]
            for field in required_fields:
                self.assertIn(field, train, f"Train entry missing required field: {field}")
                self.assertIsInstance(train[field], str, f"Field {field} must be a string")
            
            # Optional fields
            optional_fields = ["seat_types", "prices", "available_seats"]
            for field in optional_fields:
                if field in train:
                    self.assertIsInstance(train[field], dict, f"Field {field} must be a dictionary")

    def test_dataset_content_quality(self):
        """Test the quality and realism of dataset content"""
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        for train in dataset["search_results"]:
            # Check date format (YYYY-MM-DD)
            self.assertRegex(train["date"], r'^\d{4}-\d{2}-\d{2}$', 
                           f"Date format should be YYYY-MM-DD: {train['date']}")
            
            # Check time format (HH:MM)
            self.assertRegex(train["departure_time"], r'^\d{2}:\d{2}$', 
                           f"Departure time format should be HH:MM: {train['departure_time']}")
            self.assertRegex(train["arrival_time"], r'^\d{2}:\d{2}$', 
                           f"Arrival time format should be HH:MM: {train['arrival_time']}")
            self.assertRegex(train["duration"], r'^\d{2}:\d{2}$', 
                           f"Duration format should be HH:MM: {train['duration']}")
            
            # Check train number format
            self.assertRegex(train["train_number"], r'^[GCDK]\d+$', 
                           f"Train number should start with G, D, C, or K: {train['train_number']}")
            
            # Check station names are in Chinese
            self.assertTrue(all('\u4e00' <= char <= '\u9fff' for char in train["departure_station"]),
                          f"Departure station should be in Chinese: {train['departure_station']}")
            self.assertTrue(all('\u4e00' <= char <= '\u9fff' for char in train["arrival_station"]),
                          f"Arrival station should be in Chinese: {train['arrival_station']}")

    def test_dataset_deterministic_generation(self):
        """Test that dataset generation is deterministic with the same seed"""
        # Create two generators with the same seed
        generator1 = dataset_module.TrainDatasetGenerator(seed=42)
        generator2 = dataset_module.TrainDatasetGenerator(seed=42)
        
        # Generate datasets
        dataset1 = generator1.generate_dataset(num_trains=5)
        dataset2 = generator2.generate_dataset(num_trains=5)
        
        # They should be identical
        self.assertEqual(dataset1, dataset2, "Datasets generated with same seed should be identical")

    def test_dataset_varied_generation(self):
        """Test that dataset generation varies with different seeds"""
        # Create two generators with different seeds
        generator1 = dataset_module.TrainDatasetGenerator(seed=42)
        generator2 = dataset_module.TrainDatasetGenerator(seed=123)
        
        # Generate datasets
        dataset1 = generator1.generate_dataset(num_trains=5)
        dataset2 = generator2.generate_dataset(num_trains=5)
        
        # They should be different
        self.assertNotEqual(dataset1, dataset2, "Datasets generated with different seeds should be different")

    def test_dataset_generator_configuration(self):
        """Test dataset generator with different configurations"""
        generator = dataset_module.TrainDatasetGenerator(seed=42)
        
        # Test with different number of trains
        dataset_3 = generator.generate_dataset(num_trains=3)
        dataset_10 = generator.generate_dataset(num_trains=10)
        
        self.assertEqual(len(dataset_3["search_results"]), 3, "Should generate exactly 3 trains")
        self.assertEqual(len(dataset_10["search_results"]), 10, "Should generate exactly 10 trains")

    def test_dataset_realistic_routes(self):
        """Test that dataset contains realistic Chinese railway routes"""
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        # Common Chinese railway routes
        common_routes = [
            ("北京", "上海"),
            ("上海", "北京"),
            ("北京", "广州"),
            ("广州", "北京"),
            ("上海", "深圳"),
            ("深圳", "上海"),
            ("广州", "深圳"),
            ("北京", "武汉"),
            ("上海", "杭州"),
            ("北京", "天津")
        ]
        
        found_routes = []
        for train in dataset["search_results"]:
            route = (train["departure_station"], train["arrival_station"])
            found_routes.append(route)
        
        # Check that we have at least some common routes
        common_found = [route for route in common_routes if route in found_routes]
        self.assertGreater(len(common_found), 0, "Dataset should contain some common Chinese railway routes")


if __name__ == "__main__":
    unittest.main()