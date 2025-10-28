"""
Kakao Navigation Database Generator

Generates deterministic synthetic data for Kakao Navigation offline database.
Follows the DATA CONTRACT schema for addresses, directions, future directions,
and multi-destination directions.
"""

import json
import random
from typing import Dict, Any, Optional, List
from pathlib import Path


def generate_database(seed: Optional[int] = None) -> Dict[str, Any]:
    """
    Generate the complete offline database for Kakao Navigation.
    
    Args:
        seed: Optional random seed for deterministic generation
        
    Returns:
        Dictionary containing all database sections per DATA CONTRACT
    """
    if seed is not None:
        random.seed(seed)
    
    # Generate addresses (Korean landmarks and locations)
    addresses = generate_addresses()
    
    # Generate directions between addresses
    directions = generate_directions(addresses)
    
    # Generate future directions with traffic predictions
    future_directions = generate_future_directions(addresses)
    
    # Generate multi-destination directions
    multi_destination_directions = generate_multi_destination_directions(addresses)
    
    return {
        "addresses": addresses,
        "directions": directions,
        "future_directions": future_directions,
        "multi_destination_directions": multi_destination_directions
    }


def generate_addresses() -> List[Dict[str, Any]]:
    """Generate Korean addresses with coordinates."""
    return [
        {
            "placeName": "강남역",
            "address": "서울특별시 강남구 강남대로 396",
            "coordinates": {"latitude": 37.4979, "longitude": 127.0276}
        },
        {
            "placeName": "홍대입구역",
            "address": "서울특별시 마포구 양화로 160",
            "coordinates": {"latitude": 37.5572, "longitude": 126.9254}
        },
        {
            "placeName": "명동",
            "address": "서울특별시 중구 명동길 14",
            "coordinates": {"latitude": 37.5637, "longitude": 126.9826}
        },
        {
            "placeName": "동대문디자인플라자",
            "address": "서울특별시 중구 을지로 281",
            "coordinates": {"latitude": 37.5665, "longitude": 127.0097}
        },
        {
            "placeName": "여의도한강공원",
            "address": "서울특별시 영등포구 여의동로 330",
            "coordinates": {"latitude": 37.5265, "longitude": 126.9329}
        },
        {
            "placeName": "롯데월드타워",
            "address": "서울특별시 송파구 올림픽로 300",
            "coordinates": {"latitude": 37.5125, "longitude": 127.1025}
        },
        {
            "placeName": "경복궁",
            "address": "서울특별시 종로구 사직로 161",
            "coordinates": {"latitude": 37.5796, "longitude": 126.9770}
        },
        {
            "placeName": "N서울타워",
            "address": "서울특별시 용산구 남산공원길 105",
            "coordinates": {"latitude": 37.5512, "longitude": 126.9882}
        },
        {
            "placeName": "코엑스",
            "address": "서울특별시 강남구 영동대로 513",
            "coordinates": {"latitude": 37.5121, "longitude": 127.0592}
        },
        {
            "placeName": "광화문광장",
            "address": "서울특별시 종로구 세종대로 172",
            "coordinates": {"latitude": 37.5725, "longitude": 126.9769}
        }
    ]


def generate_directions(addresses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate direction routes between addresses."""
    route_pairs = [
        (0, 1),  # 강남역 -> 홍대입구역
        (1, 2),  # 홍대입구역 -> 명동
        (2, 3),  # 명동 -> 동대문디자인플라자
        (3, 4),  # 동대문디자인플라자 -> 여의도한강공원
        (4, 5),  # 여의도한강공원 -> 롯데월드타워
        (5, 6),  # 롯데월드타워 -> 경복궁
        (6, 7),  # 경복궁 -> N서울타워
        (7, 8)   # N서울타워 -> 코엑스
    ]
    
    directions = []
    for start_idx, end_idx in route_pairs:
        start_addr = addresses[start_idx]
        end_addr = addresses[end_idx]
        
        # Calculate approximate distance and duration
        lat_diff = abs(start_addr["coordinates"]["latitude"] - end_addr["coordinates"]["latitude"])
        lon_diff = abs(start_addr["coordinates"]["longitude"] - end_addr["coordinates"]["longitude"])
        base_distance = (lat_diff + lon_diff) * 111  # Rough km conversion
        distance_km = round(base_distance + random.uniform(2, 8), 1)
        duration_min = int(distance_km * 3 + random.uniform(5, 15))
        
        directions.append({
            "start_coords": start_addr["coordinates"],
            "end_coords": end_addr["coordinates"],
            "start_address": start_addr["address"],
            "end_address": end_addr["address"],
            "distance": f"{distance_km} km",
            "duration": f"{duration_min} min",
            "route_details": f"{start_addr['placeName']}에서 {end_addr['placeName']}까지 최적 경로. 주요 도로 이용, {random.choice(['교통량 적음', '보통 교통', '일부 정체 구간'])}."
        })
    
    return directions


def generate_future_directions(addresses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate future directions with traffic predictions."""
    future_pairs = [
        (0, 2, "2024-03-15 08:30"),  # 강남역 -> 명동 (출근 시간)
        (1, 3, "2024-03-15 18:00"),  # 홍대입구역 -> 동대문디자인플라자 (퇴근 시간)
        (4, 6, "2024-03-16 10:00"),  # 여의도한강공원 -> 경복궁 (주말 오전)
        (5, 7, "2024-03-16 14:00"),  # 롯데월드타워 -> N서울타워 (주말 오후)
        (8, 9, "2024-03-17 12:00"),  # 코엑스 -> 광화문광장 (점심 시간)
        (9, 0, "2024-03-17 20:00")   # 광화문광장 -> 강남역 (저녁 시간)
    ]
    
    future_directions = []
    for start_idx, end_idx, departure_time in future_pairs:
        start_addr = addresses[start_idx]
        end_addr = addresses[end_idx]
        
        # Calculate approximate distance and duration with traffic factors
        lat_diff = abs(start_addr["coordinates"]["latitude"] - end_addr["coordinates"]["latitude"])
        lon_diff = abs(start_addr["coordinates"]["longitude"] - end_addr["coordinates"]["longitude"])
        base_distance = (lat_diff + lon_diff) * 111
        distance_km = round(base_distance + random.uniform(2, 8), 1)
        
        # Base duration with traffic multiplier
        base_duration = distance_km * 3
        
        # Traffic prediction based on time of day
        if "08:30" in departure_time:
            traffic_multiplier = 1.8  # Rush hour morning
            traffic_prediction = "출근 시간 대로 정체 예상"
        elif "18:00" in departure_time:
            traffic_multiplier = 1.6  # Rush hour evening
            traffic_prediction = "퇴근 시간 정체 구간 있음"
        elif "14:00" in departure_time:
            traffic_multiplier = 1.3  # Weekend afternoon
            traffic_prediction = "주말 오후 보통 교통"
        else:
            traffic_multiplier = 1.1  # Normal traffic
            traffic_prediction = "교통량 원활 예상"
            
        duration_min = int(base_duration * traffic_multiplier + random.uniform(5, 10))
        
        future_directions.append({
            "start_coords": start_addr["coordinates"],
            "end_coords": end_addr["coordinates"],
            "departure_time": departure_time,
            "distance": f"{distance_km} km",
            "duration": f"{duration_min} min",
            "traffic_prediction": traffic_prediction
        })
    
    return future_directions


def generate_multi_destination_directions(addresses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate multi-destination direction routes."""
    multi_routes = [
        {
            "start_idx": 0,  # 강남역
            "dest_indices": [2, 4, 6],  # 명동, 여의도한강공원, 경복궁
            "summary": "관광 명소 순회 코스"
        },
        {
            "start_idx": 1,  # 홍대입구역
            "dest_indices": [3, 5, 8],  # 동대문디자인플라자, 롯데월드타워, 코엑스
            "summary": "쇼핑 및 엔터테인먼트 투어"
        },
        {
            "start_idx": 4,  # 여의도한강공원
            "dest_indices": [7, 9, 0],  # N서울타워, 광화문광장, 강남역
            "summary": "서울 야경 명소 순회"
        },
        {
            "start_idx": 8,  # 코엑스
            "dest_indices": [1, 3, 5],  # 홍대입구역, 동대문디자인플라자, 롯데월드타워
            "summary": "대형 쇼핑몰 투어"
        }
    ]
    
    multi_destination_directions = []
    for route in multi_routes:
        start_addr = addresses[route["start_idx"]]
        destinations = []
        
        total_distance = 0
        total_duration = 0
        
        for dest_idx in route["dest_indices"]:
            dest_addr = addresses[dest_idx]
            
            # Calculate segment distance
            if destinations:
                prev_coords = destinations[-1]["coordinates"]
            else:
                prev_coords = start_addr["coordinates"]
                
            lat_diff = abs(prev_coords["latitude"] - dest_addr["coordinates"]["latitude"])
            lon_diff = abs(prev_coords["longitude"] - dest_addr["coordinates"]["longitude"])
            segment_distance = (lat_diff + lon_diff) * 111
            
            total_distance += segment_distance
            total_duration += segment_distance * 3 + random.uniform(5, 10)
            
            destinations.append({
                "coordinates": dest_addr["coordinates"],
                "address": dest_addr["address"]
            })
        
        multi_destination_directions.append({
            "start_coords": start_addr["coordinates"],
            "destinations": destinations,
            "summary": route["summary"],
            "total_distance": f"{round(total_distance, 1)} km",
            "total_duration": f"{int(total_duration)} min"
        })
    
    return multi_destination_directions


def update_database(updates: Dict[str, Any], database_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Update the existing database with new data.
    
    This function is for manual follow-up operations; workflow agents will not call it automatically.
    
    Args:
        updates: Dictionary containing updates to merge into the database
        database_path: Path to the database JSON file. If None, uses recommended location.
        
    Returns:
        Updated database dictionary
        
    Raises:
        FileNotFoundError: If database file doesn't exist
        ValueError: If updates violate DATA CONTRACT structure
    """
    if database_path is None:
        database_path = "generated\\travel_maps\\kakao-navigation\\kakao_navigation_database.json"
    
    # Load existing database
    try:
        with open(database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Database file not found at {database_path}")
    
    # Validate updates structure
    required_keys = ["addresses", "directions", "future_directions", "multi_destination_directions"]
    for key in updates:
        if key not in required_keys:
            raise ValueError(f"Invalid key '{key}' in updates. Must be one of: {required_keys}")
    
    # Merge updates (extend arrays, update dictionaries)
    for key in required_keys:
        if key in updates:
            if isinstance(database[key], list) and isinstance(updates[key], list):
                database[key].extend(updates[key])
            elif isinstance(database[key], dict) and isinstance(updates[key], dict):
                database[key].update(updates[key])
            else:
                raise ValueError(f"Type mismatch for key '{key}'. Expected {type(database[key])}, got {type(updates[key])}")
    
    # Save updated database
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    return database


def main():
    """Generate and save the database."""
    # Generate database with deterministic seed
    database = generate_database(seed=42)
    
    # Ensure output directory exists
    output_dir = Path("generated\\travel_maps\\kakao-navigation")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save to JSON file
    output_path = output_dir / "kakao_navigation_database.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"Database generated successfully at: {output_path}")
    print(f"Addresses: {len(database['addresses'])}")
    print(f"Directions: {len(database['directions'])}")
    print(f"Future Directions: {len(database['future_directions'])}")
    print(f"Multi-destination Directions: {len(database['multi_destination_directions'])}")


if __name__ == "__main__":
    main()