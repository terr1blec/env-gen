"""
Google Maps MCP Server

A FastMCP-compliant server that provides Google Maps functionality using an offline database.
This server exposes tools for geocoding, reverse geocoding, place search, place details,
distance matrix calculations, elevation data, and directions.
"""

import json
import os
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(name="Google Maps")

# Database path
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "google_maps_database.json")

# Fallback data structure in case database is missing
FALLBACK_DATABASE = {
    "geocoding_results": [],
    "reverse_geocoding_results": [],
    "places_search_results": [],
    "place_details": [],
    "distance_matrix_results": [],
    "elevation_data": [],
    "directions_results": []
}


def load_database() -> Dict[str, Any]:
    """Load the Google Maps database from JSON file."""
    try:
        with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load database from {DATABASE_PATH}: {e}")
        print("Using fallback database structure")
        return FALLBACK_DATABASE


@mcp.tool()
def maps_geocode(address: str) -> Dict[str, Any]:
    """Convert an address into geographic coordinates.

    Args:
        address (str): The address to geocode, e.g., "754 Main St, New York"

    Returns:
        dict: Geocoding result with latitude, longitude, formatted address, and place_id
    """
    database = load_database()
    
    # Search for matching address in geocoding_results
    for result in database.get("geocoding_results", []):
        if result.get("address", "").lower() == address.lower():
            return {
                "latitude": result.get("latitude"),
                "longitude": result.get("longitude"),
                "formatted_address": result.get("formatted_address"),
                "place_id": result.get("place_id")
            }
    
    # Return error if not found
    return {
        "error": f"Address '{address}' not found in database",
        "latitude": None,
        "longitude": None,
        "formatted_address": None,
        "place_id": None
    }


@mcp.tool()
def maps_reverse_geocode(latitude: str, longitude: str) -> Dict[str, Any]:
    """Convert geographic coordinates into a human-readable address.

    Args:
        latitude (str): The latitude coordinate as a string
        longitude (str): The longitude coordinate as a string

    Returns:
        dict: Reverse geocoding result with formatted address and address components
    """
    database = load_database()
    
    # Search for matching coordinates in reverse_geocoding_results
    for result in database.get("reverse_geocoding_results", []):
        if (result.get("latitude") == latitude and 
            result.get("longitude") == longitude):
            return {
                "formatted_address": result.get("formatted_address"),
                "address_components": result.get("address_components", [])
            }
    
    # Return error if not found
    return {
        "error": f"Coordinates ({latitude}, {longitude}) not found in database",
        "formatted_address": None,
        "address_components": []
    }


@mcp.tool()
def maps_search_places(query: str) -> Dict[str, Any]:
    """Search for places using a query string.

    Args:
        query (str): The search query, e.g., "restaurant in New York"

    Returns:
        dict: Search results with list of matching places
    """
    database = load_database()
    
    # Search for matching query in places_search_results
    for search_result in database.get("places_search_results", []):
        if search_result.get("query", "").lower() == query.lower():
            return {
                "query": search_result.get("query"),
                "results": search_result.get("results", [])
            }
    
    # Return error if not found
    return {
        "error": f"No results found for query '{query}'",
        "query": query,
        "results": []
    }


@mcp.tool()
def maps_place_details(place_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific place.

    Args:
        place_id (str): The unique identifier for the place, e.g., "PLACE_0000"

    Returns:
        dict: Detailed place information including name, address, phone, website, rating, and opening hours
    """
    database = load_database()
    
    # Search for matching place_id in place_details
    for place in database.get("place_details", []):
        if place.get("place_id") == place_id:
            return {
                "place_id": place.get("place_id"),
                "name": place.get("name"),
                "formatted_address": place.get("formatted_address"),
                "phone_number": place.get("phone_number"),
                "website": place.get("website"),
                "rating": place.get("rating"),
                "opening_hours": place.get("opening_hours", {})
            }
    
    # Return error if not found
    return {
        "error": f"Place with ID '{place_id}' not found in database",
        "place_id": place_id,
        "name": None,
        "formatted_address": None,
        "phone_number": None,
        "website": None,
        "rating": None,
        "opening_hours": {}
    }


@mcp.tool()
def maps_distance_matrix(origins: List[str], destinations: List[str]) -> Dict[str, Any]:
    """Calculate travel distance and time between multiple origins and destinations.

    Args:
        origins (list): List of origin locations as strings
        destinations (list): List of destination locations as strings

    Returns:
        dict: Distance matrix results with distances and durations
    """
    database = load_database()
    
    # Search for matching origins and destinations in distance_matrix_results
    for matrix in database.get("distance_matrix_results", []):
        if (matrix.get("origins") == origins and 
            matrix.get("destinations") == destinations):
            return {
                "origins": matrix.get("origins"),
                "destinations": matrix.get("destinations"),
                "distances": matrix.get("distances"),
                "durations": matrix.get("durations")
            }
    
    # Return error if not found
    return {
        "error": f"No distance matrix found for origins {origins} and destinations {destinations}",
        "origins": origins,
        "destinations": destinations,
        "distances": [],
        "durations": []
    }


@mcp.tool()
def maps_elevation(locations: List[Dict[str, float]]) -> Dict[str, Any]:
    """Get elevation data for geographic locations.

    Args:
        locations (list): List of location dictionaries with 'lat' and 'lng' keys

    Returns:
        dict: Elevation data with locations and corresponding elevations
    """
    database = load_database()
    
    # Search for matching locations in elevation_data
    for elevation_set in database.get("elevation_data", []):
        if elevation_set.get("locations") == locations:
            return {
                "locations": elevation_set.get("locations"),
                "elevations": elevation_set.get("elevations")
            }
    
    # Return error if not found
    return {
        "error": f"No elevation data found for locations {locations}",
        "locations": locations,
        "elevations": []
    }


@mcp.tool()
def maps_directions(origin: str, destination: str, mode: Optional[str] = "driving") -> Dict[str, Any]:
    """Get directions between two points with optional travel mode.

    Args:
        origin (str): The starting location
        destination (str): The destination location
        mode (str, optional): Travel mode - driving, walking, bicycling, transit. Defaults to "driving"

    Returns:
        dict: Directions result with steps, total distance, and duration
    """
    database = load_database()
    
    # Search for matching route in directions_results
    for directions in database.get("directions_results", []):
        if (directions.get("origin") == origin and 
            directions.get("destination") == destination and
            directions.get("mode") == mode):
            return {
                "origin": directions.get("origin"),
                "destination": directions.get("destination"),
                "mode": directions.get("mode"),
                "steps": directions.get("steps", []),
                "distance": directions.get("distance"),
                "duration": directions.get("duration")
            }
    
    # Return error if not found
    return {
        "error": f"No directions found from '{origin}' to '{destination}' with mode '{mode}'",
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "steps": [],
        "distance": None,
        "duration": None
    }


if __name__ == "__main__":
    mcp.run()