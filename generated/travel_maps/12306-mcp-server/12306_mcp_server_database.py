"""
12306 MCP Server Database Generator

Generates deterministic synthetic train ticket data for the 12306 MCP server.
The data follows the DATA CONTRACT structure and includes realistic Chinese train routes.
"""

import json
import random
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import os


def generate_train_tickets(seed: int = 42, count: int = 50) -> List[Dict[str, Any]]:
    """
    Generate synthetic train ticket data.
    
    Args:
        seed: Random seed for deterministic generation
        count: Number of train tickets to generate (default: 50)
        
    Returns:
        List of train ticket dictionaries matching DATA CONTRACT
    """
    random.seed(seed)
    
    # Major Chinese train stations
    stations = [
        "北京南站", "上海虹桥", "广州南站", "深圳北站", "杭州东站",
        "南京南站", "武汉站", "西安北站", "成都东站", "重庆北站",
        "天津西站", "苏州北站", "郑州东站", "长沙南站", "合肥南站"
    ]
    
    # Train number prefixes and types
    train_prefixes = ["G", "D", "K"]
    train_descriptions = {
        "G": "高速动车",
        "D": "动车组", 
        "K": "快速列车"
    }
    
    # Base date for generation
    base_date = datetime(2024, 1, 15)
    
    tickets = []
    
    for i in range(count):
        # Generate train number
        prefix = random.choice(train_prefixes)
        train_number = f"{prefix}{random.randint(1000, 9999)}"
        
        # Generate stations (ensure departure != arrival)
        departure_station, arrival_station = random.sample(stations, 2)
        
        # Generate date (within next 30 days)
        days_offset = random.randint(0, 30)
        date = (base_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
        
        # Generate times
        departure_hour = random.randint(6, 22)
        departure_minute = random.choice([0, 15, 30, 45])
        
        # Calculate arrival time based on distance between stations
        station_distance = abs(stations.index(departure_station) - stations.index(arrival_station))
        travel_hours = max(1, min(8, station_distance))
        travel_minutes = random.choice([0, 15, 30, 45])
        
        arrival_hour = departure_hour + travel_hours
        arrival_minute = departure_minute + travel_minutes
        
        # Handle minute overflow
        if arrival_minute >= 60:
            arrival_hour += 1
            arrival_minute -= 60
        
        # Handle hour overflow
        if arrival_hour >= 24:
            arrival_hour -= 24
        
        departure_time = f"{departure_hour:02d}:{departure_minute:02d}"
        arrival_time = f"{arrival_hour:02d}:{arrival_minute:02d}"
        
        # Generate duration
        duration = f"{travel_hours}h{travel_minutes:02d}m"
        
        # Generate seat types availability
        seat_types = {
            "business_class": "商务座" if prefix == "G" else "-",
            "first_class": "一等座",
            "second_class": "二等座", 
            "hard_seat": "硬座" if prefix == "K" else "-"
        }
        
        # Generate prices based on train type and distance
        base_multiplier = {"G": 1.5, "D": 1.2, "K": 1.0}[prefix]
        distance_factor = station_distance * 50
        
        prices = {
            "business_class": round(base_multiplier * (800 + distance_factor)) if prefix == "G" else 0,
            "first_class": round(base_multiplier * (500 + distance_factor * 0.8)),
            "second_class": round(base_multiplier * (300 + distance_factor * 0.6)),
            "hard_seat": round(base_multiplier * (100 + distance_factor * 0.3)) if prefix == "K" else 0
        }
        
        # Generate available seats
        available_seats = {
            "business_class": random.randint(5, 20) if prefix == "G" else 0,
            "first_class": random.randint(10, 30),
            "second_class": random.randint(20, 50),
            "hard_seat": random.randint(50, 100) if prefix == "K" else 0
        }
        
        ticket = {
            "train_number": train_number,
            "departure_station": departure_station,
            "arrival_station": arrival_station,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "duration": duration,
            "date": date,
            "seat_types": seat_types,
            "prices": prices,
            "available_seats": available_seats
        }
        
        tickets.append(ticket)
    
    return tickets


def create_database(seed: int = 42, count: int = 50, database_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Create the complete database with train tickets.
    
    Args:
        seed: Random seed for deterministic generation
        count: Number of train tickets to generate (default: 50)
        database_path: Path to save the database JSON (uses recommended path if None)
        
    Returns:
        Complete database dictionary
    """
    if database_path is None:
        database_path = "generated\\travel_maps\\12306-mcp-server\\12306_mcp_server_database.json"
    
    database = {
        "train_tickets": generate_train_tickets(seed, count)
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(database_path), exist_ok=True)
    
    # Write to file
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    
    print(f"Database generated with {count} train tickets (seed: {seed})")
    print(f"Saved to: {database_path}")
    
    return database


def update_database(updates: Dict[str, Any], database_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Update the existing database with new data.
    
    This function is for manual follow-up operations; workflow agents will not call it automatically.
    
    Args:
        updates: Dictionary containing updates to merge into the database
        database_path: Path to the database JSON (uses recommended path if None)
        
    Returns:
        Updated database dictionary
        
    Raises:
        FileNotFoundError: If the database file doesn't exist
        ValueError: If updates are incompatible with DATA CONTRACT
    """
    if database_path is None:
        database_path = "generated\\travel_maps\\12306-mcp-server\\12306_mcp_server_database.json"
    
    # Check if database file exists
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database file not found: {database_path}")
    
    # Load existing database
    with open(database_path, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    # Validate updates structure
    if "train_tickets" in updates:
        if not isinstance(updates["train_tickets"], list):
            raise ValueError("train_tickets must be a list")
        
        # Validate each ticket in updates
        for ticket in updates["train_tickets"]:
            if not isinstance(ticket, dict):
                raise ValueError("Each train_ticket must be a dictionary")
            
            # Check required fields
            required_fields = ["train_number", "departure_station", "arrival_station", 
                             "departure_time", "arrival_time", "date"]
            for field in required_fields:
                if field not in ticket:
                    raise ValueError(f"Missing required field: {field}")
    
    # Merge updates (extend lists, update dicts)
    for key, value in updates.items():
        if key in database:
            if isinstance(database[key], list) and isinstance(value, list):
                # Extend list
                database[key].extend(value)
            elif isinstance(database[key], dict) and isinstance(value, dict):
                # Update dictionary
                database[key].update(value)
            else:
                # Replace value
                database[key] = value
        else:
            # Add new key
            database[key] = value
    
    # Save updated database
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    
    print(f"Database updated and saved to: {database_path}")
    
    return database


if __name__ == "__main__":
    # Generate database when run directly
    database = create_database(seed=42, count=50)
    print(f"Generated {len(database['train_tickets'])} train tickets")