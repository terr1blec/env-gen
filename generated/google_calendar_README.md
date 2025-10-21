# Google Calendar MCP Server

A FastMCP server implementation for Google Calendar operations using an offline dataset.

## Overview

This module provides a complete MCP (Model Context Protocol) server for Google Calendar functionality, allowing you to manage calendars and events using a local dataset. It implements all the required tools specified in the planning notes.

## Features

- **List Calendars**: Retrieve available calendar metadata
- **List Events**: Filter and view events from specific calendars
- **Create Events**: Add new calendar events with full metadata
- **Update Events**: Modify existing event details
- **Delete Events**: Remove events from calendars
- **Time Filtering**: Filter events by time ranges
- **Error Handling**: Comprehensive validation and error reporting

## Tools

### list-calendars
Lists all available calendars with their metadata.

**Parameters:** None

**Returns:** List of calendar objects

### list-events
Lists events from a specific calendar with optional time filtering.

**Parameters:**
- `calendar_id` (required): Calendar identifier
- `time_min` (optional): Lower bound for event start time (RFC3339)
- `time_max` (optional): Upper bound for event end time (RFC3339)

**Returns:** List of event objects

### create-event
Creates a new calendar event.

**Parameters:**
- `event_data` (required): Event data including required fields

**Required Fields:**
- `summary`: Event title
- `start`: Start time with timezone
- `end`: End time with timezone

**Optional Fields:**
- `description`, `location`, `attendees`, `transparency`, `visibility`, etc.

**Returns:** Created event object

### update-event
Updates an existing calendar event.

**Parameters:**
- `event_data` (required): Event data including `id` and fields to update

**Returns:** Updated event object

### delete-event
Deletes a calendar event.

**Parameters:**
- `calendar_id` (required): Calendar identifier
- `event_id` (required): Event identifier

**Returns:** Deletion confirmation

## Dataset Structure

The server uses a JSON dataset file (`google_calendar_dataset.json`) that contains:

- **Calendar Events**: Array of event objects with Google Calendar API-compatible structure
- **Event Metadata**: Summary, description, location, times, attendees, etc.
- **Timezones**: All events use America/New_York timezone
- **Generated Data**: Realistic event scenarios including meetings, calls, and appointments

## Usage

### Running as MCP Server

```bash
python generated/google_calendar_server.py
```

### Testing

Run the test suite to verify functionality:

```bash
python generated/run_tests.py
```

Or run individual tests:

```bash
python generated/test_google_calendar_server.py
```

### Dataset Management

Generate new dataset with custom parameters:

```bash
python generated/google_calendar_dataset.py --count 20 --seed 42
```

## Data Schema

### Calendar Object
```json
{
  "id": "primary",
  "summary": "Primary Calendar",
  "description": "Default calendar",
  "timeZone": "America/New_York",
  "accessRole": "owner"
}
```

### Event Object
```json
{
  "id": "event_001_1735776000",
  "summary": "Conference Call - B",
  "description": "This is a conference call event.",
  "location": "Zoom Meeting",
  "start": {
    "dateTime": "2025-01-02T09:15:00",
    "timeZone": "America/New_York"
  },
  "end": {
    "dateTime": "2025-01-02T10:15:00",
    "timeZone": "America/New_York"
  },
  "attendees": [
    {"email": "charlie@example.com"}
  ],
  "organizer": {
    "email": "organizer@example.com",
    "displayName": "Event Organizer"
  },
  "created": "2024-12-26T09:15:00",
  "updated": "2024-12-31T09:15:00",
  "status": "confirmed",
  "transparency": "transparent",
  "visibility": "default",
  "guestsCanInviteOthers": false,
  "guestsCanModify": true,
  "guestsCanSeeOtherGuests": false
}
```

## Error Handling

The server provides comprehensive error handling for:

- Invalid calendar IDs
- Missing required parameters
- Non-existent events
- Invalid time formats
- Permission denied scenarios (simulated)

## Dependencies

- `mcp` (FastMCP framework)
- Python 3.8+
- Standard library modules only

## Notes

- This is an offline implementation using local JSON data
- All operations are performed on the local dataset
- The dataset is automatically saved after modifications
- Timezone handling is simplified to America/New_York for consistency
- Event IDs are generated deterministically for testing