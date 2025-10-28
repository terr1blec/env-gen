"""
San Francisco Dog Shelter Finder MCP Server

A FastMCP-compliant server that provides tools for finding dog shelters in San Francisco
based on location, services, and availability criteria.
"""

import json
import math
from typing import List, Optional
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(name="San Francisco Dog Shelter Finder")

# Constants for distance calculation
EARTH_RADIUS_MILES = 3958.8  # Earth's radius in miles


def load_database() -> dict:
    """Load the dog shelter database from JSON file."""
    try:
        with open("generated/travel_maps/san-francisco-dog-shelter-finder/san_francisco_dog_shelter_finder_database.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Validate required structure
        if "shelters" not in data:
            raise ValueError("Database missing required 'shelters' key")
        
        if not isinstance(data["shelters"], list):
            raise ValueError("'shelters' must be an array")
        
        # Validate each shelter has required fields
        required_fields = ["id", "name", "address", "neighborhood", "latitude", "longitude"]
        for shelter in data["shelters"]:
            for field in required_fields:
                if field not in shelter:
                    raise ValueError(f"Shelter missing required field: {field}")
        
        return data
    except FileNotFoundError:
        # Fallback to empty database if file not found
        return {"shelters": []}
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in database file: {e}")


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth using Haversine formula.
    
    Args:
        lat1, lon1: Latitude and longitude of first point in degrees
        lat2, lon2: Latitude and longitude of second point in degrees
        
    Returns:
        Distance in miles
    """
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return EARTH_RADIUS_MILES * c


def get_neighborhood_coordinates(neighborhood: str) -> Optional[tuple[float, float]]:
    """
    Get approximate coordinates for a San Francisco neighborhood.
    
    Args:
        neighborhood: Name of the neighborhood
        
    Returns:
        Tuple of (latitude, longitude) or None if neighborhood not found
    """
    # Approximate coordinates for major SF neighborhoods
    neighborhood_coords = {
        "potrero hill": (37.758, -122.397),
        "noe valley": (37.751, -122.434),
        "hayes valley": (37.777, -122.426),
        "marina": (37.803, -122.440),
        "sunset": (37.759, -122.497),
        "russian hill": (37.802, -122.424),
        "north beach": (37.805, -122.410),
        "pacific heights": (37.790, -122.442),
        "bernal heights": (37.745, -122.417)
    }
    
    return neighborhood_coords.get(neighborhood.lower())


@mcp.tool()
def find_dog_shelters(
    location: Optional[str] = None,
    max_distance: Optional[float] = None,
    services: Optional[List[str]] = None,
    has_vacancy: Optional[bool] = None
) -> dict:
    """
    Find dog shelters in San Francisco based on location and criteria.
    
    Args:
        location: Neighborhood or area in San Francisco
        max_distance: Maximum distance in miles from location
        services: Required services (adoption, boarding, grooming, training, emergency)
        has_vacancy: Only show shelters with available space
        
    Returns:
        Dictionary containing list of matching shelters with details
    """
    # Load database
    database = load_database()
    shelters = database["shelters"]
    
    # Get reference coordinates if location is specified
    reference_lat = None
    reference_lon = None
    if location and max_distance:
        coords = get_neighborhood_coordinates(location)
        if coords:
            reference_lat, reference_lon = coords
        else:
            # If neighborhood not found, try to find a shelter in that neighborhood
            # and use its coordinates as reference
            for shelter in shelters:
                if shelter["neighborhood"].lower() == location.lower():
                    reference_lat = shelter["latitude"]
                    reference_lon = shelter["longitude"]
                    break
    
    filtered_shelters = []
    
    for shelter in shelters:
        # Filter by services
        if services:
            shelter_services = set(shelter.get("services", []))
            required_services = set(services)
            if not required_services.issubset(shelter_services):
                continue
        
        # Filter by vacancy
        if has_vacancy is not None:
            capacity = shelter.get("capacity", 0)
            occupancy = shelter.get("current_occupancy", 0)
            shelter_has_vacancy = occupancy < capacity
            if has_vacancy != shelter_has_vacancy:
                continue
        
        # Filter by location and distance
        distance = None
        if reference_lat and reference_lon:
            shelter_lat = shelter["latitude"]
            shelter_lon = shelter["longitude"]
            distance = haversine_distance(reference_lat, reference_lon, shelter_lat, shelter_lon)
            
            if distance > max_distance:
                continue
        elif location and not max_distance:
            # Filter by neighborhood name only
            if shelter["neighborhood"].lower() != location.lower():
                continue
        
        # Calculate vacancy status
        capacity = shelter.get("capacity", 0)
        occupancy = shelter.get("current_occupancy", 0)
        vacancy = occupancy < capacity
        
        # Prepare shelter data for response
        shelter_data = {
            "id": shelter["id"],
            "name": shelter["name"],
            "address": shelter["address"],
            "neighborhood": shelter["neighborhood"],
            "distance": round(distance, 2) if distance is not None else None,
            "hours": shelter.get("hours"),
            "phone": shelter.get("phone"),
            "website": shelter.get("website"),
            "services": shelter.get("services", []),
            "capacity": capacity,
            "current_occupancy": occupancy,
            "vacancy": vacancy
        }
        
        filtered_shelters.append(shelter_data)
    
    # Sort by distance if available, otherwise by name
    if reference_lat and reference_lon:
        filtered_shelters.sort(key=lambda x: x["distance"] if x["distance"] is not None else float('inf'))
    else:
        filtered_shelters.sort(key=lambda x: x["name"])
    
    return {"shelters": filtered_shelters}


if __name__ == "__main__":
    mcp.run()