"""
Offline database generator for nearbysearch service.

Generates synthetic places data for testing and development.
"""

import json
import random
import math
from typing import Dict, List, Any


class NearbySearchDatabase:
    """Generates deterministic synthetic places data for nearby search."""
    
    def __init__(self, seed: int = 42):
        """Initialize with a seed for deterministic generation."""
        self.seed = seed
        random.seed(seed)
        
        # Major city coordinates as centers for place generation
        self.city_centers = [
            (40.7128, -74.0060),  # New York
            (34.0522, -118.2437), # Los Angeles
            (41.8781, -87.6298),  # Chicago
            (29.7604, -95.3698),  # Houston
            (33.4484, -112.0740), # Phoenix
            (39.7392, -104.9903), # Denver
            (47.6062, -122.3321), # Seattle
            (25.7617, -80.1918),  # Miami
        ]
        
        # Categories with weights for realistic distribution
        self.categories = {
            "restaurant": 0.3,
            "cafe": 0.2,
            "shop": 0.15,
            "hotel": 0.15,
            "park": 0.1,
            "museum": 0.1
        }
        
        # Common place name components
        self.name_components = {
            "restaurant": ["Bistro", "Grill", "Cafe", "Kitchen", "Eatery", "Restaurant", "Diner"],
            "cafe": ["Coffee", "Brew", "Roasters", "Cafe", "Espresso", "Bean"],
            "shop": ["Market", "Store", "Boutique", "Shop", "Emporium", "Gallery"],
            "hotel": ["Inn", "Hotel", "Suites", "Lodge", "Resort", "Plaza"],
            "park": ["Park", "Gardens", "Square", "Plaza", "Green", "Field"],
            "museum": ["Museum", "Gallery", "Exhibit", "Hall", "Center", "Institute"]
        }
        
        self.prefixes = ["The", "Central", "Downtown", "Urban", "City", "Metro", "Premium", "Elite"]
        self.suffixes = ["of Arts", "and Grill", "& Co", "Central", "Downtown", "Square"]
        
        # Street names for addresses
        self.streets = ["Main St", "Broadway", "Park Ave", "Oak St", "Maple Ave", "Cedar Ln", 
                        "Elm St", "Pine St", "Washington St", "Lincoln Ave", "Jefferson St"]
        
    def generate_coordinates(self, center_lat: float, center_lon: float) -> tuple:
        """Generate realistic coordinates around a city center."""
        # Generate coordinates within ~10km radius
        radius_km = random.uniform(0.5, 10.0)
        angle = random.uniform(0, 2 * math.pi)
        
        # Convert to degrees (approx 111km per degree)
        delta_lat = (radius_km * math.cos(angle)) / 111.0
        delta_lon = (radius_km * math.sin(angle)) / (111.0 * math.cos(math.radians(center_lat)))
        
        return (
            round(center_lat + delta_lat, 6),
            round(center_lon + delta_lon, 6)
        )
    
    def generate_name(self, category: str) -> str:
        """Generate a realistic place name based on category."""
        components = self.name_components[category]
        
        if random.random() < 0.3:
            # Simple name: Prefix + Component
            return f"{random.choice(self.prefixes)} {random.choice(components)}"
        elif random.random() < 0.6:
            # Two components
            return f"{random.choice(components)} {random.choice(components)}"
        else:
            # Full name with suffix
            return f"{random.choice(self.prefixes)} {random.choice(components)} {random.choice(self.suffixes)}"
    
    def generate_address(self, city_idx: int) -> str:
        """Generate a realistic street address."""
        street_num = random.randint(100, 9999)
        street = random.choice(self.streets)
        city_names = ["New York", "Los Angeles", "Chicago", "Houston", 
                     "Phoenix", "Denver", "Seattle", "Miami"]
        return f"{street_num} {street}, {city_names[city_idx]}"
    
    def generate_rating(self, category: str) -> float:
        """Generate realistic rating (1-5 stars)."""
        # Different categories have different rating distributions
        base_rating = {
            "restaurant": 3.8,
            "cafe": 4.2,
            "shop": 4.0,
            "hotel": 3.9,
            "park": 4.5,
            "museum": 4.3
        }[category]
        
        # Add some variation
        variation = random.gauss(0, 0.3)
        rating = base_rating + variation
        
        # Clamp to 1-5 range and round to 1 decimal
        return round(max(1.0, min(5.0, rating)), 1)
    
    def generate_price_level(self, category: str) -> int:
        """Generate price level (1-4)."""
        # Price level distributions by category
        distributions = {
            "restaurant": [0.1, 0.4, 0.4, 0.1],  # Mostly $$ and $$$
            "cafe": [0.3, 0.6, 0.1, 0.0],       # Mostly $
            "shop": [0.2, 0.5, 0.3, 0.0],       # Mostly $
            "hotel": [0.1, 0.3, 0.4, 0.2],      # Mostly $$$ and $$$$
            "park": [1.0, 0.0, 0.0, 0.0],       # Always free
            "museum": [0.4, 0.5, 0.1, 0.0]      # Mostly free or $
        }
        
        weights = distributions[category]
        return random.choices([1, 2, 3, 4], weights=weights)[0]
    
    def generate_opening_hours(self, category: str) -> str:
        """Generate realistic opening hours."""
        if category == "park":
            return "6:00 AM - 10:00 PM"
        elif category in ["restaurant", "cafe"]:
            if random.random() < 0.7:
                return "7:00 AM - 10:00 PM"
            else:
                return "11:00 AM - 11:00 PM"
        elif category == "shop":
            return "9:00 AM - 9:00 PM"
        elif category == "museum":
            return "10:00 AM - 5:00 PM"
        else:  # hotel
            return "24 hours"
    
    def generate_description(self, name: str, category: str) -> str:
        """Generate a simple description."""
        descriptions = {
            "restaurant": f"{name} offers delicious cuisine in a welcoming atmosphere.",
            "cafe": f"{name} serves premium coffee and light snacks in a cozy setting.",
            "shop": f"{name} features a wide selection of quality products and friendly service.",
            "hotel": f"{name} provides comfortable accommodations with modern amenities.",
            "park": f"{name} is a beautiful green space perfect for relaxation and recreation.",
            "museum": f"{name} showcases fascinating exhibits and educational displays."
        }
        return descriptions[category]
    
    def generate_places(self, count: int = 80) -> List[Dict[str, Any]]:
        """Generate the specified number of synthetic places."""
        places = []
        
        for i in range(count):
            # Choose a city center
            city_idx = i % len(self.city_centers)
            center_lat, center_lon = self.city_centers[city_idx]
            
            # Generate category based on weights
            category = random.choices(
                list(self.categories.keys()), 
                weights=list(self.categories.values())
            )[0]
            
            # Generate place data
            lat, lon = self.generate_coordinates(center_lat, center_lon)
            name = self.generate_name(category)
            
            place = {
                "id": f"place_{i+1:03d}",
                "name": name,
                "latitude": lat,
                "longitude": lon,
                "category": category,
                "address": self.generate_address(city_idx),
                "rating": self.generate_rating(category),
                "price_level": self.generate_price_level(category),
                "opening_hours": self.generate_opening_hours(category),
                "description": self.generate_description(name, category)
            }
            
            places.append(place)
        
        return places
    
    def save_to_json(self, filepath: str, count: int = 80):
        """Generate and save places data to JSON file."""
        places = self.generate_places(count)
        
        data = {
            "places": places
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Generated {len(places)} places and saved to {filepath}")


def generate_database():
    """Generate the database and save to the recommended path."""
    generator = NearbySearchDatabase(seed=42)
    output_path = "generated/travel_maps/nearbysearch/nearbysearch_database.json"
    generator.save_to_json(output_path, count=80)


if __name__ == "__main__":
    generate_database()