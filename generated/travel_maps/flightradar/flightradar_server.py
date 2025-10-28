"""
FlightRadar MCP Server

A FastMCP-compliant server that provides flight tracking and information services
using an offline database of flights, airports, and airlines.
"""

import json
import os
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(name="FlightRadar")

# Database file path
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "flightradar_database.json")

# Fallback data structure (used only if database file is missing)
FALLBACK_DATA = {
    "flights": [],
    "airports": [],
    "airlines": []
}

# Valid flight statuses for validation
VALID_STATUSES = {"scheduled", "active", "landed", "cancelled", "diverted"}


def load_database() -> Dict[str, Any]:
    """Load the flight database from JSON file with validation.
    
    Returns:
        Dict containing flights, airports, and airlines data
    """
    try:
        with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate required top-level keys per DATA CONTRACT
        required_keys = ["flights", "airports", "airlines"]
        if not all(key in data for key in required_keys):
            print(f"Warning: Database missing required keys {required_keys}. Using fallback data.")
            return FALLBACK_DATA
        
        # Validate data types
        if not isinstance(data["flights"], list) or not isinstance(data["airports"], list) or not isinstance(data["airlines"], list):
            print(f"Warning: Database has invalid data types. Using fallback data.")
            return FALLBACK_DATA
            
        # Validate flight structure against DATA CONTRACT
        if data["flights"]:
            sample_flight = data["flights"][0]
            flight_required_fields = ["flight_iata", "flight_icao", "airline_iata", "airline_icao", 
                                    "flight_number", "dep_iata", "arr_iata", "dep_time", "arr_time", 
                                    "status", "aircraft_icao", "duration", "dep_terminal", 
                                    "arr_terminal", "dep_gate", "arr_gate"]
            
            missing_fields = [field for field in flight_required_fields if field not in sample_flight]
            if missing_fields:
                print(f"Warning: Database flights missing required fields: {missing_fields}")
        
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load database from {DATABASE_PATH}: {e}")
        print("Using fallback data structure.")
        return FALLBACK_DATA


def validate_flight_status(status: str) -> bool:
    """Validate that a flight status is one of the expected values.
    
    Args:
        status (str): Flight status to validate
        
    Returns:
        bool: True if status is valid
    """
    return status.lower() in VALID_STATUSES


@mcp.tool()
def get_flight_data(flight_identifier: str) -> Dict[str, Any]:
    """Get detailed information for a specific flight.
    
    Args:
        flight_identifier (str): Flight identifier (IATA code, ICAO code, or flight number)
    
    Returns:
        Dict containing flight details including departure/arrival info, status, and aircraft
    """
    database = load_database()
    flights = database.get("flights", [])
    
    # Search for flight by various identifiers
    flight = None
    for f in flights:
        if (flight_identifier.upper() == f.get("flight_iata", "") or
            flight_identifier.upper() == f.get("flight_icao", "") or
            flight_identifier.upper() == f.get("flight_number", "")):
            flight = f
            break
    
    if not flight:
        return {
            "error": f"Flight '{flight_identifier}' not found",
            "flight_identifier": flight_identifier
        }
    
    # Get airport and airline details
    airports = database.get("airports", [])
    airlines = database.get("airlines", [])
    
    departure_airport = next((a for a in airports if a.get("iata_code") == flight.get("dep_iata")), None)
    arrival_airport = next((a for a in airports if a.get("iata_code") == flight.get("arr_iata")), None)
    airline = next((al for al in airlines if al.get("iata_code") == flight.get("airline_iata")), None)
    
    return {
        "flight_iata": flight.get("flight_iata"),
        "flight_icao": flight.get("flight_icao"),
        "flight_number": flight.get("flight_number"),
        "airline": airline.get("name") if airline else None,
        "airline_iata": flight.get("airline_iata"),
        "airline_icao": flight.get("airline_icao"),
        "departure": {
            "airport": departure_airport.get("name") if departure_airport else None,
            "iata": flight.get("dep_iata"),
            "city": departure_airport.get("city") if departure_airport else None,
            "country": departure_airport.get("country") if departure_airport else None,
            "time": flight.get("dep_time"),
            "terminal": flight.get("dep_terminal"),
            "gate": flight.get("dep_gate")
        },
        "arrival": {
            "airport": arrival_airport.get("name") if arrival_airport else None,
            "iata": flight.get("arr_iata"),
            "city": arrival_airport.get("city") if arrival_airport else None,
            "country": arrival_airport.get("country") if arrival_airport else None,
            "time": flight.get("arr_time"),
            "terminal": flight.get("arr_terminal"),
            "gate": flight.get("arr_gate")
        },
        "status": flight.get("status"),
        "aircraft": flight.get("aircraft_icao"),
        "duration": flight.get("duration")
    }


@mcp.tool()
def search_flights(
    departure_airport: Optional[str] = None,
    arrival_airport: Optional[str] = None,
    airline: Optional[str] = None,
    status: Optional[str] = None,
    max_results: int = 20
) -> Dict[str, Any]:
    """Search for flights based on various criteria.
    
    Args:
        departure_airport (Optional[str]): Departure airport IATA code
        arrival_airport (Optional[str]): Arrival airport IATA code
        airline (Optional[str]): Airline IATA code
        status (Optional[str]): Flight status (scheduled, active, landed, cancelled, diverted)
        max_results (int): Maximum number of results to return (default: 20)
    
    Returns:
        Dict containing list of matching flights and search metadata
    """
    database = load_database()
    flights = database.get("flights", [])
    
    # Validate status if provided
    if status and not validate_flight_status(status):
        return {
            "error": f"Invalid status '{status}'. Valid statuses: {', '.join(VALID_STATUSES)}",
            "search_criteria": {
                "departure_airport": departure_airport,
                "arrival_airport": arrival_airport,
                "airline": airline,
                "status": status
            },
            "total_matches": 0,
            "returned_results": 0,
            "flights": []
        }
    
    # Apply filters
    filtered_flights = flights
    
    if departure_airport:
        filtered_flights = [f for f in filtered_flights if f.get("dep_iata", "").upper() == departure_airport.upper()]
    
    if arrival_airport:
        filtered_flights = [f for f in filtered_flights if f.get("arr_iata", "").upper() == arrival_airport.upper()]
    
    if airline:
        filtered_flights = [f for f in filtered_flights if f.get("airline_iata", "").upper() == airline.upper()]
    
    if status:
        filtered_flights = [f for f in filtered_flights if f.get("status", "").lower() == status.lower()]
    
    # Limit results
    limited_flights = filtered_flights[:max_results]
    
    # Get airport and airline details for enriched results
    airports = database.get("airports", [])
    airlines = database.get("airlines", [])
    
    enriched_flights = []
    for flight in limited_flights:
        departure_airport_info = next((a for a in airports if a.get("iata_code") == flight.get("dep_iata")), {})
        arrival_airport_info = next((a for a in airports if a.get("iata_code") == flight.get("arr_iata")), {})
        airline_info = next((al for al in airlines if al.get("iata_code") == flight.get("airline_iata")), {})
        
        enriched_flights.append({
            "flight_iata": flight.get("flight_iata"),
            "flight_icao": flight.get("flight_icao"),
            "flight_number": flight.get("flight_number"),
            "airline": airline_info.get("name"),
            "airline_iata": flight.get("airline_iata"),
            "departure": {
                "airport": departure_airport_info.get("name"),
                "iata": flight.get("dep_iata"),
                "city": departure_airport_info.get("city"),
                "time": flight.get("dep_time"),
                "terminal": flight.get("dep_terminal"),
                "gate": flight.get("dep_gate")
            },
            "arrival": {
                "airport": arrival_airport_info.get("name"),
                "iata": flight.get("arr_iata"),
                "city": arrival_airport_info.get("city"),
                "time": flight.get("arr_time"),
                "terminal": flight.get("arr_terminal"),
                "gate": flight.get("arr_gate")
            },
            "status": flight.get("status"),
            "aircraft": flight.get("aircraft_icao"),
            "duration": flight.get("duration")
        })
    
    return {
        "search_criteria": {
            "departure_airport": departure_airport,
            "arrival_airport": arrival_airport,
            "airline": airline,
            "status": status
        },
        "total_matches": len(filtered_flights),
        "returned_results": len(enriched_flights),
        "flights": enriched_flights
    }


@mcp.tool()
def get_flight_status(flight_identifier: str) -> Dict[str, Any]:
    """Get the current status of a specific flight.
    
    Args:
        flight_identifier (str): Flight identifier (IATA code, ICAO code, or flight number)
    
    Returns:
        Dict containing flight status and basic flight information
    """
    database = load_database()
    flights = database.get("flights", [])
    
    # Search for flight by various identifiers
    flight = None
    for f in flights:
        if (flight_identifier.upper() == f.get("flight_iata", "") or
            flight_identifier.upper() == f.get("flight_icao", "") or
            flight_identifier.upper() == f.get("flight_number", "")):
            flight = f
            break
    
    if not flight:
        return {
            "error": f"Flight '{flight_identifier}' not found",
            "flight_identifier": flight_identifier
        }
    
    # Get airport and airline details
    airports = database.get("airports", [])
    airlines = database.get("airlines", [])
    
    departure_airport = next((a for a in airports if a.get("iata_code") == flight.get("dep_iata")), None)
    arrival_airport = next((a for a in airports if a.get("iata_code") == flight.get("arr_iata")), None)
    airline = next((al for al in airlines if al.get("iata_code") == flight.get("airline_iata")), None)
    
    return {
        "flight_iata": flight.get("flight_iata"),
        "flight_icao": flight.get("flight_icao"),
        "flight_number": flight.get("flight_number"),
        "airline": airline.get("name") if airline else None,
        "route": f"{flight.get('dep_iata')} → {flight.get('arr_iata')}",
        "departure": {
            "airport": departure_airport.get("name") if departure_airport else None,
            "time": flight.get("dep_time")
        },
        "arrival": {
            "airport": arrival_airport.get("name") if arrival_airport else None,
            "time": flight.get("arr_time")
        },
        "status": flight.get("status"),
        "status_description": get_status_description(flight.get("status")),
        "aircraft": flight.get("aircraft_icao"),
        "duration": flight.get("duration")
    }


def get_status_description(status: str) -> str:
    """Get a human-readable description for flight status.
    
    Args:
        status (str): Flight status code
    
    Returns:
        str: Human-readable status description
    """
    status_descriptions = {
        "scheduled": "Flight is scheduled to depart",
        "active": "Flight is currently in progress",
        "landed": "Flight has successfully landed",
        "cancelled": "Flight has been cancelled",
        "diverted": "Flight has been diverted to alternate airport"
    }
    return status_descriptions.get(status.lower(), "Unknown status")


if __name__ == "__main__":
    mcp.run()