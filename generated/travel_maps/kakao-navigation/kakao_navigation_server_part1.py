"""
Kakao Navigation MCP Server

A FastMCP-compliant server that provides navigation and routing services
using offline Korean navigation data.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP(name="Kakao Navigation")

# Database structure
database: Dict[str, Any] = {
    "addresses": [],
    "directions": [],
    "future_directions": [],
    "multi_destination_directions": []
}


def load_database() -> None:
    """Load the navigation database from JSON file."""
    global database
    try:
        with open("generated/travel_maps/kakao-navigation/kakao_navigation_database.json", "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
        
        # Validate required top-level keys
        required_keys = ["addresses", "directions", "future_directions", "multi_destination_directions"]
        for key in required_keys:
            if key not in loaded_data:
                logger.warning(f"Missing required key '{key}' in database, using empty list")
                loaded_data[key] = []
        
        database = loaded_data
        logger.info(f"Successfully loaded database: {len(database['addresses'])} addresses, "
                   f"{len(database['directions'])} directions, "
                   f"{len(database['future_directions'])} future directions, "
                   f"{len(database['multi_destination_directions'])} multi-destination directions")
        
    except FileNotFoundError:
        logger.warning("Database file not found, using empty database")
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing database JSON: {e}, using empty database")
    except Exception as e:
        logger.error(f"Unexpected error loading database: {e}, using empty database")


def _find_closest_address_by_coords(latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
    """Find the closest address to given coordinates."""
    if not database["addresses"]:
        return None
    
    closest_address = None
    min_distance = float('inf')
    
    for address in database["addresses"]:
        addr_lat = address["coordinates"]["latitude"]
        addr_lon = address["coordinates"]["longitude"]
        
        # Simple Euclidean distance for proximity
        distance = ((latitude - addr_lat) ** 2 + (longitude - addr_lon) ** 2) ** 0.5
        
        if distance < min_distance:
            min_distance = distance
            closest_address = address
    
    return closest_address


def _find_address_by_place_name(place_name: str) -> Optional[Dict[str, Any]]:
    """Find address by place name (case-insensitive partial match)."""
    if not database["addresses"]:
        return None
    
    place_name_lower = place_name.lower()
    for address in database["addresses"]:
        if place_name_lower in address["placeName"].lower():
            return address
    
    return None


def _find_direction_by_coords(start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> Optional[Dict[str, Any]]:
    """Find direction route by coordinates with tolerance."""
    if not database["directions"]:
        return None
    
    tolerance = 0.01  # ~1km tolerance for coordinate matching
    
    for direction in database["directions"]:
        start_coords = direction["start_coords"]
        end_coords = direction["end_coords"]
        
        start_match = (abs(start_coords["latitude"] - start_lat) < tolerance and 
                      abs(start_coords["longitude"] - start_lon) < tolerance)
        end_match = (abs(end_coords["latitude"] - end_lat) < tolerance and 
                    abs(end_coords["longitude"] - end_lon) < tolerance)
        
        if start_match and end_match:
            return direction
    
    return None


def _find_future_direction_by_coords(start_lat: float, start_lon: float, end_lat: float, end_lon: float, departure_time: str) -> Optional[Dict[str, Any]]:
    """Find future direction route by coordinates and departure time."""
    if not database["future_directions"]:
        return None
    
    tolerance = 0.01  # ~1km tolerance for coordinate matching
    
    for direction in database["future_directions"]:
        start_coords = direction["start_coords"]
        end_coords = direction["end_coords"]
        
        start_match = (abs(start_coords["latitude"] - start_lat) < tolerance and 
                      abs(start_coords["longitude"] - start_lon) < tolerance)
        end_match = (abs(end_coords["latitude"] - end_lat) < tolerance and 
                    abs(end_coords["longitude"] - end_lon) < tolerance)
        time_match = direction["departure_time"] == departure_time
        
        if start_match and end_match and time_match:
            return direction
    
    return None


@mcp.tool()
def direction_search_by_coords(start_latitude: float, start_longitude: float, 
                              end_latitude: float, end_longitude: float) -> Dict[str, Any]:
    """Search for directions between two coordinate points.

    Args:
        start_latitude (float): Starting point latitude coordinate
        start_longitude (float): Starting point longitude coordinate  
        end_latitude (float): Destination latitude coordinate
        end_longitude (float): Destination longitude coordinate

    Returns:
        result (dict): Direction information including distance, duration, and route details
    """
    direction = _find_direction_by_coords(start_latitude, start_longitude, end_latitude, end_longitude)
    
    if direction:
        return {
            "start_address": direction["start_address"],
            "end_address": direction["end_address"],
            "distance": direction["distance"],
            "duration": direction["duration"],
            "route_details": direction["route_details"]
        }
    else:
        # Return a fallback response if no exact match found
        start_address = _find_closest_address_by_coords(start_latitude, start_longitude)
        end_address = _find_closest_address_by_coords(end_latitude, end_longitude)
        
        return {
            "start_address": start_address["address"] if start_address else "Unknown location",
            "end_address": end_address["address"] if end_address else "Unknown location",
            "distance": "Route not found in database",
            "duration": "Route not found in database",
            "route_details": "No route information available for the specified coordinates"
        }


@mcp.tool()
def direction_search_by_address(start_address: str, end_address: str) -> Dict[str, Any]:
    """Search for directions between two addresses.

    Args:
        start_address (str): Starting point address
        end_address (str): Destination address

    Returns:
        result (dict): Direction information including distance, duration, and route details
    """
    # Find addresses in database
    start_addr_obj = None
    end_addr_obj = None
    
    for addr in database["addresses"]:
        if start_address.lower() in addr["address"].lower():
            start_addr_obj = addr
        if end_address.lower() in addr["address"].lower():
            end_addr_obj = addr
    
    if not start_addr_obj or not end_addr_obj:
        return {
            "start_address": start_address,
            "end_address": end_address,
            "distance": "Address not found in database",
            "duration": "Address not found in database",
            "route_details": "One or both addresses not found in the navigation database"
        }
    
    # Find direction using coordinates
    start_coords = start_addr_obj["coordinates"]
    end_coords = end_addr_obj["coordinates"]
    
    direction = _find_direction_by_coords(
        start_coords["latitude"], start_coords["longitude"],
        end_coords["latitude"], end_coords["longitude"]
    )
    
    if direction:
        return {
            "start_address": direction["start_address"],
            "end_address": direction["end_address"],
            "distance": direction["distance"],
            "duration": direction["duration"],
            "route_details": direction["route_details"]
        }
    else:
        return {
            "start_address": start_addr_obj["address"],
            "end_address": end_addr_obj["address"],
            "distance": "Route not found in database",
            "duration": "Route not found in database",
            "route_details": "No route information available between the specified addresses"
        }


@mcp.tool()
def address_search_by_place_name(place_name: str) -> Dict[str, Any]:
    """Search for address information by place name.

    Args:
        place_name (str): Name of the place to search for

    Returns:
        result (dict): Address information including place name, address, and coordinates
    """
    address = _find_address_by_place_name(place_name)
    
    if address:
        return {
            "place_name": address["placeName"],
            "address": address["address"],
            "latitude": address["coordinates"]["latitude"],
            "longitude": address["coordinates"]["longitude"]
        }
    else:
        return {
            "place_name": place_name,
            "address": "Place not found in database",
            "latitude": 0.0,
            "longitude": 0.0
        }


@mcp.tool()
def geocode(address: str) -> Dict[str, Any]:
    """Convert address to geographic coordinates.

    Args:
        address (str): Address to geocode

    Returns:
        result (dict): Geographic coordinates for the address
    """
    for addr in database["addresses"]:
        if address.lower() in addr["address"].lower():
            return {
                "address": addr["address"],
                "latitude": addr["coordinates"]["latitude"],
                "longitude": addr["coordinates"]["longitude"]
            }
    
    # If no exact match, try partial match
    for addr in database["addresses"]:
        if any(part.lower() in addr["address"].lower() for part in address.split()):
            return {
                "address": addr["address"],
                "latitude": addr["coordinates"]["latitude"],
                "longitude": addr["coordinates"]["longitude"]
            }
    
    return {
        "address": address,
        "latitude": 0.0,
        "longitude": 0.0,
        "error": "Address not found in database"
    }