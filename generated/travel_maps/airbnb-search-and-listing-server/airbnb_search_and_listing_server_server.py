"""
FastMCP Server for Airbnb Search and Listing Server

This module provides tools for searching Airbnb listings and retrieving detailed listing information.
All data is loaded from the generated dataset JSON file.
"""

import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Airbnb Search and Listing Server")

# Load dataset from JSON file
_DATASET_PATH = os.path.join(
    os.path.dirname(__file__), 
    "airbnb_search_and_listing_server_dataset.json"
)

# Fallback dataset structure if JSON file is missing
_FALLBACK_DATASET = {
    "listings": [],
    "search_results": []
}

def load_dataset() -> Dict[str, Any]:
    """Load dataset from JSON file or return fallback if file is missing."""
    try:
        with open(_DATASET_PATH, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        # Validate required keys exist
        if "listings" not in dataset or "search_results" not in dataset:
            print(f"Warning: Dataset missing required keys. Using fallback dataset.")
            return _FALLBACK_DATASET
            
        return dataset
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load dataset from {_DATASET_PATH}: {e}")
        print("Using fallback dataset.")
        return _FALLBACK_DATASET

# Load dataset at module import
_DATASET = load_dataset()
_LISTINGS = {listing["id"]: listing for listing in _DATASET.get("listings", [])}


def _filter_listings_by_location(listings: List[Dict], location: str) -> List[Dict]:
    """Filter listings by location (case-insensitive partial match)."""
    location_lower = location.lower()
    return [
        listing for listing in listings
        if location_lower in listing["location"]["city"].lower()
        or location_lower in listing["location"]["country"].lower()
    ]


def _filter_listings_by_dates(listings: List[Dict], check_in: Optional[str], check_out: Optional[str]) -> List[Dict]:
    """Filter listings by availability dates."""
    if not check_in and not check_out:
        return listings
    
    filtered = []
    for listing in listings:
        available_dates = listing.get("available_dates", [])
        
        # If only check_in is provided, check if that date is available
        if check_in and not check_out:
            if check_in in available_dates:
                filtered.append(listing)
        # If only check_out is provided, check if that date is available
        elif check_out and not check_in:
            if check_out in available_dates:
                filtered.append(listing)
        # If both dates are provided, check if all dates in range are available
        elif check_in and check_out:
            try:
                start_date = datetime.strptime(check_in, "%Y-%m-%d")
                end_date = datetime.strptime(check_out, "%Y-%m-%d")
                
                if start_date > end_date:
                    continue
                    
                # Check if all dates in range are available
                current_date = start_date
                all_available = True
                while current_date <= end_date:
                    if current_date.strftime("%Y-%m-%d") not in available_dates:
                        all_available = False
                        break
                    current_date = current_date.replace(day=current_date.day + 1)
                
                if all_available:
                    filtered.append(listing)
            except ValueError:
                # Invalid date format, skip date filtering
                filtered.append(listing)
    
    return filtered


def _filter_listings_by_guests(listings: List[Dict], guests: Optional[int]) -> List[Dict]:
    """Filter listings by maximum guest capacity."""
    if not guests:
        return listings
    return [listing for listing in listings if listing.get("max_guests", 0) >= guests]


def _filter_listings_by_price(listings: List[Dict], min_price: Optional[float], max_price: Optional[float]) -> List[Dict]:
    """Filter listings by price range (inclusive)."""
    filtered = listings
    
    if min_price is not None:
        filtered = [listing for listing in filtered if listing.get("price_per_night", 0) >= min_price]
    
    if max_price is not None:
        filtered = [listing for listing in filtered if listing.get("price_per_night", float('inf')) <= max_price]
    
    return filtered


def _filter_listings_by_property_type(listings: List[Dict], property_type: Optional[str]) -> List[Dict]:
    """Filter listings by property type (case-insensitive)."""
    if not property_type:
        return listings
    
    property_type_lower = property_type.lower()
    return [
        listing for listing in listings
        if property_type_lower in listing.get("property_type", "").lower()
    ]


@mcp.tool()
def airbnb_search(
    location: str,
    check_in: Optional[str] = None,
    check_out: Optional[str] = None,
    guests: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    property_type: Optional[str] = None,
    page: int = 1,
    per_page: int = 20
) -> Dict[str, Any]:
    """
    Search for Airbnb listings with various filters and pagination.
    
    Args:
        location: The city or country to search in (required)
        check_in: Check-in date in YYYY-MM-DD format (optional)
        check_out: Check-out date in YYYY-MM-DD format (optional)
        guests: Number of guests (optional)
        min_price: Minimum price per night (optional)
        max_price: Maximum price per night (optional)
        property_type: Type of property (e.g., "Apartment", "House") (optional)
        page: Page number for pagination (default: 1)
        per_page: Number of results per page (default: 20)
    
    Returns:
        Dictionary containing search results with pagination metadata
    """
    # Get all listings from dataset
    all_listings = list(_LISTINGS.values())
    
    # Apply filters
    filtered_listings = all_listings
    filtered_listings = _filter_listings_by_location(filtered_listings, location)
    filtered_listings = _filter_listings_by_dates(filtered_listings, check_in, check_out)
    filtered_listings = _filter_listings_by_guests(filtered_listings, guests)
    filtered_listings = _filter_listings_by_price(filtered_listings, min_price, max_price)
    filtered_listings = _filter_listings_by_property_type(filtered_listings, property_type)
    
    # Calculate pagination
    total_count = len(filtered_listings)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # Get paginated results
    paginated_results = filtered_listings[start_idx:end_idx]
    
    # Calculate pagination metadata
    has_next_page = end_idx < total_count
    has_previous_page = page > 1
    
    return {
        "results": paginated_results,
        "total_count": total_count,
        "page": page,
        "per_page": per_page,
        "has_next_page": has_next_page,
        "has_previous_page": has_previous_page
    }


@mcp.tool()
def airbnb_listing_details(listing_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific Airbnb listing.
    
    Args:
        listing_id: The unique identifier of the listing (required)
    
    Returns:
        Dictionary containing detailed listing information
    """
    # Look up listing by ID
    listing = _LISTINGS.get(listing_id)
    
    if not listing:
        return {
            "error": f"Listing with ID '{listing_id}' not found",
            "available_listing_ids": list(_LISTINGS.keys())
        }
    
    return listing


if __name__ == "__main__":
    # Run the server
    mcp.run(transport="stdio")