#!/usr/bin/env python3
"""
Verify the generated dataset structure matches the data contract.
"""

import json
import os

def verify_dataset():
    """Verify the dataset structure matches the data contract."""
    
    dataset_path = "airbnb_search_and_listing_server_dataset.json"
    
    if not os.path.exists(dataset_path):
        print("❌ Dataset file not found. Please run generate_dataset.py first.")
        return False
    
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        # Check top-level structure
        required_keys = {"listings", "search_results"}
        if not required_keys.issubset(dataset.keys()):
            print(f"❌ Missing top-level keys. Expected: {required_keys}, Got: {set(dataset.keys())}")
            return False
        
        # Verify listings structure
        listings = dataset["listings"]
        if not isinstance(listings, list):
            print("❌ Listings should be an array")
            return False
        
        if len(listings) == 0:
            print("❌ No listings generated")
            return False
        
        # Check first listing structure
        sample_listing = listings[0]
        required_listing_keys = {
            "id", "title", "description", "location", "price_per_night", "currency",
            "property_type", "bedrooms", "bathrooms", "max_guests", "amenities",
            "host", "rating", "review_count", "images", "available_dates"
        }
        
        if not required_listing_keys.issubset(sample_listing.keys()):
            print(f"❌ Missing listing keys. Expected: {required_listing_keys}, Got: {set(sample_listing.keys())}")
            return False
        
        # Check location structure
        location = sample_listing["location"]
        required_location_keys = {"city", "country", "latitude", "longitude"}
        if not required_location_keys.issubset(location.keys()):
            print(f"❌ Missing location keys. Expected: {required_location_keys}, Got: {set(location.keys())}")
            return False
        
        # Check host structure
        host = sample_listing["host"]
        required_host_keys = {"name", "rating", "response_rate"}
        if not required_host_keys.issubset(host.keys()):
            print(f"❌ Missing host keys. Expected: {required_host_keys}, Got: {set(host.keys())}")
            return False
        
        # Verify search results structure
        search_results = dataset["search_results"]
        if not isinstance(search_results, list):
            print("❌ Search results should be an array")
            return False
        
        if len(search_results) > 0:
            sample_search = search_results[0]
            required_search_keys = {
                "results", "total_count", "page", "per_page", "has_next_page", "has_previous_page"
            }
            if not required_search_keys.issubset(sample_search.keys()):
                print(f"❌ Missing search result keys. Expected: {required_search_keys}, Got: {set(sample_search.keys())}")
                return False
        
        print("✓ Dataset structure verification passed!")
        print(f"✓ Generated {len(listings)} listings")
        print(f"✓ Generated {len(search_results)} search result sets")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying dataset: {e}")
        return False

if __name__ == "__main__":
    success = verify_dataset()
    exit(0 if success else 1)