"""
Example usage of the 12306 MCP Server Dataset Generator

This script demonstrates how to generate synthetic train schedule data
for the 12306 railway system using the dataset synthesis module.
"""

import sys
import os
import importlib.util

# Add the parent directory to Python path to import the dataset module
module_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'travel_maps', '12306-mcp-server', '12306_mcp_server_dataset.py')

# Load the module dynamically to avoid Python import issues with numeric module names
spec = importlib.util.spec_from_file_location("train_dataset_generator", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Import functions from the loaded module
generate_dataset = module.generate_dataset
TrainDatasetGenerator = module.TrainDatasetGenerator

def example_usage():
    """Demonstrate various ways to use the dataset generator."""
    
    print("=== 12306 Dataset Generator Usage Examples ===\n")
    
    # Example 1: Generate dataset with default parameters
    print("1. Generating dataset with default parameters:")
    generator = TrainDatasetGenerator(seed=42)
    dataset = generator.generate_dataset(num_trains=10)
    print(f"   Generated {len(dataset['search_results'])} train schedules")
    
    # Show first train schedule
    first_train = dataset['search_results'][0]
    print(f"   First train: {first_train['train_number']} from {first_train['departure_station']} to {first_train['arrival_station']}")
    print(f"   Departure: {first_train['departure_time']}, Arrival: {first_train['arrival_time']}")
    print(f"   Date: {first_train['date']}, Duration: {first_train['duration']}\n")
    
    # Example 2: Generate dataset with specific date range
    print("2. Generating dataset for specific date range:")
    dataset2 = generator.generate_dataset(
        num_trains=5,
        start_date="2024-06-01",
        end_date="2024-06-30"
    )
    
    dates = [train['date'] for train in dataset2['search_results']]
    print(f"   Generated schedules for dates: {', '.join(sorted(set(dates)))}\n")
    
    # Example 3: Show different train types
    print("3. Train types in the dataset:")
    train_types = {}
    for train in dataset['search_results']:
        train_type = train['train_number'][0]
        train_types[train_type] = train_types.get(train_type, 0) + 1
    
    for train_type, count in train_types.items():
        type_info = generator.train_types.get(train_type, {"name": "Unknown"})
        print(f"   {train_type}-series ({type_info['name']}): {count} trains")
    
    print("\n4. Price ranges by seat type:")
    business_prices = [train['prices']['business_class'] for train in dataset['search_results']]
    second_prices = [train['prices']['second_class'] for train in dataset['search_results']]
    
    print(f"   Business class: {min(business_prices)} - {max(business_prices)}")
    print(f"   Second class: {min(second_prices)} - {max(second_prices)}")
    
    print("\n5. Available routes:")
    routes = set()
    for train in dataset['search_results']:
        route = f"{train['departure_station']} → {train['arrival_station']}"
        routes.add(route)
    
    print(f"   {len(routes)} unique routes generated")
    for route in sorted(list(routes))[:5]:  # Show first 5
        print(f"   - {route}")
    
    if len(routes) > 5:
        print(f"   ... and {len(routes) - 5} more")


def generate_custom_dataset():
    """Generate a custom dataset with specific parameters."""
    
    print("\n=== Generating Custom Dataset ===\n")
    
    # Define output path
    output_path = os.path.join(
        os.path.dirname(__file__), 
        '..', '..', '..', 
        'generated', 'travel_maps', '12306-mcp-server', 
        'custom_dataset.json'
    )
    
    # Generate dataset
    generate_dataset(
        output_path=output_path,
        num_trains=50,
        seed=123,
        start_date="2024-07-01",
        end_date="2024-07-31"
    )
    
    print(f"Custom dataset saved to: {output_path}")


if __name__ == "__main__":
    example_usage()
    generate_custom_dataset()