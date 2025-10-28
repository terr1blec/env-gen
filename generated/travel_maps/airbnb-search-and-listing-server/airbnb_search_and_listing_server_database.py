"""
Offline database generator for Airbnb Search and Listing Server.

This module generates synthetic Airbnb listing data following the DATA CONTRACT
and provides an update_database function for manual modifications.
"""

import json
import random
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
from pathlib import Path


class AirbnbDatabaseGenerator:
    """Generator for synthetic Airbnb listings data."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the generator with an optional seed for reproducibility."""
        if seed is not None:
            random.seed(seed)
        
        # Property types and their characteristics
        self.property_types = {
            "Apartment": {"min_price": 50, "max_price": 300, "min_bedrooms": 1, "max_bedrooms": 3},
            "House": {"min_price": 80, "max_price": 500, "min_bedrooms": 2, "max_bedrooms": 5},
            "Condo": {"min_price": 60, "max_price": 350, "min_bedrooms": 1, "max_bedrooms": 3},
            "Villa": {"min_price": 150, "max_price": 1000, "min_bedrooms": 3, "max_bedrooms": 6},
            "Cabin": {"min_price": 70, "max_price": 400, "min_bedrooms": 1, "max_bedrooms": 4},
            "Loft": {"min_price": 80, "max_price": 450, "min_bedrooms": 1, "max_bedrooms": 2},
            "Townhouse": {"min_price": 90, "max_price": 400, "min_bedrooms": 2, "max_bedrooms": 4},
            "Studio": {"min_price": 40, "max_price": 200, "min_bedrooms": 0, "max_bedrooms": 1}
        }
        
        # Popular locations with coordinates
        self.locations = [
            {"city": "New York", "state": "NY", "lat": 40.7128, "lon": -74.0060},
            {"city": "Los Angeles", "state": "CA", "lat": 34.0522, "lon": -118.2437},
            {"city": "Chicago", "state": "IL", "lat": 41.8781, "lon": -87.6298},
            {"city": "Miami", "state": "FL", "lat": 25.7617, "lon": -80.1918},
            {"city": "Seattle", "state": "WA", "lat": 47.6062, "lon": -122.3321},
            {"city": "Austin", "state": "TX", "lat": 30.2672, "lon": -97.7431},
            {"city": "Denver", "state": "CO", "lat": 39.7392, "lon": -104.9903},
            {"city": "Portland", "state": "OR", "lat": 45.5152, "lon": -122.6784},
            {"city": "San Francisco", "state": "CA", "lat": 37.7749, "lon": -122.4194},
            {"city": "Boston", "state": "MA", "lat": 42.3601, "lon": -71.0589}
        ]
        
        # Common amenities
        self.amenities_pool = [
            "WiFi", "Kitchen", "Air conditioning", "Heating", "Washer", "Dryer", 
            "Parking", "Pool", "Hot tub", "Gym", "Breakfast", "Workspace",
            "Family-friendly", "Pets allowed", "Smoking allowed", "Elevator",
            "Wheelchair accessible", "Security cameras", "Fireplace", "Balcony"
        ]
        
        # Host names
        self.host_names = [
            "Alex Johnson", "Maria Garcia", "David Smith", "Sarah Williams", 
            "James Brown", "Lisa Davis", "Michael Wilson", "Emily Taylor",
            "Robert Miller", "Jennifer Anderson", "Thomas Martinez", "Amanda Lee",
            "Christopher Clark", "Jessica Rodriguez", "Daniel Lewis", "Michelle Walker"
        ]
        
        # Property titles templates
        self.title_templates = [
            "Cozy {property_type} in {city}",
            "Beautiful {property_type} near {city} Downtown",
            "Modern {property_type} with Amazing Views",
            "Spacious {property_type} in {city}",
            "Luxury {property_type} in Prime {city} Location",
            "Charming {property_type} in {city}",
            "Stylish {property_type} with Great Amenities",
            "Comfortable {property_type} in {city}"
        ]
        
        # Description templates
        self.description_templates = [
            "This beautiful {property_type} offers a perfect getaway in {city}. "
            "Enjoy comfortable accommodations with modern amenities.",
            "Experience {city} like a local in this charming {property_type}. "
            "Perfect for families, couples, or solo travelers.",
            "Welcome to our lovely {property_type} in the heart of {city}. "
            "This space combines comfort and convenience for your stay.",
            "Discover {city} from this amazing {property_type}. "
            "Featuring modern design and all the comforts of home.",
            "Your perfect {city} retreat awaits in this stunning {property_type}. "
            "Designed for relaxation and memorable experiences."
        ]

    def generate_listing(self, listing_id: str) -> Dict[str, Any]:
        """Generate a single synthetic Airbnb listing."""
        
        # Select random location and property type
        location = random.choice(self.locations)
        property_type = random.choice(list(self.property_types.keys()))
        prop_config = self.property_types[property_type]
        
        # Generate property characteristics
        bedrooms = random.randint(prop_config["min_bedrooms"], prop_config["max_bedrooms"])
        beds = bedrooms + random.randint(0, 2)  # Usually more beds than bedrooms
        bathrooms = round(random.uniform(max(1, bedrooms - 1), bedrooms + 1), 1)
        max_guests = bedrooms * 2 + random.randint(0, 2)
        
        # Generate price
        base_price = random.uniform(prop_config["min_price"], prop_config["max_price"])
        price_per_night = round(base_price, 2)
        
        # Generate ratings and reviews
        rating = round(random.uniform(4.0, 5.0), 1)
        review_count = random.randint(5, 200)
        host_rating = round(random.uniform(4.5, 5.0), 1)
        
        # Generate amenities (4-8 random amenities)
        num_amenities = random.randint(4, 8)
        amenities = random.sample(self.amenities_pool, num_amenities)
        
        # Generate title and description
        title_template = random.choice(self.title_templates)
        title = title_template.format(property_type=property_type, city=location["city"])
        
        description_template = random.choice(self.description_templates)
        description = description_template.format(property_type=property_type, city=location["city"])
        
        # Generate boolean flags
        instant_book = random.choice([True, False])
        superhost = random.choice([True, False]) if rating > 4.7 else False
        
        # Add slight coordinate variation within the city
        lat_variation = random.uniform(-0.1, 0.1)
        lon_variation = random.uniform(-0.1, 0.1)
        
        return {
            "id": listing_id,
            "title": title,
            "description": description,
            "location": f"{location['city']}, {location['state']}",
            "price_per_night": price_per_night,
            "max_guests": max_guests,
            "bedrooms": bedrooms,
            "beds": beds,
            "bathrooms": bathrooms,
            "amenities": amenities,
            "host_name": random.choice(self.host_names),
            "host_rating": host_rating,
            "property_type": property_type,
            "rating": rating,
            "review_count": review_count,
            "latitude": round(location["lat"] + lat_variation, 6),
            "longitude": round(location["lon"] + lon_variation, 6),
            "instant_book": instant_book,
            "superhost": superhost
        }

    def generate_database(self, count: int = 50) -> Dict[str, Any]:
        """Generate a complete database with the specified number of listings."""
        
        listings = []
        for i in range(count):
            listing_id = f"listing_{i+1:03d}"
            listing = self.generate_listing(listing_id)
            listings.append(listing)
        
        metadata = {
            "total_listings": count,
            "generated_at": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
        return {
            "listings": listings,
            "metadata": metadata
        }


def generate_airbnb_database(
    count: int = 50, 
    seed: Optional[int] = None, 
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate synthetic Airbnb listings database.
    
    Args:
        count: Number of listings to generate (default: 50)
        seed: Random seed for reproducibility
        output_path: Path to save the JSON file. If None, uses recommended path
    
    Returns:
        Dictionary containing the generated database
    """
    if output_path is None:
        # Use the recommended path
        output_path = "generated\\travel_maps\\airbnb-search-and-listing-server\\airbnb_search_and_listing_server_database.json"
    
    generator = AirbnbDatabaseGenerator(seed=seed)
    database = generator.generate_database(count)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write to JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {count} Airbnb listings and saved to {output_path}")
    return database


def update_database(updates: Dict[str, Any], database_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Update the existing database with new data.
    
    This function is for manual follow-up operations; workflow agents will not call it automatically.
    
    Args:
        updates: Dictionary containing updates to merge into the database
        database_path: Path to the database JSON file. If None, uses recommended path
    
    Returns:
        Updated database dictionary
    
    Raises:
        FileNotFoundError: If the database file doesn't exist
        ValueError: If updates are incompatible with DATA CONTRACT
    """
    if database_path is None:
        # Use the recommended path
        database_path = "generated\\travel_maps\\airbnb-search-and-listing-server\\airbnb_search_and_listing_server_database.json"
    
    # Check if database file exists
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database file not found at {database_path}")
    
    # Load existing database
    with open(database_path, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    # Validate updates against DATA CONTRACT
    if "listings" in updates:
        if not isinstance(updates["listings"], list):
            raise ValueError("Updates to 'listings' must be a list")
        
        # Check each listing has required fields
        required_fields = {"id", "title", "location", "price_per_night", "max_guests", 
                          "bedrooms", "beds", "bathrooms", "host_name", "property_type", 
                          "rating", "review_count"}
        
        for listing in updates["listings"]:
            if not isinstance(listing, dict):
                raise ValueError("Each listing must be a dictionary")
            
            missing_fields = required_fields - set(listing.keys())
            if missing_fields:
                raise ValueError(f"Listing missing required fields: {missing_fields}")
    
    if "metadata" in updates:
        if not isinstance(updates["metadata"], dict):
            raise ValueError("Updates to 'metadata' must be a dictionary")
    
    # Merge updates
    for key, value in updates.items():
        if key == "listings" and isinstance(value, list):
            # For listings, we can either replace or extend
            # Here we'll extend by default, but you could add logic for replacement
            database["listings"].extend(value)
            # Update metadata total_listings
            database["metadata"]["total_listings"] = len(database["listings"])
            database["metadata"]["generated_at"] = datetime.now().isoformat()
        elif key == "metadata" and isinstance(value, dict):
            # For metadata, update individual fields
            database["metadata"].update(value)
        else:
            # For other keys, replace entirely
            database[key] = value
    
    # Save updated database
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"Updated database saved to {database_path}")
    return database


# Auto-generate the database when this module is imported
# This ensures the JSON file exists for the server to use
try:
    database_path = "generated\\travel_maps\\airbnb-search-and-listing-server\\airbnb_search_and_listing_server_database.json"
    if not os.path.exists(database_path):
        print("Generating Airbnb database...")
        generate_airbnb_database(count=50, seed=42)
        print("Database generation complete!")
except Exception as e:
    print(f"Warning: Could not auto-generate database: {e}")
    print("The database will need to be generated manually")