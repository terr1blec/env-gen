"""
Offline database generator for flight and stay search server.

This module generates deterministic mock data for flights, offers, stays, and reviews
following the DATA CONTRACT schema. The data is designed to be realistic and useful
for testing the flight and stay search functionality.
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path


def generate_database(counts: Dict[str, int] = None, seed: int = 42) -> Dict[str, Any]:
    """
    Generate a deterministic offline database with flights, offers, stays, and reviews.
    
    Args:
        counts: Dictionary specifying counts for each data type
                Default: {"flights": 50, "offers": 100, "stays": 30, "reviews": 200}
        seed: Random seed for deterministic generation
    
    Returns:
        Database dictionary matching the DATA CONTRACT schema
    """
    if counts is None:
        counts = {"flights": 50, "offers": 100, "stays": 30, "reviews": 200}
    
    random.seed(seed)
    
    # Common data for realistic generation
    airports = [
        ("JFK", "New York"), ("LAX", "Los Angeles"), ("ORD", "Chicago"), 
        ("DFW", "Dallas"), ("DEN", "Denver"), ("SFO", "San Francisco"),
        ("SEA", "Seattle"), ("MIA", "Miami"), ("ATL", "Atlanta"),
        ("LHR", "London"), ("CDG", "Paris"), ("FRA", "Frankfurt"),
        ("DXB", "Dubai"), ("SIN", "Singapore"), ("NRT", "Tokyo")
    ]
    
    airlines = ["Delta", "United", "American", "Southwest", "JetBlue", "British Airways", 
                "Air France", "Lufthansa", "Emirates", "Singapore Airlines"]
    
    cabin_classes = ["economy", "premium_economy", "business", "first"]
    
    hotel_names = [
        "Grand Plaza Hotel", "Seaside Resort", "City Center Inn", "Mountain View Lodge",
        "Business Tower Hotel", "Luxury Suites", "Budget Stay Inn", "Heritage Hotel",
        "Modern Lofts", "Garden Retreat", "Executive Residence", "Boutique Hotel",
        "Airport Transit Hotel", "Downtown Palace", "Riverside Lodge"
    ]
    
    review_comments = [
        "Great stay, would recommend!", "Comfortable rooms and friendly staff.",
        "Perfect location for exploring the city.", "Clean and modern facilities.",
        "Excellent service throughout our stay.", "Good value for money.",
        "Beautiful views from the room.", "Convenient location near attractions.",
        "Breakfast was delicious.", "Rooms were spacious and clean.",
        "Helpful concierge service.", "Peaceful and quiet atmosphere.",
        "Modern amenities and comfortable beds.", "Great for business travelers.",
        "Family-friendly with good facilities."
    ]
    
    # Generate flights
    flights = []
    for i in range(counts["flights"]):
        origin_airport = random.choice(airports)
        destination_airport = random.choice([a for a in airports if a != origin_airport])
        
        departure_date = (datetime.now() + timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")
        
        # Generate flight segments
        max_segments = random.randint(1, 3)
        segments = []
        current_origin = origin_airport[0]
        
        for seg_num in range(max_segments):
            if seg_num == max_segments - 1:
                # Last segment goes to final destination
                segment_dest = destination_airport[0]
            else:
                # Intermediate segment
                possible_dests = [a[0] for a in airports if a[0] != current_origin and a[0] != destination_airport[0]]
                segment_dest = random.choice(possible_dests)
            
            segment = {
                "id": str(uuid.uuid4()),
                "origin": current_origin,
                "destination": segment_dest,
                "departure_time": f"{random.randint(6, 22):02d}:{random.randint(0, 59):02d}",
                "arrival_time": f"{random.randint(6, 22):02d}:{random.randint(0, 59):02d}",
                "duration_minutes": random.randint(60, 480),
                "airline": random.choice(airlines),
                "flight_number": f"{random.choice(airlines)[:2].upper()}{random.randint(100, 999)}"
            }
            segments.append(segment)
            current_origin = segment_dest
        
        flight = {
            "id": f"flt_{i+1:03d}",
            "origin": origin_airport[0],
            "destination": destination_airport[0],
            "departure_date": departure_date,
            "airline": random.choice(airlines),
            "price": round(random.uniform(150, 1500), 2),
            "cabin_class": random.choice(cabin_classes),
            "max_connections": max_segments - 1,
            "segments": segments
        }
        flights.append(flight)
    
    # Generate offers
    offers = []
    for i in range(counts["offers"]):
        flight = random.choice(flights)
        offer = {
            "id": f"off_{i+1:03d}",
            "flight_id": flight["id"],
            "price": round(flight["price"] * random.uniform(0.8, 1.2), 2),  # Slight variation from flight price
            "cabin_class": flight["cabin_class"],
            "airline": flight["airline"],
            "details": {
                "baggage_allowance": f"{random.randint(1, 3)} checked bags",
                "refundable": random.choice([True, False]),
                "seat_selection": random.choice(["Free", "Paid", "At check-in"]),
                "meal_service": random.choice(["Included", "Available for purchase", "None"])
            }
        }
        offers.append(offer)
    
    # Generate stays
    stays = []
    locations = ["New York", "Los Angeles", "Chicago", "Miami", "San Francisco", 
                 "London", "Paris", "Tokyo", "Dubai", "Singapore"]
    
    for i in range(counts["stays"]):
        location = random.choice(locations)
        check_in_date = (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
        check_out_date = (datetime.strptime(check_in_date, "%Y-%m-%d") + timedelta(days=random.randint(2, 14))).strftime("%Y-%m-%d")
        
        # Generate realistic coordinates based on location
        if location == "New York":
            lat, lon = 40.7128, -74.0060
        elif location == "Los Angeles":
            lat, lon = 34.0522, -118.2437
        elif location == "Chicago":
            lat, lon = 41.8781, -87.6298
        elif location == "Miami":
            lat, lon = 25.7617, -80.1918
        elif location == "San Francisco":
            lat, lon = 37.7749, -122.4194
        elif location == "London":
            lat, lon = 51.5074, -0.1278
        elif location == "Paris":
            lat, lon = 48.8566, 2.3522
        elif location == "Tokyo":
            lat, lon = 35.6762, 139.6503
        elif location == "Dubai":
            lat, lon = 25.2048, 55.2708
        else:  # Singapore
            lat, lon = 1.3521, 103.8198
        
        # Add some random variation to coordinates
        lat += random.uniform(-0.1, 0.1)
        lon += random.uniform(-0.1, 0.1)
        
        stay = {
            "id": f"stay_{i+1:03d}",
            "name": random.choice(hotel_names),
            "location": location,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "price_per_night": round(random.uniform(80, 500), 2),
            "guests": random.randint(1, 6),
            "check_in_date": check_in_date,
            "check_out_date": check_out_date
        }
        stays.append(stay)
    
    # Generate reviews
    reviews = []
    for i in range(counts["reviews"]):
        stay = random.choice(stays)
        review_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
        
        review = {
            "id": f"rev_{i+1:03d}",
            "stay_id": stay["id"],
            "rating": round(random.uniform(3.0, 5.0), 1),
            "comment": random.choice(review_comments),
            "date": review_date
        }
        reviews.append(review)
    
    return {
        "flights": flights,
        "offers": offers,
        "stays": stays,
        "reviews": reviews
    }


def update_database(updates: Dict[str, Any], database_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Update the existing database with new data.
    
    This function is for manual follow-up operations; workflow agents will not call it automatically.
    
    Args:
        updates: Dictionary containing updates to merge into the database
        database_path: Path to the database JSON file. If None, uses the recommended location.
    
    Returns:
        Updated database dictionary
    
    Raises:
        FileNotFoundError: If the database file doesn't exist
        ValueError: If updates are incompatible with the DATA CONTRACT
    """
    if database_path is None:
        database_path = "generated\\travel_maps\\flight--stay-search-server-duffel-api\\flight__stay_search_server_duffel_api_database.json"
    
    # Load existing database
    try:
        with open(database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Database file not found at {database_path}")
    
    # Validate updates against DATA CONTRACT
    required_keys = {"flights", "offers", "stays", "reviews"}
    if not all(key in updates for key in required_keys):
        raise ValueError("Updates must contain all required keys: flights, offers, stays, reviews")
    
    # Merge updates (extend lists)
    for key in required_keys:
        if key in updates:
            if not isinstance(updates[key], list):
                raise ValueError(f"{key} must be a list")
            if key in database:
                database[key].extend(updates[key])
            else:
                database[key] = updates[key]
    
    # Save updated database
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2)
    
    return database


def main():
    """Generate and save the database to the recommended location."""
    database = generate_database()
    
    # Ensure directory exists
    Path("generated\\travel_maps\\flight--stay-search-server-duffel-api").mkdir(parents=True, exist_ok=True)
    
    # Save database
    database_path = "generated\\travel_maps\\flight--stay-search-server-duffel-api\\flight__stay_search_server_duffel_api_database.json"
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2)
    
    print(f"Database generated with:")
    print(f"  - {len(database['flights'])} flights")
    print(f"  - {len(database['offers'])} offers")
    print(f"  - {len(database['stays'])} stays")
    print(f"  - {len(database['reviews'])} reviews")
    print(f"Saved to: {database_path}")


if __name__ == "__main__":
    main()