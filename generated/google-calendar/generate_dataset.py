#!/usr/bin/env python3
"""
Script to generate the Google Calendar dataset JSON file.
This is a convenience script that imports and uses the dataset generator.
"""

import sys
import os

# Add current directory to path to import the module
sys.path.insert(0, os.path.dirname(__file__))

from google_calendar_dataset import GoogleCalendarDatasetGenerator
import json

def main():
    """Generate and save the dataset."""
    # Use a fixed seed for deterministic generation
    generator = GoogleCalendarDatasetGenerator(seed=42)
    dataset = generator.generate_dataset(event_count=50)
    
    # Save to JSON file
    output_path = "google_calendar_dataset.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"Generated dataset with {len(dataset['calendars'])} calendars and {len(dataset['events'])} events")
    print(f"Dataset saved to: {output_path}")

if __name__ == "__main__":
    main()