"""
Google Calendar Dataset Synthesis Module

Generates deterministic mock datasets for Google Calendar MCP server.
Provides synthetic calendar and event data with realistic properties.
"""

import json
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class GoogleCalendarDatasetGenerator:
    """Generates synthetic Google Calendar dataset with deterministic output."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize generator with optional seed for deterministic output."""
        self.random = random.Random(seed)
        self.calendars = []
        self.events = []
        
    def generate_calendars(self, count: int = 3) -> List[Dict]:
        """Generate calendar objects with realistic properties."""
        calendar_templates = [
            {
                "summary": "Work Calendar",
                "description": "Professional meetings and work-related events",
                "timeZone": "America/New_York",
                "primary": True
            },
            {
                "summary": "Personal Calendar", 
                "description": "Personal appointments and family events",
                "timeZone": "America/Los_Angeles",
                "primary": False
            },
            {
                "summary": "Project Calendar",
                "description": "Project deadlines and milestones",
                "timeZone": "UTC",
                "primary": False
            }
        ]
        
        # Extend templates if more calendars are needed
        while len(calendar_templates) < count:
            calendar_templates.append({
                "summary": f"Additional Calendar {len(calendar_templates) - 2}",
                "description": f"Additional calendar for testing",
                "timeZone": self.random.choice(["America/Chicago", "Europe/London", "Asia/Tokyo"]),
                "primary": False
            })
        
        self.calendars = []
        for i, template in enumerate(calendar_templates[:count]):
            calendar = {
                "id": str(uuid.UUID(int=self.random.getrandbits(128))),
                "summary": template["summary"],
                "description": template["description"],
                "timeZone": template["timeZone"],
                "primary": template["primary"]
            }
            self.calendars.append(calendar)
        
        return self.calendars
    
    def generate_events(self, count: int = 10) -> List[Dict]:
        """Generate diverse event objects across different calendars and time periods."""
        if not self.calendars:
            raise ValueError("Calendars must be generated before events")
        
        event_templates = [
            # Work events
            {
                "summary": "Team Standup",
                "description": "Daily team synchronization meeting",
                "location": "Conference Room A",
                "attendees": [
                    {"email": "alice@company.com", "displayName": "Alice Smith"},
                    {"email": "bob@company.com", "displayName": "Bob Johnson"},
                    {"email": "carol@company.com", "displayName": "Carol Davis"}
                ],
                "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"],
                "status": "confirmed"
            },
            {
                "summary": "Client Presentation",
                "description": "Quarterly review with major client",
                "location": "Client Office",
                "attendees": [
                    {"email": "client@example.com", "displayName": "Client Representative"},
                    {"email": "manager@company.com", "displayName": "Project Manager"}
                ],
                "status": "confirmed"
            },
            # Personal events
            {
                "summary": "Doctor Appointment",
                "description": "Annual checkup",
                "location": "Medical Center",
                "status": "confirmed"
            },
            {
                "summary": "Family Dinner",
                "description": "Weekly family gathering",
                "location": "Home",
                "attendees": [
                    {"email": "family@example.com", "displayName": "Family Member"}
                ],
                "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=SU"],
                "status": "tentative"
            },
            # Project events
            {
                "summary": "Project Deadline",
                "description": "Final submission for current project",
                "status": "confirmed"
            },
            {
                "summary": "Code Review",
                "description": "Peer review of new features",
                "location": "Virtual Meeting",
                "attendees": [
                    {"email": "dev1@company.com", "displayName": "Developer 1"},
                    {"email": "dev2@company.com", "displayName": "Developer 2"}
                ],
                "status": "confirmed"
            }
        ]
        
        # Generate additional event templates if needed
        while len(event_templates) < count:
            event_types = ["Meeting", "Appointment", "Deadline", "Reminder", "Workshop"]
            event_type = self.random.choice(event_types)
            event_templates.append({
                "summary": f"{event_type} {len(event_templates) - 5}",
                "description": f"Automatically generated {event_type.lower()}",
                "location": self.random.choice(["Office", "Remote", "", "Conference Room"]),
                "status": self.random.choice(["confirmed", "tentative"])
            })
        
        self.events = []
        base_date = datetime.now()
        
        for i, template in enumerate(event_templates[:count]):
            # Distribute events across different calendars
            calendar = self.random.choice(self.calendars)
            
            # Generate event times spanning past, present, and future
            days_offset = self.random.randint(-30, 30)  # Events within ±30 days
            hours_offset = self.random.randint(0, 8)    # Start between 8am-4pm
            duration_hours = self.random.choice([0.5, 1, 1.5, 2])  # Event duration
            
            start_time = base_date + timedelta(days=days_offset, hours=hours_offset)
            end_time = start_time + timedelta(hours=duration_hours)
            
            event = {
                "id": str(uuid.UUID(int=self.random.getrandbits(128))),
                "calendarId": calendar["id"],
                "summary": template["summary"],
                "description": template.get("description", ""),
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": calendar["timeZone"]
                },
                "end": {
                    "dateTime": end_time.isoformat(), 
                    "timeZone": calendar["timeZone"]
                },
                "location": template.get("location", ""),
                "attendees": template.get("attendees", []),
                "recurrence": template.get("recurrence", []),
                "status": template["status"]
            }
            self.events.append(event)
        
        return self.events
    
    def generate_dataset(self, calendar_count: int = 3, event_count: int = 10) -> Dict:
        """Generate complete dataset with calendars and events."""
        self.generate_calendars(calendar_count)
        self.generate_events(event_count)
        
        return {
            "calendars": self.calendars,
            "events": self.events
        }


def generate_dataset(
    calendar_count: int = 3, 
    event_count: int = 10, 
    seed: Optional[int] = None,
    output_path: Optional[str] = None
) -> Dict:
    """
    Generate Google Calendar dataset and optionally save to JSON.
    
    Args:
        calendar_count: Number of calendars to generate (minimum 3)
        event_count: Number of events to generate (minimum 10)
        seed: Random seed for deterministic output
        output_path: Optional path to save JSON output
    
    Returns:
        Dictionary containing calendars and events arrays
    """
    generator = GoogleCalendarDatasetGenerator(seed)
    dataset = generator.generate_dataset(
        calendar_count=max(3, calendar_count),
        event_count=max(10, event_count)
    )
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    return dataset


if __name__ == "__main__":
    # Generate default dataset when run directly
    import os
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    
    # Generate and save dataset
    dataset = generate_dataset(
        calendar_count=3,
        event_count=15,  # Extra events for testing
        seed=42,  # Fixed seed for deterministic output
        output_path="generated\\google-calendar\\google_calendar_dataset.json"
    )
    
    print(f"Generated dataset with {len(dataset['calendars'])} calendars and {len(dataset['events'])} events")
    print(f"Saved to: generated\\google-calendar\\google_calendar_dataset.json")