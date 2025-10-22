"""
Tests for Google Calendar FastMCP Server

Validates that the server can load the offline dataset and satisfies schema behaviors.
Tests ensure the DATA CONTRACT keys are present and consumed correctly.
"""

import json
import pytest
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the generated directory to Python path to import the server
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'generated' / 'google-calendar'))

from google_calendar_server import (
    load_dataset, 
    save_dataset, 
    validate_calendar_exists, 
    validate_event_exists,
    filter_events_by_time_range,
    list_calendars,
    list_events,
    create_event,
    update_event,
    delete_event
)


class TestGoogleCalendarServer:
    """Test suite for Google Calendar FastMCP server functionality."""
    
    @pytest.fixture
    def dataset_path(self):
        """Return the path to the dataset JSON file."""
        return Path(__file__).parent.parent.parent / 'generated' / 'google-calendar' / 'google_calendar_dataset.json'
    
    @pytest.fixture
    def metadata_path(self):
        """Return the path to the metadata JSON file."""
        return Path(__file__).parent.parent.parent / 'generated' / 'google-calendar' / 'google_calendar_metadata.json'
    
    @pytest.fixture
    def sample_dataset(self):
        """Load and return the sample dataset for testing."""
        return load_dataset()
    
    @pytest.fixture
    def sample_metadata(self, metadata_path):
        """Load and return the metadata for validation."""
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_load_dataset(self, sample_dataset):
        """Test that the dataset loads successfully."""
        assert sample_dataset is not None
        assert 'calendars' in sample_dataset
        assert 'events' in sample_dataset
        assert isinstance(sample_dataset['calendars'], list)
        assert isinstance(sample_dataset['events'], list)
        assert len(sample_dataset['calendars']) > 0
        assert len(sample_dataset['events']) > 0
    
    def test_dataset_calendar_structure(self, sample_dataset):
        """Test that calendar objects have required DATA CONTRACT fields."""
        required_fields = ['id', 'summary', 'accessRole']
        
        for calendar in sample_dataset['calendars']:
            for field in required_fields:
                assert field in calendar, f"Calendar missing required field: {field}"
                assert calendar[field] is not None, f"Calendar field {field} is None"
    
    def test_dataset_event_structure(self, sample_dataset):
        """Test that event objects have required DATA CONTRACT fields."""
        required_fields = ['id', 'calendarId', 'summary', 'start', 'end', 'status']
        
        for event in sample_dataset['events']:
            for field in required_fields:
                assert field in event, f"Event missing required field: {field}"
                assert event[field] is not None, f"Event field {field} is None"
            
            # Test nested required fields for start and end
            assert 'dateTime' in event['start'], "Event start missing dateTime"
            assert 'timeZone' in event['start'], "Event start missing timeZone"
            assert 'dateTime' in event['end'], "Event end missing dateTime"
            assert 'timeZone' in event['end'], "Event end missing timeZone"
    
    def test_metadata_alignment(self, sample_metadata):
        """Test that metadata JSON reflects the server's public API."""
        expected_tools = ['list_calendars', 'list_events', 'create_event', 'update_event', 'delete_event']
        
        assert 'tools' in sample_metadata
        tool_names = [tool['name'] for tool in sample_metadata['tools']]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Expected tool {expected_tool} not found in metadata"
    
    def test_list_calendars_tool(self, sample_dataset):
        """Test the list_calendars tool functionality."""
        result = list_calendars()
        
        assert isinstance(result, list)
        assert len(result) == len(sample_dataset['calendars'])
        
        # Verify structure matches DATA CONTRACT
        for calendar in result:
            assert 'id' in calendar
            assert 'summary' in calendar
            assert 'accessRole' in calendar
    
    def test_list_events_tool_no_filters(self, sample_dataset):
        """Test the list_events tool without filters."""
        result = list_events()
        
        assert isinstance(result, list)
        assert len(result) == len(sample_dataset['events'])
        
        # Verify structure matches DATA CONTRACT
        for event in result:
            assert 'id' in event
            assert 'calendarId' in event
            assert 'summary' in event
            assert 'start' in event
            assert 'end' in event
            assert 'status' in event
    
    def test_list_events_tool_with_calendar_filter(self):
        """Test the list_events tool with calendar filter."""
        calendar_id = 'calendar-1'
        result = list_events(calendar_id=calendar_id)
        
        assert isinstance(result, list)
        
        # All events should belong to the specified calendar
        for event in result:
            assert event['calendarId'] == calendar_id
    
    def test_list_events_tool_with_time_filters(self):
        """Test the list_events tool with time range filters."""
        time_min = '2025-11-01T00:00:00'
        time_max = '2025-11-30T23:59:59'
        
        result = list_events(time_min=time_min, time_max=time_max)
        
        assert isinstance(result, list)
        
        # All events should be within the time range
        for event in result:
            event_start = event['start']['dateTime']
            event_dt = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
            min_dt = datetime.fromisoformat(time_min.replace('Z', '+00:00'))
            max_dt = datetime.fromisoformat(time_max.replace('Z', '+00:00'))
            
            assert min_dt <= event_dt <= max_dt, f"Event {event['id']} outside time range"
    
    def test_create_event_tool(self, sample_dataset):
        """Test the create_event tool functionality."""
        initial_event_count = len(sample_dataset['events'])
        
        new_event = create_event(
            calendar_id='calendar-1',
            summary='Test Event',
            start_time='2025-12-01T10:00:00',
            end_time='2025-12-01T11:00:00',
            description='Test event description',
            location='Test location',
            time_zone='America/New_York'
        )
        
        # Verify the response structure
        assert 'id' in new_event
        assert new_event['calendarId'] == 'calendar-1'
        assert new_event['summary'] == 'Test Event'
        assert new_event['description'] == 'Test event description'
        assert new_event['location'] == 'Test location'
        assert new_event['status'] == 'confirmed'
        
        # Verify the event was added to the dataset
        updated_dataset = load_dataset()
        assert len(updated_dataset['events']) == initial_event_count + 1
        
        # Clean up - remove the test event
        delete_event(calendar_id='calendar-1', event_id=new_event['id'])
    
    def test_update_event_tool(self):
        """Test the update_event tool functionality."""
        # First, create a test event
        new_event = create_event(
            calendar_id='calendar-1',
            summary='Original Event',
            start_time='2025-12-01T10:00:00',
            end_time='2025-12-01T11:00:00'
        )
        
        # Update the event
        updated_event = update_event(
            event_id=new_event['id'],
            summary='Updated Event',
            description='Updated description',
            location='Updated location',
            status='tentative'
        )
        
        # Verify the updates
        assert updated_event['summary'] == 'Updated Event'
        assert updated_event['description'] == 'Updated description'
        assert updated_event['location'] == 'Updated location'
        assert updated_event['status'] == 'tentative'
        
        # Clean up
        delete_event(calendar_id='calendar-1', event_id=new_event['id'])
    
    def test_delete_event_tool(self):
        """Test the delete_event tool functionality."""
        # First, create a test event
        new_event = create_event(
            calendar_id='calendar-1',
            summary='Event to Delete',
            start_time='2025-12-01T10:00:00',
            end_time='2025-12-01T11:00:00'
        )
        
        initial_dataset = load_dataset()
        initial_event_count = len(initial_dataset['events'])
        
        # Delete the event
        delete_result = delete_event(
            calendar_id='calendar-1',
            event_id=new_event['id']
        )
        
        # Verify the response
        assert 'message' in delete_result
        assert 'deleted_event' in delete_result
        assert delete_result['deleted_event']['id'] == new_event['id']
        
        # Verify the event was removed from the dataset
        updated_dataset = load_dataset()
        assert len(updated_dataset['events']) == initial_event_count - 1
    
    def test_validate_calendar_exists(self, sample_dataset):
        """Test calendar validation function."""
        # Test with existing calendar
        validate_calendar_exists('calendar-1', sample_dataset)
        
        # Test with non-existent calendar
        with pytest.raises(ValueError, match="Calendar 'nonexistent' not found"):
            validate_calendar_exists('nonexistent', sample_dataset)
    
    def test_validate_event_exists(self, sample_dataset):
        """Test event validation function."""
        # Get an existing event ID
        existing_event_id = sample_dataset['events'][0]['id']
        validate_event_exists(existing_event_id, sample_dataset)
        
        # Test with non-existent event
        with pytest.raises(ValueError, match="Event 'nonexistent' not found"):
            validate_event_exists('nonexistent', sample_dataset)
    
    def test_filter_events_by_time_range(self, sample_dataset):
        """Test time-based event filtering."""
        events = sample_dataset['events']
        
        # Test filtering with time range
        time_min = '2025-11-01T00:00:00'
        time_max = '2025-11-30T23:59:59'
        
        filtered = filter_events_by_time_range(events, time_min, time_max)
        
        assert isinstance(filtered, list)
        
        # Verify all filtered events are within the time range
        for event in filtered:
            event_start = event['start']['dateTime']
            event_dt = datetime.fromisoformat(event_start.replace('Z', '+00:00'))
            min_dt = datetime.fromisoformat(time_min.replace('Z', '+00:00'))
            max_dt = datetime.fromisoformat(time_max.replace('Z', '+00:00'))
            
            assert min_dt <= event_dt <= max_dt
    
    def test_error_handling_invalid_calendar(self):
        """Test error handling for invalid calendar operations."""
        with pytest.raises(ValueError, match="Calendar 'invalid-calendar' not found"):
            list_events(calendar_id='invalid-calendar')
        
        with pytest.raises(ValueError, match="Calendar 'invalid-calendar' not found"):
            create_event(
                calendar_id='invalid-calendar',
                summary='Test',
                start_time='2025-12-01T10:00:00',
                end_time='2025-12-01T11:00:00'
            )
    
    def test_error_handling_invalid_event(self):
        """Test error handling for invalid event operations."""
        with pytest.raises(ValueError, match="Event 'invalid-event' not found"):
            update_event(event_id='invalid-event', summary='Updated')
        
        with pytest.raises(ValueError, match="Event 'invalid-event' not found"):
            delete_event(calendar_id='calendar-1', event_id='invalid-event')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])