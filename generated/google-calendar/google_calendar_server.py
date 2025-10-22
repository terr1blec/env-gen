"""
Google Calendar MCP Server

FastMCP server implementation for Google Calendar operations using offline dataset.
Provides calendar and event management tools backed by synthetic data.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Google Calendar")

# Dataset file path
DATASET_PATH = "generated/google-calendar/google_calendar_dataset.json"


def load_dataset() -> Dict[str, Any]:
    """Load the dataset from JSON file."""
    try:
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Failed to load dataset from {DATASET_PATH}: {e}")


def save_dataset(data: Dict[str, Any]) -> None:
    """Save the dataset back to JSON file."""
    try:
        with open(DATASET_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise RuntimeError(f"Failed to save dataset to {DATASET_PATH}: {e}")


def validate_calendar_exists(calendar_id: str, data: Dict[str, Any]) -> None:
    """Validate that a calendar exists in the dataset."""
    calendar_ids = [cal["id"] for cal in data["calendars"]]
    if calendar_id not in calendar_ids:
        raise ValueError(f"Calendar '{calendar_id}' not found")


def validate_event_exists(event_id: str, data: Dict[str, Any]) -> None:
    """Validate that an event exists in the dataset."""
    event_ids = [event["id"] for event in data["events"]]
    if event_id not in event_ids:
        raise ValueError(f"Event '{event_id}' not found")


def filter_events_by_time_range(
    events: List[Dict[str, Any]],
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Filter events by time range."""
    filtered_events = []

    for event in events:
        event_start = event["start"]["dateTime"]

        # Parse datetime for comparison
        event_dt = datetime.fromisoformat(event_start.replace("Z", "+00:00"))

        # Apply time filters
        if time_min:
            min_dt = datetime.fromisoformat(time_min.replace("Z", "+00:00"))
            if event_dt < min_dt:
                continue

        if time_max:
            max_dt = datetime.fromisoformat(time_max.replace("Z", "+00:00"))
            if event_dt > max_dt:
                continue

        filtered_events.append(event)

    return filtered_events


@mcp.tool()
def list_calendars() -> List[Dict[str, Any]]:
    """List all available calendars."""
    data = load_dataset()
    return data["calendars"]


@mcp.tool()
def list_events(
    calendar_id: Optional[str] = None,
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    List events, optionally filtered by calendar and time range.

    Args:
        calendar_id: Optional calendar ID to filter events
        time_min: Optional start time for filtering (ISO 8601 format)
        time_max: Optional end time for filtering (ISO 8601 format)
    """
    data = load_dataset()

    # Filter by calendar if specified
    if calendar_id:
        validate_calendar_exists(calendar_id, data)
        events = [
            event for event in data["events"] if event["calendarId"] == calendar_id
        ]
    else:
        events = data["events"]

    # Filter by time range if specified
    if time_min or time_max:
        events = filter_events_by_time_range(events, time_min, time_max)

    return events


@mcp.tool()
def create_event(
    calendar_id: str,
    summary: str,
    start_time: str,
    end_time: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    time_zone: str = "America/New_York",
) -> Dict[str, Any]:
    """
    Create a new calendar event.

    Args:
        calendar_id: ID of the calendar to add the event to
        summary: Event title
        start_time: Event start time (ISO 8601 format)
        end_time: Event end time (ISO 8601 format)
        description: Optional event description
        location: Optional event location
        time_zone: Timezone for the event (default: America/New_York)
    """
    data = load_dataset()
    validate_calendar_exists(calendar_id, data)

    # Generate UUID for the new event
    event_id = str(uuid.uuid4())

    # Create new event
    new_event = {
        "id": event_id,
        "calendarId": calendar_id,
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_time, "timeZone": time_zone},
        "end": {"dateTime": end_time, "timeZone": time_zone},
        "location": location,
        "status": "confirmed",
        "reminders": {"useDefault": True, "overrides": []},
    }

    # Add to dataset and save
    data["events"].append(new_event)
    save_dataset(data)

    return new_event


@mcp.tool()
def update_event(
    event_id: str,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    location: Optional[str] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update an existing calendar event.

    Args:
        event_id: ID of the event to update
        summary: New event title (optional)
        description: New event description (optional)
        start_time: New start time (ISO 8601 format, optional)
        end_time: New end time (ISO 8601 format, optional)
        location: New event location (optional)
        status: New event status (optional)
    """
    data = load_dataset()
    validate_event_exists(event_id, data)

    # Find and update the event
    for event in data["events"]:
        if event["id"] == event_id:
            # Update provided fields
            if summary is not None:
                event["summary"] = summary
            if description is not None:
                event["description"] = description
            if location is not None:
                event["location"] = location
            if status is not None:
                event["status"] = status
            if start_time is not None:
                event["start"]["dateTime"] = start_time
            if end_time is not None:
                event["end"]["dateTime"] = end_time

            # Save updated dataset
            save_dataset(data)
            return event

    # This should not happen due to validation
    raise ValueError(f"Event '{event_id}' not found after validation")


@mcp.tool()
def delete_event(calendar_id: str, event_id: str) -> Dict[str, Any]:
    """
    Delete a calendar event.

    Args:
        calendar_id: ID of the calendar containing the event
        event_id: ID of the event to delete
    """
    data = load_dataset()
    validate_calendar_exists(calendar_id, data)
    validate_event_exists(event_id, data)

    # Find and remove the event
    for i, event in enumerate(data["events"]):
        if event["id"] == event_id and event["calendarId"] == calendar_id:
            deleted_event = data["events"].pop(i)
            save_dataset(data)
            return {
                "message": f"Event '{event_id}' deleted successfully",
                "deleted_event": deleted_event,
            }

    raise ValueError(f"Event '{event_id}' not found in calendar '{calendar_id}'")


if __name__ == "__main__":
    # Run the server
    mcp.run()
