"""
Amadeus MCP Server Database Generator

Generates deterministic synthetic flight data for offline testing.
Follows the DATA CONTRACT structure for flight offers.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path


class FlightDatabaseGenerator:
    """Generates synthetic flight data following the DATA CONTRACT."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize generator with optional seed for deterministic output."""
        if seed is not None:
            random.seed(seed)
        
        # Major airport codes and cities
        self.airports = {
            'JFK': 'New York',
            'LAX': 'Los Angeles', 
            'LHR': 'London',
            'CDG': 'Paris',
            'FRA': 'Frankfurt',
            'DXB': 'Dubai',
            'SFO': 'San Francisco',
            'ORD': 'Chicago',
            'DFW': 'Dallas',
            'ATL': 'Atlanta'
        }
        
        # Major airlines
        self.airlines = [
            'Delta Air Lines',
            'United Airlines', 
            'American Airlines',
            'British Airways',
            'Lufthansa',
            'Air France',
            'Emirates',
            'Qatar Airways',
            'Singapore Airlines',
            'KLM'
        ]
        
        # Travel classes
        self.travel_classes = [
            'ECONOMY',
            'PREMIUM_ECONOMY', 
            'BUSINESS',
            'FIRST'
        ]
        
        # Common flight routes
        self.routes = [
            ('JFK', 'LAX'),  # NYC to LA
            ('LHR', 'CDG'),  # London to Paris
            ('JFK', 'FRA'),  # NYC to Frankfurt
            ('LAX', 'LHR'),  # LA to London
            ('SFO', 'DXB'),  # San Francisco to Dubai
            ('ORD', 'CDG'),  # Chicago to Paris
            ('DFW', 'LHR'),  # Dallas to London
            ('ATL', 'FRA'),  # Atlanta to Frankfurt
            ('JFK', 'SFO'),  # NYC to San Francisco
            ('LAX', 'CDG')   # LA to Paris
        ]
    
    def generate_flight_offers(self, count: int = 150) -> List[Dict[str, Any]]:
        """Generate synthetic flight offers.
        
        Args:
            count: Number of flight offers to generate
            
        Returns:
            List of flight offer dictionaries following DATA CONTRACT
        """
        flight_offers = []
        base_date = datetime.now() + timedelta(days=1)
        
        for i in range(count):
            # Select random route
            origin, destination = random.choice(self.routes)
            
            # Generate departure date (1-30 days from now)
            days_offset = random.randint(1, 30)
            departure_date = (base_date + timedelta(days=days_offset)).strftime('%Y-%m-%d')
            
            # 50% chance of having a return flight
            has_return = random.random() > 0.5
            if has_return:
                return_days = random.randint(1, 14)
                return_date = (base_date + timedelta(days=days_offset + return_days)).strftime('%Y-%m-%d')
            else:
                return_date = ""
            
            # Passenger counts (following realistic distributions)
            adults = random.randint(1, 4)
            children = random.randint(0, 2) if adults >= 2 else 0
            infants = random.randint(0, 1) if adults >= 1 else 0
            
            # Travel class with realistic distribution
            class_prob = random.random()
            if class_prob < 0.7:
                travel_class = 'ECONOMY'
            elif class_prob < 0.9:
                travel_class = 'PREMIUM_ECONOMY'
            elif class_prob < 0.98:
                travel_class = 'BUSINESS'
            else:
                travel_class = 'FIRST'
            
            # Generate price based on route distance and class
            base_price = self._get_base_price(origin, destination, travel_class)
            price_variation = random.uniform(-0.2, 0.3)  # -20% to +30% variation
            price = round(base_price * (1 + price_variation), 2)
            
            # Generate flight details
            airline = random.choice(self.airlines)
            flight_number = f"{airline[:2].upper()}{random.randint(100, 999)}"
            
            # Duration based on distance
            duration = self._get_flight_duration(origin, destination)
            
            # Generate departure and arrival times
            departure_time, arrival_time = self._generate_flight_times(duration)
            
            # Number of stops (70% direct, 25% 1 stop, 5% 2 stops)
            stop_prob = random.random()
            if stop_prob < 0.7:
                stops = 0
            elif stop_prob < 0.95:
                stops = 1
            else:
                stops = 2
            
            flight_offer = {
                "id": f"FL{i+1:03d}",
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "return_date": return_date,
                "adults": adults,
                "children": children,
                "infants": infants,
                "travel_class": travel_class,
                "currency": "USD",
                "price": price,
                "airline": airline,
                "flight_number": flight_number,
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "duration": duration,
                "stops": stops
            }
            
            flight_offers.append(flight_offer)
        
        return flight_offers
    
    def _get_base_price(self, origin: str, destination: str, travel_class: str) -> float:
        """Get base price for a route based on distance and travel class."""
        # Base prices by route type
        domestic_us = {'JFK', 'LAX', 'SFO', 'ORD', 'DFW', 'ATL'}
        if origin in domestic_us and destination in domestic_us:
            base_price = random.uniform(200, 800)
        elif (origin in {'JFK', 'LHR', 'CDG', 'FRA'} and 
              destination in {'JFK', 'LHR', 'CDG', 'FRA'}):
            base_price = random.uniform(400, 1200)  # Transatlantic
        else:
            base_price = random.uniform(600, 1500)  # Long-haul
        
        # Apply class multipliers
        class_multipliers = {
            'ECONOMY': 1.0,
            'PREMIUM_ECONOMY': 1.8,
            'BUSINESS': 3.0,
            'FIRST': 5.0
        }
        
        return base_price * class_multipliers[travel_class]
    
    def _get_flight_duration(self, origin: str, destination: str) -> str:
        """Get flight duration string based on route."""
        # Domestic US flights
        domestic_us = {'JFK', 'LAX', 'SFO', 'ORD', 'DFW', 'ATL'}
        if origin in domestic_us and destination in domestic_us:
            hours = random.randint(3, 6)
        # Transatlantic flights
        elif (origin in {'JFK', 'LHR', 'CDG', 'FRA'} and 
              destination in {'JFK', 'LHR', 'CDG', 'FRA'}):
            hours = random.randint(6, 9)
        # Long-haul flights
        else:
            hours = random.randint(8, 16)
        
        minutes = random.choice([0, 15, 30, 45])
        return f"{hours}h {minutes}m"
    
    def _generate_flight_times(self, duration_str: str) -> tuple[str, str]:
        """Generate departure and arrival times based on flight duration."""
        # Parse duration
        hours, minutes = map(int, duration_str.replace('h', '').replace('m', '').split())
        total_minutes = hours * 60 + minutes
        
        # Generate random departure time (6 AM to 10 PM)
        departure_hour = random.randint(6, 22)
        departure_minute = random.choice([0, 15, 30, 45])
        departure_time = f"{departure_hour:02d}:{departure_minute:02d}"
        
        # Calculate arrival time
        arrival_minutes = departure_hour * 60 + departure_minute + total_minutes
        arrival_hour = (arrival_minutes // 60) % 24
        arrival_minute = arrival_minutes % 60
        arrival_time = f"{arrival_hour:02d}:{arrival_minute:02d}"
        
        return departure_time, arrival_time


def generate_database(count: int = 150, seed: Optional[int] = 42) -> Dict[str, Any]:
    """Generate the complete flight database.
    
    Args:
        count: Number of flight offers to generate
        seed: Random seed for deterministic generation
        
    Returns:
        Database dictionary following DATA CONTRACT
    """
    generator = FlightDatabaseGenerator(seed=seed)
    flight_offers = generator.generate_flight_offers(count)
    
    return {
        "flight_offers": flight_offers
    }


def update_database(updates: Dict[str, Any], database_path: Optional[str] = None) -> Dict[str, Any]:
    """Update the existing database with new data.
    
    This function is for manual follow-up operations; workflow agents will not call it automatically.
    
    Args:
        updates: Dictionary containing updates to merge into the database
        database_path: Path to the database JSON file. If None, uses recommended path.
        
    Returns:
        Updated database dictionary
        
    Raises:
        FileNotFoundError: If database file doesn't exist
        ValueError: If updates violate DATA CONTRACT structure
    """
    if database_path is None:
        # Use forward slashes for cross-platform compatibility
        database_path = "generated/travel_maps/amadeus-mcp-server/amadeus_mcp_server_database.json"
    
    # Check if database file exists
    if not Path(database_path).exists():
        raise FileNotFoundError(f"Database file not found at {database_path}")
    
    # Load existing database
    with open(database_path, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    # Validate updates against DATA CONTRACT
    if "flight_offers" in updates:
        if not isinstance(updates["flight_offers"], list):
            raise ValueError("flight_offers must be a list")
        
        # Validate each flight offer
        for offer in updates["flight_offers"]:
            if not isinstance(offer, dict):
                raise ValueError("Each flight offer must be a dictionary")
            
            # Check required fields from DATA CONTRACT
            required_fields = ["id", "origin", "destination", "departure_date", "price", "airline"]
            for field in required_fields:
                if field not in offer:
                    raise ValueError(f"Flight offer missing required field: {field}")
            
            # Validate field types
            if not isinstance(offer["id"], str):
                raise ValueError("id must be a string")
            if not isinstance(offer["origin"], str):
                raise ValueError("origin must be a string")
            if not isinstance(offer["destination"], str):
                raise ValueError("destination must be a string")
            if not isinstance(offer["departure_date"], str):
                raise ValueError("departure_date must be a string")
            if not isinstance(offer["price"], (int, float)):
                raise ValueError("price must be a number")
            if not isinstance(offer["airline"], str):
                raise ValueError("airline must be a string")
    
    # Merge updates (extend lists, update dictionaries)
    for key, value in updates.items():
        if key == "flight_offers" and key in database:
            # Extend flight offers list
            database[key].extend(value)
        else:
            # Update other keys
            database[key] = value
    
    # Save updated database
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2)
    
    return database


if __name__ == "__main__":
    # Generate database with deterministic seed
    database = generate_database(count=150, seed=42)
    
    # Write to JSON file using forward slashes for cross-platform compatibility
    output_path = "generated/travel_maps/amadeus-mcp-server/amadeus_mcp_server_database.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2)
    
    print(f"Generated {len(database['flight_offers'])} flight offers")
    print(f"Database saved to: {output_path}")