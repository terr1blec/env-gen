# Google Calendar Dataset Synthesis

## Overview

This module provides deterministic generation of synthetic Google Calendar data that matches the DATA CONTRACT specifications. The generated dataset includes calendars and events with realistic attributes for testing MCP server functionality.

## Generated Files

- `google_calendar_dataset.py` - Main dataset synthesis module
- `google_calendar_dataset.json` - Generated dataset in JSON format
- `generate_dataset.py` - Convenience script for dataset generation

## Dataset Structure

### Top-Level Keys
- `calendars`: Array of calendar objects
- `events`: Array of event objects

### Calendar Object Structure
```json
{
  "id": "string",
  "summary": "string",
  "description": "string (optional)",
  "timeZone": "string (optional)",
  "primary": "boolean (optional)",
  "accessRole": "string"
}
```

### Event Object Structure
```json
{
  "id": "string",
  "calendarId": "string",
  "summary": "string",
  "description": "string (optional)",
  "start": {
    "dateTime": "ISO string",
    "timeZone": "string"
  },
  "end": {
    "dateTime": "ISO string",
    "timeZone": "string"
  },
  "location": "string (optional)",
  "status": "string",
  "attendees": "array (optional)",
  "recurrence": "array (optional)",
  "reminders": "object"
}
```

## Usage

### Command Line
```bash
cd generated/google-calendar
python google_calendar_dataset.py --count_events 50 --seed 42
```

### Programmatic
```python
from google_calendar_dataset import GoogleCalendarDatasetGenerator

generator = GoogleCalendarDatasetGenerator(seed=42)
dataset = generator.generate_dataset(event_count=50)
```

## Features

- **Deterministic Generation**: Uses random seeds for reproducible datasets
- **Realistic Data**: Includes various event types, statuses, and attributes
- **Time Zone Support**: Events across different time zones
- **Recurring Events**: Support for RRULE patterns
- **Attendee Management**: Synthetic attendees with response statuses
- **Reminder Settings**: Custom and default reminder configurations

## Generated Dataset Summary

The current dataset includes:
- 4 calendars (Work, Personal, Holidays, Team Projects)
- 10 sample events with various attributes
- Events across different calendars and time zones
- Mixed statuses (confirmed, tentative, cancelled)
- Recurring events and events with attendees
- Custom reminder settings