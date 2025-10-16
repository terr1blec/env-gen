"""
Google Maps MCP Server Module

This module provides offline Google Maps API functionality using a local dataset.
All tools operate on pre-generated dataset without external API calls.

Revised implementation addressing code review feedback:
- Fixed parameter naming inconsistencies
- Added missing required parameters
- Improved dataset structure alignment
- Enhanced error handling and validation
"""

import json
import os
import re
from typing import Dict, List, Optional, Any
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Google Maps")

# Load dataset
_DATASET_PATH = os.path.join(os.path.dirname(__file__), "google-maps_dataset.json")


def load_dataset() -> Dict[str, Any]:
    """Load the offline dataset from JSON file."""
    try:
        with open(_DATASET_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "geocoding": [],
            "reverse_geocoding": [],
            "places": [],
            "place_details": [],
            "distance_matrix": [],
            "elevation": [],
            "directions": []
        }


def find_best_match(query: str, dataset_key: str, search_fields: List[str]) -> Optional[Dict[str, Any]]:
    """Find the best matching record in the dataset."""
    dataset = load_dataset()
    records = dataset.get(dataset_key, [])
    
    if not records:
        return None
    
    query_lower = query.lower().strip()
    
    # Try exact match first
    for record in records:
        for field in search_fields:
            if field in record and record[field] and record[field].lower().strip() == query_lower:
                return record
    
    # Try partial match
    for record in records:
        for field in search_fields:
            if field in record and record[field] and query_lower in record[field].lower():
                return record
    
    # Try fuzzy match (simple contains)
    for record in records:
        for field in search_fields:
            if field in record and record[field] and any(word in record[field].lower() for word in query_lower.split()):
                return record
    
    return records[0] if records else None


def parse_coordinates(coords_str: str) -> Optional[Dict[str, float]]:
    """Parse coordinate string in format 'lat,lng' or 'lat,lng|lat,lng'."""
    try:
        # Handle single coordinate pair
        if ',' in coords_str and '|' not in coords_str:
            lat, lng = coords_str.split(',')
            return {"lat": float(lat.strip()), "lng": float(lng.strip())}
        # Handle multiple coordinate pairs
        elif '|' in coords_str:
            pairs = coords_str.split('|')
            return [parse_coordinates(pair) for pair in pairs if parse_coordinates(pair)]
    except (ValueError, AttributeError):
        pass
    return None


@mcp.tool()
def maps_geocode(address: str) -> Dict[str, Any]:
    """Convert address to geographic coordinates.
    
    Args:
        address: The address to geocode
    
    Returns:
        Dictionary containing latitude, longitude, and formatted address
    """
    dataset = load_dataset()
    geocoding_data = dataset.get("geocoding", [])
    
    # Search for matching geocoding record
    for record in geocoding_data:
        input_data = record.get("input", {})
        output_data = record.get("output", {})
        
        if input_data.get("address", "").lower() == address.lower():
            results = output_data.get("results", [])
            if results:
                geometry = results[0].get("geometry", {})
                location = geometry.get("location", {})
                return {
                    "results": results,
                    "status": output_data.get("status", "OK")
                }
    
    # Return default coordinates if no match found
    return {
        "results": [{
            "formatted_address": address,
            "geometry": {
                "location": {
                    "lat": 40.7128,
                    "lng": -74.0060
                }
            }
        }],
        "status": "OK"
    }


@mcp.tool()
def maps_reverse_geocode(latitude: str, longitude: str) -> Dict[str, Any]:
    """Convert geographic coordinates to address.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
    
    Returns:
        Dictionary containing formatted address and location details
    """
    try:
        lat = float(latitude)
        lng = float(longitude)
    except ValueError:
        return {
            "results": [],
            "status": "INVALID_REQUEST",
            "error_message": "Invalid coordinate format"
        }
    
    dataset = load_dataset()
    reverse_geocoding_data = dataset.get("reverse_geocoding", [])
    
    # Search for matching reverse geocoding record
    for record in reverse_geocoding_data:
        input_data = record.get("input", {})
        latlng_str = input_data.get("latlng", "")
        
        if latlng_str:
            try:
                record_lat, record_lng = map(float, latlng_str.split(','))
                # Check if coordinates are close enough (within 0.1 degrees)
                if abs(record_lat - lat) < 0.1 and abs(record_lng - lng) < 0.1:
                    return record.get("output", {"results": [], "status": "ZERO_RESULTS"})
            except (ValueError, IndexError):
                continue
    
    return {
        "results": [{
            "formatted_address": f"Approximate location near {lat:.4f}, {lng:.4f}",
            "geometry": {
                "location": {
                    "lat": lat,
                    "lng": lng
                }
            }
        }],
        "status": "OK"
    }


@mcp.tool()
def maps_search_places(query: str, radius: Optional[str] = None, location: Optional[str] = None) -> Dict[str, Any]:
    """Search for places based on query.
    
    Args:
        query: Search query for places
        radius: Search radius in meters (optional)
        location: Location to search around (optional)
    
    Returns:
        Dictionary containing list of matching places
    """
    dataset = load_dataset()
    places_data = dataset.get("places", [])
    
    query_lower = query.lower()
    matching_places = []
    
    for place in places_data:
        place_name = place.get("name", "").lower()
        place_types = place.get("types", [])
        
        # Check if query matches name or types
        if (query_lower in place_name or 
            any(query_lower in str(t).lower() for t in place_types)):
            matching_places.append({
                "place_id": place.get("place_id", ""),
                "name": place.get("name", ""),
                "formatted_address": place.get("formatted_address", ""),
                "geometry": place.get("geometry", {}),
                "types": place.get("types", []),
                "rating": place.get("rating", 0)
            })
    
    # If no matches, return some default places
    if not matching_places and places_data:
        matching_places = [{
            "place_id": place.get("place_id", ""),
            "name": place.get("name", ""),
            "formatted_address": place.get("formatted_address", ""),
            "geometry": place.get("geometry", {}),
            "types": place.get("types", []),
            "rating": place.get("rating", 0)
        } for place in places_data[:5]]
    
    return {
        "results": matching_places,
        "status": "OK",
        "query": query
    }


@mcp.tool()
def maps_place_details(place_id: str) -> Dict[str, Any]:
    """Get detailed information about a place.
    
    Args:
        place_id: Unique identifier for the place
    
    Returns:
        Dictionary containing comprehensive place details
    """
    dataset = load_dataset()
    place_details_data = dataset.get("place_details", [])
    
    for record in place_details_data:
        input_data = record.get("input", {})
        if input_data.get("place_id") == place_id:
            return record.get("output", {"result": {}, "status": "NOT_FOUND"})
    
    # Return default place details if not found
    return {
        "result": {
            "place_id": place_id,
            "name": "Unknown Place",
            "formatted_address": "Address not available",
            "formatted_phone_number": "Phone not available",
            "geometry": {"location": {"lat": 0.0, "lng": 0.0}},
            "rating": 0,
            "types": ["establishment"],
            "website": "",
            "opening_hours": {"open_now": False}
        },
        "status": "NOT_FOUND"
    }


@mcp.tool()
def maps_distance_matrix(origins: str, destinations: str, mode: Optional[str] = "driving") -> Dict[str, Any]:
    """Calculate travel distance and time between locations.
    
    Args:
        origins: Starting locations (comma-separated or pipe-separated)
        destinations: Destination locations (comma-separated or pipe-separated)
        mode: Travel mode (driving, walking, transit, bicycling)
    
    Returns:
        Dictionary containing distance matrix results
    """
    dataset = load_dataset()
    distance_matrix_data = dataset.get("distance_matrix", [])
    
    # Search for matching distance matrix record
    for record in distance_matrix_data:
        input_data = record.get("input", {})
        record_origins = input_data.get("origins", [])
        record_destinations = input_data.get("destinations", [])
        
        # Check if origins and destinations match
        origins_list = [o.strip() for o in origins.split('|')] if '|' in origins else [origins]
        destinations_list = [d.strip() for d in destinations.split('|')] if '|' in destinations else [destinations]
        
        if (set(origins_list) == set(record_origins) and 
            set(destinations_list) == set(record_destinations)):
            return record.get("output", {"rows": [], "status": "OK"})
    
    # Return default distance matrix
    return {
        "origin_addresses": origins_list,
        "destination_addresses": destinations_list,
        "rows": [{
            "elements": [{
                "distance": {"text": "1.5 km", "value": 1500},
                "duration": {"text": "5 mins", "value": 300},
                "status": "OK"
            } for _ in destinations_list]
        } for _ in origins_list],
        "status": "OK"
    }


@mcp.tool()
def maps_elevation(locations: str) -> Dict[str, Any]:
    """Get elevation data for locations.
    
    Args:
        locations: Locations to get elevation for (format: "lat,lng" or "lat,lng|lat,lng")
    
    Returns:
        Dictionary containing elevation data
    """
    dataset = load_dataset()
    elevation_data = dataset.get("elevation", [])
    
    # Parse input locations
    parsed_locations = parse_coordinates(locations)
    if not parsed_locations:
        return {
            "results": [],
            "status": "INVALID_REQUEST",
            "error_message": "Invalid locations format"
        }
    
    # Search for matching elevation record
    for record in elevation_data:
        input_data = record.get("input", {})
        record_locations = input_data.get("locations", [])
        
        # Check if locations match
        if isinstance(parsed_locations, dict):
            # Single location
            for rec_loc in record_locations:
                if (rec_loc.get("lat") == parsed_locations.get("lat") and 
                    rec_loc.get("lng") == parsed_locations.get("lng")):
                    return record.get("output", {"results": [], "status": "OK"})
        else:
            # Multiple locations
            if len(record_locations) == len(parsed_locations):
                match = True
                for i, loc in enumerate(parsed_locations):
                    if (record_locations[i].get("lat") != loc.get("lat") or 
                        record_locations[i].get("lng") != loc.get("lng")):
                        match = False
                        break
                if match:
                    return record.get("output", {"results": [], "status": "OK"})
    
    # Generate elevation data for input locations
    elevation_results = []
    locations_list = [parsed_locations] if isinstance(parsed_locations, dict) else parsed_locations
    
    for i, loc in enumerate(locations_list):
        elevation_results.append({
            "elevation": 100.0 + (i * 10),  # Simple elevation calculation
            "location": loc,
            "resolution": 1.0
        })
    
    return {
        "results": elevation_results,
        "status": "OK"
    }


@mcp.tool()
def maps_directions(origin: str, destination: str, mode: Optional[str] = "driving") -> Dict[str, Any]:
    """Get directions between two locations.
    
    Args:
        origin: Starting location
        destination: Ending location
        mode: Travel mode (driving, walking, transit, bicycling)
    
    Returns:
        Dictionary containing route information
    """
    dataset = load_dataset()
    directions_data = dataset.get("directions", [])
    
    # Find matching route
    for record in directions_data:
        input_data = record.get("input", {})
        route_origin = input_data.get("origin", "")
        route_destination = input_data.get("destination", "")
        route_mode = input_data.get("mode", "driving")
        
        if (origin.lower() in route_origin.lower() and 
            destination.lower() in route_destination.lower() and
            mode.lower() == route_mode.lower()):
            return record.get("output", {"routes": [], "status": "OK"})
    
    # Return default directions
    return {
        "routes": [{
            "summary": f"Route from {origin} to {destination}",
            "legs": [{
                "distance": {"text": "10 km", "value": 10000},
                "duration": {"text": "15 mins", "value": 900},
                "start_address": origin,
                "end_address": destination,
                "steps": [
                    {
                        "html_instructions": f"Start at {origin}",
                        "distance": {"text": "0.1 km", "value": 100},
                        "duration": {"text": "1 min", "value": 60}
                    },
                    {
                        "html_instructions": f"Arrive at {destination}",
                        "distance": {"text": "0.1 km", "value": 100},
                        "duration": {"text": "1 min", "value": 60}
                    }
                ]
            }],
            "overview_polyline": {"points": ""}
        }],
        "status": "OK"
    }


if __name__ == "__main__":
    # Run the server
    mcp.run(transport="stdio")