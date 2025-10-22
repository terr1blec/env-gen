"""
Tests for metadata validation and DATA CONTRACT compliance.
"""

import json
import pytest
from pathlib import Path


class TestMetadataValidation:
    """Test suite for metadata validation and DATA CONTRACT compliance."""
    
    @pytest.fixture
    def metadata(self):
        """Load the metadata JSON file."""
        metadata_path = Path(__file__).parent.parent.parent / 'generated' / 'google-calendar' / 'google_calendar_metadata.json'
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_metadata_structure(self, metadata):
        """Test that metadata has the expected top-level structure."""
        assert 'name' in metadata
        assert 'description' in metadata
        assert 'version' in metadata
        assert 'tools' in metadata
        assert 'usage_examples' in metadata
        
        assert isinstance(metadata['name'], str)
        assert isinstance(metadata['description'], str)
        assert isinstance(metadata['version'], str)
        assert isinstance(metadata['tools'], list)
        assert isinstance(metadata['usage_examples'], dict)
    
    def test_tool_structure(self, metadata):
        """Test that each tool has the required structure."""
        for tool in metadata['tools']:
            assert 'name' in tool
            assert 'description' in tool
            assert 'input_schema' in tool
            assert 'output_schema' in tool
            
            assert isinstance(tool['name'], str)
            assert isinstance(tool['description'], str)
            assert isinstance(tool['input_schema'], dict)
            assert isinstance(tool['output_schema'], dict)
    
    def test_list_calendars_tool_schema(self, metadata):
        """Test the list_calendars tool schema."""
        tool = next(t for t in metadata['tools'] if t['name'] == 'list_calendars')
        
        # Input schema should be empty
        assert tool['input_schema']['type'] == 'object'
        assert tool['input_schema']['properties'] == {}
        assert tool['input_schema']['required'] == []
        
        # Output schema should be array of calendar objects
        assert tool['output_schema']['type'] == 'array'
        assert 'items' in tool['output_schema']
        assert tool['output_schema']['items']['type'] == 'object'
        
        # Calendar object properties
        calendar_props = tool['output_schema']['items']['properties']
        assert 'id' in calendar_props
        assert 'summary' in calendar_props
        assert 'accessRole' in calendar_props
        
        # Required fields
        assert 'id' in tool['output_schema']['items']['required']
        assert 'summary' in tool['output_schema']['items']['required']
        assert 'accessRole' in tool['output_schema']['items']['required']
    
    def test_list_events_tool_schema(self, metadata):
        """Test the list_events tool schema."""
        tool = next(t for t in metadata['tools'] if t['name'] == 'list_events')
        
        # Input schema should have optional filters
        assert tool['input_schema']['type'] == 'object'
        assert 'properties' in tool['input_schema']
        assert 'calendar_id' in tool['input_schema']['properties']
        assert 'time_min' in tool['input_schema']['properties']
        assert 'time_max' in tool['input_schema']['properties']
        assert tool['input_schema']['required'] == []
        
        # Output schema should be array of event objects
        assert tool['output_schema']['type'] == 'array'
        assert 'items' in tool['output_schema']
        assert tool['output_schema']['items']['type'] == 'object'
        
        # Event object properties
        event_props = tool['output_schema']['items']['properties']
        required_fields = tool['output_schema']['items']['required']
        
        assert 'id' in event_props
        assert 'calendarId' in event_props
        assert 'summary' in event_props
        assert 'start' in event_props
        assert 'end' in event_props
        assert 'status' in event_props
        
        # Required fields
        assert 'id' in required_fields
        assert 'calendarId' in required_fields
        assert 'summary' in required_fields
        assert 'start' in required_fields
        assert 'end' in required_fields
        assert 'status' in required_fields
        
        # Nested start/end structure
        assert event_props['start']['type'] == 'object'
        assert 'dateTime' in event_props['start']['required']
        assert 'timeZone' in event_props['start']['required']
        
        assert event_props['end']['type'] == 'object'
        assert 'dateTime' in event_props['end']['required']
        assert 'timeZone' in event_props['end']['required']
    
    def test_create_event_tool_schema(self, metadata):
        """Test the create_event tool schema."""
        tool = next(t for t in metadata['tools'] if t['name'] == 'create_event')
        
        # Input schema should have required fields
        assert tool['input_schema']['type'] == 'object'
        assert 'properties' in tool['input_schema']
        
        required_fields = tool['input_schema']['required']
        assert 'calendar_id' in required_fields
        assert 'summary' in required_fields
        assert 'start_time' in required_fields
        assert 'end_time' in required_fields
        
        # Output schema should match event structure
        assert tool['output_schema']['type'] == 'object'
        event_props = tool['output_schema']['properties']
        required_fields = tool['output_schema']['required']
        
        assert 'id' in event_props
        assert 'calendarId' in event_props
        assert 'summary' in event_props
        assert 'start' in event_props
        assert 'end' in event_props
        assert 'status' in event_props
        
        # Required fields
        assert 'id' in required_fields
        assert 'calendarId' in required_fields
        assert 'summary' in required_fields
        assert 'start' in required_fields
        assert 'end' in required_fields
        assert 'status' in required_fields
    
    def test_update_event_tool_schema(self, metadata):
        """Test the update_event tool schema."""
        tool = next(t for t in metadata['tools'] if t['name'] == 'update_event')
        
        # Input schema should have event_id as required
        assert tool['input_schema']['type'] == 'object'
        assert 'properties' in tool['input_schema']
        
        required_fields = tool['input_schema']['required']
        assert 'event_id' in required_fields
        
        # Output schema should match event structure
        assert tool['output_schema']['type'] == 'object'
        event_props = tool['output_schema']['properties']
        required_fields = tool['output_schema']['required']
        
        assert 'id' in event_props
        assert 'calendarId' in event_props
        assert 'summary' in event_props
        assert 'start' in event_props
        assert 'end' in event_props
        assert 'status' in event_props
    
    def test_delete_event_tool_schema(self, metadata):
        """Test the delete_event tool schema."""
        tool = next(t for t in metadata['tools'] if t['name'] == 'delete_event')
        
        # Input schema should have both calendar_id and event_id as required
        assert tool['input_schema']['type'] == 'object'
        assert 'properties' in tool['input_schema']
        
        required_fields = tool['input_schema']['required']
        assert 'calendar_id' in required_fields
        assert 'event_id' in required_fields
        
        # Output schema should have message and deleted_event
        assert tool['output_schema']['type'] == 'object'
        assert 'message' in tool['output_schema']['properties']
        assert 'deleted_event' in tool['output_schema']['properties']
        
        required_fields = tool['output_schema']['required']
        assert 'message' in required_fields
        assert 'deleted_event' in required_fields
    
    def test_usage_examples(self, metadata):
        """Test that usage examples are provided for all tools."""
        tool_names = [tool['name'] for tool in metadata['tools']]
        
        for tool_name in tool_names:
            assert tool_name in metadata['usage_examples'], f"Missing usage example for {tool_name}"
            assert isinstance(metadata['usage_examples'][tool_name], str)
            assert len(metadata['usage_examples'][tool_name]) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])