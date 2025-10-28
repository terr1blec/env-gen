#!/usr/bin/env python3
"""
Script to generate the Airbnb database JSON file.
"""

import sys
import os

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from airbnb_search_and_listing_server_database import generate_airbnb_database

if __name__ == "__main__":
    # Generate the database with 50 listings and a fixed seed for reproducibility
    database = generate_airbnb_database(count=50, seed=42)
    print(f"Successfully generated database with {len(database['listings'])} listings")