"""
FlightRadar Database Generator

Generates deterministic synthetic flight data for offline FlightRadar MCP server.
Exports data to JSON format matching the DATA CONTRACT schema.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class FlightRadarDatabaseGenerator:
    """Generates synthetic flight data for FlightRadar MCP server."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize generator with optional seed for deterministic output."""
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        
        # Initialize data structures
        self.airports: List[Dict] = []
        self.airlines: List[Dict] = []
        self.flights: List[Dict] = []
        
        self._generate_airports()
        self._generate_airlines()
        self._generate_flights()
    
    def _generate_airports(self):
        """Generate major airports worldwide."""
        airports_data = [
            # North America
            {"iata_code": "JFK", "icao_code": "KJFK", "name": "John F. Kennedy International Airport", 
             "city": "New York", "country": "United States", "latitude": 40.6413, "longitude": -73.7781, "timezone": "America/New_York"},
            {"iata_code": "LAX", "icao_code": "KLAX", "name": "Los Angeles International Airport", 
             "city": "Los Angeles", "country": "United States", "latitude": 33.9416, "longitude": -118.4085, "timezone": "America/Los_Angeles"},
            {"iata_code": "ORD", "icao_code": "KORD", "name": "O'Hare International Airport", 
             "city": "Chicago", "country": "United States", "latitude": 41.9742, "longitude": -87.9073, "timezone": "America/Chicago"},
            {"iata_code": "YYZ", "icao_code": "CYYZ", "name": "Toronto Pearson International Airport", 
             "city": "Toronto", "country": "Canada", "latitude": 43.6777, "longitude": -79.6248, "timezone": "America/Toronto"},
            
            # Europe
            {"iata_code": "LHR", "icao_code": "EGLL", "name": "Heathrow Airport", 
             "city": "London", "country": "United Kingdom", "latitude": 51.4700, "longitude": -0.4543, "timezone": "Europe/London"},
            {"iata_code": "CDG", "icao_code": "LFPG", "name": "Charles de Gaulle Airport", 
             "city": "Paris", "country": "France", "latitude": 49.0097, "longitude": 2.5479, "timezone": "Europe/Paris"},
            {"iata_code": "FRA", "icao_code": "EDDF", "name": "Frankfurt Airport", 
             "city": "Frankfurt", "country": "Germany", "latitude": 50.0379, "longitude": 8.5622, "timezone": "Europe/Berlin"},
            {"iata_code": "AMS", "icao_code": "EHAM", "name": "Amsterdam Airport Schiphol", 
             "city": "Amsterdam", "country": "Netherlands", "latitude": 52.3086, "longitude": 4.7639, "timezone": "Europe/Amsterdam"},
            
            # Asia
            {"iata_code": "HND", "icao_code": "RJTT", "name": "Tokyo Haneda Airport", 
             "city": "Tokyo", "country": "Japan", "latitude": 35.5494, "longitude": 139.7798, "timezone": "Asia/Tokyo"},
            {"iata_code": "PEK", "icao_code": "ZBAA", "name": "Beijing Capital International Airport", 
             "city": "Beijing", "country": "China", "latitude": 40.0799, "longitude": 116.6031, "timezone": "Asia/Shanghai"},
            {"iata_code": "DXB", "icao_code": "OMDB", "name": "Dubai International Airport", 
             "city": "Dubai", "country": "United Arab Emirates", "latitude": 25.2532, "longitude": 55.3657, "timezone": "Asia/Dubai"},
            {"iata_code": "SIN", "icao_code": "WSSS", "name": "Singapore Changi Airport", 
             "city": "Singapore", "country": "Singapore", "latitude": 1.3644, "longitude": 103.9915, "timezone": "Asia/Singapore"},
            
            # Oceania
            {"iata_code": "SYD", "icao_code": "YSSY", "name": "Sydney Kingsford Smith Airport", 
             "city": "Sydney", "country": "Australia", "latitude": -33.9399, "longitude": 151.1753, "timezone": "Australia/Sydney"},
        ]
        
        self.airports = airports_data
    
    def _generate_airlines(self):
        """Generate major airlines."""
        airlines_data = [
            {"iata_code": "AA", "icao_code": "AAL", "name": "American Airlines", "country": "United States", "fleet_size": 956},
            {"iata_code": "DL", "icao_code": "DAL", "name": "Delta Air Lines", "country": "United States", "fleet_size": 912},
            {"iata_code": "UA", "icao_code": "UAL", "name": "United Airlines", "country": "United States", "fleet_size": 868},
            {"iata_code": "LH", "icao_code": "DLH", "name": "Lufthansa", "country": "Germany", "fleet_size": 271},
            {"iata_code": "AF", "icao_code": "AFR", "name": "Air France", "country": "France", "fleet_size": 212},
            {"iata_code": "BA", "icao_code": "BAW", "name": "British Airways", "country": "United Kingdom", "fleet_size": 255},
            {"iata_code": "JL", "icao_code": "JAL", "name": "Japan Airlines", "country": "Japan", "fleet_size": 167},
            {"iata_code": "SQ", "icao_code": "SIA", "name": "Singapore Airlines", "country": "Singapore", "fleet_size": 142},
            {"iata_code": "EK", "icao_code": "UAE", "name": "Emirates", "country": "United Arab Emirates", "fleet_size": 262},
            {"iata_code": "QF", "icao_code": "QFA", "name": "Qantas", "country": "Australia", "fleet_size": 125},
        ]
        
        self.airlines = airlines_data
    
    def _generate_flights(self):
        """Generate realistic flight data with relationships to airports and airlines."""
        flight_statuses = ["scheduled", "active", "landed", "cancelled", "diverted"]
        aircraft_types = ["A320", "A321", "B737", "B738", "B772", "B773", "A333", "A359"]
        
        # Common flight routes
        routes = [
            ("JFK", "LAX"), ("LAX", "JFK"), ("JFK", "LHR"), ("LHR", "JFK"),
            ("LAX", "HND"), ("HND", "LAX"), ("FRA", "DXB"), ("DXB", "FRA"),
            ("SYD", "SIN"), ("SIN", "SYD"), ("CDG", "AMS"), ("AMS", "CDG"),
            ("ORD", "YYZ"), ("YYZ", "ORD"), ("PEK", "HND"), ("HND", "PEK"),
            ("LHR", "DXB"), ("DXB", "LHR"), ("FRA", "SIN"), ("SIN", "FRA"),
        ]
        
        flight_counter = 100
        
        for dep_iata, arr_iata in routes:
            # Find departure and arrival airports
            dep_airport = next((a for a in self.airports if a["iata_code"] == dep_iata), None)
            arr_airport = next((a for a in self.airports if a["iata_code"] == arr_iata), None)
            
            if not dep_airport or not arr_airport:
                continue
            
            # Select random airline
            airline = random.choice(self.airlines)
            
            # Generate multiple flights per route
            for _ in range(2):  # 2 flights per route
                flight_number = str(flight_counter)
                flight_iata = airline["iata_code"] + flight_number
                flight_icao = airline["icao_code"] + flight_number
                
                # Generate times (deterministic based on route and flight number)
                base_hour = (hash(dep_iata + arr_iata + flight_number) % 12) + 6  # 6 AM to 6 PM
                flight_duration = self._calculate_flight_duration(dep_iata, arr_iata)
                
                dep_time = f"{base_hour:02d}:{random.randint(0, 59):02d}"
                arr_hour = (base_hour + flight_duration // 60) % 24
                arr_minute = (int(dep_time.split(':')[1]) + flight_duration % 60) % 60
                arr_time = f"{arr_hour:02d}:{arr_minute:02d}"
                
                # Generate flight data
                flight = {
                    "flight_iata": flight_iata,
                    "flight_icao": flight_icao,
                    "airline_iata": airline["iata_code"],
                    "airline_icao": airline["icao_code"],
                    "flight_number": flight_number,
                    "dep_iata": dep_iata,
                    "arr_iata": arr_iata,
                    "dep_time": dep_time,
                    "arr_time": arr_time,
                    "status": random.choice(flight_statuses),
                    "aircraft_icao": random.choice(aircraft_types),
                    "duration": self._format_duration(flight_duration),
                    "dep_terminal": str(random.randint(1, 5)),
                    "arr_terminal": str(random.randint(1, 5)),
                    "dep_gate": f"{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 50)}",
                    "arr_gate": f"{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 50)}",
                }
                
                self.flights.append(flight)
                flight_counter += 1
    
    def _calculate_flight_duration(self, dep_iata: str, arr_iata: str) -> int:
        """Calculate flight duration in minutes based on route."""
        # Simple approximation based on known major routes
        route_durations = {
            ("JFK", "LAX"): 360, ("LAX", "JFK"): 360,
            ("JFK", "LHR"): 420, ("LHR", "JFK"): 420,
            ("LAX", "HND"): 660, ("HND", "LAX"): 660,
            ("FRA", "DXB"): 360, ("DXB", "FRA"): 360,
            ("SYD", "SIN"): 480, ("SIN", "SYD"): 480,
            ("CDG", "AMS"): 75, ("AMS", "CDG"): 75,
            ("ORD", "YYZ"): 90, ("YYZ", "ORD"): 90,
            ("PEK", "HND"): 180, ("HND", "PEK"): 180,
            ("LHR", "DXB"): 420, ("DXB", "LHR"): 420,
            ("FRA", "SIN"): 720, ("SIN", "FRA"): 720,
        }
        
        return route_durations.get((dep_iata, arr_iata), 120)  # Default 2 hours
    
    def _format_duration(self, minutes: int) -> str:
        """Format duration as 'Xh Ym'."""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins:02d}m"
    
    def to_dict(self) -> Dict:
        """Return complete database as dictionary matching DATA CONTRACT."""
        return {
            "flights": self.flights,
            "airports": self.airports,
            "airlines": self.airlines
        }
    
    def save_to_json(self, filepath: str):
        """Save database to JSON file."""
        data = self.to_dict()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def generate_database(seed: Optional[int] = 42, output_path: Optional[str] = None):
    """
    Generate FlightRadar database and save to JSON.
    
    Args:
        seed: Random seed for deterministic generation (default: 42)
        output_path: Path to save JSON file. If None, uses recommended path.
    """
    if output_path is None:
        output_path = "generated\\travel_maps\\flightradar\\flightradar_database.json"
    
    generator = FlightRadarDatabaseGenerator(seed=seed)
    generator.save_to_json(output_path)
    
    print(f"Generated database with:")
    print(f"  - {len(generator.flights)} flights")
    print(f"  - {len(generator.airports)} airports")
    print(f"  - {len(generator.airlines)} airlines")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    # Generate database when run directly
    generate_database(seed=42)