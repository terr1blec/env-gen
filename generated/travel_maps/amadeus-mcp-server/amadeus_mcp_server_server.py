"""
Amadeus MCP Server - FastMCP-compliant server for flight search operations.

This server provides flight search capabilities using an offline database
of flight offers. It implements the MCP protocol and exposes tools for
searching flight data.
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(name="Amadeus MCP Server")

# Database configuration - use forward slashes for cross-platform compatibility
DATABASE_PATH = Path("generated/travel_maps/amadeus-mcp-server/amadeus_mcp_server_database.json")

# Fallback database structure if JSON file is missing
FALLBACK_DATABASE = {
    "flight_offers": []
}


def load_database() -> Dict[str, Any]:
    """
    Load the flight database from JSON file.
    
    Returns:
        Dict containing flight offers data
    """
    try:
        if DATABASE_PATH.exists():
            with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            # Validate required top-level key
            if "flight_offers" not in database:
                print(f"Warning: Database missing 'flight_offers' key. Using fallback.")
                return FALLBACK_DATABASE
            
            return database
        else:
            print(f"Warning: Database file not found at {DATABASE_PATH}. Using fallback.")
            return FALLBACK_DATABASE
    except Exception as e:
        print(f"Error loading database: {e}. Using fallback.")
        return FALLBACK_DATABASE


@mcp.tool()
def search_flight_offers(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    adults: Optional[int] = 1,
    children: Optional[int] = 0,
    infants: Optional[int] = 0,
    travel_class: Optional[str] = None,
    currency: Optional[str] = "USD"
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Search for flight offers based on search criteria.

    Args:
        origin (str): Departure airport code (e.g., "JFK", "LAX")
        destination (str): Arrival airport code (e.g., "LHR", "CDG")
        departure_date (str): Departure date in YYYY-MM-DD format
        return_date (str, optional): Return date in YYYY-MM-DD format for round trips
        adults (int, optional): Number of adult passengers (default: 1)
        children (int, optional): Number of child passengers (default: 0)
        infants (int, optional): Number of infant passengers (default: 0)
        travel_class (str, optional): Travel class (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST)
        currency (str, optional): Currency code for pricing (default: "USD")

    Returns:
        Dict with 'flight_offers' key containing list of matching flight offers
    """
    # Load database
    database = load_database()
    flight_offers = database.get("flight_offers", [])
    
    # Filter flight offers based on search criteria
    matching_offers = []
    
    for offer in flight_offers:
        # Check required criteria
        if (offer.get("origin") == origin and 
            offer.get("destination") == destination and 
            offer.get("departure_date") == departure_date):
            
            # Check optional criteria
            matches = True
            
            if return_date and offer.get("return_date") != return_date:
                matches = False
            
            if travel_class and offer.get("travel_class") != travel_class:
                matches = False
            
            if currency and offer.get("currency") != currency:
                matches = False
            
            # Check passenger capacity (if specified)
            if adults and offer.get("adults", 0) < adults:
                matches = False
            
            if children and offer.get("children", 0) < children:
                matches = False
            
            if infants and offer.get("infants", 0) < infants:
                matches = False
            
            if matches:
                matching_offers.append(offer)
    
    return {"flight_offers": matching_offers}


if __name__ == "__main__":
    mcp.run()