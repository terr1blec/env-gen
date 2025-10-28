"""
China Railway MCP - Offline Database Generator

This module generates deterministic synthetic train ticket data for China Railway (12306)
following the DATA CONTRACT structure.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path


class ChinaRailwayDatabaseGenerator:
    """Generator for China Railway train ticket data."""
    
    def __init__(self, seed: int = 42):
        """Initialize generator with optional seed for deterministic output."""
        self.random = random.Random(seed)
        
        # Major Chinese railway stations
        self.stations = [
            "北京", "上海", "广州", "深圳", "杭州", 
            "南京", "武汉", "西安", "成都", "重庆"
        ]
        
        # Station coordinates for distance calculation (approximate)
        self.station_coords = {
            "北京": (39.9042, 116.4074),
            "上海": (31.2304, 121.4737),
            "广州": (23.1291, 113.2644),
            "深圳": (22.5431, 114.0579),
            "杭州": (30.2741, 120.1551),
            "南京": (32.0603, 118.7969),
            "武汉": (30.5928, 114.3055),
            "西安": (34.3416, 108.9398),
            "成都": (30.5728, 104.0668),
            "重庆": (29.5630, 106.5516)
        }
        
        # Train prefixes and their characteristics
        self.train_types = {
            "G": {"name": "高铁", "speed": "High-speed", "base_price_multiplier": 1.5},
            "D": {"name": "动车", "speed": "Bullet", "base_price_multiplier": 1.3},
            "C": {"name": "城际", "speed": "Intercity", "base_price_multiplier": 1.2},
            "Z": {"name": "直达", "speed": "Direct Express", "base_price_multiplier": 1.0},
            "T": {"name": "特快", "speed": "Express", "base_price_multiplier": 0.8},
            "K": {"name": "快速", "speed": "Fast", "base_price_multiplier": 0.6}
        }
        
        # Seat types
        self.seat_types = ["business_class", "first_class", "second_class", "soft_sleeper", "hard_sleeper", "hard_seat"]
        
        # Base prices per km for different seat types
        self.base_prices_per_km = {
            "business_class": 0.8,
            "first_class": 0.6,
            "second_class": 0.4,
            "soft_sleeper": 0.3,
            "hard_sleeper": 0.2,
            "hard_seat": 0.1
        }
    
    def calculate_distance(self, station1: str, station2: str) -> float:
        """Calculate approximate distance between two stations in km."""
        if station1 not in self.station_coords or station2 not in self.station_coords:
            return 500  # Default distance
        
        lat1, lon1 = self.station_coords[station1]
        lat2, lon2 = self.station_coords[station2]
        
        # Simple distance calculation (approximate)
        return ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5 * 111  # Rough km conversion
    
    def generate_train_number(self, train_type: str) -> str:
        """Generate realistic train number."""
        number = self.random.randint(1, 9999)
        return f"{train_type}{number:04d}"
    
    def generate_time(self, base_hour: int, variation: int = 2) -> str:
        """Generate departure/arrival time."""
        hour = (base_hour + self.random.randint(-variation, variation)) % 24
        minute = self.random.choice([0, 15, 30, 45])
        return f"{hour:02d}:{minute:02d}"
    
    def calculate_duration(self, distance: float, train_type: str) -> str:
        """Calculate travel duration based on distance and train type."""
        # Average speeds in km/h
        speeds = {
            "G": 300, "D": 250, "C": 200, 
            "Z": 160, "T": 140, "K": 120
        }
        
        speed = speeds.get(train_type, 120)
        travel_hours = distance / speed
        
        # Add some buffer time
        total_hours = travel_hours + self.random.uniform(0.2, 0.8)
        
        hours = int(total_hours)
        minutes = int((total_hours - hours) * 60)
        
        return f"{hours:02d}:{minutes:02d}"
    
    def generate_prices(self, distance: float, train_type: str) -> Dict[str, float]:
        """Generate realistic prices for different seat types."""
        multiplier = self.train_types[train_type]["base_price_multiplier"]
        prices = {}
        
        for seat_type in self.seat_types:
            base_price = self.base_prices_per_km[seat_type] * distance * multiplier
            # Add some variation
            variation = self.random.uniform(0.9, 1.1)
            prices[seat_type] = round(base_price * variation, 2)
        
        return prices
    
    def generate_available_seats(self) -> Dict[str, int]:
        """Generate available seats for different seat types."""
        return {
            "business_class": self.random.randint(5, 20),
            "first_class": self.random.randint(10, 40),
            "second_class": self.random.randint(50, 200),
            "soft_sleeper": self.random.randint(10, 30),
            "hard_sleeper": self.random.randint(20, 60),
            "hard_seat": self.random.randint(100, 400)
        }
    
    def generate_seat_types_availability(self) -> Dict[str, str]:
        """Generate seat type availability status."""
        statuses = ["有", "无", "少量"]
        weights = [0.7, 0.1, 0.2]  # Mostly available, some sold out, some limited
        
        return {
            seat_type: self.random.choices(statuses, weights=weights)[0]
            for seat_type in self.seat_types
        }
    
    def generate_train_data(self, count: int = 100) -> List[Dict[str, Any]]:
        """Generate synthetic train ticket data."""
        trains = []
        
        # Generate dates for next 30 days
        base_date = datetime.now()
        dates = [base_date + timedelta(days=i) for i in range(30)]
        
        for _ in range(count):
            # Randomly select stations
            departure_station, arrival_station = self.random.sample(self.stations, 2)
            
            # Select train type
            train_type = self.random.choice(list(self.train_types.keys()))
            
            # Calculate distance
            distance = self.calculate_distance(departure_station, arrival_station)
            
            # Generate train data
            train_data = {
                "train_number": self.generate_train_number(train_type),
                "departure_station": departure_station,
                "arrival_station": arrival_station,
                "departure_time": self.generate_time(8, 4),  # Mostly morning departures
                "arrival_time": self.generate_time(16, 4),   # Mostly afternoon arrivals
                "duration": self.calculate_duration(distance, train_type),
                "date": self.random.choice(dates).strftime("%Y-%m-%d"),
                "seat_types": self.generate_seat_types_availability(),
                "prices": self.generate_prices(distance, train_type),
                "available_seats": self.generate_available_seats()
            }
            
            trains.append(train_data)
        
        return trains


def generate_database(
    count: int = 100, 
    seed: int = 42, 
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate the China Railway offline database.
    
    Args:
        count: Number of train records to generate
        seed: Random seed for deterministic generation
        output_path: Path to save the JSON database
    
    Returns:
        Dictionary containing the generated database
    """
    generator = ChinaRailwayDatabaseGenerator(seed=seed)
    trains = generator.generate_train_data(count)
    
    database = {
        "trains": trains
    }
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
    
    return database


def update_database(updates: Dict[str, Any], database_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Update the existing database with new data.
    
    This function is for manual follow-up operations; workflow agents will not call it automatically.
    
    Args:
        updates: Dictionary containing updates to merge into the database
        database_path: Path to the database JSON file. If None, uses recommended location
    
    Returns:
        Updated database dictionary
    
    Raises:
        FileNotFoundError: If database file doesn't exist
        ValueError: If updates are incompatible with DATA CONTRACT
    """
    if database_path is None:
        # Use recommended location
        database_path = "generated\\travel_maps\\chinarailway-mcp-\\chinarailway_mcp__database.json"
    
    # Check if database file exists
    if not Path(database_path).exists():
        raise FileNotFoundError(f"Database file not found at {database_path}")
    
    # Load existing database
    with open(database_path, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    # Validate updates against DATA CONTRACT
    if "trains" in updates:
        if not isinstance(updates["trains"], list):
            raise ValueError("Updates 'trains' must be a list")
        
        # Validate each train record
        for train in updates["trains"]:
            required_fields = ["train_number", "departure_station", "arrival_station", 
                             "departure_time", "arrival_time", "duration", "date"]
            for field in required_fields:
                if field not in train:
                    raise ValueError(f"Train record missing required field: {field}")
    
    # Merge updates
    for key, value in updates.items():
        if key == "trains" and key in database:
            # For trains, extend the list
            database[key].extend(value)
        else:
            # For other keys, update/replace
            database[key] = value
    
    # Save updated database
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    
    return database


if __name__ == "__main__":
    # Generate database when run directly
    database = generate_database(
        count=150,  # Generate 150 train records
        seed=42,    # Fixed seed for deterministic generation
        output_path="generated\\travel_maps\\chinarailway-mcp-\\chinarailway_mcp__database.json"
    )
    print(f"Generated database with {len(database['trains'])} train records")