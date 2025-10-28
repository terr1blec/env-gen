"""
Flight Search Service MCP Server

A FastMCP-compliant server that provides flight search capabilities
using an offline database of flights, airports, airlines, and bookings.
"""

import json
import os
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(name="Flight Search Service")

# Database loading and validation
_DATABASE_PATH = os.path.join(
    os.path.dirname(__file__), 
    "flight_search_service_database.json"
)

# Define fallback data structure according to DATA CONTRACT
_FALLBACK_DATABASE = {
    "flights": [],
    "airports": [],
    "airlines": [],
    "bookings": []
}


def load_database() -> Dict[str, Any]:
    """Load and validate the flight database from JSON file."""
    try:
        if os.path.exists(_DATABASE_PATH):
            with open(_DATABASE_PATH, 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            # Validate required top-level keys
            required_keys = ["flights", "airports", "airlines", "bookings"]
            if all(key in database for key in required_keys):
                return database
            else:
                print(f"Warning: Database missing required keys. Using fallback data.")
                return _FALLBACK_DATABASE
        else:
            print(f"Warning: Database file not found at {_DATABASE_PATH}. Using fallback data.")
            return _FALLBACK_DATABASE
    except Exception as e:
        print(f"Error loading database: {e}. Using fallback data.")
        return _FALLBACK_DATABASE


@mcp.tool()
def search_flights(
    departure_airport: str,
    arrival_airport: str,
    departure_date: str
) -> Dict[str, Any]:
    """Search for available flights based on departure and arrival airports.

    Args:
        departure_airport (str): IATA code of departure airport (e.g., "JFK", "LAX")
        arrival_airport (str): IATA code of arrival airport (e.g., "LAX", "LHR")
        departure_date (str): Departure date in YYYY-MM-DD format

    Returns:
        dict: Search results containing flights array and total count
    """
    try:
        # Load database
        database = load_database()
        flights = database.get("flights", [])
        
        # Convert airport codes to uppercase for case-insensitive matching
        departure_upper = departure_airport.upper().strip()
        arrival_upper = arrival_airport.upper().strip()
        
        # Filter flights by departure and arrival airports
        matching_flights = [
            flight for flight in flights
            if flight.get("departure_airport", "").upper() == departure_upper
            and flight.get("arrival_airport", "").upper() == arrival_upper
        ]
        
        # Note: The database doesn't currently store date information in flights,
        # so we return all matching flights regardless of date
        # In a real implementation, we would filter by date as well
        
        return {
            "flights": matching_flights,
            "total_results": len(matching_flights),
            "search_criteria": {
                "departure_airport": departure_upper,
                "arrival_airport": arrival_upper,
                "departure_date": departure_date
            }
        }
        
    except Exception as e:
        return {
            "flights": [],
            "total_results": 0,
            "error": f"Search failed: {str(e)}"
        }


@mcp.tool()
def get_airport_info(airport_code: str) -> Dict[str, Any]:
    """Get detailed information about a specific airport.

    Args:
        airport_code (str): IATA code of the airport (e.g., "JFK", "LAX")

    Returns:
        dict: Airport information including name, city, country, and timezone
    """
    try:
        database = load_database()
        airports = database.get("airports", [])
        
        airport_code_upper = airport_code.upper().strip()
        
        for airport in airports:
            if airport.get("code", "").upper() == airport_code_upper:
                return airport
        
        return {
            "error": f"Airport code '{airport_code}' not found in database"
        }
        
    except Exception as e:
        return {
            "error": f"Failed to retrieve airport info: {str(e)}"
        }


@mcp.tool()
def get_airline_info(airline_code: str) -> Dict[str, Any]:
    """Get information about a specific airline.

    Args:
        airline_code (str): IATA code of the airline (e.g., "DL", "UA")

    Returns:
        dict: Airline information including name and hub airport
    """
    try:
        database = load_database()
        airlines = database.get("airlines", [])
        
        airline_code_upper = airline_code.upper().strip()
        
        for airline in airlines:
            if airline.get("code", "").upper() == airline_code_upper:
                return airline
        
        return {
            "error": f"Airline code '{airline_code}' not found in database"
        }
        
    except Exception as e:
        return {
            "error": f"Failed to retrieve airline info: {str(e)}"
        }


@mcp.tool()
def get_flight_details(flight_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific flight.

    Args:
        flight_id (str): Unique identifier of the flight (e.g., "FL0001")

    Returns:
        dict: Complete flight details
    """
    try:
        database = load_database()
        flights = database.get("flights", [])
        
        for flight in flights:
            if flight.get("flight_id", "") == flight_id:
                return flight
        
        return {
            "error": f"Flight ID '{flight_id}' not found in database"
        }
        
    except Exception as e:
        return {
            "error": f"Failed to retrieve flight details: {str(e)}"
        }


if __name__ == "__main__":
    mcp.run()