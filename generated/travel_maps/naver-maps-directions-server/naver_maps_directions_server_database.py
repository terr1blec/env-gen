"""
Naver Maps Directions Server Database Generator

Generates deterministic synthetic data for Naver Maps Directions API simulation.
Includes directions, geocoding, reverse geocoding, and static map data.
"""

import json
import random
import base64
from typing import Dict, Any, Optional, List
from pathlib import Path


def generate_database(seed: Optional[int] = None, counts: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    """
    Generate a deterministic offline database for Naver Maps Directions Server.
    
    Args:
        seed: Random seed for deterministic generation
        counts: Dictionary specifying record counts for each collection
               (directions, geocoding, reverse_geocoding, static_maps)
    
    Returns:
        Database dictionary matching the DATA CONTRACT schema
    """
    if seed is not None:
        random.seed(seed)
    
    # Default counts if not provided
    default_counts = {
        "directions": 20,
        "geocoding": 15,
        "reverse_geocoding": 15,
        "static_maps": 10
    }
    
    if counts:
        default_counts.update(counts)
    counts = default_counts
    
    # Korean locations and addresses
    korean_locations = [
        {"name": "Gangnam Station", "address": "서울특별시 강남구 강남대로 396", "lat": "37.4979", "lng": "127.0276"},
        {"name": "Myeongdong", "address": "서울특별시 중구 명동길 14", "lat": "37.5637", "lng": "126.9826"},
        {"name": "Hongdae", "address": "서울특별시 마포구 홍익로 5", "lat": "37.5569", "lng": "126.9239"},
        {"name": "Itaewon", "address": "서울특별시 용산구 이태원로 177", "lat": "37.5345", "lng": "126.9946"},
        {"name": "Jamsil Lotte World", "address": "서울특별시 송파구 올림픽로 240", "lat": "37.5111", "lng": "127.0982"},
        {"name": "Gwanghwamun", "address": "서울특별시 종로구 세종대로 172", "lat": "37.5760", "lng": "126.9768"},
        {"name": "Dongdaemun", "address": "서울특별시 종로구 종로 266", "lat": "37.5712", "lng": "127.0098"},
        {"name": "COEX Mall", "address": "서울특별시 강남구 영동대로 513", "lat": "37.5125", "lng": "127.0587"},
        {"name": "Namsan Tower", "address": "서울특별시 용산구 남산공원길 105", "lat": "37.5512", "lng": "126.9882"},
        {"name": "Incheon Airport", "address": "인천광역시 중구 공항로 272", "lat": "37.4602", "lng": "126.4407"},
        {"name": "Busan Station", "address": "부산광역시 동구 중앙대로 206", "lat": "35.1145", "lng": "129.0413"},
        {"name": "Gyeongbokgung Palace", "address": "서울특별시 종로구 사직로 161", "lat": "37.5796", "lng": "126.9770"},
        {"name": "Lotte Tower", "address": "서울특별시 송파구 올림픽로 300", "lat": "37.5121", "lng": "127.1021"},
        {"name": "Yeouido Park", "address": "서울특별시 영등포구 여의동로 330", "lat": "37.5217", "lng": "126.9242"},
        {"name": "Insadong", "address": "서울특별시 종로구 인사동길 62", "lat": "37.5736", "lng": "126.9864"},
    ]
    
    # Generate directions data
    directions = []
    for i in range(counts["directions"]):
        start_idx = i % len(korean_locations)
        goal_idx = (i + 1) % len(korean_locations)
        
        start_loc = korean_locations[start_idx]
        goal_loc = korean_locations[goal_idx]
        
        # Calculate approximate distance and duration
        lat_diff = abs(float(start_loc["lat"]) - float(goal_loc["lat"]))
        lng_diff = abs(float(start_loc["lng"]) - float(goal_loc["lng"]))
        distance_km = round((lat_diff + lng_diff) * 111, 1)  # Rough conversion
        duration_min = int(distance_km * 2 + random.randint(5, 20))
        
        directions.append({
            "id": f"dir_{i+1:03d}",
            "goal": goal_loc["name"],
            "start": start_loc["name"],
            "option": random.choice(["fastest", "shortest", "recommended", "avoid_tolls", None]),
            "waypoints": random.choice([None, f"{korean_locations[(i+2) % len(korean_locations)]['name']}"]),
            "route_info": {
                "distance": f"{distance_km} km",
                "duration": f"{duration_min}분",
                "steps": [
                    f"{start_loc['name']}에서 출발",
                    f"주요 도로로 진입",
                    f"{goal_loc['name']} 방향으로 진행",
                    f"{goal_loc['name']} 도착"
                ]
            }
        })
    
    # Generate geocoding data
    geocoding = []
    for i, loc in enumerate(korean_locations[:counts["geocoding"]]):
        geocoding.append({
            "id": f"geo_{i+1:03d}",
            "address": loc["address"],
            "coordinates": {
                "lat": loc["lat"],
                "lng": loc["lng"]
            }
        })
    
    # Generate reverse geocoding data
    reverse_geocoding = []
    for i, loc in enumerate(korean_locations[:counts["reverse_geocoding"]]):
        reverse_geocoding.append({
            "id": f"rev_{i+1:03d}",
            "lat": loc["lat"],
            "lng": loc["lng"],
            "address": loc["address"]
        })
    
    # Generate static maps data
    # Create simple placeholder base64 images (small 10x10 red PNG)
    placeholder_image = base64.b64encode(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\n\x00\x00\x00\n\x08\x02\x00\x00\x00\x02PX\xea\x00\x00\x00\x16IDATx\x9cc\xf8\x0f\x04\x0c\x0c\x0c\x0c\x8c\x8c\x8c\x8c\x8c\x8c\x8c\x8c\x00\x00\x00\x00IEND\xaeB`\x82').decode('utf-8')
    
    static_maps = []
    for i, loc in enumerate(korean_locations[:counts["static_maps"]]):
        static_maps.append({
            "id": f"map_{i+1:03d}",
            "center": f"{loc['lat']},{loc['lng']}",
            "h": random.choice(["300", "400", "500", None]),
            "w": random.choice(["400", "500", "600", None]),
            "level": random.choice(["10", "12", "14", None]),
            "format": random.choice(["png", "jpg", None]),
            "image_data": placeholder_image
        })
    
    return {
        "directions": directions,
        "geocoding": geocoding,
        "reverse_geocoding": reverse_geocoding,
        "static_maps": static_maps
    }


def update_database(updates: Dict[str, Any], database_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Update the existing database with new data.
    
    This function is for manual follow-up operations; workflow agents will not call it automatically.
    
    Args:
        updates: Dictionary with updates to merge into the database
        database_path: Path to the database JSON file. If None, uses recommended location
    
    Returns:
        Updated database dictionary
    
    Raises:
        FileNotFoundError: If database file doesn't exist
        ValueError: If updates violate DATA CONTRACT schema
    """
    if database_path is None:
        database_path = "generated\\travel_maps\\naver-maps-directions-server\\naver_maps_directions_server_database.json"
    
    # Load existing database
    if not Path(database_path).exists():
        raise FileNotFoundError(f"Database file not found: {database_path}")
    
    with open(database_path, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    # Validate updates against DATA CONTRACT
    required_keys = {"directions", "geocoding", "reverse_geocoding", "static_maps"}
    update_keys = set(updates.keys())
    
    if not update_keys.issubset(required_keys):
        invalid_keys = update_keys - required_keys
        raise ValueError(f"Invalid update keys: {invalid_keys}. Must be one of: {required_keys}")
    
    # Merge updates (extend arrays, update dictionaries by key)
    for key in update_keys:
        if key not in database:
            database[key] = []
        
        if isinstance(updates[key], list):
            # For arrays, extend the existing list
            database[key].extend(updates[key])
        elif isinstance(updates[key], dict):
            # For dictionaries, update by merging
            database[key].update(updates[key])
        else:
            raise ValueError(f"Invalid update type for {key}: {type(updates[key])}")
    
    # Save updated database
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    return database


def main():
    """Generate and save the database to the recommended location."""
    # Ensure output directory exists
    Path("generated\\travel_maps\\naver-maps-directions-server").mkdir(parents=True, exist_ok=True)
    
    # Generate database with deterministic seed
    database = generate_database(seed=42)
    
    # Save to JSON file
    database_path = "generated\\travel_maps\\naver-maps-directions-server\\naver_maps_directions_server_database.json"
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"Database generated with:")
    print(f"  - {len(database['directions'])} directions")
    print(f"  - {len(database['geocoding'])} geocoding records")
    print(f"  - {len(database['reverse_geocoding'])} reverse geocoding records")
    print(f"  - {len(database['static_maps'])} static maps")
    print(f"Saved to: {database_path}")


if __name__ == "__main__":
    main()