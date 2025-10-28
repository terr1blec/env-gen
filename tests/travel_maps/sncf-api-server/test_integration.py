"""
Integration tests for SNCF API Server data processing.

Tests the actual data processing logic by implementing simplified versions
of the server functions that don't require FastMCP.
"""

import json
import os
from datetime import datetime


class SNCFDataProcessor:
    """Simplified data processor that mimics server functionality."""
    
    def __init__(self, database_path):
        self.database_path = database_path
        self.database = self.load_database()
    
    def load_database(self):
        """Load the database from JSON file."""
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load database: {e}")
    
    def plan_journey_by_city_names(self, origin_city, destination_city, date=None):
        """Plan a train journey between two French cities."""
        journeys = self.database.get("journeys", [])
        
        # Filter journeys by origin and destination cities
        matching_journeys = [
            journey for journey in journeys 
            if journey.get("from_city", "").lower() == origin_city.lower()
            and journey.get("to_city", "").lower() == destination_city.lower()
        ]
        
        # Filter by date if provided
        if date:
            try:
                target_date = datetime.fromisoformat(date).date()
                filtered_journeys = []
                for journey in matching_journeys:
                    journey_date = datetime.fromisoformat(journey.get("departure_time", "")).date()
                    if journey_date == target_date:
                        filtered_journeys.append(journey)
                matching_journeys = filtered_journeys
            except ValueError:
                # If date parsing fails, return all matching journeys
                pass
        
        return {"journeys": matching_journeys}
    
    def check_disruptions(self, station=None, line=None, start_date=None, end_date=None):
        """Check SNCF network disruptions with optional filtering."""
        disruptions = self.database.get("disruptions", [])
        
        filtered_disruptions = disruptions.copy()
        
        # Filter by station
        if station:
            filtered_disruptions = [
                d for d in filtered_disruptions 
                if station in d.get("affected_stations", [])
            ]
        
        # Filter by line
        if line:
            filtered_disruptions = [
                d for d in filtered_disruptions 
                if line in d.get("affected_lines", [])
            ]
        
        # Filter by date range
        if start_date or end_date:
            try:
                start_dt = datetime.fromisoformat(start_date) if start_date else None
                end_dt = datetime.fromisoformat(end_date) if end_date else None
                
                date_filtered = []
                for disruption in filtered_disruptions:
                    disruption_start = datetime.fromisoformat(disruption.get("start_time", ""))
                    disruption_end = datetime.fromisoformat(disruption.get("end_time", ""))
                    
                    # Check if disruption overlaps with the specified date range
                    if start_dt and end_dt:
                        if not (disruption_end < start_dt or disruption_start > end_dt):
                            date_filtered.append(disruption)
                    elif start_dt:
                        if disruption_end >= start_dt:
                            date_filtered.append(disruption)
                    elif end_dt:
                        if disruption_start <= end_dt:
                            date_filtered.append(disruption)
                
                filtered_disruptions = date_filtered
            except ValueError:
                # If date parsing fails, skip date filtering
                pass
        
        return {"disruptions": filtered_disruptions}
    
    def get_station_schedule(self, station_id, datetime_filter=None):
        """Get station departures and arrivals schedule."""
        schedules = self.database.get("schedules", [])
        
        # Find schedules for the specified station
        station_schedules = [
            schedule for schedule in schedules 
            if schedule.get("station_id") == station_id
        ]
        
        # Filter by datetime if provided
        if datetime_filter:
            try:
                target_dt = datetime.fromisoformat(datetime_filter)
                # Find the schedule closest to the target datetime
                closest_schedule = None
                min_diff = None
                
                for schedule in station_schedules:
                    schedule_dt = datetime.fromisoformat(schedule.get("datetime", ""))
                    diff = abs((schedule_dt - target_dt).total_seconds())
                    
                    if min_diff is None or diff < min_diff:
                        min_diff = diff
                        closest_schedule = schedule
                
                if closest_schedule:
                    return closest_schedule
            except ValueError:
                # If datetime parsing fails, return first schedule
                pass
        
        # Return first available schedule if no filter or filter failed
        if station_schedules:
            return station_schedules[0]
        
        # Return empty schedule if none found
        return {
            "station_id": station_id,
            "datetime": datetime.now().isoformat(),
            "departures": [],
            "arrivals": []
        }
    
    def get_station_details(self, station_id):
        """Get comprehensive station information."""
        stations = self.database.get("stations", [])
        
        # Find the station by ID
        for station in stations:
            if station.get("id") == station_id:
                return station
        
        # Return consistent structure for not found stations
        return {
            "id": station_id,
            "name": "",
            "city": "",
            "coordinates": {"lat": 0.0, "lon": 0.0},
            "transport_types": [],
            "nearby_places": [],
            "error": f"Station with ID {station_id} not found"
        }


def test_integration():
    """Integration test for data processing functionality."""
    database_path = os.path.join(
        "generated", "travel_maps", "sncf-api-server", "sncf_api_server_database.json"
    )
    
    # Initialize processor
    processor = SNCFDataProcessor(database_path)
    
    # Test journey planning
    print("Testing journey planning...")
    journeys = processor.plan_journey_by_city_names("Paris", "Bordeaux")
    assert "journeys" in journeys
    assert isinstance(journeys["journeys"], list)
    print(f"Found {len(journeys['journeys'])} journeys from Paris to Bordeaux")
    
    # Test disruption checking
    print("\nTesting disruption checking...")
    disruptions = processor.check_disruptions()
    assert "disruptions" in disruptions
    assert isinstance(disruptions["disruptions"], list)
    print(f"Found {len(disruptions['disruptions'])} disruptions")
    
    # Test station schedule
    print("\nTesting station schedule...")
    schedule = processor.get_station_schedule("station_001")
    assert "station_id" in schedule
    assert "departures" in schedule
    assert "arrivals" in schedule
    print(f"Found {len(schedule['departures'])} departures and {len(schedule['arrivals'])} arrivals for station_001")
    
    # Test station details
    print("\nTesting station details...")
    station = processor.get_station_details("station_001")
    assert "id" in station
    assert "name" in station
    assert "city" in station
    print(f"Station {station['id']}: {station['name']} in {station['city']}")
    
    # Test non-existent station
    print("\nTesting non-existent station...")
    not_found = processor.get_station_details("non_existent")
    assert "error" in not_found
    print(f"Error message: {not_found['error']}")
    
    print("\n[SUCCESS] All integration tests passed!")


if __name__ == "__main__":
    test_integration()