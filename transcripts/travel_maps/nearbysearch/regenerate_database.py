#!/usr/bin/env python3
"""
Script to regenerate the full 80-record database.
"""

import sys
import os

# Add the generated directory to the path so we can import the module
sys.path.insert(0, 'generated/travel_maps/nearbysearch')

from nearbysearch_database import generate_database

if __name__ == "__main__":
    print("Regenerating database with 80 records...")
    generate_database()
    print("Database regeneration complete!")