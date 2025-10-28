"""
Korea Tour Database Generator

Generates deterministic synthetic Korean tourism data following the DATA CONTRACT.
Exports to JSON format for use by the Korea Tour Server.

This module creates a comprehensive offline database with:
- Hierarchical area codes for Korean regions
- Tourism information for attractions, festivals, accommodations
- Detailed information for specific content items

All data generation is deterministic when using the same seed parameter.
"""

import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
import sys


class KoreaTourDatabaseGenerator:
    """Generates synthetic Korean tourism data deterministically."""
    
    def __init__(self, seed: int = 42):
        """
        Initialize with seed for deterministic generation.
        
        Args:
            seed: Random seed for reproducible data generation
        """
        self.seed = seed
        self.random = random.Random(seed)
        
        # Korean provinces and major cities
        self.provinces = [
            ("1", "Seoul", "서울특별시"),
            ("2", "Busan", "부산광역시"),
            ("3", "Daegu", "대구광역시"),
            ("4", "Incheon", "인천광역시"),
            ("5", "Gwangju", "광주광역시"),
            ("6", "Daejeon", "대전광역시"),
            ("7", "Ulsan", "울산광역시"),
            ("8", "Gyeonggi", "경기도"),
            ("31", "Gangwon", "강원도"),
            ("32", "Chungbuk", "충청북도"),
            ("33", "Chungnam", "충청남도"),
            ("34", "Jeonbuk", "전라북도"),
            ("35", "Jeonnam", "전라남도"),
            ("36", "Gyeongbuk", "경상북도"),
            ("37", "Gyeongnam", "경상남도"),
            ("39", "Jeju", "제주도")
        ]
        
        # Content type mappings
        self.content_types = {
            "12": "Tourist Attraction",
            "14": "Cultural Facility", 
            "15": "Festival",
            "28": "Leisure Sports",
            "32": "Accommodation",
            "38": "Shopping",
            "39": "Restaurant"
        }

    def generate_area_codes(self) -> List[Dict[str, Any]]:
        """Generate hierarchical area codes for Korean regions."""
        area_codes = []
        
        for area_code, eng_name, kor_name in self.provinces:
            province = {
                "areaCode": area_code,
                "name": kor_name,
                "rnum": int(area_code) if area_code.isdigit() else 0,
                "sub_areas": []
            }
            
            # Generate sub-areas (cities/districts)
            num_sub_areas = self.random.randint(3, 8)
            for i in range(1, num_sub_areas + 1):
                sub_code = f"{area_code}{i:02d}"
                sub_area = {
                    "areaCode": sub_code,
                    "name": f"{kor_name} {i}구",
                    "rnum": int(sub_code)
                }
                province["sub_areas"].append(sub_area)
            
            area_codes.append(province)
        
        return area_codes

    def generate_tour_info(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate tourism information entries."""
        tour_info = []
        
        for i in range(count):
            content_id = f"{i + 100000:06d}"
            content_type = self.random.choice(list(self.content_types.keys()))
            
            # Select appropriate name based on content type
            if content_type == "15":  # Festival
                title = "Korean Festival"
            elif content_type == "32":  # Accommodation
                title = "Hotel Seoul"
            elif content_type == "39":  # Restaurant
                title = "Korean Restaurant"
            else:
                title = "Tourist Attraction"
            
            # Select random area
            province = self.random.choice(self.provinces)
            area_code = province[0]
            sigungu_code = self.random.choice([f"{area_code}{i:02d}" for i in range(1, 9)])
            
            # Generate coordinates around major Korean cities
            base_coords = {
                "1": ("127.024612", "37.532600"),  # Seoul
                "2": ("129.075641", "35.179554"),  # Busan
                "3": ("128.601445", "35.871435"),  # Daegu
                "4": ("126.705150", "37.456256"),  # Incheon
                "39": ("126.531188", "33.489011")  # Jeju
            }
            
            base_x, base_y = base_coords.get(area_code, ("127.024612", "37.532600"))
            mapx = str(float(base_x) + self.random.uniform(-0.1, 0.1))
            mapy = str(float(base_y) + self.random.uniform(-0.05, 0.05))
            
            # Generate timestamps
            base_date = datetime(2023, 1, 1)
            created_time = base_date + timedelta(days=self.random.randint(0, 365))
            modified_time = created_time + timedelta(days=self.random.randint(0, 30))
            
            tour_entry = {
                "contentid": content_id,
                "contenttypeid": content_type,
                "title": title,
                "addr1": f"{province[1]} Address {i+1}",
                "addr2": f"Detail Address {i+1}",
                "mapx": mapx,
                "mapy": mapy,
                "createdtime": created_time.strftime("%Y%m%d%H%M%S"),
                "modifiedtime": modified_time.strftime("%Y%m%d%H%M%S"),
                "tel": f"02-{self.random.randint(1000, 9999)}-{self.random.randint(1000, 9999)}",
                "firstimage": f"https://example.com/images/{content_id}_1.jpg",
                "firstimage2": f"https://example.com/images/{content_id}_2.jpg",
                "areacode": area_code,
                "sigungucode": sigungu_code,
                "cat1": content_type,
                "cat2": f"{content_type}01",
                "cat3": f"{content_type}0101",
                "dist": str(self.random.randint(100, 5000))
            }
            
            tour_info.append(tour_entry)
        
        return tour_info

    def generate_detail_common(self, tour_info: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate detailed information for tour entries."""
        detail_common = []
        
        overviews = [
            "A must-visit landmark showcasing traditional Korean architecture and history.",
            "Popular tourist destination offering beautiful views and cultural experiences.",
            "Modern attraction featuring entertainment, shopping, and dining options.",
            "Cultural heritage site preserving Korea's rich history and traditions.",
            "Vibrant area known for its lively atmosphere and diverse activities.",
            "Scenic location perfect for relaxation and enjoying natural beauty.",
            "Historical site with significant cultural and architectural value."
        ]
        
        for entry in tour_info:
            detail_entry = {
                "contentid": entry["contentid"],
                "contenttypeid": entry["contenttypeid"],
                "title": entry["title"],
                "createdtime": entry["createdtime"],
                "modifiedtime": entry["modifiedtime"],
                "tel": entry["tel"],
                "telname": "Information Desk",
                "homepage": f"https://example.com/{entry['contentid']}",
                "firstimage": entry["firstimage"],
                "firstimage2": entry["firstimage2"],
                "cpyrhtDivCd": "Type1",
                "areacode": entry["areacode"],
                "sigungucode": entry["sigungucode"],
                "cat1": entry["cat1"],
                "cat2": entry["cat2"],
                "cat3": entry["cat3"],
                "addr1": entry["addr1"],
                "addr2": entry["addr2"],
                "zipcode": f"{self.random.randint(10000, 99999)}",
                "mapx": entry["mapx"],
                "mapy": entry["mapy"],
                "mlevel": str(self.random.randint(1, 4)),
                "overview": self.random.choice(overviews)
            }
            
            detail_common.append(detail_entry)
        
        return detail_common

    def generate_database(self, tour_count: int = 50) -> Dict[str, Any]:
        """
        Generate complete database with all required sections.
        
        Args:
            tour_count: Number of tour_info entries to generate
            
        Returns:
            Dictionary containing the generated database
        """
        database = {
            "area_codes": self.generate_area_codes(),
            "tour_info": self.generate_tour_info(tour_count),
            "detail_common": []
        }
        
        # Generate detail_common after tour_info to ensure contentid consistency
        database["detail_common"] = self.generate_detail_common(database["tour_info"])
        
        return database


def generate_korea_tour_database(
    tour_count: int = 50,
    seed: int = 42,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate Korea tour database and optionally save to JSON.
    
    Args:
        tour_count: Number of tour_info entries to generate
        seed: Random seed for deterministic generation
        output_path: Path to save JSON file (optional)
    
    Returns:
        Dictionary containing the generated database
    """
    generator = KoreaTourDatabaseGenerator(seed)
    database = generator.generate_database(tour_count)
    
    if output_path:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        print(f"Database generated and saved to: {output_path}")
    
    return database


def update_database(updates: Dict[str, Any], database_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Update existing database with new data.
    
    This function is for manual follow-up operations; workflow agents will not call it automatically.
    
    Args:
        updates: Dictionary with updates to apply
        database_path: Path to database JSON file (defaults to recommended location)
    
    Returns:
        Updated database dictionary
    
    Raises:
        FileNotFoundError: If database file doesn't exist
        ValueError: If updates violate DATA CONTRACT structure
        JSONDecodeError: If database file contains invalid JSON
    """
    if database_path is None:
        database_path = "generated\\travel_maps\\korea-tour\\korea_tour_database.json"
    
    # Check if database file exists
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database file not found: {database_path}")
    
    try:
        # Load existing database
        with open(database_path, 'r', encoding='utf-8') as f:
            database = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in database file {database_path}: {e}")
    
    # Validate updates against DATA CONTRACT structure
    required_keys = ["area_codes", "tour_info", "detail_common"]
    
    for key in updates:
        if key not in required_keys:
            raise ValueError(f"Invalid key in updates: {key}. Must be one of {required_keys}")
    
    # Apply updates (extend lists, update dictionaries by key)
    for key in required_keys:
        if key in updates:
            if isinstance(database[key], list) and isinstance(updates[key], list):
                # For lists, extend with new items
                database[key].extend(updates[key])
            elif isinstance(database[key], dict) and isinstance(updates[key], dict):
                # For dictionaries, update with new key-value pairs
                database[key].update(updates[key])
            else:
                raise ValueError(f"Type mismatch for key '{key}'. Expected {type(database[key])}, got {type(updates[key])}")
    
    # Save updated database
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"Database updated and saved to: {database_path}")
    return database


if __name__ == "__main__":
    # Generate database when script is run directly
    output_path = "generated\\travel_maps\\korea-tour\\korea_tour_database.json"
    
    # Parse command line arguments
    tour_count = 50
    seed = 42
    
    if len(sys.argv) > 1:
        try:
            tour_count = int(sys.argv[1])
        except ValueError:
            print(f"Invalid tour_count: {sys.argv[1]}, using default: 50")
    
    if len(sys.argv) > 2:
        try:
            seed = int(sys.argv[2])
        except ValueError:
            print(f"Invalid seed: {sys.argv[2]}, using default: 42")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Generate and save database
    database = generate_korea_tour_database(
        tour_count=tour_count, 
        seed=seed, 
        output_path=output_path
    )
    
    print(f"Generated database with:")
    print(f"  - {len(database['area_codes'])} area codes")
    print(f"  - {len(database['tour_info'])} tour info entries")
    print(f"  - {len(database['detail_common'])} detail common entries")