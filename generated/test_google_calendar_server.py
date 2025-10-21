"""
Test script for Google Calendar MCP Server

This script tests the basic functionality of the Google Calendar server module
using the offline dataset.
"""

import sys
import os

# Add the generated directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from google_calendar_server import (
    list_calendars,
    list_events,
    create_event,
    update_event,
    delete_event,
    load_dataset
)


def test_list_calendars():
    """Test listing available calendars."""
    print("Testing list_calendars...")
    calendars = list_calendars()
    print(f"Found {len(calendars)} calendars:")
    for cal in calendars:
        print(f"  - {cal['id']}: {cal['summary']}")
    print()


def test_list_events():
    """Test listing events from a calendar."""
    print("Testing list_events...")
    
    # Test with primary calendar
    events = list_events("primary")
    print(f"Found {len(events)} events in primary calendar:")
    for event in events[:3]:  # Show first 3 events
        print(f"  - {event['id']}: {event['summary']}")
    
    # Test with invalid calendar
    try:
        list_events("invalid_calendar")
    except ValueError as e:
        print(f"Correctly caught error for invalid calendar: {e}")
    print()


def test_create_event():
    """Test creating a new event."""
    print("Testing create_event...")
    
    new_event_data = {
        "summary": "Test Meeting",
        "description": "This is a test event created by the test script",
        "location": "Test Location",
        "start": {
            "dateTime": "2025-01-10T14:00:00",
            "timeZone": "America/New_York"
        },
        "end": {
            "dateTime": "2025-01-10T15:00:00",
            "timeZone": "America/New_York"
        },
        "attendees": [
            {"email": "test1@example.com"},
            {"email": "test2@example.com"}
        ]
    }
    
    created_event = create_event(new_event_data)
    print(f"Created event: {created_event['id']}")
    print(f"  Summary: {created_event['summary']}")
    print(f"  Description: {created_event['description']}")
    print()
    
    return created_event["id"]


def test_update_event(event_id: str):
    """Test updating an existing event."""
    print("Testing update_event...")
    
    update_data = {
        "id": event_id,
        "summary": "Updated Test Meeting",
        "description": "This event has been updated",
        "location": "Updated Location"
    }
    
    updated_event = update_event(update_data)
    print(f"Updated event: {updated_event['id']}")
    print(f"  New summary: {updated_event['summary']}")
    print(f"  New description: {updated_event['description']}")
    print()


def test_delete_event(event_id: str):
    """Test deleting an event."""
    print("Testing delete_event...")
    
    result = delete_event("primary", event_id)
    print(f"Delete result: {result['message']}")
    print()


def test_dataset_integrity():
    """Test that the dataset is properly loaded and saved."""
    print("Testing dataset integrity...")
    
    initial_events = load_dataset()
    print(f"Initial dataset has {len(initial_events)} events")
    
    # Create a test event
    test_event_data = {
        "summary": "Dataset Integrity Test",
        "start": {
            "dateTime": "2025-01-11T10:00:00",
            "timeZone": "America/New_York"
        },
        "end": {
            "dateTime": "2025-01-11T11:00:00",
            "timeZone": "America/New_York"
        }
    }
    
    created_event = create_event(test_event_data)
    
    # Verify the event was added
    updated_events = load_dataset()
    print(f"After creation, dataset has {len(updated_events)} events")
    
    # Delete the test event
    delete_event("primary", created_event["id"])
    
    final_events = load_dataset()
    print(f"After deletion, dataset has {len(final_events)} events")
    
    if len(final_events) == len(initial_events):
        print("Dataset integrity: PASSED")
    else:
        print("Dataset integrity: FAILED")
    print()


def main():
    """Run all tests."""
    print("=" * 60)
    print("Google Calendar MCP Server Tests")
    print("=" * 60)
    print()
    
    # Run tests
    test_list_calendars()
    test_list_events()
    
    created_event_id = test_create_event()
    test_update_event(created_event_id)
    test_delete_event(created_event_id)
    
    test_dataset_integrity()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()