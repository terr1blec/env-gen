"""
NearbySearch FastMCP Server Module

This module provides location-based search functionality for nearby places.
It loads data from a generated offline database and implements Haversine
distance calculations for proximity-based filtering.
"""

import json
import math
import os
from typing import List, Dict, Any, Optional


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth.
    
    Args:
        lat1: Latitude of first point in degrees
        lon1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lon2: Longitude of second point in degrees
        
    Returns:
        Distance in meters
    """
    # Earth radius in meters
    R = 6371000
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


class NearbySearchServer:
    """NearbySearch server implementation using offline database."""
    
    def __init__(self, database_path: Optional[str] = None):
        """
        Initialize the server with database from specified path.
        
        Args:
            database_path: Path to the database JSON file. If None, uses default path.
        """
        if database_path is None:
            # Use the recommended path from the database generator
            database_path = "generated/travel_maps/nearbysearch/nearbysearch_database.json"
        
        self.database_path = database_path
        self.places = self._load_database()
    
    def _load_database(self) -> List[Dict[str, Any]]:
        """
        Load and validate the database from JSON file.
        
        Returns:
            List of place records
            
        Raises:
            FileNotFoundError: If database file doesn't exist
            ValueError: If database structure doesn't match DATA CONTRACT
        """
        if not os.path.exists(self.database_path):
            raise FileNotFoundError(f"Database file not found: {self.database_path}")
        
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in database file: {e}")
        
        # Validate DATA CONTRACT structure
        if "places" not in data:
            raise ValueError("Database missing required top-level key 'places'")
        
        if not isinstance(data["places"], list):
            raise ValueError("Database 'places' must be a list")
        
        # Validate required fields in each place
        required_fields = {"id", "name", "latitude", "longitude", "category"}
        for i, place in enumerate(data["places"]):
            missing_fields = required_fields - set(place.keys())
            if missing_fields:
                raise ValueError(f"Place {i} missing required fields: {missing_fields}")
            
            # Validate field types
            if not isinstance(place["id"], str):
                raise ValueError(f"Place {i} 'id' must be a string")
            if not isinstance(place["name"], str):
                raise ValueError(f"Place {i} 'name' must be a string")
            if not isinstance(place["latitude"], (int, float)):
                raise ValueError(f"Place {i} 'latitude' must be a number")
            if not isinstance(place["longitude"], (int, float)):
                raise ValueError(f"Place {i} 'longitude' must be a number")
            if not isinstance(place["category"], str):
                raise ValueError(f"Place {i} 'category' must be a string")
        
        return data["places"]
    
    def search_nearby(self, latitude: float, longitude: float, category: str, radius: float = 1000) -> Dict[str, Any]:
        """
        Search for nearby places based on location and category.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            category: Category of places to search for
            radius: Search radius in meters (default: 1000)
            
        Returns:
            Dictionary containing list of places within the specified radius
        """
        # Convert category to lowercase for case-insensitive matching
        category_lower = category.lower()
        
        # Filter and calculate distances
        nearby_places = []
        for place in self.places:
            # Check category match (case-insensitive)
            if place["category"].lower() != category_lower:
                continue
            
            # Calculate distance
            distance = haversine_distance(
                latitude, longitude,
                place["latitude"], place["longitude"]
            )
            
            # Check if within radius
            if distance <= radius:
                # Create result with distance field
                result_place = place.copy()
                result_place["distance"] = round(distance, 2)  # Distance in meters, rounded to 2 decimals
                nearby_places.append(result_place)
        
        # Sort by distance (closest first)
        nearby_places.sort(key=lambda x: x["distance"])
        
        return {"places": nearby_places}


# Create global server instance
server = NearbySearchServer()


def search_nearby(latitude: float, longitude: float, category: str, radius: float = 1000) -> Dict[str, Any]:
    """
    Search for nearby places based on location and category.
    
    This is the main MCP tool function that will be exposed.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        category: Category of places to search for
        radius: Search radius in meters (default: 1000)
        
    Returns:
        Dictionary containing list of places within the specified radius
    """
    return server.search_nearby(latitude, longitude, category, radius)