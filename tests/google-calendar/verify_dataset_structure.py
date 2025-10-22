#!/usr/bin/env python3
"""
Verify that the generated dataset matches the DATA CONTRACT structure.
"""

import json
import os
import sys

def verify_dataset_structure():
    """Verify the dataset structure against DATA CONTRACT."""
    
    # Load the dataset
    dataset_path = os.path.join('generated', 'google-calendar', 'google_calendar_dataset.json')
    
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
    except FileNotFoundError:
        print(f"❌ Dataset file not found at: {dataset_path}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in dataset: {e}")
        return False
    
    # Verify top-level structure
    required_keys = ['calendars', 'events']
    for key in required_keys:
        if key not in dataset:
            print(f"❌ Missing top-level key: {key}")
            return False
    
    if not isinstance(dataset['calendars'], list):
        print("❌ 'calendars' should be a list")
        return False
    
    if not isinstance(dataset['events'], list):
        print("❌ 'events' should be a list")
        return False
    
    # Verify calendar structure
    calendar_required = ['id', 'summary', 'timeZone', 'accessRole']
    calendar_optional = ['description', 'primary']
    
    for i, calendar in enumerate(dataset['calendars']):
        for field in calendar_required:
            if field not in calendar:
                print(f"❌ Calendar {i} missing required field: {field}")
                return False
        
        # Check for at least one primary calendar
        if i == 0 and not calendar.get('primary', False):
            print("⚠️  No primary calendar found (recommended but not required)")
    
    # Verify event structure
    event_required = ['id', 'calendarId', 'summary', 'start', 'end', 'status']
    event_optional = ['description', 'location', 'attendees', 'recurrence', 'reminders']
    
    for i, event in enumerate(dataset['events']):
        for field in event_required:
            if field not in event:
                print(f"❌ Event {i} missing required field: {field}")
                return False
        
        # Verify event ID format (UUID v4)
        event_id = event['id']
        if len(event_id) != 36 or event_id.count('-') != 4:
            print(f"❌ Event {i} has invalid UUID format: {event_id}")
            return False
        
        # Verify start/end structure
        for time_field in ['start', 'end']:
            time_obj = event[time_field]
            if 'dateTime' not in time_obj or 'timeZone' not in time_obj:
                print(f"❌ Event {i} {time_field} missing required fields")
                return False
        
        # Verify calendarId references exist
        calendar_ids = [cal['id'] for cal in dataset['calendars']]
        if event['calendarId'] not in calendar_ids:
            print(f"❌ Event {i} references non-existent calendar: {event['calendarId']}")
            return False
    
    print("✅ Dataset structure verification passed!")
    print(f"   Calendars: {len(dataset['calendars'])}")
    print(f"   Events: {len(dataset['events'])}")
    print(f"   Event ID format: UUID v4 (verified)")
    
    # Show distribution
    calendar_counts = {}
    status_counts = {}
    
    for event in dataset['events']:
        calendar_counts[event['calendarId']] = calendar_counts.get(event['calendarId'], 0) + 1
        status_counts[event['status']] = status_counts.get(event['status'], 0) + 1
    
    print("\nEvent Distribution:")
    for cal_id, count in calendar_counts.items():
        calendar_name = next((cal['summary'] for cal in dataset['calendars'] if cal['id'] == cal_id), cal_id)
        print(f"   {calendar_name}: {count} events")
    
    print("\nStatus Distribution:")
    for status, count in status_counts.items():
        print(f"   {status}: {count} events")
    
    return True

if __name__ == "__main__":
    print("Verifying Google Calendar Dataset Structure...")
    print("=" * 60)
    
    success = verify_dataset_structure()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Dataset verification completed successfully!")
    else:
        print("❌ Dataset verification failed!")
        sys.exit(1)