"""
San Francisco Dog Shelter Finder Database Generator

Generates deterministic synthetic data for dog shelters in San Francisco.
Exports data to JSON format following the DATA CONTRACT.
"""

import json
import random
from typing import Dict, List, Any
from pathlib import Path


def generate_dog_shelter_data(seed: int = 42, count: int = 18) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generate synthetic dog shelter data for San Francisco.
    
    Args:
        seed: Random seed for deterministic generation
        count: Number of shelters to generate
        
    Returns:
        Dictionary with 'shelters' key containing list of shelter objects
    """
    random.seed(seed)
    
    # San Francisco neighborhoods with approximate coordinates
    neighborhoods = [
        {"name": "Mission", "lat": 37.7599, "lon": -122.4148},
        {"name": "Pacific Heights", "lat": 37.7877, "lon": -122.4376},
        {"name": "Marina", "lat": 37.8026, "lon": -122.4358},
        {"name": "Noe Valley", "lat": 37.7502, "lon": -122.4337},
        {"name": "Hayes Valley", "lat": 37.7766, "lon": -122.4273},
        {"name": "Castro", "lat": 37.7609, "lon": -122.4350},
        {"name": "Haight-Ashbury", "lat": 37.7699, "lon": -122.4467},
        {"name": "Richmond", "lat": 37.7804, "lon": -122.5102},
        {"name": "Sunset", "lat": 37.7549, "lon": -122.4924},
        {"name": "Bernal Heights", "lat": 37.7441, "lon": -122.4142},
        {"name": "Potrero Hill", "lat": 37.7582, "lon": -122.3966},
        {"name": "Dogpatch", "lat": 37.7597, "lon": -122.3909},
        {"name": "Financial District", "lat": 37.7955, "lon": -122.4007},
        {"name": "North Beach", "lat": 37.8050, "lon": -122.4100},
        {"name": "Russian Hill", "lat": 37.8014, "lon": -122.4186}
    ]
    
    # Available services
    all_services = ["adoption", "boarding", "grooming", "training", "emergency"]
    
    # Shelter name components
    name_prefixes = ["San Francisco", "Bay Area", "Golden Gate", "Pacific", "Mission", "Coastal"]
    name_suffixes = ["Dog Rescue", "Animal Shelter", "Pet Haven", "Canine Center", "Dog Sanctuary", "Paws & Claws"]
    
    shelters = []
    
    for i in range(count):
        # Select neighborhood
        neighborhood_data = random.choice(neighborhoods)
        neighborhood = neighborhood_data["name"]
        base_lat = neighborhood_data["lat"]
        base_lon = neighborhood_data["lon"]
        
        # Generate slight variations in coordinates within neighborhood
        lat = base_lat + random.uniform(-0.005, 0.005)
        lon = base_lon + random.uniform(-0.005, 0.005)
        
        # Generate shelter name
        name = f"{random.choice(name_prefixes)} {random.choice(name_suffixes)}"
        
        # Generate address
        street_numbers = ["123", "456", "789", "101", "202", "303", "404", "505"]
        street_names = ["Mission St", "Market St", "Van Ness Ave", "Geary Blvd", "Fulton St", "California St", "Clement St"]
        address = f"{random.choice(street_numbers)} {random.choice(street_names)}"
        
        # Generate hours
        hour_variations = [
            "Mon-Fri 9am-6pm, Sat-Sun 10am-4pm",
            "Mon-Sat 8am-7pm, Sun 9am-5pm", 
            "Daily 7am-8pm",
            "Mon-Fri 10am-8pm, Sat-Sun 9am-6pm",
            "24/7 Emergency Services, Regular hours: Mon-Fri 9am-5pm"
        ]
        hours = random.choice(hour_variations)
        
        # Generate phone
        phone_prefix = "(415) "
        phone_suffix = f"{random.randint(200, 999)}-{random.randint(1000, 9999)}"
        phone = phone_prefix + phone_suffix
        
        # Generate website
        website_name = name.lower().replace(" ", "-").replace("&", "and")
        website = f"https://{website_name}.org"
        
        # Generate services (2-4 services per shelter)
        num_services = random.randint(2, 4)
        services = random.sample(all_services, num_services)
        
        # Generate capacity and occupancy
        capacity = random.choice([20, 30, 40, 50, 60, 75, 100])
        occupancy_rate = random.uniform(0.3, 0.95)  # 30% to 95% occupied
        current_occupancy = int(capacity * occupancy_rate)
        
        shelter = {
            "id": f"shelter_{i+1:03d}",
            "name": name,
            "address": address,
            "neighborhood": neighborhood,
            "hours": hours,
            "phone": phone,
            "website": website,
            "services": services,
            "capacity": capacity,
            "current_occupancy": current_occupancy,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6)
        }
        
        shelters.append(shelter)
    
    return {"shelters": shelters}


def write_database_json(data: Dict[str, List[Dict[str, Any]]], output_path: str) -> None:
    """
    Write database data to JSON file.
    
    Args:
        data: Database data dictionary
        output_path: Path to write JSON file
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Database written to {output_path}")


def main(seed: int = 42, count: int = 18) -> None:
    """
    Main function to generate and write database.
    
    Args:
        seed: Random seed for deterministic generation
        count: Number of shelters to generate
    """
    # Generate data
    data = generate_dog_shelter_data(seed=seed, count=count)
    
    # Write to JSON
    output_path = Path(__file__).parent / "san_francisco_dog_shelter_finder_database.json"
    write_database_json(data, str(output_path))
    
    print(f"Generated {len(data['shelters'])} dog shelters with seed {seed}")


if __name__ == "__main__":
    # Generate database when run directly
    main()