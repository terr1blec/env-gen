"""
Google Maps Offline Database Generator

This module generates deterministic synthetic data for Google Maps API simulation.
The data follows the DATA CONTRACT schema and can be seeded for reproducible results.
"""

import json
import os
import random
from typing import Dict, Any, Optional, List
from pathlib import Path


def generate_google_maps_database(seed: Optional[int] = None, record_count: int = 20) -> Dict[str, Any]:
    """
    Generate a deterministic offline database for Google Maps API simulation.
    
    Args:
        seed: Random seed for deterministic generation
        record_count: Number of records to generate for each category
        
    Returns:
        Dictionary matching the DATA CONTRACT schema
    """
    if seed is not None:
        random.seed(seed)
    
    # Geographic coordinates for major cities
    cities = [
        {"name": "New York", "lat": "40.7128", "lng": "-74.0060"},
        {"name": "Los Angeles", "lat": "34.0522", "lng": "-118.2437"},
        {"name": "Chicago", "lat": "41.8781", "lng": "-87.6298"},
        {"name": "Houston", "lat": "29.7604", "lng": "-95.3698"},
        {"name": "Phoenix", "lat": "33.4484", "lng": "-112.0740"},
        {"name": "Philadelphia", "lat": "39.9526", "lng": "-75.1652"},
        {"name": "San Antonio", "lat": "29.4241", "lng": "-98.4936"},
        {"name": "San Diego", "lat": "32.7157", "lng": "-117.1611"},
        {"name": "Dallas", "lat": "32.7767", "lng": "-96.7970"},
        {"name": "San Jose", "lat": "37.3382", "lng": "-121.8863"},
    ]
    
    # Common place types
    place_types = [
        "restaurant", "hotel", "museum", "park", "shopping_mall", 
        "hospital", "school", "gas_station", "coffee_shop", "bank"
    ]
    
    # Generate geocoding results
    geocoding_results = []
    for i in range(record_count):
        city = cities[i % len(cities)]
        address_num = random.randint(100, 999)
        street_names = ["Main St", "Broadway", "Park Ave", "Oak St", "Maple Dr"]
        street = random.choice(street_names)
        
        geocoding_results.append({
            "address": f"{address_num} {street}, {city['name']}",
            "latitude": str(float(city['lat']) + random.uniform(-0.01, 0.01)),
            "longitude": str(float(city['lng']) + random.uniform(-0.01, 0.01)),
            "formatted_address": f"{address_num} {street}, {city['name']}, USA",
            "place_id": f"GEO_{i:04d}"
        })
    
    # Generate reverse geocoding results
    reverse_geocoding_results = []
    for i in range(record_count):
        city = cities[i % len(cities)]
        address_num = random.randint(100, 999)
        street_names = ["Main St", "Broadway", "Park Ave", "Oak St", "Maple Dr"]
        street = random.choice(street_names)
        
        reverse_geocoding_results.append({
            "latitude": str(float(city['lat']) + random.uniform(-0.01, 0.01)),
            "longitude": str(float(city['lng']) + random.uniform(-0.01, 0.01)),
            "formatted_address": f"{address_num} {street}, {city['name']}, USA",
            "address_components": [
                {"long_name": str(address_num), "types": ["street_number"]},
                {"long_name": street, "types": ["route"]},
                {"long_name": city['name'], "types": ["locality", "political"]},
                {"long_name": "USA", "types": ["country", "political"]}
            ]
        })
    
    # Generate places search results
    places_search_results = []
    place_names = [
        "Central Cafe", "Grand Hotel", "City Museum", "Main Park", "Mega Mall",
        "General Hospital", "High School", "Gas Express", "Coffee Corner", "National Bank",
        "Pizza Palace", "Burger Joint", "Sushi Spot", "Italian Bistro", "Mexican Grill"
    ]
    
    for i in range(min(record_count, len(place_names))):
        city = cities[i % len(cities)]
        place_type = place_types[i % len(place_types)]
        
        places_search_results.append({
            "query": f"{place_type} in {city['name']}",
            "results": [{
                "name": place_names[i],
                "place_id": f"PLACE_{i:04d}",
                "formatted_address": f"{random.randint(100, 999)} {random.choice(['Main St', 'Broadway', 'Park Ave'])}, {city['name']}, USA",
                "latitude": str(float(city['lat']) + random.uniform(-0.01, 0.01)),
                "longitude": str(float(city['lng']) + random.uniform(-0.01, 0.01))
            }]
        })
    
    # Generate place details
    place_details = []
    for i in range(min(record_count, len(place_names))):
        place_details.append({
            "place_id": f"PLACE_{i:04d}",
            "name": place_names[i],
            "formatted_address": f"{random.randint(100, 999)} {random.choice(['Main St', 'Broadway', 'Park Ave'])}, {cities[i % len(cities)]['name']}, USA",
            "phone_number": f"+1-555-{random.randint(100, 999):03d}-{random.randint(1000, 9999):04d}",
            "website": f"https://www.{place_names[i].lower().replace(' ', '')}.com",
            "rating": round(random.uniform(3.0, 5.0), 1),
            "opening_hours": {
                "periods": [
                    {"open": {"day": 0, "time": "0900"}, "close": {"day": 0, "time": "1700"}},
                    {"open": {"day": 1, "time": "0900"}, "close": {"day": 1, "time": "1700"}},
                    {"open": {"day": 2, "time": "0900"}, "close": {"day": 2, "time": "1700"}},
                    {"open": {"day": 3, "time": "0900"}, "close": {"day": 3, "time": "1700"}},
                    {"open": {"day": 4, "time": "0900"}, "close": {"day": 4, "time": "1700"}},
                    {"open": {"day": 5, "time": "1000"}, "close": {"day": 5, "time": "1500"}}
                ],
                "weekday_text": [
                    "Monday: 9:00 AM – 5:00 PM",
                    "Tuesday: 9:00 AM – 5:00 PM", 
                    "Wednesday: 9:00 AM – 5:00 PM",
                    "Thursday: 9:00 AM – 5:00 PM",
                    "Friday: 9:00 AM – 5:00 PM",
                    "Saturday: 10:00 AM – 3:00 PM",
                    "Sunday: Closed"
                ]
            }
        })
    
    # Generate distance matrix results
    distance_matrix_results = []
    for i in range(record_count // 2):
        origin_city = cities[i % len(cities)]
        dest_city = cities[(i + 1) % len(cities)]
        
        origins = [f"{origin_city['name']}, USA"]
        destinations = [f"{dest_city['name']}, USA"]
        
        # Calculate approximate distance (simplified)
        lat_diff = abs(float(origin_city['lat']) - float(dest_city['lat']))
        lng_diff = abs(float(origin_city['lng']) - float(dest_city['lng']))
        approx_distance_km = int((lat_diff + lng_diff) * 111)  # Rough conversion
        approx_duration_min = int(approx_distance_km * 1.2)  # Rough estimate
        
        distance_matrix_results.append({
            "origins": origins,
            "destinations": destinations,
            "distances": [f"{approx_distance_km} km"],
            "durations": [f"{approx_duration_min} mins"]
        })
    
    # Generate elevation data
    elevation_data = []
    for i in range(record_count):
        city = cities[i % len(cities)]
        locations = [
            {"lat": float(city['lat']) + random.uniform(-0.1, 0.1), 
             "lng": float(city['lng']) + random.uniform(-0.1, 0.1)}
        ]
        
        # Generate realistic elevations based on city
        base_elevations = {
            "Denver": 1600, "Salt Lake City": 1300, "Phoenix": 300,
            "Los Angeles": 100, "New York": 10, "Chicago": 180
        }
        base_elevation = base_elevations.get(city['name'], random.randint(0, 500))
        
        elevation_data.append({
            "locations": locations,
            "elevations": [base_elevation + random.randint(-50, 50)]
        })
    
    # Generate directions results
    directions_results = []
    travel_modes = ["driving", "walking", "bicycling", "transit"]
    
    for i in range(record_count // 2):
        origin_city = cities[i % len(cities)]
        dest_city = cities[(i + 1) % len(cities)]
        
        lat_diff = abs(float(origin_city['lat']) - float(dest_city['lat']))
        lng_diff = abs(float(origin_city['lng']) - float(dest_city['lng']))
        approx_distance_km = int((lat_diff + lng_diff) * 111)
        approx_duration_min = int(approx_distance_km * 1.2)
        
        directions_results.append({
            "origin": f"{origin_city['name']}, USA",
            "destination": f"{dest_city['name']}, USA",
            "mode": random.choice(travel_modes),
            "steps": [
                {
                    "description": f"Start at {origin_city['name']}",
                    "distance": "0 km"
                },
                {
                    "description": f"Take highway towards {dest_city['name']}",
                    "distance": f"{approx_distance_km // 2} km"
                },
                {
                    "description": f"Arrive at {dest_city['name']}",
                    "distance": f"{approx_distance_km} km"
                }
            ],
            "distance": f"{approx_distance_km} km",
            "duration": f"{approx_duration_min} mins"
        })
    
    return {
        "geocoding_results": geocoding_results,
        "reverse_geocoding_results": reverse_geocoding_results,
        "places_search_results": places_search_results,
        "place_details": place_details,
        "distance_matrix_results": distance_matrix_results,
        "elevation_data": elevation_data,
        "directions_results": directions_results
    }


def update_database(updates: Dict[str, Any], database_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Update the existing database with new data.
    
    This function is for manual follow-up operations; workflow agents will not call it automatically.
    
    Args:
        updates: Dictionary with updates to merge into the database
        database_path: Path to the database JSON file. If None, uses recommended location.
        
    Returns:
        Updated database dictionary
        
    Raises:
        FileNotFoundError: If database file doesn't exist
        ValueError: If updates violate DATA CONTRACT schema
    """
    if database_path is None:
        database_path = "generated/travel_maps/google-maps/google_maps_database.json"
    
    # Check if database exists
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database file not found: {database_path}")
    
    # Load existing database
    with open(database_path, 'r', encoding='utf-8') as f:
        existing_db = json.load(f)
    
    # Validate top-level keys
    expected_keys = {
        "geocoding_results", "reverse_geocoding_results", "places_search_results",
        "place_details", "distance_matrix_results", "elevation_data", "directions_results"
    }
    
    for key in updates:
        if key not in expected_keys:
            raise ValueError(f"Invalid key in updates: {key}. Must be one of {expected_keys}")
    
    # Merge updates (extend lists, update dicts by place_id where applicable)
    for key, new_data in updates.items():
        if key in existing_db:
            if isinstance(existing_db[key], list) and isinstance(new_data, list):
                # For lists, extend with new items
                existing_db[key].extend(new_data)
            elif isinstance(existing_db[key], dict) and isinstance(new_data, dict):
                # For dicts, update recursively
                existing_db[key].update(new_data)
            else:
                # Replace if types don't match
                existing_db[key] = new_data
        else:
            # Add new key
            existing_db[key] = new_data
    
    # Save updated database
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(existing_db, f, indent=2, ensure_ascii=False)
    
    return existing_db


def main():
    """Generate and save the database."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    
    # Generate database with deterministic seed
    database = generate_google_maps_database(seed=42, record_count=20)
    
    # Save to JSON
    database_path = "generated/travel_maps/google-maps/google_maps_database.json"
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"Database generated with {len(database['geocoding_results'])} records per category")
    print(f"Saved to: {database_path}")


if __name__ == "__main__":
    main()