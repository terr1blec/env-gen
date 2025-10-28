"""
Test suite for SNCF API Server FastMCP implementation.

Validates that the server can load the offline database and correctly expose tools
that consume the DATA CONTRACT keys from the database.
"""

import json
import os
import sys
import pytest
from datetime import datetime

# Add the generated module path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'travel_maps', 'sncf-api-server'))

# Import the server module
from sncf_api_server_server import (
    load_database,
    plan_journey_by_city_names,
    check_disruptions,
    get_station_schedule,
    get_station_details,
    DATABASE_PATH
)


class TestSNCFAPIServer:
    """Test suite for SNCF API Server functionality."""

    def test_database_loading(self):
        """Test that the database can be loaded and contains required keys."""
        database = load_database()
        
        # Check that database is loaded
        assert database is not None
        
        # Check required DATA CONTRACT keys exist
        required_keys = ["stations", "journeys", "disruptions", "schedules"]
        for key in required_keys:
            assert key in database, f"Required key '{key}' missing from database"
            assert isinstance(database[key], list), f"Database key '{key}' should be a list"
        
        # Verify database has some data
        assert len(database["stations"]) > 0, "No stations found in database"
        assert len(database["journeys"]) > 0, "No journeys found in database"
        assert len(database["disruptions"]) > 0, "No disruptions found in database"
        assert len(database["schedules"]) > 0, "No schedules found in database"

    def test_plan_journey_by_city_names(self):
        """Test journey planning functionality."""
        # Test basic journey planning
        result = plan_journey_by_city_names("Paris", "Bordeaux")
        assert "journeys" in result
        assert isinstance(result["journeys"], list)
        
        # Verify journey structure
        if result["journeys"]:
            journey = result["journeys"][0]
            required_journey_keys = ["id", "from_city", "to_city", "departure_time", "arrival_time", "duration", "transfers", "price"]
            for key in required_journey_keys:
                assert key in journey, f"Journey missing required key: {key}"
        
        # Test with date filter
        result_with_date = plan_journey_by_city_names("Paris", "Bordeaux", "2024-01-15")
        assert "journeys" in result_with_date
        
        # Test non-existent route
        result_empty = plan_journey_by_city_names("Paris", "NonExistentCity")
        assert "journeys" in result_empty
        assert len(result_empty["journeys"]) == 0

    def test_check_disruptions(self):
        """Test disruption checking functionality."""
        # Test without filters
        result = check_disruptions()
        assert "disruptions" in result
        assert isinstance(result["disruptions"], list)
        
        # Verify disruption structure
        if result["disruptions"]:
            disruption = result["disruptions"][0]
            required_disruption_keys = ["id", "severity", "message", "affected_stations", "affected_lines", "start_time", "end_time"]
            for key in required_disruption_keys:
                assert key in disruption, f"Disruption missing required key: {key}"
        
        # Test with station filter
        result_station = check_disruptions(station="station_001")
        assert "disruptions" in result_station
        
        # Test with line filter
        result_line = check_disruptions(line="TGV Est")
        assert "disruptions" in result_line
        
        # Test with date filters
        result_date = check_disruptions(start_date="2025-10-27T00:00:00Z", end_date="2025-10-27T12:00:00Z")
        assert "disruptions" in result_date

    def test_get_station_schedule(self):
        """Test station schedule functionality."""
        # Test with valid station
        result = get_station_schedule("station_001")
        assert "station_id" in result
        assert result["station_id"] == "station_001"
        assert "datetime" in result
        assert "departures" in result
        assert "arrivals" in result
        assert isinstance(result["departures"], list)
        assert isinstance(result["arrivals"], list)
        
        # Verify departure/arrival structure
        if result["departures"]:
            departure = result["departures"][0]
            required_departure_keys = ["time", "train_type", "train_number", "status", "platform", "destination"]
            for key in required_departure_keys:
                assert key in departure, f"Departure missing required key: {key}"
        
        if result["arrivals"]:
            arrival = result["arrivals"][0]
            required_arrival_keys = ["time", "train_type", "train_number", "status", "platform", "origin"]
            for key in required_arrival_keys:
                assert key in arrival, f"Arrival missing required key: {key}"
        
        # Test with datetime filter
        result_filtered = get_station_schedule("station_001", datetime_filter="2025-10-27T00:30:00Z")
        assert "station_id" in result_filtered
        
        # Test with non-existent station
        result_empty = get_station_schedule("non_existent_station")
        assert "station_id" in result_empty
        assert result_empty["station_id"] == "non_existent_station"
        assert result_empty["departures"] == []
        assert result_empty["arrivals"] == []

    def test_get_station_details(self):
        """Test station details functionality."""
        # Test with valid station
        result = get_station_details("station_001")
        assert "id" in result
        assert result["id"] == "station_001"
        assert "name" in result
        assert "city" in result
        assert "coordinates" in result
        assert "transport_types" in result
        assert "nearby_places" in result
        
        # Verify station structure
        required_station_keys = ["id", "name", "city", "coordinates", "transport_types", "nearby_places"]
        for key in required_station_keys:
            assert key in result, f"Station missing required key: {key}"
        
        # Verify coordinates structure
        assert "lat" in result["coordinates"]
        assert "lon" in result["coordinates"]
        
        # Test with non-existent station
        result_not_found = get_station_details("non_existent_station")
        assert "id" in result_not_found
        assert result_not_found["id"] == "non_existent_station"
        assert "error" in result_not_found
        assert "not found" in result_not_found["error"].lower()

    def test_metadata_alignment(self):
        """Test that server tools align with metadata specification."""
        # Load metadata
        metadata_path = os.path.join(
            os.path.dirname(DATABASE_PATH), 
            "sncf_api_server_metadata.json"
        )
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Check top-level metadata structure
        assert "name" in metadata
        assert "description" in metadata
        assert "tools" in metadata
        assert isinstance(metadata["tools"], list)
        
        # Verify server name matches metadata
        assert metadata["name"] == "SNCF API Server"
        
        # Check each tool in metadata
        tool_names = [tool["name"] for tool in metadata["tools"]]
        expected_tools = [
            "plan_journey_by_city_names",
            "check_disruptions", 
            "get_station_schedule",
            "get_station_details"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Tool {expected_tool} missing from metadata"
        
        # Verify each tool has required schema fields
        for tool in metadata["tools"]:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool
            assert "output_schema" in tool
            
            # Check input schema structure
            input_schema = tool["input_schema"]
            assert "type" in input_schema
            assert input_schema["type"] == "object"
            assert "properties" in input_schema
            
            # Check output schema structure
            output_schema = tool["output_schema"]
            assert "type" in output_schema
            assert output_schema["type"] == "object"
            assert "properties" in output_schema


if __name__ == "__main__":
    pytest.main([__file__, "-v"])