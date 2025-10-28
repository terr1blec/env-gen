"""
Weather360 Server Database Generator

Generates deterministic offline weather data for the weather360-server.
Creates synthetic weather data for various geographic locations worldwide.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os


def generate_weather_data(seed: int = 42, count: int = 50) -> Dict[str, Any]:
    """
    Generate synthetic weather data for various geographic locations.
    
    Args:
        seed: Random seed for deterministic generation
        count: Number of weather records to generate
        
    Returns:
        Dictionary with weather_data array following DATA CONTRACT
    """
    random.seed(seed)
    
    # Major cities and geographic locations worldwide
    locations = [
        # North America
        (40.7128, -74.0060, "New York", "urban"),  # New York City
        (34.0522, -118.2437, "Los Angeles", "coastal"),  # Los Angeles
        (41.8781, -87.6298, "Chicago", "urban"),  # Chicago
        (25.7617, -80.1918, "Miami", "coastal"),  # Miami
        (47.6062, -122.3321, "Seattle", "coastal"),  # Seattle
        (39.7392, -104.9903, "Denver", "mountain"),  # Denver
        
        # Europe
        (51.5074, -0.1278, "London", "urban"),  # London
        (48.8566, 2.3522, "Paris", "urban"),  # Paris
        (52.5200, 13.4050, "Berlin", "urban"),  # Berlin
        (41.9028, 12.4964, "Rome", "urban"),  # Rome
        (55.7558, 37.6173, "Moscow", "urban"),  # Moscow
        (59.3293, 18.0686, "Stockholm", "coastal"),  # Stockholm
        
        # Asia
        (35.6762, 139.6503, "Tokyo", "coastal"),  # Tokyo
        (31.2304, 121.4737, "Shanghai", "coastal"),  # Shanghai
        (28.6139, 77.2090, "Delhi", "urban"),  # Delhi
        (22.3193, 114.1694, "Hong Kong", "coastal"),  # Hong Kong
        (1.3521, 103.8198, "Singapore", "coastal"),  # Singapore
        (25.0330, 121.5654, "Taipei", "coastal"),  # Taipei
        
        # South America
        (-23.5505, -46.6333, "Sao Paulo", "urban"),  # Sao Paulo
        (-34.6037, -58.3816, "Buenos Aires", "coastal"),  # Buenos Aires
        (-12.0464, -77.0428, "Lima", "coastal"),  # Lima
        
        # Africa
        (-33.9249, 18.4241, "Cape Town", "coastal"),  # Cape Town
        (30.0444, 31.2357, "Cairo", "desert"),  # Cairo
        (6.5244, 3.3792, "Lagos", "coastal"),  # Lagos
        
        # Oceania
        (-33.8688, 151.2093, "Sydney", "coastal"),  # Sydney
        (-37.8136, 144.9631, "Melbourne", "coastal"),  # Melbourne
        
        # Additional diverse locations
        (27.9881, 86.9250, "Mount Everest", "mountain"),  # Mount Everest
        (36.7783, -119.4179, "California Valley", "rural"),  # Central Valley
        (64.2008, -149.4937, "Fairbanks", "arctic"),  # Fairbanks, Alaska
        (-54.8019, -68.3030, "Ushuaia", "coastal"),  # Ushuaia, Argentina
        (28.3949, 84.1240, "Annapurna", "mountain"),  # Annapurna
    ]
    
    weather_data = []
    base_time = datetime.now() - timedelta(days=30)
    
    # Weather descriptions
    weather_descriptions = [
        "clear sky",
        "few clouds", 
        "scattered clouds",
        "broken clouds",
        "shower rain",
        "rain",
        "thunderstorm",
        "snow",
        "mist",
    ]
    
    for i in range(count):
        if i < len(locations):
            lat, lon, name, location_type = locations[i]
        else:
            # Generate random locations for additional records
            lat = round(random.uniform(-90, 90), 4)
            lon = round(random.uniform(-180, 180), 4)
            name = f"Location_{i+1}"
            location_type = random.choice(["urban", "coastal", "mountain", "rural", "desert"])
        
        # Generate weather parameters based on location type and latitude
        base_temp = generate_base_temperature(lat, location_type)
        temp_variation = random.uniform(-5, 5)
        temperature = round(base_temp + temp_variation, 1)
        
        humidity = generate_humidity(location_type, temperature)
        wind_speed = generate_wind_speed(location_type)
        
        # Select weather description
        description = select_weather_description(location_type, lat)
        
        # Generate timestamp (spread over last 30 days)
        days_offset = random.uniform(0, 30)
        timestamp = (base_time + timedelta(days=days_offset)).isoformat() + "Z"
        
        # Create weather record following DATA CONTRACT exactly
        weather_record = {
            "latitude": lat,
            "longitude": lon,
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "description": description,
            "timestamp": timestamp
        }
        
        weather_data.append(weather_record)
    
    return {"weather_data": weather_data}


def generate_base_temperature(latitude: float, location_type: str) -> float:
    """Generate base temperature based on latitude and location type."""
    # Base temperature decreases with absolute latitude
    lat_factor = 1 - (abs(latitude) / 90)
    base_temp = 15 + 25 * lat_factor  # Range from 15°C to 40°C
    
    # Adjust for location type
    if location_type == "mountain":
        base_temp -= 10
    elif location_type == "arctic":
        base_temp -= 25
    elif location_type == "desert":
        base_temp += 5
    elif location_type == "coastal":
        base_temp -= 2  # Coastal areas are generally cooler
    
    return base_temp


def generate_humidity(location_type: str, temperature: float) -> float:
    """Generate humidity based on location type and temperature."""
    if location_type == "desert":
        return round(random.uniform(10, 40), 1)
    elif location_type == "coastal":
        return round(random.uniform(60, 90), 1)
    elif location_type == "mountain":
        return round(random.uniform(40, 80), 1)
    elif location_type == "urban":
        return round(random.uniform(45, 75), 1)
    else:  # rural
        return round(random.uniform(50, 85), 1)


def generate_wind_speed(location_type: str) -> float:
    """Generate wind speed based on location type."""
    if location_type == "coastal":
        return round(random.uniform(3, 15), 1)
    elif location_type == "mountain":
        return round(random.uniform(5, 20), 1)
    elif location_type == "desert":
        return round(random.uniform(2, 12), 1)
    else:  # urban, rural
        return round(random.uniform(1, 8), 1)


def select_weather_description(location_type: str, latitude: float) -> str:
    """Select weather description based on location and latitude."""
    weather_descriptions = [
        "clear sky",
        "few clouds", 
        "scattered clouds",
        "broken clouds",
        "shower rain",
        "rain",
        "thunderstorm",
        "snow",
        "mist",
    ]
    
    # Weight probabilities based on location type and latitude
    weights = [0.15, 0.2, 0.2, 0.15, 0.1, 0.1, 0.05, 0.03, 0.02]
    
    # Adjust weights for location type
    if location_type == "coastal":
        weights = [0.1, 0.15, 0.2, 0.15, 0.15, 0.15, 0.05, 0.0, 0.05]
    elif location_type == "mountain":
        weights = [0.1, 0.1, 0.15, 0.2, 0.15, 0.1, 0.1, 0.05, 0.05]
    elif location_type == "desert":
        weights = [0.3, 0.25, 0.2, 0.15, 0.05, 0.02, 0.01, 0.0, 0.02]
    
    # Adjust for latitude (more snow at higher latitudes)
    if abs(latitude) > 45:
        weights[7] += 0.1  # Increase snow probability
        weights[0] -= 0.05  # Decrease clear sky probability
    
    # Normalize weights
    total = sum(weights)
    weights = [w / total for w in weights]
    
    return random.choices(weather_descriptions, weights=weights)[0]


def update_database(updates: Dict[str, Any], database_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Update the weather database with new data.
    
    This function is for manual follow-up operations; workflow agents will not call it automatically.
    
    Args:
        updates: Dictionary containing updates to merge into the database
        database_path: Path to the database JSON file. If None, uses recommended location
        
    Returns:
        Updated database dictionary
        
    Raises:
        FileNotFoundError: If database file doesn't exist
        ValueError: If updates violate DATA CONTRACT structure
    """
    if database_path is None:
        database_path = "generated\\weather\\weather360-server\\weather360_server_database.json"
    
    # Check if database file exists
    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Database file not found: {database_path}")
    
    # Load existing database
    with open(database_path, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    # Validate updates structure
    if "weather_data" in updates:
        if not isinstance(updates["weather_data"], list):
            raise ValueError("weather_data must be a list")
        
        # Validate each weather record against DATA CONTRACT
        required_fields = {"latitude", "longitude", "temperature", "humidity", 
                          "wind_speed", "description", "timestamp"}
        
        for record in updates["weather_data"]:
            if not isinstance(record, dict):
                raise ValueError("Each weather_data item must be a dictionary")
            
            missing_fields = required_fields - set(record.keys())
            if missing_fields:
                raise ValueError(f"Missing required fields in weather record: {missing_fields}")
            
            # Validate field types
            if not isinstance(record["latitude"], (int, float)):
                raise ValueError("latitude must be a number")
            if not isinstance(record["longitude"], (int, float)):
                raise ValueError("longitude must be a number")
            if not isinstance(record["temperature"], (int, float)):
                raise ValueError("temperature must be a number")
            if not isinstance(record["humidity"], (int, float)):
                raise ValueError("humidity must be a number")
            if not isinstance(record["wind_speed"], (int, float)):
                raise ValueError("wind_speed must be a number")
            if not isinstance(record["description"], str):
                raise ValueError("description must be a string")
            if not isinstance(record["timestamp"], str):
                raise ValueError("timestamp must be a string")
    
    # Merge updates (extend weather_data list)
    if "weather_data" in updates:
        database["weather_data"].extend(updates["weather_data"])
    
    # Save updated database
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2)
    
    return database


def main():
    """Generate and save the weather database."""
    database = generate_weather_data(seed=42, count=50)
    
    database_path = "generated\\weather\\weather360-server\\weather360_server_database.json"
    
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2)
    
    print(f"Generated {len(database['weather_data'])} weather records")
    print(f"Database saved to: {database_path}")


if __name__ == "__main__":
    main()