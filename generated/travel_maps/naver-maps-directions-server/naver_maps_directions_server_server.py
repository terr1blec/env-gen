"""
Naver Maps Directions Server - FastMCP implementation

This server provides offline Korean map services including:
- Directions between locations
- Address geocoding
- Reverse geocoding from coordinates
- Static map generation

All data is loaded from the local database JSON file.
"""

import json
import os
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(name="Naver Maps Directions Server")

# Database file path
DATABASE_PATH = os.path.join(
    os.path.dirname(__file__), 
    "naver_maps_directions_server_database.json"
)

# Default values for optional parameters
DEFAULT_HEIGHT = "400"
DEFAULT_WIDTH = "500"
DEFAULT_LEVEL = "12"
DEFAULT_FORMAT = "png"

# Load database from JSON file
def load_database() -> Dict[str, Any]:
    """Load the database from JSON file with fallback to empty structure."""
    try:
        with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load database from {DATABASE_PATH}: {e}")
        # Return empty structure matching DATA CONTRACT
        return {
            "directions": [],
            "geocoding": [],
            "reverse_geocoding": [],
            "static_maps": []
        }

@mcp.tool()
def naver_directions(
    goal: str,
    start: str,
    option: Optional[str] = None,
    waypoints: Optional[str] = None
) -> Dict[str, Any]:
    """Get directions between two locations in Korea.

    Args:
        goal (str): The destination location.
        start (str): The starting location.
        option (str, optional): Route option (fastest, shortest, recommended, avoid_tolls).
        waypoints (str, optional): Waypoints to pass through.

    Returns:
        dict: Route information including distance, duration, and steps.
    """
    database = load_database()
    
    # Search for matching direction record
    for direction in database.get("directions", []):
        # Match start and goal (case-insensitive partial match)
        if (direction.get("start", "").lower() in start.lower() or 
            start.lower() in direction.get("start", "").lower()) and \
           (direction.get("goal", "").lower() in goal.lower() or 
            goal.lower() in direction.get("goal", "").lower()):
            
            # Check if option matches (if specified)
            if option and direction.get("option") != option:
                continue
                
            # Check if waypoints match (if specified)
            if waypoints and direction.get("waypoints") != waypoints:
                continue
            
            return {
                "route_id": direction.get("id"),
                "start": direction.get("start"),
                "goal": direction.get("goal"),
                "option": direction.get("option"),
                "waypoints": direction.get("waypoints"),
                "route_info": direction.get("route_info", {})
            }
    
    return {
        "error": "No route found for the specified locations",
        "start": start,
        "goal": goal,
        "option": option,
        "waypoints": waypoints
    }

@mcp.tool()
def naver_geocode(address: str) -> Dict[str, Any]:
    """Convert a Korean address to geographic coordinates.

    Args:
        address (str): The Korean address to geocode.

    Returns:
        dict: Coordinates (latitude and longitude) for the address.
    """
    database = load_database()
    
    # Search for matching geocoding record
    for geocode in database.get("geocoding", []):
        # Case-insensitive partial match
        if address.lower() in geocode.get("address", "").lower():
            return {
                "geocode_id": geocode.get("id"),
                "address": geocode.get("address"),
                "coordinates": geocode.get("coordinates", {})
            }
    
    return {
        "error": "Address not found in database",
        "address": address
    }

@mcp.tool()
def naver_reverse_geocode(lat: str, lng: str) -> Dict[str, Any]:
    """Convert geographic coordinates to a Korean address.

    Args:
        lat (str): Latitude coordinate.
        lng (str): Longitude coordinate.

    Returns:
        dict: Address corresponding to the coordinates.
    """
    database = load_database()
    
    # Search for matching reverse geocoding record
    for reverse_geocode in database.get("reverse_geocoding", []):
        # Match coordinates (exact match for string values)
        if (reverse_geocode.get("lat") == lat and 
            reverse_geocode.get("lng") == lng):
            return {
                "reverse_geocode_id": reverse_geocode.get("id"),
                "lat": lat,
                "lng": lng,
                "address": reverse_geocode.get("address")
            }
    
    return {
        "error": "Coordinates not found in database",
        "lat": lat,
        "lng": lng
    }

@mcp.tool()
def naver_static_map(
    center: str,
    h: Optional[str] = None,
    w: Optional[str] = None,
    level: Optional[str] = None,
    format: Optional[str] = None
) -> Dict[str, Any]:
    """Generate a static map image for the specified location.

    Args:
        center (str): Center coordinates in "lat,lng" format.
        h (str, optional): Map height in pixels.
        w (str, optional): Map width in pixels.
        level (str, optional): Zoom level.
        format (str, optional): Image format (png, jpg).

    Returns:
        dict: Static map data including base64-encoded image.
    """
    database = load_database()
    
    # Apply defaults for optional parameters
    target_h = h or DEFAULT_HEIGHT
    target_w = w or DEFAULT_WIDTH
    target_level = level or DEFAULT_LEVEL
    target_format = format or DEFAULT_FORMAT
    
    # Search for matching static map record
    for static_map in database.get("static_maps", []):
        # Match center coordinates
        if static_map.get("center") == center:
            # Check if optional parameters match (if specified)
            if h and static_map.get("h") != h:
                continue
            if w and static_map.get("w") != w:
                continue
            if level and static_map.get("level") != level:
                continue
            if format and static_map.get("format") != format:
                continue
            
            # Use the record's values or defaults
            return {
                "map_id": static_map.get("id"),
                "center": center,
                "h": static_map.get("h") or target_h,
                "w": static_map.get("w") or target_w,
                "level": static_map.get("level") or target_level,
                "format": static_map.get("format") or target_format,
                "image_data": static_map.get("image_data")
            }
    
    return {
        "error": "Static map not found for the specified center coordinates",
        "center": center,
        "h": target_h,
        "w": target_w,
        "level": target_level,
        "format": target_format
    }

if __name__ == "__main__":
    mcp.run()