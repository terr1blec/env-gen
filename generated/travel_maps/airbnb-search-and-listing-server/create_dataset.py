#!/usr/bin/env python3
"""Create the fixed dataset with 100 listings."""

import json
import random
from datetime import datetime, timedelta

# Set seed for deterministic generation
random.seed(42)

# Generate 100 listings
listings = []
for i in range(100):
    listing_id = f"listing_{i+1:03d}"
    
    # Simple generation for demonstration
    cities = ["New York", "Los Angeles", "London", "Paris", "Tokyo", "Sydney", "Barcelona", "Rome", "Amsterdam", "Berlin"]
    city = random.choice(cities)
    countries = {
        "New York": "USA", "Los Angeles": "USA", "London": "UK", "Paris": "France", 
        "Tokyo": "Japan", "Sydney": "Australia", "Barcelona": "Spain", "Rome": "Italy",
        "Amsterdam": "Netherlands", "Berlin": "Germany"
    }
    
    property_types = ["Apartment", "House", "Condo", "Villa", "Studio", "Loft"]
    property_type = random.choice(property_types)
    
    bedrooms = random.randint(1, 5)
    bathrooms = max(1, bedrooms - random.randint(0, 1))
    max_guests = bedrooms * 2 + random.randint(0, 2)
    
    # Generate price
    base_price = 50 if property_type in ["Studio", "Apartment"] else 80
    location_multiplier = 1.5 if city in ["New York", "London", "Tokyo"] else 1.0
    price_per_night = round(base_price * location_multiplier * (1 + bedrooms * 0.3) * random.uniform(0.8, 1.2), 2)
    
    # Generate host info
    host_names = ["Sarah Johnson", "Michael Chen", "Emma Rodriguez", "David Kim", "Lisa Wang"]
    host_name = random.choice(host_names)
    host_rating = round(random.uniform(4.0, 5.0), 1)
    host_response_rate = random.randint(85, 100)
    
    # Generate property rating
    rating = round(random.uniform(4.2, 5.0), 1)
    review_count = random.randint(5, 200)
    
    # Generate amenities
    amenities_pool = ["WiFi", "Kitchen", "Air conditioning", "Heating", "Washer", "Dryer", "Parking", "Pool", "TV"]
    num_amenities = random.randint(5, 9)
    amenities = random.sample(amenities_pool, num_amenities)
    
    # Generate available dates
    start_date = datetime.now()
    available_dates = []
    for i in range(90):
        if random.random() > 0.3:
            date = start_date + timedelta(days=i)
            available_dates.append(date.strftime("%Y-%m-%d"))
    
    listing = {
        "id": listing_id,
        "title": f"Cozy {property_type} in {city}",
        "description": f"This beautiful {property_type} is located in the heart of {city}. Perfect for {max_guests} guests, it features {bedrooms} bedrooms and {bathrooms} bathrooms.",
        "location": {
            "city": city,
            "country": countries[city],
            "latitude": 40.7128 if city == "New York" else 34.0522 if city == "Los Angeles" else 51.5074,
            "longitude": -74.0060 if city == "New York" else -118.2437 if city == "Los Angeles" else -0.1278
        },
        "price_per_night": price_per_night,
        "currency": "USD",
        "property_type": property_type,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "max_guests": max_guests,
        "amenities": amenities,
        "host": {
            "name": host_name,
            "rating": host_rating,
            "response_rate": host_response_rate
        },
        "rating": rating,
        "review_count": review_count,
        "images": [
            f"https://example.com/images/{listing_id}/1.jpg",
            f"https://example.com/images/{listing_id}/2.jpg",
            f"https://example.com/images/{listing_id}/3.jpg"
        ],
        "available_dates": available_dates
    }
    listings.append(listing)

# Generate search results
def generate_search_results(listings, page=1, per_page=20):
    total_count = len(listings)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    page_listings = listings[start_idx:end_idx]
    listing_ids = [listing["id"] for listing in page_listings]
    
    return {
        "results": listing_ids,
        "total_count": total_count,
        "page": page,
        "per_page": per_page,
        "has_next_page": end_idx < total_count,
        "has_previous_page": page > 1
    }

search_results = []

# Example 1: First page of all listings
search_results.append(generate_search_results(listings, page=1, per_page=20))

# Example 2: Second page of all listings
search_results.append(generate_search_results(listings, page=2, per_page=20))

# Example 3: Search for listings in New York
ny_listings = [listing for listing in listings if listing["location"]["city"] == "New York"]
if ny_listings:
    search_results.append(generate_search_results(ny_listings, page=1, per_page=10))

# Example 4: Search for apartments only
apartment_listings = [listing for listing in listings if listing["property_type"] == "Apartment"]
if apartment_listings:
    search_results.append(generate_search_results(apartment_listings, page=1, per_page=15))

# Create dataset
dataset = {
    "listings": listings,
    "search_results": search_results
}

# Save to JSON file
with open("airbnb_search_and_listing_server_dataset.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)

print(f"Generated {len(listings)} listings")
print(f"Generated {len(search_results)} search result examples")
print("Dataset saved to: airbnb_search_and_listing_server_dataset.json")