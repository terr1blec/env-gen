from fastmcp import FastMCP
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

mcp = FastMCP(name="Flight & Stay Search Server (Duffel API)")

# Load the database
DATABASE_PATH = os.path.join(
    os.path.dirname(__file__), 
    "flight__stay_search_server_duffel_api_database.json"
)

def load_database() -> Dict[str, Any]:
    """Load the offline database from JSON file."""
    try:
        with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Fallback to empty structure if database is missing
        return {
            "flights": [],
            "offers": [],
            "stays": [],
            "reviews": []
        }

@mcp.tool()
def search_flights(
    adults: int,
    cabin_class: str,
    max_connections: int,
    origin: str,
    destination: str,
    departure_date: str
) -> Dict[str, Any]:
    """Search for flights between origin and destination.

    Args:
        adults (int): Number of adult passengers
        cabin_class (str): Desired cabin class (economy, premium_economy, business, first)
        max_connections (int): Maximum number of connections allowed
        origin (str): Departure airport code (e.g., LAX, JFK)
        destination (str): Arrival airport code (e.g., CDG, LHR)
        departure_date (str): Departure date in YYYY-MM-DD format

    Returns:
        Dict with 'flights' key containing matching flight data
    """
    database = load_database()
    
    # Filter flights based on criteria
    matching_flights = []
    for flight in database.get("flights", []):
        if (flight.get("origin") == origin.upper() and 
            flight.get("destination") == destination.upper() and
            flight.get("departure_date") == departure_date):
            
            # Check cabin class filter
            if cabin_class and flight.get("cabin_class") != cabin_class:
                continue
                
            # Check max connections filter
            if flight.get("max_connections", 0) > max_connections:
                continue
                
            matching_flights.append(flight)
    
    return {"flights": matching_flights}

@mcp.tool()
def get_offer_details(offer_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific flight offer.

    Args:
        offer_id (str): The unique identifier for the offer

    Returns:
        Dict with 'offer' key containing offer details
    """
    database = load_database()
    
    # Find the offer by ID
    for offer in database.get("offers", []):
        if offer.get("id") == offer_id:
            # Find the corresponding flight
            flight = None
            for f in database.get("flights", []):
                if f.get("id") == offer.get("flight_id"):
                    flight = f
                    break
            
            return {
                "offer": {
                    **offer,
                    "flight_details": flight
                }
            }
    
    return {"offer": None}

@mcp.tool()
def search_multi_city(
    adults: int,
    segments: str,
    cabin_class: str,
    max_connections: int
) -> Dict[str, Any]:
    """Search for multi-city flight itineraries.

    Args:
        adults (int): Number of adult passengers
        segments (str): JSON string representing flight segments. 
                       Expected format: [{"origin": "LAX", "destination": "JFK", "departure_date": "2025-12-01"}, ...]
        cabin_class (str): Desired cabin class
        max_connections (int): Maximum number of connections per segment

    Returns:
        Dict with 'itineraries' key containing multi-city flight options
    """
    database = load_database()
    
    try:
        # Parse segments JSON
        segment_list = json.loads(segments)
    except json.JSONDecodeError:
        return {"itineraries": []}
    
    # For each segment, find matching flights
    itineraries = []
    
    for segment in segment_list:
        origin = segment.get("origin", "")
        destination = segment.get("destination", "")
        departure_date = segment.get("departure_date", "")
        
        segment_flights = []
        for flight in database.get("flights", []):
            if (flight.get("origin") == origin.upper() and 
                flight.get("destination") == destination.upper() and
                flight.get("departure_date") == departure_date):
                
                if cabin_class and flight.get("cabin_class") != cabin_class:
                    continue
                    
                if flight.get("max_connections", 0) > max_connections:
                    continue
                    
                segment_flights.append(flight)
        
        itineraries.append({
            "segment": segment,
            "available_flights": segment_flights
        })
    
    return {"itineraries": itineraries}

@mcp.tool()
def search_stays(
    guests: int,
    location: str,
    radius_km: str,
    check_in_date: str,
    check_out_date: str
) -> Dict[str, Any]:
    """Search for accommodation stays in a specific location.

    Args:
        guests (int): Number of guests
        location (str): Location/city name for the stay
        radius_km (str): Search radius in kilometers (not implemented in offline mode)
        check_in_date (str): Check-in date in YYYY-MM-DD format
        check_out_date (str): Check-out date in YYYY-MM-DD format

    Returns:
        Dict with 'stays' key containing matching accommodation data
    """
    database = load_database()
    
    # Filter stays based on criteria
    matching_stays = []
    for stay in database.get("stays", []):
        # Check location (case-insensitive partial match)
        if location.lower() not in stay.get("location", "").lower():
            continue
            
        # Check guest capacity
        if stay.get("guests", 0) < guests:
            continue
            
        # Check date availability
        if (stay.get("check_in_date") <= check_in_date and 
            stay.get("check_out_date") >= check_out_date):
            matching_stays.append(stay)
    
    return {"stays": matching_stays}

@mcp.tool()
def get_stay_reviews(
    stay_id: str,
    limit: int,
    after: str,
    before: str
) -> Dict[str, Any]:
    """Get reviews for a specific accommodation stay with pagination.

    Args:
        stay_id (str): The unique identifier for the stay
        limit (int): Maximum number of reviews to return
        after (str): Return reviews after this date (YYYY-MM-DD)
        before (str): Return reviews before this date (YYYY-MM-DD)

    Returns:
        Dict with 'reviews' key containing filtered reviews
    """
    database = load_database()
    
    # Filter reviews for the specific stay
    stay_reviews = []
    for review in database.get("reviews", []):
        if review.get("stay_id") == stay_id:
            review_date = review.get("date", "")
            
            # Apply date filters
            if after and review_date <= after:
                continue
            if before and review_date >= before:
                continue
                
            stay_reviews.append(review)
    
    # Sort by date (most recent first) and apply limit
    stay_reviews.sort(key=lambda x: x.get("date", ""), reverse=True)
    
    return {"reviews": stay_reviews[:limit]}

if __name__ == "__main__":
    mcp.run()