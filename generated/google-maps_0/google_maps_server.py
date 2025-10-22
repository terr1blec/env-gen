"""
Google Maps MCP Server

A FastMCP server that provides Google Maps-like functionality using offline dataset.
Implements geocoding, reverse geocoding, place search, place details, distance matrix,
elevation data, and directions using locally generated test data.
"""

import json
import math
import re
from typing import Dict, List, Optional, Any
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Google Maps")

# Load offline dataset
DATASET_PATH = "generated/google-maps/google_maps_dataset.json"

# Sample dataset structure for fallback
default_dataset = {
    "geocoding_data": [
        {
            "address": "1600 Amphitheatre Parkway, Mountain View, CA",
            "latitude": "37.4220656",
            "longitude": "-122.0840897",
            "place_id": "ChIJj61dQgK6j4AR4GeTYWZsKWw"
        },
        {
            "address": "1 Infinite Loop, Cupertino, CA",
            "latitude": "37.33182",
            "longitude": "-122.03118",
            "place_id": "ChIJ5bQ6w4e3j4ARy7vSxHhQnwQ"
        }
    ],
    "reverse_geocoding_data": [
        {
            "latitude": "37.4220656",
            "longitude": "-122.0840897",
            "address": "1600 Amphitheatre Parkway, Mountain View, CA"
        }
    ],
    "places_data": [
        {
            "name": "Googleplex",
            "address": "1600 Amphitheatre Parkway, Mountain View, CA",
            "place_id": "ChIJj61dQgK6j4AR4GeTYWZsKWw",
            "types": ["point_of_interest", "establishment"],
            "rating": 4.6,
            "user_ratings_total": 15000
        }
    ],
    "place_details": {
        "ChIJj61dQgK6j4AR4GeTYWZsKWw": {
            "name": "Googleplex",
            "formatted_address": "1600 Amphitheatre Parkway, Mountain View, CA 94043, USA",
            "formatted_phone_number": "(650) 253-0000",
            "website": "https://about.google/locations/",
            "rating": 4.6,
            "user_ratings_total": 15000,
            "types": ["point_of_interest", "establishment"],
            "geometry": {
                "location": {
                    "lat": 37.4220656,
                    "lng": -122.0840897
                }
            }
        }
    },
    "distance_matrix": [
        {
            "origin": "1600 Amphitheatre Parkway, Mountain View, CA",
            "destination": "1 Infinite Loop, Cupertino, CA",
            "distance": {
                "text": "8.2 mi",
                "value": 13197
            },
            "duration": {
                "text": "15 mins",
                "value": 900
            }
        }
    ],
    "elevation_data": [
        {
            "location": "37.4220656,-122.0840897",
            "elevation": 32.0
        }
    ],
    "directions": [
        {
            "origin": "1600 Amphitheatre Parkway, Mountain View, CA",
            "destination": "1 Infinite Loop, Cupertino, CA",
            "summary": "I-280 S",
            "distance": {
                "text": "8.2 mi",
                "value": 13197
            },
            "duration": {
                "text": "15 mins",
                "value": 900
            },
            "steps": [
                {
                    "instruction": "Head northwest on Amphitheatre Pkwy",
                    "distance": {
                        "text": "0.2 mi",
                        "value": 322
                    },
                    "duration": {
                        "text": "1 min",
                        "value": 60
                    }
                }
            ]
        }
    ]
}


def load_dataset() -> Dict[str, Any]:
    """Load the offline dataset from JSON file."""
    try:
        with open(DATASET_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return default_dataset
    except json.JSONDecodeError:
        return default_dataset


@mcp.tool()
def maps_geocode(address: str) -> Dict[str, Any]:
    """Convert an address to geographic coordinates."""
    dataset = load_dataset()
    
    for location in dataset.get("geocoding_data", []):
        if address.lower() in location["address"].lower():
            return {
                "status": "OK",
                "results": [{
                    "formatted_address": location["address"],
                    "geometry": {
                        "location": {
                            "lat": float(location["latitude"]),
                            "lng": float(location["longitude"])
                        }
                    },
                    "place_id": location["place_id"]
                }]
            }
    
    return {
        "status": "ZERO_RESULTS",
        "results": []
    }


@mcp.tool()
def maps_reverse_geocode(latitude: str, longitude: str) -> Dict[str, Any]:
    """Convert geographic coordinates to a human-readable address."""
    try:
        lat = float(latitude)
        lon = float(longitude)
    except ValueError:
        return {
            "status": "INVALID_REQUEST",
            "error_message": "Invalid latitude or longitude format"
        }
    
    dataset = load_dataset()
    
    for location in dataset.get("reverse_geocoding_data", []):
        try:
            loc_lat = float(location["latitude"])
            loc_lon = float(location["longitude"])
            if abs(lat - loc_lat) < 0.1 and abs(lon - loc_lon) < 0.1:
                return {
                    "status": "OK",
                    "results": [{
                        "formatted_address": location["address"],
                        "geometry": {
                            "location": {
                                "lat": loc_lat,
                                "lng": loc_lon
                            }
                        }
                    }]
                }
        except (ValueError, KeyError):
            continue
    
    return {
        "status": "ZERO_RESULTS",
        "results": []
    }


@mcp.tool()
def maps_search_places(query: str, radius: Optional[str] = None, location: Optional[str] = None) -> Dict[str, Any]:
    """Search for places based on a query."""
    dataset = load_dataset()
    
    matching_places = []
    
    for place in dataset.get("places_data", []):
        if query.lower() in place["name"].lower():
            matching_places.append({
                "name": place["name"],
                "formatted_address": place.get("address", ""),
                "place_id": place["place_id"],
                "types": place.get("types", []),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("user_ratings_total")
            })
    
    return {
        "status": "OK",
        "results": matching_places
    }


@mcp.tool()
def maps_place_details(place_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific place."""
    dataset = load_dataset()
    
    place_details = dataset.get("place_details", {})
    
    if place_id in place_details:
        return {
            "status": "OK",
            "result": place_details[place_id]
        }
    
    return {
        "status": "NOT_FOUND",
        "error_message": f"Place ID {place_id} not found"
    }


@mcp.tool()
def maps_distance_matrix(origins: Optional[str] = None, destinations: Optional[str] = None) -> Dict[str, Any]:
    """Calculate travel distance and time between multiple origins and destinations."""
    dataset = load_dataset()
    
    return {
        "status": "OK",
        "rows": [{
            "elements": dataset.get("distance_matrix", [])
        }]
    }


@mcp.tool()
def maps_elevation(locations: str) -> Dict[str, Any]:
    """Get elevation data for specific locations."""
    dataset = load_dataset()
    
    elevation_results = []
    
    for location in dataset.get("elevation_data", []):
        elevation_results.append({
            "location": {
                "lat": float(location["location"].split(',')[0]),
                "lng": float(location["location"].split(',')[1])
            },
            "elevation": location["elevation"]
        })
    
    return {
        "status": "OK",
        "results": elevation_results
    }


@mcp.tool()
def maps_directions(origin: str, destination: str, mode: Optional[str] = "driving") -> Dict[str, Any]:
    """Get directions between two locations."""
    dataset = load_dataset()
    
    for route in dataset.get("directions", []):
        if origin.lower() in route["origin"].lower() and destination.lower() in route["destination"].lower():
            return {
                "status": "OK",
                "routes": [{
                    "summary": route["summary"],
                    "legs": [{
                        "distance": route["distance"],
                        "duration": route["duration"],
                        "steps": route.get("steps", [])
                    }]
                }]
            }
    
    return {
        "status": "OK",
        "routes": [{
            "summary": f"Route from {origin} to {destination}",
            "legs": [{
                "distance": {
                    "text": "Unknown",
                    "value": 0
                },
                "duration": {
                    "text": "Unknown",
                    "value": 0
                },
                "steps": []
            }]
        }]
    }


# Main entry point for the server
if __name__ == "__main__":
    mcp.run(transport="stdio")