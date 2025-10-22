"""
Test configuration for Google Calendar FastMCP server tests.
"""

import pytest
import json
import sys
from pathlib import Path

# Add the generated directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'generated' / 'google-calendar'))


@pytest.fixture(scope="session")
def dataset_backup():
    """
    Backup the original dataset and restore it after tests.
    This ensures tests don't permanently modify the dataset.
    """
    dataset_path = Path(__file__).parent.parent.parent / 'generated' / 'google-calendar' / 'google_calendar_dataset.json'
    
    # Read original data
    with open(dataset_path, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    yield original_data
    
    # Restore original data
    with open(dataset_path, 'w', encoding='utf-8') as f:
        json.dump(original_data, f, indent=2, ensure_ascii=False)