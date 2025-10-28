"""
Kakao Map MCP Server

A FastMCP-compliant server that provides place recommendations based on location
and user preferences using the offline database of Korean travel locations.
This version removes the fallback database and adds proper validation.
"""

import json
import os
from typing import List, Dict, Any
from fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP(name="Kakao Map")

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "kakao_map_database.json")


def load_database() -> Dict[str, Any]:
    """Load the database from JSON file with proper validation."""
    if not os.path.exists(DATABASE_PATH):
        raise FileNotFoundError(f"Database file not found: {DATABASE_PATH}")
    
    try:
        with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
            database = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Database file is not valid JSON: {e}")
    
    # Validate database structure
    if "places" not in database:
        raise ValueError("Database missing 'places' key")
    
    if not isinstance(database["places"], list):
        raise ValueError("Database 'places' must be a list")
    
    # Validate each place structure
    required_fields = ["id", "name", "location", "type", "description", "rating", "price_range", "tags", "coordinates"]
    
    for i, place in enumerate(database["places"]):
        if not isinstance(place, dict):
            raise ValueError(f"Place {i} is not a dictionary")
        
        for field in required_fields:
            if field not in place:
                raise ValueError(f"Place {i} missing required field: {field}")
        
        # Validate coordinates structure
        if not isinstance(place["coordinates"], dict):
            raise ValueError(f"Place {i} coordinates is not a dictionary")
        
        if "latitude" not in place["coordinates"] or "longitude" not in place["coordinates"]:
            raise ValueError(f"Place {i} coordinates missing latitude or longitude")
    
    return database


@mcp.tool()
def kakao_map_place_recommender(location: str, preferences: str) -> Dict[str, Any]:
    """
    Recommends places based on location and preferences.

    Args:
        location (str): Location to search around (e.g., "Seoul", "Busan", "Gangnam")
        preferences (str): User preferences for place types (e.g., "restaurant", "cafe", "cultural_site")

    Returns:
        Dict[str, Any]: A dictionary containing 'recommendations' list with matching places
    """
    # Load the database with validation
    try:
        database = load_database()
    except (FileNotFoundError, ValueError) as e:
        return {
            "error": f"Failed to load database: {e}",
            "recommendations": []
        }
    
    places = database.get("places", [])
    
    # Normalize inputs for case-insensitive matching
    location_lower = location.lower()
    preferences_lower = preferences.lower()
    
    # Filter places based on location and preferences
    recommendations = []
    
    for place in places:
        # Check if place location matches (case-insensitive substring match)
        place_location = place.get("location", "").lower()
        place_type = place.get("type", "").lower()
        place_tags = [tag.lower() for tag in place.get("tags", [])]
        
        # Check location match (substring match for flexibility)
        location_match = location_lower in place_location
        
        # Check preference match - either type matches or tags contain preference
        preference_match = (
            preferences_lower in place_type or
            any(preferences_lower in tag for tag in place_tags)
        )
        
        if location_match and preference_match:
            recommendations.append(place)
    
    # Sort by rating (highest first) and limit to top 10
    recommendations.sort(key=lambda x: x.get("rating", 0), reverse=True)
    recommendations = recommendations[:10]
    
    return {
        "recommendations": recommendations
    }


if __name__ == "__main__":
    mcp.run()