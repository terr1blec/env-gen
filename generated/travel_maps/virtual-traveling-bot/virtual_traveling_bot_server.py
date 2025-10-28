"""
Virtual Traveling Bot MCP Server

A FastMCP-compliant server that provides virtual traveling assistance
using an offline database of travelers, locations, facilities, journeys, and settings.
"""

import json
import os
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(name="Virtual Traveling Bot")

# Database file path
DATABASE_PATH = os.path.join(
    os.path.dirname(__file__), 
    "virtual_traveling_bot_database.json"
)

# Fallback data structure (used only if database file is missing)
FALLBACK_DATABASE = {
    "travelers": [],
    "locations": [],
    "facilities": [],
    "journeys": [],
    "settings": []
}


def load_database() -> Dict[str, Any]:
    """Load the database from JSON file or return fallback data."""
    try:
        if os.path.exists(DATABASE_PATH):
            with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Validate required top-level keys
            required_keys = ["travelers", "locations", "facilities", "journeys", "settings"]
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"Missing required key in database: {key}")
            
            return data
        else:
            print(f"Warning: Database file not found at {DATABASE_PATH}. Using fallback data.")
            return FALLBACK_DATABASE
    except Exception as e:
        print(f"Error loading database: {e}. Using fallback data.")
        return FALLBACK_DATABASE


@mcp.tool()
def get_traveler_view_info(traveler_id: str) -> Dict[str, Any]:
    """Get location address + nearby facilities + view snapshot for a traveler.

    Args:
        traveler_id (str): The ID of the traveler to get view information for.

    Returns:
        Dict containing location address, nearby facilities, and view snapshot.
    """
    database = load_database()
    
    # Find the traveler
    traveler = next((t for t in database["travelers"] if t["traveler_id"] == traveler_id), None)
    if not traveler:
        return {"error": f"Traveler with ID {traveler_id} not found"}
    
    # Find the current location
    location_id = traveler.get("current_location_id")
    if not location_id:
        return {"error": f"Traveler {traveler_id} has no current location"}
    
    location = next((l for l in database["locations"] if l["location_id"] == location_id), None)
    if not location:
        return {"error": f"Location with ID {location_id} not found"}
    
    # Get nearby facilities
    nearby_facility_ids = location.get("nearby_facilities", [])
    nearby_facilities = []
    for facility_id in nearby_facility_ids:
        facility = next((f for f in database["facilities"] if f["facility_id"] == facility_id), None)
        if facility:
            nearby_facilities.append({
                "facility_id": facility["facility_id"],
                "name": facility["name"],
                "type": facility["type"],
                "description": facility["description"]
            })
    
    return {
        "traveler_id": traveler_id,
        "traveler_name": traveler["name"],
        "location_address": location["address"],
        "coordinates": location["coordinates"],
        "view_snapshot": location["view_snapshot"],
        "nearby_facilities": nearby_facilities
    }


@mcp.tool()
def get_traveler_location(traveler_id: str) -> Dict[str, Any]:
    """Get current traveler location address.

    Args:
        traveler_id (str): The ID of the traveler to get location for.

    Returns:
        Dict containing the current location address.
    """
    database = load_database()
    
    # Find the traveler
    traveler = next((t for t in database["travelers"] if t["traveler_id"] == traveler_id), None)
    if not traveler:
        return {"error": f"Traveler with ID {traveler_id} not found"}
    
    # Find the current location
    location_id = traveler.get("current_location_id")
    if not location_id:
        return {"error": f"Traveler {traveler_id} has no current location"}
    
    location = next((l for l in database["locations"] if l["location_id"] == location_id), None)
    if not location:
        return {"error": f"Location with ID {location_id} not found"}
    
    return {
        "traveler_id": traveler_id,
        "traveler_name": traveler["name"],
        "current_location": {
            "location_id": location["location_id"],
            "address": location["address"],
            "coordinates": location["coordinates"]
        }
    }


@mcp.tool()
def tips(traveler_id: str) -> Dict[str, Any]:
    """Get device recommendations for a traveler.

    Args:
        traveler_id (str): The ID of the traveler to get tips for.

    Returns:
        Dict containing device tips and current setting.
    """
    database = load_database()
    
    # Find the traveler's settings
    setting = next((s for s in database["settings"] if s["traveler_id"] == traveler_id), None)
    if not setting:
        return {"error": f"Settings for traveler {traveler_id} not found"}
    
    # Find the traveler
    traveler = next((t for t in database["travelers"] if t["traveler_id"] == traveler_id), None)
    traveler_name = traveler["name"] if traveler else "Unknown Traveler"
    
    return {
        "traveler_id": traveler_id,
        "traveler_name": traveler_name,
        "current_setting": setting["current_setting"],
        "device_tips": setting["device_tips"]
    }


@mcp.tool()
def get_setting(traveler_id: str) -> Dict[str, Any]:
    """Get current setting for a traveler.

    Args:
        traveler_id (str): The ID of the traveler to get setting for.

    Returns:
        Dict containing the current setting.
    """
    database = load_database()
    
    # Find the traveler's settings
    setting = next((s for s in database["settings"] if s["traveler_id"] == traveler_id), None)
    if not setting:
        return {"error": f"Settings for traveler {traveler_id} not found"}
    
    return {
        "traveler_id": traveler_id,
        "current_setting": setting["current_setting"]
    }


@mcp.tool()
def get_traveler_info(traveler_id: str) -> Dict[str, Any]:
    """Get traveler settings (name, language, personality, speaking habits).

    Args:
        traveler_id (str): The ID of the traveler to get info for.

    Returns:
        Dict containing traveler information.
    """
    database = load_database()
    
    # Find the traveler
    traveler = next((t for t in database["travelers"] if t["traveler_id"] == traveler_id), None)
    if not traveler:
        return {"error": f"Traveler with ID {traveler_id} not found"}
    
    return {
        "traveler_id": traveler["traveler_id"],
        "name": traveler["name"],
        "language": traveler["language"],
        "personality": traveler["personality"],
        "speaking_habits": traveler["speaking_habits"],
        "current_location_id": traveler["current_location_id"],
        "active_journey_id": traveler["active_journey_id"]
    }


@mcp.tool()
def set_traveler_info(
    traveler_id: str,
    name: Optional[str] = None,
    language: Optional[str] = None,
    personality: Optional[str] = None,
    speaking_habits: Optional[str] = None
) -> Dict[str, Any]:
    """Set traveler settings.

    Note: This operation does not persist changes to the database file.
    Changes are only reflected in the current session.

    Args:
        traveler_id (str): The ID of the traveler to update.
        name (str, optional): New name for the traveler.
        language (str, optional): New language for the traveler.
        personality (str, optional): New personality for the traveler.
        speaking_habits (str, optional): New speaking habits for the traveler.

    Returns:
        Dict containing updated traveler information.
    """
    database = load_database()
    
    # Find the traveler
    traveler = next((t for t in database["travelers"] if t["traveler_id"] == traveler_id), None)
    if not traveler:
        return {"error": f"Traveler with ID {traveler_id} not found"}
    
    # Update fields if provided
    updates = []
    if name is not None:
        traveler["name"] = name
        updates.append("name")
    if language is not None:
        traveler["language"] = language
        updates.append("language")
    if personality is not None:
        traveler["personality"] = personality
        updates.append("personality")
    if speaking_habits is not None:
        traveler["speaking_habits"] = speaking_habits
        updates.append("speaking_habits")
    
    return {
        "traveler_id": traveler["traveler_id"],
        "updated_fields": updates,
        "current_info": {
            "name": traveler["name"],
            "language": traveler["language"],
            "personality": traveler["personality"],
            "speaking_habits": traveler["speaking_habits"],
            "current_location_id": traveler["current_location_id"],
            "active_journey_id": traveler["active_journey_id"]
        }
    }


@mcp.tool()
def start_traveler_journey(traveler_id: str, destination_location_id: str) -> Dict[str, Any]:
    """Start journey to destination for a traveler.

    Note: This operation does not persist changes to the database file.
    Changes are only reflected in the current session.

    Args:
        traveler_id (str): The ID of the traveler starting the journey.
        destination_location_id (str): The ID of the destination location.

    Returns:
        Dict containing journey information.
    """
    database = load_database()
    
    # Find the traveler
    traveler = next((t for t in database["travelers"] if t["traveler_id"] == traveler_id), None)
    if not traveler:
        return {"error": f"Traveler with ID {traveler_id} not found"}
    
    # Find the destination location
    destination = next((l for l in database["locations"] if l["location_id"] == destination_location_id), None)
    if not destination:
        return {"error": f"Destination location with ID {destination_location_id} not found"}
    
    # Check if traveler already has an active journey
    if traveler.get("active_journey_id"):
        return {"error": f"Traveler {traveler_id} already has an active journey"}
    
    # Create a new journey ID
    journey_id = f"journey_{len(database['journeys']) + 1:03d}"
    
    # Update traveler's active journey
    traveler["active_journey_id"] = journey_id
    
    return {
        "traveler_id": traveler_id,
        "traveler_name": traveler["name"],
        "journey_id": journey_id,
        "destination_location_id": destination_location_id,
        "destination_address": destination["address"],
        "status": "active",
        "message": f"Journey {journey_id} started to {destination['address']}"
    }


@mcp.tool()
def stop_traveler_journey(traveler_id: str) -> Dict[str, Any]:
    """Stop current journey for a traveler.

    Note: This operation does not persist changes to the database file.
    Changes are only reflected in the current session.

    Args:
        traveler_id (str): The ID of the traveler to stop journey for.

    Returns:
        Dict containing journey stop information.
    """
    database = load_database()
    
    # Find the traveler
    traveler = next((t for t in database["travelers"] if t["traveler_id"] == traveler_id), None)
    if not traveler:
        return {"error": f"Traveler with ID {traveler_id} not found"}
    
    # Check if traveler has an active journey
    active_journey_id = traveler.get("active_journey_id")
    if not active_journey_id:
        return {"error": f"Traveler {traveler_id} has no active journey to stop"}
    
    # Find the active journey
    journey = next((j for j in database["journeys"] if j["journey_id"] == active_journey_id), None)
    
    # Update traveler's active journey
    traveler["active_journey_id"] = ""
    
    journey_info = {
        "journey_id": active_journey_id,
        "status": journey["status"] if journey else "unknown"
    }
    
    if journey:
        journey_info["destination"] = journey["destination_location_id"]
    
    return {
        "traveler_id": traveler_id,
        "traveler_name": traveler["name"],
        "stopped_journey": journey_info,
        "message": f"Journey {active_journey_id} stopped for traveler {traveler_id}"
    }


if __name__ == "__main__":
    mcp.run()