"""
Google Calendar Dataset Synthesis Module

This module generates deterministic mock datasets for Google Calendar server testing.
It creates synthetic events, calendars, and other calendar-related data with consistent
schemas that match the server expectations.

Usage:
    python generated/google_calendar_dataset.py [--seed SEED] [--event_count COUNT] [--calendar_count COUNT]
    
Parameters:
    --seed: Random seed for deterministic generation (default: 42)
    --event_count: Number of events to generate (default: 50)
    --calendar_count: Number of calendars to generate (default: 5)
    
Output:
    Writes generated dataset to generated/google_calendar_dataset.json
"""

import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional
import argparse
import sys
import os


class GoogleCalendarDatasetGenerator:
    """Generator for deterministic Google Calendar mock datasets."""
    
    def __init__(self, seed: int = 42):
        """Initialize generator with seed for deterministic output."""
        self.seed = seed
        random.seed(seed)
        
        # Predefined calendar templates
        self.calendar_templates = [
            {
                "name": "Work Calendar",
                "description": "Work-related meetings and events",
                "timeZone": "America/New_York",
                "backgroundColor": "#1d76db",
                "foregroundColor": "#ffffff"
            },
            {
                "name": "Personal Calendar", 
                "description": "Personal appointments and reminders",
                "timeZone": "America/New_York",
                "backgroundColor": "#0b8043",
                "foregroundColor": "#ffffff"
            },
            {
                "name": "Family Calendar",
                "description": "Family events and activities",
                "timeZone": "America/New_York", 
                "backgroundColor": "#8e24aa",
                "foregroundColor": "#ffffff"
            },
            {
                "name": "Holidays",
                "description": "Public holidays and observances",
                "timeZone": "America/New_York",
                "backgroundColor": "#f6c026",
                "foregroundColor": "#000000"
            },
            {
                "name": "Birthdays",
                "description": "Birthday reminders",
                "timeZone": "America/New_York",
                "backgroundColor": "#e67c73",
                "foregroundColor": "#ffffff"
            }
        ]
        
        # Event templates for different types
        self.event_templates = [
            {
                "type": "meeting",
                "summary_prefixes": ["Team Meeting", "Project Review", "Client Call", "Standup", "Planning Session"],
                "locations": ["Conference Room A", "Zoom", "Google Meet", "Office", "Remote"],
                "durations": [30, 60, 90, 120],  # minutes
                "recurrence_chance": 0.2
            },
            {
                "type": "appointment", 
                "summary_prefixes": ["Doctor Appointment", "Dentist", "Haircut", "Car Service", "Meeting"],
                "locations": ["Medical Center", "Clinic", "Salon", "Garage", "Office"],
                "durations": [30, 45, 60],
                "recurrence_chance": 0.1
            },
            {
                "type": "reminder",
                "summary_prefixes": ["Birthday", "Anniversary", "Payment Due", "Follow Up", "Deadline"],
                "locations": ["", "", "", "", ""],
                "durations": [0],  # all-day events
                "recurrence_chance": 0.3
            },
            {
                "type": "social",
                "summary_prefixes": ["Dinner Party", "Movie Night", "Game Night", "Concert", "Party"],
                "locations": ["Home", "Restaurant", "Theater", "Friend's House", "Venue"],
                "durations": [120, 180, 240],
                "recurrence_chance": 0.05
            }
        ]
        
        # Common attendee emails
        self.attendee_emails = [
            "alice@example.com", "bob@example.com", "charlie@example.com",
            "diana@example.com", "eve@example.com", "frank@example.com",
            "grace@example.com", "henry@example.com", "irene@example.com",
            "jack@example.com"
        ]
    
    def generate_calendar_id(self, calendar_name: str) -> str:
        """Generate a deterministic calendar ID based on name."""
        # Use UUID5 with namespace to ensure deterministic generation
        namespace = uuid.UUID('{12345678-1234-5678-1234-567812345678}')
        return str(uuid.uuid5(namespace, f"calendar_{calendar_name}_{self.seed}"))
    
    def generate_event_id(self, summary: str, start_time: Dict[str, str]) -> str:
        """Generate a deterministic event ID matching server format."""
        # Use UUID5 with namespace for deterministic generation matching server
        namespace = uuid.UUID('{87654321-4321-8765-4321-876543210987}')
        start_str = start_time.get("dateTime") or start_time.get("date", "")
        return str(uuid.uuid5(namespace, f"event_{summary}_{start_str}_{self.seed}"))
    
    def generate_calendars(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate calendar entries."""
        calendars = []
        
        for i in range(min(count, len(self.calendar_templates))):
            template = self.calendar_templates[i]
            calendar_id = self.generate_calendar_id(template["name"])
            
            calendar = {
                "id": calendar_id,
                "summary": template["name"],
                "description": template["description"],
                "timeZone": template["timeZone"],
                "backgroundColor": template["backgroundColor"],
                "foregroundColor": template["foregroundColor"],
                "accessRole": "owner"
            }
            calendars.append(calendar)
        
        return calendars
    
    def generate_datetime(self, base_date: Optional[datetime] = None, 
                         days_offset: int = 0, 
                         is_all_day: bool = False) -> Dict[str, str]:
        """Generate datetime in proper Google Calendar format."""
        if base_date is None:
            base_date = datetime.now(timezone.utc)
        
        # Add random offset within the day
        target_date = base_date + timedelta(days=days_offset)
        
        if is_all_day:
            # All-day events use date only
            return {"date": target_date.strftime("%Y-%m-%d")}
        else:
            # Regular events use datetime with timezone
            # Add random time between 8 AM and 6 PM
            hour = random.randint(8, 17)
            minute = random.choice([0, 15, 30, 45])
            event_time = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Format with timezone offset for New York (EST/EDT)
            # Simple approach: use UTC and let server handle timezone
            return {"dateTime": event_time.isoformat()}
    
    def generate_attendees(self, max_attendees: int = 3) -> List[Dict[str, str]]:
        """Generate random attendees for an event."""
        num_attendees = random.randint(0, max_attendees)
        attendees = []
        
        for _ in range(num_attendees):
            email = random.choice(self.attendee_emails)
            attendees.append({
                "email": email,
                "responseStatus": random.choice(["needsAction", "accepted", "declined", "tentative"])
            })
        
        return attendees
    
    def generate_event(self, calendar_id: str, event_index: int) -> Dict[str, Any]:
        """Generate a single event with proper schema."""
        # Choose event template
        template = random.choice(self.event_templates)
        summary_prefix = random.choice(template["summary_prefixes"])
        
        # Generate event details
        days_offset = random.randint(-30, 30)  # Events within ±30 days
        is_all_day = template["type"] == "reminder"
        
        start_time = self.generate_datetime(days_offset=days_offset, is_all_day=is_all_day)
        
        # Calculate end time
        if is_all_day:
            end_time = start_time  # All-day events have same start/end date
        else:
            duration = random.choice(template["durations"])
            start_dt_str = start_time["dateTime"]
            # Parse the datetime string
            if start_dt_str.endswith('Z'):
                start_dt = datetime.fromisoformat(start_dt_str.replace('Z', '+00:00'))
            else:
                start_dt = datetime.fromisoformat(start_dt_str)
            end_dt = start_dt + timedelta(minutes=duration)
            end_time = {"dateTime": end_dt.isoformat()}
        
        # Generate summary with some variety
        summary_suffixes = ["", " (Important)", " - Review", " - Final"]
        summary = f"{summary_prefix}{random.choice(summary_suffixes)}"
        
        # Generate location
        location = random.choice(template["locations"]) if template["locations"][0] else ""
        
        # Generate description
        descriptions = [
            f"Automatically generated event for testing",
            f"Sample event {event_index}",
            f"Test event with seed {self.seed}"
        ]
        description = random.choice(descriptions)
        
        # Generate event ID deterministically (matching server format)
        event_id = self.generate_event_id(summary, start_time)
        
        # Current time for created/updated fields
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Build event
        event = {
            "id": event_id,
            "summary": summary,
            "description": description,
            "location": location,
            "start": start_time,
            "end": end_time,
            "organizer": {
                "email": "user@example.com",  # Consistent with server expectation
                "displayName": "Test User"
            },
            "attendees": self.generate_attendees(),
            "created": current_time,
            "updated": current_time,
            "status": "confirmed",
            "transparency": "opaque",
            "visibility": "default",
            "iCalUID": f"{event_id}@google.com",
            "sequence": 0,
            "guestsCanInviteOthers": True,
            "guestsCanModify": False,
            "guestsCanSeeOtherGuests": True,
            "reminders": {
                "useDefault": True
            }
        }
        
        # Set transparency for all-day events
        if is_all_day:
            event["transparency"] = "transparent"
        
        # Add recurrence for some events
        if random.random() < template["recurrence_chance"]:
            event["recurrence"] = ["RRULE:FREQ=WEEKLY;COUNT=5"]
        
        return event
    
    def generate_dataset(self, event_count: int = 50, calendar_count: int = 5) -> Dict[str, Any]:
        """Generate complete dataset with calendars and events."""
        print(f"Generating dataset with seed {self.seed}...")
        print(f"Creating {calendar_count} calendars and {event_count} events...")
        
        # Generate calendars
        calendars = self.generate_calendars(calendar_count)
        
        # Generate events distributed across calendars
        events_by_calendar = {}
        events_per_calendar = event_count // calendar_count
        
        for i, calendar in enumerate(calendars):
            calendar_id = calendar["id"]
            events = []
            
            # Distribute events with some variation
            actual_count = events_per_calendar
            if i == 0:  # First calendar gets extra events
                actual_count += event_count % calendar_count
            
            for j in range(actual_count):
                event = self.generate_event(calendar_id, j)
                events.append(event)
            
            events_by_calendar[calendar_id] = events
        
        # Build final dataset
        dataset = {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "seed": self.seed,
                "event_count": event_count,
                "calendar_count": calendar_count,
                "version": "1.0"
            },
            "calendars": calendars,
            "events": events_by_calendar
        }
        
        print(f"Dataset generation complete!")
        print(f"- Generated {len(calendars)} calendars")
        total_events = sum(len(events) for events in events_by_calendar.values())
        print(f"- Generated {total_events} events across calendars")
        
        return dataset


def main():
    """Main function to generate and save dataset."""
    parser = argparse.ArgumentParser(description='Generate Google Calendar mock dataset')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for deterministic generation')
    parser.add_argument('--event_count', type=int, default=50, help='Number of events to generate')
    parser.add_argument('--calendar_count', type=int, default=5, help='Number of calendars to generate')
    parser.add_argument('--output', type=str, default='generated/google_calendar_dataset.json', 
                       help='Output file path')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Generate dataset
    generator = GoogleCalendarDatasetGenerator(seed=args.seed)
    dataset = generator.generate_dataset(
        event_count=args.event_count,
        calendar_count=args.calendar_count
    )
    
    # Save to JSON file
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"Dataset saved to {args.output}")
    
    # Print sample data
    print("\nSample Calendar:")
    print(json.dumps(dataset["calendars"][0], indent=2))
    
    print("\nSample Event:")
    first_calendar_id = dataset["calendars"][0]["id"]
    if dataset["events"].get(first_calendar_id):
        print(json.dumps(dataset["events"][first_calendar_id][0], indent=2))


if __name__ == "__main__":
    main()