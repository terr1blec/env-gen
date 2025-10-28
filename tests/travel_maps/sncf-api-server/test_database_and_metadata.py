"""
Database and metadata validation tests for SNCF API Server.

Tests the database structure, metadata alignment, and core data validation
without requiring FastMCP dependencies.
"""

import json
import os
import pytest


class TestDatabaseAndMetadata:
    """Test suite for database structure and metadata alignment."""

    @property
    def database_path(self):
        """Get the path to the database file."""
        return os.path.join(
            "generated", "travel_maps", "sncf-api-server", "sncf_api_server_database.json"
        )

    @property
    def metadata_path(self):
        """Get the path to the metadata file."""
        return os.path.join(
            "generated", "travel_maps", "sncf-api-server", "sncf_api_server_metadata.json"
        )

    def test_database_file_exists(self):
        """Test that the database file exists."""
        assert os.path.exists(self.database_path), f"Database file not found at {self.database_path}"

    def test_metadata_file_exists(self):
        """Test that the metadata file exists."""
        assert os.path.exists(self.metadata_path), f"Metadata file not found at {self.metadata_path}"

    def test_database_structure(self):
        """Test that the database has the correct structure."""
        with open(self.database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
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

    def test_stations_structure(self):
        """Test station data structure."""
        with open(self.database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        stations = database["stations"]
        assert len(stations) > 0, "No stations in database"
        
        # Check first station structure
        station = stations[0]
        required_station_keys = ["id", "name", "city", "coordinates", "transport_types", "nearby_places"]
        for key in required_station_keys:
            assert key in station, f"Station missing required key: {key}"
        
        # Check coordinates structure
        assert "lat" in station["coordinates"], "Station coordinates missing 'lat'"
        assert "lon" in station["coordinates"], "Station coordinates missing 'lon'"
        
        # Check data types
        assert isinstance(station["transport_types"], list), "transport_types should be a list"
        assert isinstance(station["nearby_places"], list), "nearby_places should be a list"

    def test_journeys_structure(self):
        """Test journey data structure."""
        with open(self.database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        journeys = database["journeys"]
        assert len(journeys) > 0, "No journeys in database"
        
        # Check first journey structure
        journey = journeys[0]
        required_journey_keys = ["id", "from_city", "to_city", "departure_time", "arrival_time", "duration", "transfers", "price"]
        for key in required_journey_keys:
            assert key in journey, f"Journey missing required key: {key}"
        
        # Check data types
        assert isinstance(journey["duration"], int), "duration should be an integer"
        assert isinstance(journey["transfers"], int), "transfers should be an integer"
        assert isinstance(journey["price"], (int, float)), "price should be a number"

    def test_disruptions_structure(self):
        """Test disruption data structure."""
        with open(self.database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        disruptions = database["disruptions"]
        assert len(disruptions) > 0, "No disruptions in database"
        
        # Check first disruption structure
        disruption = disruptions[0]
        required_disruption_keys = ["id", "severity", "message", "affected_stations", "affected_lines", "start_time", "end_time"]
        for key in required_disruption_keys:
            assert key in disruption, f"Disruption missing required key: {key}"
        
        # Check data types
        assert isinstance(disruption["affected_stations"], list), "affected_stations should be a list"
        assert isinstance(disruption["affected_lines"], list), "affected_lines should be a list"

    def test_schedules_structure(self):
        """Test schedule data structure."""
        with open(self.database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        schedules = database["schedules"]
        assert len(schedules) > 0, "No schedules in database"
        
        # Check first schedule structure
        schedule = schedules[0]
        required_schedule_keys = ["station_id", "datetime", "departures", "arrivals"]
        for key in required_schedule_keys:
            assert key in schedule, f"Schedule missing required key: {key}"
        
        # Check departures structure
        if schedule["departures"]:
            departure = schedule["departures"][0]
            required_departure_keys = ["time", "train_type", "train_number", "status", "platform", "destination"]
            for key in required_departure_keys:
                assert key in departure, f"Departure missing required key: {key}"
        
        # Check arrivals structure
        if schedule["arrivals"]:
            arrival = schedule["arrivals"][0]
            required_arrival_keys = ["time", "train_type", "train_number", "status", "platform", "origin"]
            for key in required_arrival_keys:
                assert key in arrival, f"Arrival missing required key: {key}"

    def test_metadata_structure(self):
        """Test metadata structure."""
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Check top-level metadata structure
        assert "name" in metadata, "Metadata missing 'name'"
        assert "description" in metadata, "Metadata missing 'description'"
        assert "tools" in metadata, "Metadata missing 'tools'"
        assert isinstance(metadata["tools"], list), "'tools' should be a list"
        
        # Verify server name
        assert metadata["name"] == "SNCF API Server", "Server name mismatch"

    def test_metadata_tools(self):
        """Test metadata tools structure."""
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        tools = metadata["tools"]
        assert len(tools) > 0, "No tools defined in metadata"
        
        # Check expected tools exist
        tool_names = [tool["name"] for tool in tools]
        expected_tools = [
            "plan_journey_by_city_names",
            "check_disruptions", 
            "get_station_schedule",
            "get_station_details"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Tool {expected_tool} missing from metadata"

    def test_tool_schemas(self):
        """Test that each tool has proper input and output schemas."""
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        for tool in metadata["tools"]:
            # Check tool structure
            assert "name" in tool, "Tool missing 'name'"
            assert "description" in tool, f"Tool {tool['name']} missing 'description'"
            assert "input_schema" in tool, f"Tool {tool['name']} missing 'input_schema'"
            assert "output_schema" in tool, f"Tool {tool['name']} missing 'output_schema'"
            
            # Check input schema structure
            input_schema = tool["input_schema"]
            assert "type" in input_schema, f"Input schema for {tool['name']} missing 'type'"
            assert input_schema["type"] == "object", f"Input schema for {tool['name']} should be 'object'"
            assert "properties" in input_schema, f"Input schema for {tool['name']} missing 'properties'"
            
            # Check output schema structure
            output_schema = tool["output_schema"]
            assert "type" in output_schema, f"Output schema for {tool['name']} missing 'type'"
            assert output_schema["type"] == "object", f"Output schema for {tool['name']} should be 'object'"
            assert "properties" in output_schema, f"Output schema for {tool['name']} missing 'properties'"

    def test_data_consistency(self):
        """Test data consistency between database and metadata."""
        # Load both files
        with open(self.database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Check that all station IDs referenced in schedules exist in stations
        station_ids = {station["id"] for station in database["stations"]}
        
        for schedule in database["schedules"]:
            assert schedule["station_id"] in station_ids, f"Schedule references non-existent station: {schedule['station_id']}"
        
        # Check that all affected stations in disruptions exist
        for disruption in database["disruptions"]:
            for station_id in disruption["affected_stations"]:
                assert station_id in station_ids, f"Disruption references non-existent station: {station_id}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])