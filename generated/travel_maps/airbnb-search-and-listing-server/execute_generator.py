#!/usr/bin/env python3
"""Execute the dataset generator directly."""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


class AirbnbDatasetGenerator:
    """Generates synthetic Airbnb dataset with deterministic randomness."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the generator with an optional seed for deterministic output."""
        self.random = random.Random(seed)
        self.cities = [
            {"city": "New York", "country": "USA", "lat": 40.7128, "lon": -74.0060},
            {"city": "Los Angeles", "country": "USA", "lat": 34.0522, "lon": -118.2437},
            {"city": "London", "country": "UK", "lat": 51.5074, "lon": -0.1278},
            {"city": "Paris", "country": "France", "lat": 48.8566, "lon": 2.3522},
            {"city": "Tokyo", "country": "Japan", "lat": 35.6762, "lon": 139.6503},
            {"city": "Sydney", "country": "Australia", "lat": -33.8688, "lon": 151.2093},
            {"city": "Barcelona", "country": "Spain", "lat": 41.3851, "lon": 2.1734},
            {"city": "Rome", "country": "Italy", "lat": 41.9028, "lon": 12.4964},
            {"city": "Amsterdam", "country": "Netherlands", "lat": 52.3676, "lon": 4.9041},
            {"city": "Berlin", "country": "Germany", "lat": 52.5200, "lon": 13.4050},
        ]
        
        self.property_types = ["Apartment", "House", "Condo", "Villa", "Studio", "Loft"]
        self.amenities_pool = [
            "WiFi", "Kitchen", "Air conditioning", "Heating", "Washer", "Dryer",
            "Parking", "Pool", "Hot tub", "Gym", "Balcony", "Garden", "Patio",
            "Coffee maker", "Microwave", "Oven", "Refrigerator", "Dishwasher",
            "TV", "Netflix", "Hulu", "Amazon Prime", "Fireplace", "BBQ grill",
            "Beach access", "Mountain view", "City view", "Ocean view"
        ]
        
        self.host_names = [
            "Sarah Johnson", "Michael Chen", "Emma Rodriguez", "David Kim", "Lisa Wang",
            "James Smith", "Maria Garcia", "Robert Brown", "Jennifer Lee", "Thomas Wilson",
            "Jessica Taylor", "Christopher Davis", "Amanda Martinez", "Daniel Anderson",
            "Michelle Thomas", "Kevin Jackson", "Nicole White", "Brian Harris",
            "Stephanie Martin", "Jason Thompson"
        ]
        
        self.title_templates = [
            "Cozy {property_type} in {city}",
            "Beautiful {property_type} with amazing views",
            "Modern {property_type} in the heart of {city}",
            "Spacious {property_type} near attractions",
            "Luxury {property_type} with premium amenities",
            "Charming {property_type} in {city}",
            "Stylish {property_type} with great location",
            "Comfortable {property_type} for your stay",
            "Elegant {property_type} in {city}",
            "Bright and airy {property_type} with modern design"
        ]
        
        self.description_templates = [
            "This beautiful {property_type} is located in the heart of {city}. Perfect for {max_guests} guests, it features {bedrooms} bedrooms and {bathrooms} bathrooms. Enjoy all the modern amenities during your stay.",
            "Welcome to our lovely {property_type} in {city}! This spacious accommodation offers {bedrooms} bedrooms and {bathrooms} bathrooms, comfortably hosting up to {max_guests} guests. Experience the best of {city} from this central location.",
            "Discover this charming {property_type} nestled in {city}. With {bedrooms} bedrooms and {bathrooms} bathrooms, it's ideal for {max_guests} guests. The property combines comfort with convenience in a prime location.",
            "Experience luxury living in this stunning {property_type} in {city}. Featuring {bedrooms} bedrooms and {bathrooms} bathrooms, it accommodates {max_guests} guests. Premium amenities and thoughtful design make this the perfect getaway.",
            "This modern {property_type} offers the perfect base for exploring {city}. With {bedrooms} bedrooms and {bathrooms} bathrooms, it comfortably sleeps {max_guests}. Enjoy contemporary design and all the comforts of home."
        ]

    def generate_listing(self, listing_id: str) -> Dict[str, Any]:
        """Generate a single Airbnb listing with realistic data."""
        city_info = self.random.choice(self.cities)
        property_type = self.random.choice(self.property_types)
        
        # Generate realistic property details
        bedrooms = self.random.randint(1, 5)
        bathrooms = max(1, bedrooms - self.random.randint(0, 1))
        max_guests = bedrooms * 2 + self.random.randint(0, 2)
        
        # Generate price based on location and property type
        base_price = 50 if property_type in ["Studio", "Apartment"] else 80
        location_multiplier = 1.5 if city_info["city"] in ["New York", "London", "Tokyo"] else 1.0
        price_per_night = round(base_price * location_multiplier * (1 + bedrooms * 0.3) * self.random.uniform(0.8, 1.2), 2)
        
        # Generate host info
        host_name = self.random.choice(self.host_names)
        host_rating = round(self.random.uniform(4.0, 5.0), 1)
        host_response_rate = self.random.randint(85, 100)
        
        # Generate property rating and reviews
        rating = round(self.random.uniform(4.2, 5.0), 1)
        review_count = self.random.randint(5, 200)
        
        # Generate amenities
        num_amenities = self.random.randint(5, 12)
        amenities = self.random.sample(self.amenities_pool, num_amenities)
        
        # Generate title and description
        title_template = self.random.choice(self.title_templates)
        title = title_template.format(property_type=property_type, city=city_info["city"])
        
        description_template = self.random.choice(self.description_templates)
        description = description_template.format(
            property_type=property_type,
            city=city_info["city"],
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            max_guests=max_guests
        )
        
        # Generate available dates (next 90 days)
        start_date = datetime.now()
        available_dates = []
        for i in range(90):
            if self.random.random() > 0.3:  # 70% chance date is available
                date = start_date + timedelta(days=i)
                available_dates.append(date.strftime("%Y-%m-%d"))
        
        # Generate image URLs
        images = [
            f"https://example.com/images/{listing_id}/1.jpg",
            f"https://example.com/images/{listing_id}/2.jpg",
            f"https://example.com/images/{listing_id}/3.jpg"
        ]
        
        return {
            "id": listing_id,
            "title": title,
            "description": description,
            "location": {
                "city": city_info["city"],
                "country": city_info["country"],
                "latitude": round(city_info["lat"] + self.random.uniform(-0.1, 0.1), 6),
                "longitude": round(city_info["lon"] + self.random.uniform(-0.1, 0.1), 6)
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
            "images": images,
            "available_dates": available_dates
        }

    def generate_search_results(self, listings: List[Dict], page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Generate search results with pagination."""
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

    def generate_dataset(self, num_listings: int = 100, seed: Optional[int] = None) -> Dict[str, Any]:
        """Generate the complete dataset with listings and search results."""
        if seed is not None:
            self.random = random.Random(seed)
        
        # Generate listings
        listings = []
        for i in range(num_listings):
            listing_id = f"listing_{i+1:03d}"
            listing = self.generate_listing(listing_id)
            listings.append(listing)
        
        # Generate multiple search result examples with different pagination
        search_results = []
        
        # Example 1: First page of all listings
        search_results.append(self.generate_search_results(listings, page=1, per_page=20))
        
        # Example 2: Second page of all listings
        search_results.append(self.generate_search_results(listings, page=2, per_page=20))
        
        # Example 3: Search for listings in New York (filtered)
        ny_listings = [listing for listing in listings if listing["location"]["city"] == "New York"]
        if ny_listings:
            search_results.append(self.generate_search_results(ny_listings, page=1, per_page=10))
        
        # Example 4: Search for apartments only
        apartment_listings = [listing for listing in listings if listing["property_type"] == "Apartment"]
        if apartment_listings:
            search_results.append(self.generate_search_results(apartment_listings, page=1, per_page=15))
        
        # Example 5: Search for budget listings (under $100)
        budget_listings = [listing for listing in listings if listing["price_per_night"] < 100]
        if budget_listings:
            search_results.append(self.generate_search_results(budget_listings, page=1, per_page=10))
        
        return {
            "listings": listings,
            "search_results": search_results
        }


# Generate the dataset
generator = AirbnbDatasetGenerator(seed=42)
dataset = generator.generate_dataset(num_listings=100)

# Save to JSON file
with open("airbnb_search_and_listing_server_dataset.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)

print(f"Generated {len(dataset['listings'])} listings")
print(f"Generated {len(dataset['search_results'])} search result examples")
print("Dataset saved to: airbnb_search_and_listing_server_dataset.json")