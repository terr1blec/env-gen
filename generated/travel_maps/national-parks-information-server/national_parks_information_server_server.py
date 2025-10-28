"""
National Parks Information Server - FastMCP Implementation

This server provides information about national parks, alerts, visitor centers, 
campgrounds, and events using an offline database.
"""

import json
import os
from typing import List, Optional, Dict, Any
from fastmcp import FastMCP
from datetime import datetime

# Initialize FastMCP server
mcp = FastMCP(name="National Parks Information Server")

# Database configuration
DATABASE_PATH = os.path.join(
    os.path.dirname(__file__), 
    "national_parks_information_server_database.json"
)

# Fallback data structure (used only if JSON is missing)
FALLBACK_DATA = {
    "parks": [],
    "alerts": [],
    "visitor_centers": [],
    "campgrounds": [],
    "events": []
}


def load_database() -> Dict[str, Any]:
    """Load the database from JSON file or return fallback data."""
    try:
        if os.path.exists(DATABASE_PATH):
            with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate required top-level keys
            required_keys = ["parks", "alerts", "visitor_centers", "campgrounds", "events"]
            for key in required_keys:
                if key not in data:
                    print(f"Warning: Missing required key '{key}' in database, using fallback")
                    return FALLBACK_DATA
            
            return data
        else:
            print(f"Warning: Database file not found at {DATABASE_PATH}, using fallback data")
            return FALLBACK_DATA
    except Exception as e:
        print(f"Error loading database: {e}, using fallback data")
        return FALLBACK_DATA


@mcp.tool()
def findParks(
    search_term: Optional[str] = None,
    state: Optional[str] = None,
    activity: Optional[str] = None,
    limit: int = 10,
    start: int = 0
) -> Dict[str, Any]:
    """Search and filter national parks by various criteria.

    Args:
        search_term: Search term to match against park name, description, or location (case-insensitive)
        state: Filter by state code (e.g., "ME", "WY")
        activity: Filter by activity (e.g., "Hiking", "Camping")
        limit: Maximum number of results to return (default: 10)
        start: Starting index for pagination (default: 0)

    Returns:
        Dictionary containing parks array and total count
    """
    data = load_database()
    parks = data.get("parks", [])
    
    filtered_parks = parks
    
    # Apply search term filter
    if search_term:
        search_lower = search_term.lower()
        filtered_parks = [
            park for park in filtered_parks
            if (search_lower in park.get("name", "").lower() or
                 search_lower in park.get("description", "").lower() or
                 search_lower in park.get("location", "").lower())
        ]
    
    # Apply state filter
    if state:
        state_upper = state.upper()
        filtered_parks = [
            park for park in filtered_parks
            if state_upper in park.get("states", "").upper()
        ]
    
    # Apply activity filter
    if activity:
        activity_lower = activity.lower()
        filtered_parks = [
            park for park in filtered_parks
            if any(activity_lower in act.lower() for act in park.get("activities", []))
        ]
    
    # Apply pagination
    total_count = len(filtered_parks)
    paginated_parks = filtered_parks[start:start + limit]
    
    return {
        "parks": paginated_parks,
        "total": total_count,
        "limit": limit,
        "start": start
    }


@mcp.tool()
def getParkDetails(parkCode: str) -> Dict[str, Any]:
    """Get detailed information for a specific park by its park code.

    Args:
        parkCode: The unique park code (e.g., "acad", "yell")

    Returns:
        Dictionary containing park details or error if not found
    """
    data = load_database()
    parks = data.get("parks", [])
    
    park_code_lower = parkCode.lower()
    
    for park in parks:
        if park.get("parkCode", "").lower() == park_code_lower:
            return park
    
    return {"error": f"Park with code '{parkCode}' not found"}


@mcp.tool()
def getAlerts(
    parkCode: Optional[str] = None,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 10,
    start: int = 0
) -> Dict[str, Any]:
    """Get alerts with filtering options.

    Args:
        parkCode: Filter by park code (e.g., "acad", "yell")
        category: Filter by alert category (e.g., "closure", "hazard", "weather")
        severity: Filter by severity level (e.g., "extreme", "severe", "moderate")
        status: Filter by status (e.g., "active", "inactive", "expired")
        limit: Maximum number of results to return (default: 10)
        start: Starting index for pagination (default: 0)

    Returns:
        Dictionary containing alerts array and total count
    """
    data = load_database()
    alerts = data.get("alerts", [])
    
    filtered_alerts = alerts
    
    # Apply park code filter
    if parkCode:
        park_code_lower = parkCode.lower()
        filtered_alerts = [
            alert for alert in filtered_alerts
            if alert.get("parkCode", "").lower() == park_code_lower
        ]
    
    # Apply category filter
    if category:
        category_lower = category.lower()
        filtered_alerts = [
            alert for alert in filtered_alerts
            if alert.get("category", "").lower() == category_lower
        ]
    
    # Apply severity filter
    if severity:
        severity_lower = severity.lower()
        filtered_alerts = [
            alert for alert in filtered_alerts
            if alert.get("severity", "").lower() == severity_lower
        ]
    
    # Apply status filter
    if status:
        status_lower = status.lower()
        filtered_alerts = [
            alert for alert in filtered_alerts
            if alert.get("status", "").lower() == status_lower
        ]
    
    # Apply pagination
    total_count = len(filtered_alerts)
    paginated_alerts = filtered_alerts[start:start + limit]
    
    return {
        "alerts": paginated_alerts,
        "total": total_count,
        "limit": limit,
        "start": start
    }


@mcp.tool()
def getVisitorCenters(
    parkCode: Optional[str] = None,
    limit: int = 10,
    start: int = 0
) -> Dict[str, Any]:
    """Get visitor centers information.

    Args:
        parkCode: Filter by park code (e.g., "acad", "yell")
        limit: Maximum number of results to return (default: 10)
        start: Starting index for pagination (default: 0)

    Returns:
        Dictionary containing visitor centers array and total count
    """
    data = load_database()
    visitor_centers = data.get("visitor_centers", [])
    
    filtered_centers = visitor_centers
    
    # Apply park code filter
    if parkCode:
        park_code_lower = parkCode.lower()
        filtered_centers = [
            center for center in filtered_centers
            if center.get("parkCode", "").lower() == park_code_lower
        ]
    
    # Apply pagination
    total_count = len(filtered_centers)
    paginated_centers = filtered_centers[start:start + limit]
    
    return {
        "visitor_centers": paginated_centers,
        "total": total_count,
        "limit": limit,
        "start": start
    }


@mcp.tool()
def getCampgrounds(
    parkCode: Optional[str] = None,
    amenity: Optional[str] = None,
    limit: int = 10,
    start: int = 0
) -> Dict[str, Any]:
    """Get campgrounds information with filtering options.

    Args:
        parkCode: Filter by park code (e.g., "acad", "yell")
        amenity: Filter by specific amenity (e.g., "Restrooms", "Fire Rings")
        limit: Maximum number of results to return (default: 10)
        start: Starting index for pagination (default: 0)

    Returns:
        Dictionary containing campgrounds array and total count
    """
    data = load_database()
    campgrounds = data.get("campgrounds", [])
    
    filtered_campgrounds = campgrounds
    
    # Apply park code filter
    if parkCode:
        park_code_lower = parkCode.lower()
        filtered_campgrounds = [
            campground for campground in filtered_campgrounds
            if campground.get("parkCode", "").lower() == park_code_lower
        ]
    
    # Apply amenity filter
    if amenity:
        amenity_lower = amenity.lower()
        filtered_campgrounds = [
            campground for campground in filtered_campgrounds
            if any(amenity_lower in am.lower() for am in campground.get("amenities", []))
        ]
    
    # Apply pagination
    total_count = len(filtered_campgrounds)
    paginated_campgrounds = filtered_campgrounds[start:start + limit]
    
    return {
        "campgrounds": paginated_campgrounds,
        "total": total_count,
        "limit": limit,
        "start": start
    }


@mcp.tool()
def getEvents(
    parkCode: Optional[str] = None,
    category: Optional[str] = None,
    dateStart: Optional[str] = None,
    dateEnd: Optional[str] = None,
    limit: int = 50,
    start: int = 0
) -> Dict[str, Any]:
    """Get events with date filtering options.

    Args:
        parkCode: Filter by park code (e.g., "acad", "yell")
        category: Filter by event category (e.g., "ranger-led", "festival")
        dateStart: Filter events starting on or after this date (YYYY-MM-DD format)
        dateEnd: Filter events ending on or before this date (YYYY-MM-DD format)
        limit: Maximum number of results to return (default: 50)
        start: Starting index for pagination (default: 0)

    Returns:
        Dictionary containing events array and total count
    """
    data = load_database()
    events = data.get("events", [])
    
    filtered_events = events
    
    # Apply park code filter
    if parkCode:
        park_code_lower = parkCode.lower()
        filtered_events = [
            event for event in filtered_events
            if event.get("parkCode", "").lower() == park_code_lower
        ]
    
    # Apply category filter
    if category:
        category_lower = category.lower()
        filtered_events = [
            event for event in filtered_events
            if event.get("category", "").lower() == category_lower
        ]
    
    # Apply date range filters
    if dateStart:
        try:
            start_date = datetime.strptime(dateStart, "%Y-%m-%d")
            filtered_events = [
                event for event in filtered_events
                if event.get("dateEnd", "") >= dateStart  # Event ends on or after start date
            ]
        except ValueError:
            return {"error": "Invalid dateStart format. Use YYYY-MM-DD"}
    
    if dateEnd:
        try:
            end_date = datetime.strptime(dateEnd, "%Y-%m-%d")
            filtered_events = [
                event for event in filtered_events
                if event.get("dateStart", "") <= dateEnd  # Event starts on or before end date
            ]
        except ValueError:
            return {"error": "Invalid dateEnd format. Use YYYY-MM-DD"}
    
    # Apply pagination
    total_count = len(filtered_events)
    paginated_events = filtered_events[start:start + limit]
    
    return {
        "events": paginated_events,
        "total": total_count,
        "limit": limit,
        "start": start
    }


if __name__ == "__main__":
    mcp.run()