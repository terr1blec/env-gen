"""
GeoPal Travel and Logistics Server - FastMCP Implementation

This server provides travel and logistics tools using offline database data.
All tools query the local database JSON file for responses.
"""

import json
import os
from typing import Dict, List, Any, Optional
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(name="GeoPal Travel and Logistics Server")

# Database file path
DATABASE_PATH = os.path.join(
    os.path.dirname(__file__), 
    "geopal_travel_and_logistics_server_database.json"
)


def load_database() -> Dict[str, Any]:
    """Load the offline database from JSON file."""
    try:
        with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Fallback to minimal structure if database is missing
        print(f"Warning: Could not load database from {DATABASE_PATH}: {e}")
        return {
            "geocoding_results": [],
            "isochrone_data": [],
            "poi_data": [],
            "route_data": [],
            "optimization_data": [],
            "traveling_salesman_data": []
        }


@mcp.tool()
def get_directions(
    start: List[float], 
    end: List[float], 
    profile: str = "driving"
) -> Dict[str, Any]:
    """Get directions between two locations.

    Args:
        start (List[float]): Starting coordinates [longitude, latitude]
        end (List[float]): Destination coordinates [longitude, latitude]
        profile (str): Transportation profile (driving, cycling, walking, truck)

    Returns:
        Dict[str, Any]: Route information including distance, duration, and geometry
    """
    database = load_database()
    
    # Find matching route in database
    for route in database.get("route_data", []):
        if (route.get("start") == start and 
            route.get("end") == end and 
            route.get("profile") == profile):
            return {
                "distance": route.get("distance"),
                "duration": route.get("duration"),
                "geometry": route.get("geometry"),
                "profile": route.get("profile")
            }
    
    # Return default response if no match found
    return {
        "distance": 0,
        "duration": 0,
        "geometry": {"type": "LineString", "coordinates": [start, end]},
        "profile": profile,
        "note": "Route not found in database, returning default response"
    }


@mcp.tool()
def geocode_address(address: str) -> Dict[str, Any]:
    """Geocode an address to get coordinates.

    Args:
        address (str): Address or location query to geocode

    Returns:
        Dict[str, Any]: Geocoding result with coordinates and properties
    """
    database = load_database()
    
    # Find matching geocoding result
    for result in database.get("geocoding_results", []):
        if result.get("query", "").lower() == address.lower():
            return {
                "coordinates": result.get("coordinates"),
                "properties": result.get("properties", {}),
                "confidence": result.get("confidence", 0.0)
            }
    
    # Return default response if no match found
    return {
        "coordinates": [0.0, 0.0],
        "properties": {"query": address},
        "confidence": 0.0,
        "note": "Address not found in database"
    }


@mcp.tool()
def get_isochrones(
    location: List[float], 
    profile: str = "driving", 
    ranges: List[int] = [300, 600, 900]
) -> Dict[str, Any]:
    """Generate isochrones (travel time polygons) from a location.

    Args:
        location (List[float]): Starting coordinates [longitude, latitude]
        profile (str): Transportation profile (driving, cycling, walking)
        ranges (List[int]): Time ranges in seconds for isochrone generation

    Returns:
        Dict[str, Any]: Isochrone data with polygons for each range
    """
    database = load_database()
    
    # Find matching isochrone data
    for isochrone in database.get("isochrone_data", []):
        if (isochrone.get("locations", [[]])[0] == location and 
            isochrone.get("profile") == profile):
            return {
                "polygons": isochrone.get("polygons", []),
                "ranges": isochrone.get("range", ranges),
                "profile": profile,
                "location": location
            }
    
    # Return default response if no match found
    return {
        "polygons": [],
        "ranges": ranges,
        "profile": profile,
        "location": location,
        "note": "Isochrone data not found in database"
    }


@mcp.tool()
def get_pois(
    location: List[float], 
    buffer: int = 1000, 
    limit: int = 10,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Get points of interest near a location.

    Args:
        location (List[float]): Center coordinates [longitude, latitude]
        buffer (int): Search radius in meters
        limit (int): Maximum number of POIs to return
        filters (Optional[Dict[str, Any]]): Filter criteria for POI categories

    Returns:
        Dict[str, Any]: POI data with features matching the criteria
    """
    database = load_database()
    
    # Find matching POI data
    for poi_set in database.get("poi_data", []):
        if (poi_set.get("coordinates") == location and 
            poi_set.get("buffer") == buffer):
            
            # Apply filters if provided
            features = poi_set.get("features", [])
            if filters:
                filtered_features = []
                for feature in features:
                    properties = feature.get("properties", {})
                    matches = True
                    for key, value in filters.items():
                        if properties.get(key) != value:
                            matches = False
                            break
                    if matches:
                        filtered_features.append(feature)
                features = filtered_features[:limit]
            else:
                features = features[:limit]
            
            return {
                "features": features,
                "count": len(features),
                "buffer": buffer,
                "location": location
            }
    
    # Return default response if no match found
    return {
        "features": [],
        "count": 0,
        "buffer": buffer,
        "location": location,
        "note": "POI data not found in database"
    }


@mcp.tool()
def get_poi_names(
    location: List[float], 
    buffer: int = 1000, 
    limit: int = 10
) -> Dict[str, Any]:
    """Get names of points of interest near a location.

    Args:
        location (List[float]): Center coordinates [longitude, latitude]
        buffer (int): Search radius in meters
        limit (int): Maximum number of POI names to return

    Returns:
        Dict[str, Any]: List of POI names with basic information
    """
    # Use get_pois to get the full data
    poi_result = get_pois(location, buffer, limit)
    
    # Extract just the names and basic info
    poi_names = []
    for feature in poi_result.get("features", []):
        properties = feature.get("properties", {})
        poi_names.append({
            "name": properties.get("name", "Unknown"),
            "category": properties.get("category", "unknown"),
            "coordinates": feature.get("geometry", {}).get("coordinates", [])
        })
    
    return {
        "poi_names": poi_names,
        "count": len(poi_names),
        "buffer": buffer,
        "location": location
    }


@mcp.tool()
def optimize_vehicle_routes(
    jobs: List[Dict[str, Any]],
    vehicles: List[Dict[str, Any]],
    shipments: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Optimize vehicle routing for deliveries and pickups.

    Args:
        jobs (List[Dict[str, Any]]): List of delivery jobs with locations and requirements
        vehicles (List[Dict[str, Any]]): List of available vehicles with capacities
        shipments (Optional[List[Dict[str, Any]]]): List of shipments with pickup/delivery pairs

    Returns:
        Dict[str, Any]: Optimized routing solution
    """
    database = load_database()
    
    # Find matching optimization data
    for optimization in database.get("optimization_data", []):
        # Simple matching based on job and vehicle counts
        if (len(optimization.get("jobs", [])) == len(jobs) and 
            len(optimization.get("vehicles", [])) == len(vehicles)):
            return optimization.get("solution", {})
    
    # Return default response if no match found
    return {
        "total_distance": 0,
        "total_time": 0,
        "routes": [],
        "note": "Optimization data not found in database, returning default response"
    }


@mcp.tool()
def create_simple_delivery_problem(
    deliveries: List[List[float]],
    vehicle_capacity: int = 50,
    start_location: Optional[List[float]] = None
) -> Dict[str, Any]:
    """Create a simple delivery problem for optimization.

    Args:
        deliveries (List[List[float]]): List of delivery locations [longitude, latitude]
        vehicle_capacity (int): Vehicle capacity for deliveries
        start_location (Optional[List[float]]): Starting location for the vehicle

    Returns:
        Dict[str, Any]: Formatted delivery problem ready for optimization
    """
    # Use first delivery as start location if not provided
    if not start_location and deliveries:
        start_location = deliveries[0]
    
    # Create jobs from delivery locations
    jobs = []
    for i, location in enumerate(deliveries):
        jobs.append({
            "id": i,
            "location": location,
            "service": 600,  # 10 minutes service time
            "delivery": [1]   # One unit per delivery
        })
    
    # Create vehicle
    vehicles = [{
        "id": 0,
        "start": start_location or [0.0, 0.0],
        "end": start_location or [0.0, 0.0],
        "capacity": [vehicle_capacity],
        "time_window": [25200, 68400]  # 7am-7pm
    }]
    
    return {
        "jobs": jobs,
        "vehicles": vehicles,
        "problem_type": "simple_delivery"
    }


@mcp.tool()
def optimize_traveling_salesman(
    locations: List[List[float]],
    start_location: Optional[List[float]] = None,
    return_to_start: bool = True
) -> Dict[str, Any]:
    """Solve traveling salesman problem for optimal route through locations.

    Args:
        locations (List[List[float]]): List of locations to visit [longitude, latitude]
        start_location (Optional[List[float]]): Starting location (defaults to first location)
        return_to_start (bool): Whether to return to starting location

    Returns:
        Dict[str, Any]: Optimized TSP solution
    """
    database = load_database()
    
    # Set start location
    if not start_location and locations:
        start_location = locations[0]
    
    # Find matching TSP data
    for tsp in database.get("traveling_salesman_data", []):
        if (len(tsp.get("locations", [])) == len(locations) and 
            tsp.get("return_to_start") == return_to_start):
            return tsp.get("solution", {})
    
    # Return default response if no match found
    return {
        "total_distance": 0,
        "total_time": 0,
        "route": locations,  # Return original order as fallback
        "return_to_start": return_to_start,
        "note": "TSP data not found in database, returning default response"
    }


if __name__ == "__main__":
    mcp.run()