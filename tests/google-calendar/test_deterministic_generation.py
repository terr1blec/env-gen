#!/usr/bin/env python3
"""
Test script to verify deterministic generation of Google Calendar dataset.
This demonstrates that the same seed produces identical datasets.
"""

import sys
import os

# Add the generated module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'generated', 'google-calendar'))

from google_calendar_dataset import GoogleCalendarDatasetGenerator

def test_deterministic_generation():
    """Test that the same seed produces identical datasets."""
    
    # Generate two datasets with the same seed
    generator1 = GoogleCalendarDatasetGenerator(seed=42)
    dataset1 = generator1.generate_dataset(event_count=10)
    
    generator2 = GoogleCalendarDatasetGenerator(seed=42)
    dataset2 = generator2.generate_dataset(event_count=10)
    
    # Verify they are identical
    assert dataset1 == dataset2, "Datasets with same seed should be identical"
    
    # Verify event IDs are UUID format
    for event in dataset1['events']:
        event_id = event['id']
        assert len(event_id) == 36, f"Event ID should be 36 characters: {event_id}"
        assert event_id.count('-') == 4, f"Event ID should have 4 hyphens: {event_id}"
    
    print("✅ Deterministic generation test passed!")
    print(f"   Generated {len(dataset1['calendars'])} calendars and {len(dataset1['events'])} events")
    print(f"   All event IDs use UUID v4 format")
    
    # Show a sample event ID
    sample_event_id = dataset1['events'][0]['id']
    print(f"   Sample event ID: {sample_event_id}")

def test_different_seeds():
    """Test that different seeds produce different datasets."""
    
    generator1 = GoogleCalendarDatasetGenerator(seed=123)
    dataset1 = generator1.generate_dataset(event_count=5)
    
    generator2 = GoogleCalendarDatasetGenerator(seed=456)
    dataset2 = generator2.generate_dataset(event_count=5)
    
    # They should be different
    assert dataset1 != dataset2, "Datasets with different seeds should be different"
    
    print("✅ Different seeds test passed!")
    print(f"   Seed 123 produced {len(dataset1['events'])} events")
    print(f"   Seed 456 produced {len(dataset2['events'])} events")

if __name__ == "__main__":
    print("Testing Google Calendar Dataset Deterministic Generation...")
    print("=" * 60)
    
    test_deterministic_generation()
    print()
    test_different_seeds()
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Dataset generator is working correctly.")