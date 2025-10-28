"""
SNCF API Server - FastMCP server module for French train information.

This server provides tools for journey planning, disruption checking, 
schedule lookup, and station information using an offline database.
"""

import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(name="SNCF API Server")

# Database loading and validation - using os.path.join for cross-platform compatibility
DATABASE_PATH = os.path.join("generated", "travel_maps", "sncf-api-server", "sncf_api_server_database.json")

# Default fallback data structure if database is missing
FALLBACK_DATA = {
    "stations": [],
    "journeys": [],
    "disruptions": [],
    "schedules": []
}


def load_database() -> Dict[str, Any]:
    """Load the database from JSON file with fallback to empty data."""
    try:
        with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate required top-level keys
        required_keys = ["stations", "journeys", "disruptions", "schedules"]
        for key in required_keys:
            if key not in data:
                data[key] = FALLBACK_DATA[key]
        
        return data
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Warning: Could not load database from {DATABASE_PATH}: {e}")
        return FALLBACK_DATA


@mcp.tool()
def plan_journey_by_city_names(
    origin_city: str,
    destination_city: str,
    date: Optional[str] = None
) -> Dict[str, Any]:
    """Plan a train journey between two French cities.

    Args:
        origin_city (str): The departure city name (e.g., "Paris", "Lyon", "Marseille").
        destination_city (str): The arrival city name (e.g., "Bordeaux", "Lille").
        date (Optional[str]): The travel date in ISO format (YYYY-MM-DD). If not provided, 
                              returns all available journeys.

    Returns:
        Dict[str, Any]: Object containing 'journeys' property with list of available journeys.
    """
    database = load_database()
    journeys = database.get("journeys", [])
    
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


@mcp.tool()
def check_disruptions(
    coverage: Optional[str] = None,
    station: Optional[str] = None,
    line: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Check SNCF network disruptions with optional filtering.

    Args:
        coverage (Optional[str]): Coverage area to filter by (e.g., "regional", "national").
        station (Optional[str]): Specific station ID to filter disruptions.
        line (Optional[str]): Specific train line to filter disruptions.
        start_date (Optional[str]): Start date for disruption period in ISO format.
        end_date (Optional[str]): End date for disruption period in ISO format.

    Returns:
        Dict[str, Any]: Object containing 'disruptions' property with list of disruptions.
    """
    database = load_database()
    disruptions = database.get("disruptions", [])
    
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
    
    # Note: coverage parameter is not currently used in the database structure
    # but kept for API compatibility
    
    return {"disruptions": filtered_disruptions}


@mcp.tool()
def get_station_schedule(
    station_id: str,
    datetime_filter: Optional[str] = None,
    data_freshness: str = "base_schedule"
) -> Dict[str, Any]:
    """Get station departures and arrivals schedule.

    Args:
        station_id (str): The station ID to get schedule for.
        datetime_filter (Optional[str]): Date/time filter in ISO format to get specific schedule.
        data_freshness (str): Data freshness mode - "base_schedule" or "realtime". 
                             Defaults to "base_schedule" for offline database.

    Returns:
        Dict[str, Any]: Station schedule information including departures and arrivals.
    """
    database = load_database()
    schedules = database.get("schedules", [])
    
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


@mcp.tool()
def get_station_details(station_id: str) -> Dict[str, Any]:
    """Get comprehensive station information.

    Args:
        station_id (str): The station ID to get details for.

    Returns:
        Dict[str, Any]: Comprehensive station information including transport types 
                       and nearby places. Returns empty station object with error flag if not found.
    """
    database = load_database()
    stations = database.get("stations", [])
    
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


if __name__ == "__main__":
    mcp.run()