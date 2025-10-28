"""
Usage Example for Airbnb Search and Listing Server

This script demonstrates how to use the MCP tools programmatically.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from airbnb_search_and_listing_server_server import airbnb_search, airbnb_listing_details

def demonstrate_search():
    """Demonstrate various search scenarios."""
    
    print("🔍 Airbnb Search Examples")
    print("=" * 50)
    
    # Example 1: Basic search by location
    print("\n1. Basic search by location:")
    result = airbnb_search(location="New York")
    print(f"   Found {result['total_count']} listings in New York")
    for listing in result['results']:
        print(f"   - {listing['title']}: ${listing['price_per_night']}/night")
    
    # Example 2: Search with price filter
    print("\n2. Search with price filter:")
    result = airbnb_search(location="USA", min_price=100, max_price=150)
    print(f"   Found {result['total_count']} listings in USA between $100-$150")
    for listing in result['results']:
        print(f"   - {listing['title']}: ${listing['price_per_night']}/night")
    
    # Example 3: Search with guest count
    print("\n3. Search for listings that accommodate 4+ guests:")
    result = airbnb_search(location="USA", guests=4)
    print(f"   Found {result['total_count']} listings that can accommodate 4+ guests")


def demonstrate_listing_details():
    """Demonstrate listing details retrieval."""
    
    print("\n🏠 Listing Details Examples")
    print("=" * 50)
    
    # Get available listing IDs first
    search_result = airbnb_search(location="USA")
    
    if search_result['results']:
        first_listing = search_result['results'][0]
        listing_id = first_listing['id']
        
        print(f"\n1. Getting details for listing: {listing_id}")
        details = airbnb_listing_details(listing_id=listing_id)
        
        print(f"   Title: {details['title']}")
        print(f"   Location: {details['location']['city']}, {details['location']['country']}")
        print(f"   Price: ${details['price_per_night']} {details['currency']}/night")
        print(f"   Property Type: {details['property_type']}")
        print(f"   Bedrooms: {details['bedrooms']}, Bathrooms: {details['bathrooms']}")
        print(f"   Max Guests: {details['max_guests']}")
        print(f"   Rating: {details['rating']} ⭐ ({details['review_count']} reviews)")
        print(f"   Host: {details['host']['name']} (Rating: {details['host']['rating']})")
        print(f"   Amenities: {', '.join(details['amenities'][:5])}...")
        print(f"   Available dates: {len(details['available_dates'])} days available")


def demonstrate_error_handling():
    """Demonstrate error handling for invalid requests."""
    
    print("\n⚠️  Error Handling Examples")
    print("=" * 50)
    
    # Example 1: Non-existent listing
    print("\n1. Requesting non-existent listing:")
    result = airbnb_listing_details(listing_id="invalid_id_123")
    if "error" in result:
        print(f"   ✅ Error handled: {result['error']}")
    
    # Example 2: Search with no results
    print("\n2. Search with no matching results:")
    result = airbnb_search(location="Mars")
    print(f"   Found {result['total_count']} listings on Mars")


if __name__ == "__main__":
    print("🚀 Airbnb Search and Listing Server - Usage Examples")
    print("=" * 60)
    
    demonstrate_search()
    demonstrate_listing_details()
    demonstrate_error_handling()
    
    print("\n✨ All examples completed successfully!")