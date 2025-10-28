"""
National Parks Server Database Generator

Generates a deterministic offline database for the National Parks Server.
Supports seeding for reproducible data generation.
"""

import json
import uuid
import random
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


def get_database_path() -> str:
    """Get the database JSON file path relative to this module."""
    module_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(module_dir, "national_parks_server_database.json")


def generate_database(seed: Optional[int] = None, park_count: int = 15) -> Dict[str, Any]:
    """Generate a synthetic national parks database."""
    if seed is not None:
        random.seed(seed)
    
    major_parks = [
        {"name": "Yellowstone", "parkCode": "yell", "states": "WY,MT,ID", "description": "World's first national park with geothermal wonders."},
        {"name": "Yosemite", "parkCode": "yose", "states": "CA", "description": "Famous for giant sequoias and granite cliffs."},
        {"name": "Grand Canyon", "parkCode": "grca", "states": "AZ", "description": "Awe-inspiring canyon carved by Colorado River."},
        {"name": "Great Smoky Mountains", "parkCode": "grsm", "states": "TN,NC", "description": "America's most visited national park."},
        {"name": "Rocky Mountain", "parkCode": "romo", "states": "CO", "description": "Mountain wilderness with alpine lakes."},
        {"name": "Zion", "parkCode": "zion", "states": "UT", "description": "Dramatic desert landscape with sandstone cliffs."},
        {"name": "Acadia", "parkCode": "acad", "states": "ME", "description": "Coastal park with rocky beaches and mountains."},
        {"name": "Olympic", "parkCode": "olym", "states": "WA", "description": "Diverse ecosystems including rainforest."},
        {"name": "Glacier", "parkCode": "glac", "states": "MT", "description": "Crown of the Continent with glaciers."},
        {"name": "Grand Teton", "parkCode": "grte", "states": "WY", "description": "Dramatic mountain range."},
        {"name": "Bryce Canyon", "parkCode": "brca", "states": "UT", "description": "Unique geological structures called hoodoos."},
        {"name": "Arches", "parkCode": "arch", "states": "UT", "description": "World's largest concentration of stone arches."},
        {"name": "Sequoia", "parkCode": "seki", "states": "CA", "description": "Home to giant sequoia trees."},
        {"name": "Joshua Tree", "parkCode": "jotr", "states": "CA", "description": "Desert landscape with Joshua trees."},
        {"name": "Shenandoah", "parkCode": "shen", "states": "VA", "description": "Scenic park along Blue Ridge Mountains."}
    ]
    
    selected_parks = major_parks[:park_count]
    
    database = {
        "parks": generate_parks(selected_parks),
        "park_details": generate_park_details(selected_parks),
        "alerts": generate_alerts(selected_parks),
        "visitor_centers": generate_visitor_centers(selected_parks),
        "campgrounds": generate_campgrounds(selected_parks),
        "events": generate_events(selected_parks)
    }
    
    return database


def generate_parks(parks_data: List[Dict]) -> List[Dict]:
    parks = []
    for park in parks_data:
        parks.append({
            "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"park-{park['parkCode']}")),
            "name": f"{park['name']} National Park",
            "parkCode": park["parkCode"],
            "description": park["description"],
            "states": park["states"],
            "designation": "National Park"
        })
    return parks


def generate_park_details(parks_data: List[Dict]) -> List[Dict]:
    details = []
    activities = ["Hiking", "Camping", "Wildlife Viewing", "Scenic Driving", "Bird Watching", "Fishing", "Photography"]
    
    for park in parks_data:
        details.append({
            "parkCode": park["parkCode"],
            "fullName": f"{park['name']} National Park",
            "description": park["description"],
            "directions": f"Main entrance accessible via highway. Check NPS website for directions.",
            "weather": "Weather varies by season. Check current conditions before visiting.",
            "activities": random.sample(activities, random.randint(3, 5)),
            "entranceFees": [{"cost": "35.00", "description": "Private Vehicle (7-day pass)", "title": "Vehicle Fee"}],
            "operatingHours": [{"description": "Open 24 hours", "standardHours": {"sunday": "All Day", "monday": "All Day", "tuesday": "All Day", "wednesday": "All Day", "thursday": "All Day", "friday": "All Day", "saturday": "All Day"}, "exceptions": []}]
        })
    return details


def generate_alerts(parks_data: List[Dict]) -> List[Dict]:
    alerts = []
    categories = ["Weather", "Roads", "Safety", "Fire"]
    templates = {
        "Weather": ["Severe weather warning", "Winter storm advisory"],
        "Roads": ["Road closure for maintenance", "Construction delays"],
        "Safety": ["Bear activity reported", "Trail closure"],
        "Fire": ["Fire restrictions in effect", "Prescribed burn operations"]
    }
    
    for park in parks_data:
        for i in range(random.randint(1, 3)):
            category = random.choice(categories)
            days_ago = random.randint(0, 30)
            alert_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            
            alerts.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"alert-{park['parkCode']}-{i}")),
                "title": f"{category} Alert - {park['name']}",
                "description": random.choice(templates[category]),
                "category": category,
                "parkCode": park["parkCode"],
                "lastIndexedDate": alert_date
            })
    return alerts


def generate_visitor_centers(parks_data: List[Dict]) -> List[Dict]:
    centers = []
    for park in parks_data:
        for i in range(random.randint(1, 2)):
            centers.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"center-{park['parkCode']}-{i}")),
                "name": f"{park['name']} Visitor Center",
                "description": "Provides park information, maps, and ranger assistance.",
                "parkCode": park["parkCode"],
                "operatingHours": [{"description": "Visitor Center Hours", "standardHours": {"sunday": "9AM-5PM", "monday": "9AM-5PM", "tuesday": "9AM-5PM", "wednesday": "9AM-5PM", "thursday": "9AM-5PM", "friday": "9AM-5PM", "saturday": "9AM-5PM"}, "exceptions": []}]
            })
    return centers


def generate_campgrounds(parks_data: List[Dict]) -> List[Dict]:
    campgrounds = []
    amenities = ["Picnic Tables", "Fire Rings", "Drinking Water", "Restrooms"]
    
    for park in parks_data:
        for i in range(random.randint(1, 3)):
            campgrounds.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"camp-{park['parkCode']}-{i}")),
                "name": f"{park['name']} Campground",
                "description": "Scenic campground with access to park trails.",
                "parkCode": park["parkCode"],
                "amenities": random.sample(amenities, random.randint(2, 4)),
                "reservationInfo": "Reservations available through Recreation.gov."
            })
    return campgrounds


def generate_events(parks_data: List[Dict]) -> List[Dict]:
    events = []
    categories = ["Ranger Program", "Guided Hike", "Evening Program"]
    
    for park in parks_data:
        for i in range(random.randint(2, 4)):
            days_from_now = random.randint(30, 90)
            event_start = (datetime.now() + timedelta(days=days_from_now)).strftime("%Y-%m-%d")
            event_end = (datetime.now() + timedelta(days=days_from_now + 1)).strftime("%Y-%m-%d")
            
            events.append({
                "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"event-{park['parkCode']}-{i}")),
                "title": f"{random.choice(categories)} - {park['name']}",
                "description": "Join park staff for educational programs and activities.",
                "parkCode": park["parkCode"],
                "dateStart": event_start,
                "dateEnd": event_end,
                "category": random.choice(categories)
            })
    return events


def update_database(updates: Dict[str, Any], database_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Update the existing database with new data.
    
    This function is for manual follow-up operations; workflow agents will not call it automatically.
    """
    if database_path is None:
        database_path = get_database_path()
    
    try:
        with open(database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Database file not found at {database_path}")
    
    required_keys = ["parks", "park_details", "alerts", "visitor_centers", "campgrounds", "events"]
    
    for key in updates:
        if key not in required_keys:
            raise ValueError(f"Invalid key '{key}' in updates. Must be one of: {required_keys}")
        if not isinstance(updates[key], list):
            raise ValueError(f"Update for '{key}' must be a list")
    
    for key in updates:
        if key in database:
            database[key].extend(updates[key])
        else:
            database[key] = updates[key]
    
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    return database


if __name__ == "__main__":
    database = generate_database(seed=42)
    
    output_path = get_database_path()
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"Database generated with {len(database['parks'])} parks")
    print(f"  - Park details: {len(database['park_details'])}")
    print(f"  - Alerts: {len(database['alerts'])}")
    print(f"  - Visitor centers: {len(database['visitor_centers'])}")
    print(f"  - Campgrounds: {len(database['campgrounds'])}")
    print(f"  - Events: {len(database['events'])}")
    print(f"Database saved to: {output_path}")