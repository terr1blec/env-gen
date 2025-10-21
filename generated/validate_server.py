#!/usr/bin/env python3
"""
Quick validation script for Google Calendar MCP Server
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def validate_imports():
    """Validate that all required modules can be imported."""
    print("🔍 Validating imports...")
    
    try:
        from google_calendar_server import (
            list_calendars,
            list_events,
            create_event,
            update_event,
            delete_event,
            load_dataset
        )
        print("✅ All server functions imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def validate_dataset():
    """Validate that the dataset can be loaded."""
    print("\n🔍 Validating dataset...")
    
    try:
        from google_calendar_server import load_dataset
        events = load_dataset()
        print(f"✅ Dataset loaded successfully with {len(events)} events")
        
        if events:
            print(f"   First event: {events[0]['summary']}")
        return True
    except Exception as e:
        print(f"❌ Dataset error: {e}")
        return False

def validate_calendars():
    """Validate that calendars can be listed."""
    print("\n🔍 Validating calendars...")
    
    try:
        from google_calendar_server import list_calendars
        calendars = list_calendars()
        print(f"✅ Found {len(calendars)} calendars:")
        for cal in calendars:
            print(f"   - {cal['id']}: {cal['summary']}")
        return True
    except Exception as e:
        print(f"❌ Calendar error: {e}")
        return False

def validate_events_listing():
    """Validate that events can be listed."""
    print("\n🔍 Validating events listing...")
    
    try:
        from google_calendar_server import list_events
        events = list_events("primary")
        print(f"✅ Found {len(events)} events in primary calendar")
        
        if events:
            print(f"   Sample event: {events[0]['summary']}")
        return True
    except Exception as e:
        print(f"❌ Events listing error: {e}")
        return False

def main():
    """Run all validations."""
    print("🚀 Google Calendar MCP Server Validation")
    print("=" * 50)
    
    results = [
        validate_imports(),
        validate_dataset(),
        validate_calendars(),
        validate_events_listing()
    ]
    
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 All validations passed! The server is ready to use.")
        return True
    else:
        print("❌ Some validations failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)