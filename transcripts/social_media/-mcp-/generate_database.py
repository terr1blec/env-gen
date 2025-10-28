#!/usr/bin/env python3
"""
Script to generate the social media database using the database module.
"""

import sys
import os

# Add the generated directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'social_media', '-mcp-'))

from _mcp__database import generate_offline_database

if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'social_media', '-mcp-', '_mcp__database.json')
    
    generate_offline_database(
        output_path=output_path,
        seed=42,
        user_count=10,
        notes_per_user=3,
        max_comments_per_note=5
    )