"""
Test that the server module can be imported and initialized correctly.
"""

import sys
import pytest
from pathlib import Path

# Add the generated directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'generated' / 'google-calendar'))


def test_server_import():
    """Test that the server module can be imported successfully."""
    # This should not raise any import errors
    from google_calendar_server import mcp
    
    # Verify the MCP server is properly initialized
    assert mcp is not None
    assert hasattr(mcp, 'name')
    assert mcp.name == "Google Calendar"
    
    # Verify the server can be imported and basic functionality works
    import google_calendar_server
    
    # Test that we can load the dataset
    dataset = google_calendar_server.load_dataset()
    assert dataset is not None
    assert 'calendars' in dataset
    assert 'events' in dataset


def test_server_module_attributes():
    """Test that the server module has expected attributes."""
    import google_calendar_server
    
    # Verify module has expected functions
    assert hasattr(google_calendar_server, 'load_dataset')
    assert hasattr(google_calendar_server, 'save_dataset')
    assert hasattr(google_calendar_server, 'list_calendars')
    assert hasattr(google_calendar_server, 'list_events')
    assert hasattr(google_calendar_server, 'create_event')
    assert hasattr(google_calendar_server, 'update_event')
    assert hasattr(google_calendar_server, 'delete_event')
    
    # Verify these are callable functions
    assert callable(google_calendar_server.load_dataset)
    assert callable(google_calendar_server.save_dataset)
    assert callable(google_calendar_server.list_calendars)
    assert callable(google_calendar_server.list_events)
    assert callable(google_calendar_server.create_event)
    assert callable(google_calendar_server.update_event)
    assert callable(google_calendar_server.delete_event)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])