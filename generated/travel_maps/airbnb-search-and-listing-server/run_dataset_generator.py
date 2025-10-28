#!/usr/bin/env python3
"""
Script to run the dataset generator and create the updated dataset.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from airbnb_search_and_listing_server_dataset import generate_dataset

if __name__ == "__main__":
    # Generate dataset with 100 listings and save to JSON
    dataset = generate_dataset(
        num_listings=100,
        seed=42,
        output_path="airbnb_search_and_listing_server_dataset.json"
    )
    
    print(f"Successfully generated dataset with {len(dataset['listings'])} listings")
    print(f"Generated {len(dataset['search_results'])} search result examples")
    print("Dataset saved to: airbnb_search_and_listing_server_dataset.json")