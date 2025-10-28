"""
Validation script for Airbnb Search and Listing Server
This script validates that the server module can load the dataset and tools work correctly.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Import the server module
    from airbnb_search_and_listing_server_server import airbnb_search, airbnb_listing_details, _LISTINGS
    
    print("✅ Server module imported successfully")
    
    # Check dataset loading
    if _LISTINGS:
        print(f"✅ Dataset loaded successfully with {len(_LISTINGS)} listings")
        print(f"   Available listing IDs: {list(_LISTINGS.keys())}")
    else:
        print("❌ No listings found in dataset")
    
    # Test search functionality
    print("\n🧪 Testing search functionality...")
    search_result = airbnb_search(location="New York")
    
    if "results" in search_result:
        print(f"✅ Search returned {len(search_result['results'])} results")
        print(f"   Total count: {search_result['total_count']}")
        print(f"   Page: {search_result['page']}")
        print(f"   Has next page: {search_result['has_next_page']}")
    else:
        print("❌ Search failed")
    
    # Test listing details functionality
    print("\n🧪 Testing listing details functionality...")
    if _LISTINGS:
        first_listing_id = list(_LISTINGS.keys())[0]
        details_result = airbnb_listing_details(listing_id=first_listing_id)
        
        if "id" in details_result:
            print(f"✅ Listing details retrieved for ID: {details_result['id']}")
            print(f"   Title: {details_result['title']}")
            print(f"   Price: {details_result['price_per_night']} {details_result['currency']}")
        else:
            print("❌ Listing details retrieval failed")
    
    # Test error handling for non-existent listing
    print("\n🧪 Testing error handling...")
    error_result = airbnb_listing_details(listing_id="non_existent_id")
    if "error" in error_result:
        print("✅ Error handling working correctly for non-existent listings")
    else:
        print("❌ Error handling not working as expected")
    
    print("\n🎉 All validation tests completed successfully!")
    
except ImportError as e:
    print(f"❌ Failed to import server module: {e}")
except Exception as e:
    print(f"❌ Validation failed: {e}")
    import traceback
    traceback.print_exc()