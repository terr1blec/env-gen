# Google Calendar MCP Server Implementation Notes

## Overview
This implementation provides a FastMCP server for Google Calendar operations using an offline dataset. The server implements all 5 required tools and maintains data consistency with the generated dataset.

## Key Features

### 1. Dataset Integration
- **Data Source**: Loads from `generated/google-calendar/google_calendar_dataset.json`
- **Data Contract Compliance**: Follows the exact structure specified in the DATA CONTRACT notes
- **UUID Consistency**: Both dataset and server use UUID v4 format for event IDs
- **Error Handling**: Fails hard if dataset is unavailable (no fallback to defaults)

### 2. Tool Implementation

#### list_calendars()
- Returns all calendars from the dataset
- No parameters required
- Output: Array of calendar objects with full structure

#### list_events(calendar_id, time_min, time_max)
- Optional filtering by calendar ID
- Optional time range filtering using ISO 8601 timestamps
- Supports both calendar and time filters simultaneously
- Output: Array of event objects

#### create_event(calendar_id, summary, start_time, end_time, ...)
- Creates new events with UUID v4 generation
- Validates calendar existence
- Sets default status as "confirmed"
- Includes optional fields: description, location, time_zone
- Output: Created event object

#### update_event(event_id, ...)
- Partial updates - only modifies provided fields
- Validates event existence
- Maintains existing event structure
- Output: Updated event object

#### delete_event(calendar_id, event_id)
- Validates both calendar and event existence
- Ensures event belongs to specified calendar
- Output: Confirmation message and deleted event

### 3. Data Consistency
- **Event ID Format**: UUID v4 (matches dataset format)
- **Calendar References**: Validated before operations
- **Time Handling**: ISO 8601 format with timezone support
- **CRUD Operations**: All operations persist to the dataset JSON

### 4. Error Handling
- **Missing Dataset**: Raises RuntimeError with clear message
- **Invalid IDs**: Raises ValueError with descriptive messages
- **Time Parsing**: Handles ISO 8601 with timezone support
- **File Operations**: Proper exception handling for read/write operations

## Technical Implementation

### Dependencies
- `mcp.server.fastmcp` for FastMCP server framework
- `uuid` for event ID generation
- `datetime` for time filtering
- `json` for dataset serialization

### Architecture
- **Modular Functions**: Separate functions for dataset loading, validation, filtering
- **Tool Decorators**: Each tool decorated with `@mcp.tool()`
- **Type Hints**: Full type annotations for better code clarity
- **Documentation**: Comprehensive docstrings for all functions

## Usage Examples

```python
# List all calendars
calendars = list_calendars()

# List events for specific calendar
work_events = list_events(calendar_id="calendar-1")

# List events within time range
january_events = list_events(time_min="2024-01-01T00:00:00", time_max="2024-01-31T23:59:59")

# Create new event
new_event = create_event(
    calendar_id="calendar-1",
    summary="Team Meeting",
    start_time="2024-01-25T10:00:00",
    end_time="2024-01-25T11:00:00",
    description="Weekly team sync"
)

# Update existing event
updated_event = update_event(
    event_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    summary="Updated Meeting Title"
)

# Delete event
result = delete_event(
    calendar_id="calendar-1",
    event_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890"
)
```

## Data Contract Adherence

The implementation strictly follows the DATA CONTRACT specifications:
- **Top-level keys**: `calendars` and `events` arrays
- **Calendar structure**: All required fields (id, summary, accessRole) and optional fields
- **Event structure**: All required fields (id, calendarId, summary, start, end, status) and optional fields
- **Value types**: Correct string, boolean, array, and object types
- **UUID format**: Consistent UUID v4 usage for event IDs

## Testing Notes

While test files are not included in this implementation, the server has been designed with testability in mind:
- Pure functions for validation and filtering
- Clear separation between data loading and business logic
- Comprehensive error handling for edge cases
- Type hints for better static analysis