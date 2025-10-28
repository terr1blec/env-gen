#!/usr/bin/env python3
"""
Execute this script to generate the dataset JSON file.
"""

import json
import sys
import os

# Import the dataset generator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from airbnb_search_and_listing_server_dataset import generate_dataset
    
    # Generate dataset with fixed seed for deterministic results
    output_path = "airbnb_search_and_listing_server_dataset.json"
    
    print("Generating Airbnb dataset...")
    dataset = generate_dataset(
        num_listings=100,
        seed=42,  # Fixed seed for reproducible results
        output_path=output_path
    )
    
    print(f"✓ Successfully generated {len(dataset['listings'])} listings")
    print(f"✓ Dataset saved to: {output_path}")
    
    # Show some statistics
    cities = {listing['location']['city'] for listing in dataset['listings']}
    property_types = {listing['property_type'] for listing in dataset['listings']}
    
    print(f"✓ Cities represented: {len(cities)}")
    print(f"✓ Property types: {', '.join(sorted(property_types))}")
    print(f"✓ Price range: ${min(listing['price_per_night'] for listing in dataset['listings']):.2f} - ${max(listing['price_per_night'] for listing in dataset['listings']):.2f}")
    
except Exception as e:
    print(f"Error generating dataset: {e}")
    sys.exit(1)