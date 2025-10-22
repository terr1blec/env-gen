"""
Google Calendar Dataset Synthesis Module

Generates deterministic mock datasets for Google Calendar MCP server.
This module creates synthetic calendar and event data that matches the
DATA CONTRACT specifications.

Usage:
    python google_calendar_dataset.py [--count_events N] [--seed SEED]
    
Parameters:
    --count_events: Number of events to generate (default: 50)
    --seed: Random seed for deterministic generation (optional)
"""

import json
import uuid
import random
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class GoogleCalendarDatasetGenerator:
    """Generates synthetic Google Calendar datasets."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the generator with optional seed for determinism."""
        if seed is not None:
            random.seed(seed)
        self._reset_state()
    
    def _reset_state(self):
        """Reset internal state for fresh generation."""
        self.calendars = []
        self.events = []
        self.calendar_ids = []
        self.generated_event_ids = set()
    
    def generate_calendars(self) -> List[Dict[str, Any]]:
        """Generate calendar objects according to data contract."""
        calendar_templates = [
            {
                "id": "calendar-1",
                "summary": "Work Calendar",
                "description": "Professional meetings and work-related events",
                "timeZone": "America/New_York",
                "primary": True,
                "accessRole": "owner"
            },
            {
                "id": "calendar-2", 
                "summary": "Personal Calendar",
                "description": "Personal appointments and family events",
                "timeZone": "America/New_York",
                "primary": False,
                "accessRole": "owner"
            },
            {
                "id": "calendar-3",
                "summary": "Holidays",
                "description": "Public holidays and observances",
                "timeZone": "America/New_York",
                "primary": False,
                "accessRole": "reader"
            },
            {
                "id": "calendar-4",
                "summary": "Team Projects",
                "description": "Team collaboration and project timelines",
                "timeZone": "America/Los_Angeles",
                "primary": False,
                "accessRole": "writer"
            }
        ]
        
        self.calendars = calendar_templates
        self.calendar_ids = [cal["id"] for cal in calendar_templates]
        return self.calendars
    
    def _generate_event_id(self) -> str:
        """Generate a unique event ID using UUID v4."""
        while True:
            event_id = str(uuid.uuid4())
            if event_id not in self.generated_event_ids:
                self.generated_event_ids.add(event_id)
                return event_id
    
    def _generate_datetime_range(self, base_date: datetime, hour_range: tuple = (8, 18)) -> tuple:
        """Generate start and end datetimes for an event."""
        # Random hour between specified range
        start_hour = random.randint(hour_range[0], hour_range[1] - 1)
        start_minute = random.choice([0, 15, 30, 45])
        
        # Duration between 30 minutes and 3 hours
        duration_hours = random.choice([0.5, 1, 1.5, 2, 2.5, 3])
        
        start_dt = base_date.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        end_dt = start_dt + timedelta(hours=duration_hours)
        
        return start_dt, end_dt
    
    def _generate_attendees(self, count: int = 3) -> List[Dict[str, str]]:
        """Generate synthetic attendees for events."""
        names = ["Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", 
                "Eva Brown", "Frank Miller", "Grace Lee", "Henry Taylor"]
        domains = ["company.com", "example.org", "test.net"]
        
        attendees = []
        for i in range(min(count, len(names))):
            name = names[i]
            email = f"{name.lower().replace(' ', '.')}@{random.choice(domains)}"
            response_status = random.choice(["accepted", "declined", "needsAction", "tentative"])
            
            attendees.append({
                "email": email,
                "displayName": name,
                "responseStatus": response_status
            })
        
        return attendees
    
    def _generate_recurrence_rule(self) -> Optional[List[str]]:
        """Generate recurrence rules for events."""
        if random.random() < 0.2:  # 20% of events are recurring
            patterns = [
                "RRULE:FREQ=DAILY;COUNT=5",
                "RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR",
                "RRULE:FREQ=MONTHLY;BYMONTHDAY=15",
                "RRULE:FREQ=WEEKLY;INTERVAL=2;BYDAY=TU,TH"
            ]
            return [random.choice(patterns)]
        return None
    
    def _generate_reminders(self) -> Dict[str, Any]:
        """Generate reminder settings for events."""
        if random.random() < 0.7:  # 70% of events have custom reminders
            overrides = [
                {"minutes": 10, "method": "popup"},
                {"minutes": 15, "method": "email"},
                {"minutes": 30, "method": "popup"},
                {"minutes": 60, "method": "email"}
            ]
            return {
                "useDefault": False,
                "overrides": random.sample(overrides, random.randint(1, 2))
            }
        else:
            return {"useDefault": True, "overrides": []}
    
    def generate_events(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate event objects according to data contract."""
        if not self.calendars:
            self.generate_calendars()
        
        event_templates = [
            # Work events
            {"summary": "Team Standup", "calendar": "calendar-1", "hour_range": (9, 10)},
            {"summary": "Project Planning", "calendar": "calendar-1", "hour_range": (10, 12)},
            {"summary": "Client Meeting", "calendar": "calendar-1", "hour_range": (14, 16)},
            {"summary": "Code Review", "calendar": "calendar-1", "hour_range": (11, 12)},
            {"summary": "Sprint Retrospective", "calendar": "calendar-1", "hour_range": (15, 17)},
            
            # Personal events
            {"summary": "Doctor Appointment", "calendar": "calendar-2", "hour_range": (9, 17)},
            {"summary": "Gym Session", "calendar": "calendar-2", "hour_range": (6, 8)},
            {"summary": "Dinner with Friends", "calendar": "calendar-2", "hour_range": (18, 21)},
            {"summary": "Grocery Shopping", "calendar": "calendar-2", "hour_range": (10, 12)},
            {"summary": "Movie Night", "calendar": "calendar-2", "hour_range": (19, 22)},
            
            # Holiday events
            {"summary": "New Year's Day", "calendar": "calendar-3", "hour_range": (0, 24), "all_day": True},
            {"summary": "Independence Day", "calendar": "calendar-3", "hour_range": (0, 24), "all_day": True},
            {"summary": "Christmas Day", "calendar": "calendar-3", "hour_range": (0, 24), "all_day": True},
            
            # Team project events
            {"summary": "Project Kickoff", "calendar": "calendar-4", "hour_range": (10, 12)},
            {"summary": "Design Review", "calendar": "calendar-4", "hour_range": (13, 15)},
            {"summary": "Deployment Planning", "calendar": "calendar-4", "hour_range": (11, 13)},
        ]
        
        # Base date - start from today and generate events over the next 30 days
        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        events = []
        for i in range(count):
            template = random.choice(event_templates)
            
            # Generate event date (within next 30 days)
            days_offset = random.randint(0, 30)
            event_date = base_date + timedelta(days=days_offset)
            
            # Generate start and end times
            if template.get("all_day", False):
                start_dt = event_date.replace(hour=0, minute=0)
                end_dt = event_date.replace(hour=23, minute=59)
            else:
                start_dt, end_dt = self._generate_datetime_range(event_date, template["hour_range"])
            
            # Get calendar timezone
            calendar = next((cal for cal in self.calendars if cal["id"] == template["calendar"]), None)
            timezone = calendar["timeZone"] if calendar else "America/New_York"
            
            # Create event
            event = {
                "id": self._generate_event_id(),  # Fixed: Now uses UUID format
                "calendarId": template["calendar"],
                "summary": template["summary"],
                "description": f"Description for {template['summary']}" if random.random() < 0.8 else None,
                "start": {
                    "dateTime": start_dt.isoformat(),
                    "timeZone": timezone
                },
                "end": {
                    "dateTime": end_dt.isoformat(),
                    "timeZone": timezone
                },
                "location": f"Location for {template['summary']}" if random.random() < 0.6 else None,
                "status": random.choice(["confirmed", "tentative", "cancelled"]),
                "attendees": self._generate_attendees(random.randint(0, 5)) if random.random() < 0.7 else [],
                "recurrence": self._generate_recurrence_rule(),
                "reminders": self._generate_reminders()
            }
            
            # Remove None values to match data contract
            event = {k: v for k, v in event.items() if v is not None}
            
            events.append(event)
        
        self.events = events
        return events
    
    def generate_dataset(self, event_count: int = 50) -> Dict[str, Any]:
        """Generate complete dataset with calendars and events."""
        self._reset_state()
        
        calendars = self.generate_calendars()
        events = self.generate_events(event_count)
        
        return {
            "calendars": calendars,
            "events": events
        }


def main():
    """Main function to generate and save dataset."""
    parser = argparse.ArgumentParser(description="Generate Google Calendar dataset")
    parser.add_argument("--count_events", type=int, default=50, 
                       help="Number of events to generate (default: 50)")
    parser.add_argument("--seed", type=int, default=None,
                       help="Random seed for deterministic generation")
    
    args = parser.parse_args()
    
    # Generate dataset
    generator = GoogleCalendarDatasetGenerator(seed=args.seed)
    dataset = generator.generate_dataset(event_count=args.count_events)
    
    # Save to JSON file using recommended path
    output_path = "generated\\google-calendar\\google_calendar_dataset.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"Generated dataset with {len(dataset['calendars'])} calendars and {len(dataset['events'])} events")
    print(f"Dataset saved to: {output_path}")
    
    # Print summary
    calendar_summary = {}
    status_summary = {}
    
    for event in dataset['events']:
        cal_id = event['calendarId']
        status = event['status']
        
        calendar_summary[cal_id] = calendar_summary.get(cal_id, 0) + 1
        status_summary[status] = status_summary.get(status, 0) + 1
    
    print("\nEvent distribution by calendar:")
    for cal_id, count in calendar_summary.items():
        calendar_name = next((cal['summary'] for cal in dataset['calendars'] if cal['id'] == cal_id), cal_id)
        print(f"  {calendar_name}: {count} events")
    
    print("\nEvent distribution by status:")
    for status, count in status_summary.items():
        print(f"  {status}: {count} events")


if __name__ == "__main__":
    main()