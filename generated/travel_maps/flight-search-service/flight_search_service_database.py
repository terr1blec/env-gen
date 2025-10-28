"""
Flight Search Service Database Generator

This module generates a deterministic offline database for flight search operations.
The database includes flights, airports, airlines, and bookings data.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any


class FlightDatabaseGenerator:
    """Generates deterministic flight search database."""
    
    def __init__(self, seed: int = 42):
        """Initialize with a seed for deterministic generation."""
        self.seed = seed
        random.seed(seed)
        
        # Core data structures
        self.airports = []
        self.airlines = []
        self.flights = []
        self.bookings = []
        
        self._initialize_base_data()
    
    def _initialize_base_data(self):
        """Initialize base airports and airlines data."""
        # Major international airports
        self.airports = [
            {"code": "JFK", "name": "John F. Kennedy International Airport", "city": "New York", "country": "USA", "timezone": "America/New_York"},
            {"code": "LAX", "name": "Los Angeles International Airport", "city": "Los Angeles", "country": "USA", "timezone": "America/Los_Angeles"},
            {"code": "LHR", "name": "Heathrow Airport", "city": "London", "country": "UK", "timezone": "Europe/London"},
            {"code": "CDG", "name": "Charles de Gaulle Airport", "city": "Paris", "country": "France", "timezone": "Europe/Paris"},
            {"code": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany", "timezone": "Europe/Berlin"},
            {"code": "DXB", "name": "Dubai International Airport", "city": "Dubai", "country": "UAE", "timezone": "Asia/Dubai"},
            {"code": "SIN", "name": "Singapore Changi Airport", "city": "Singapore", "country": "Singapore", "timezone": "Asia/Singapore"},
            {"code": "HND", "name": "Haneda Airport", "city": "Tokyo", "country": "Japan", "timezone": "Asia/Tokyo"},
            {"code": "SYD", "name": "Sydney Kingsford Smith Airport", "city": "Sydney", "country": "Australia", "timezone": "Australia/Sydney"},
            {"code": "YYZ", "name": "Toronto Pearson International Airport", "city": "Toronto", "country": "Canada", "timezone": "America/Toronto"},
            {"code": "MEX", "name": "Mexico City International Airport", "city": "Mexico City", "country": "Mexico", "timezone": "America/Mexico_City"},
            {"code": "GRU", "name": "São Paulo–Guarulhos International Airport", "city": "São Paulo", "country": "Brazil", "timezone": "America/Sao_Paulo"}
        ]
        
        # Major airlines
        self.airlines = [
            {"code": "DL", "name": "Delta Air Lines", "hub_airport": "ATL"},
            {"code": "UA", "name": "United Airlines", "hub_airport": "ORD"},
            {"code": "AA", "name": "American Airlines", "hub_airport": "DFW"},
            {"code": "BA", "name": "British Airways", "hub_airport": "LHR"},
            {"code": "AF", "name": "Air France", "hub_airport": "CDG"},
            {"code": "LH", "name": "Lufthansa", "hub_airport": "FRA"},
            {"code": "EK", "name": "Emirates", "hub_airport": "DXB"},
            {"code": "SQ", "name": "Singapore Airlines", "hub_airport": "SIN"},
            {"code": "JL", "name": "Japan Airlines", "hub_airport": "HND"},
            {"code": "QF", "name": "Qantas", "hub_airport": "SYD"}
        ]
    
    def _generate_flight_number(self, airline_code: str) -> str:
        """Generate a realistic flight number."""
        return f"{airline_code}{random.randint(100, 9999)}"
    
    def _generate_time(self, base_hour: int, variation: int = 2) -> str:
        """Generate a flight time with some variation."""
        hour = (base_hour + random.randint(-variation, variation)) % 24
        minute = random.choice([0, 15, 30, 45])
        return f"{hour:02d}:{minute:02d}"
    
    def _calculate_arrival_time(self, departure_time: str, duration: str) -> str:
        """Calculate arrival time based on departure time and duration."""
        dep_hour, dep_minute = map(int, departure_time.split(':'))
        dur_hour, dur_minute = map(int, duration.split(':'))
        
        total_minutes = dep_hour * 60 + dep_minute + dur_hour * 60 + dur_minute
        arr_hour = (total_minutes // 60) % 24
        arr_minute = total_minutes % 60
        
        return f"{arr_hour:02d}:{arr_minute:02d}"
    
    def _generate_duration(self, distance_category: str) -> str:
        """Generate flight duration based on distance category."""
        if distance_category == "short":
            hours = random.randint(1, 3)
        elif distance_category == "medium":
            hours = random.randint(3, 6)
        else:  # long
            hours = random.randint(6, 14)
        
        minutes = random.choice([0, 15, 30, 45])
        return f"{hours:02d}:{minutes:02d}"
    
    def _get_distance_category(self, departure: str, arrival: str) -> str:
        """Determine distance category between airports."""
        # Simple categorization based on continent/country
        us_airports = {"JFK", "LAX"}
        europe_airports = {"LHR", "CDG", "FRA"}
        asia_airports = {"DXB", "SIN", "HND"}
        
        if departure in us_airports and arrival in us_airports:
            return "medium" if departure != arrival else "short"
        elif (departure in us_airports and arrival in europe_airports) or \
             (departure in europe_airports and arrival in us_airports):
            return "long"
        elif (departure in us_airports and arrival in asia_airports) or \
             (departure in asia_airports and arrival in us_airports):
            return "long"
        elif (departure in europe_airports and arrival in asia_airports) or \
             (departure in asia_airports and arrival in europe_airports):
            return "long"
        else:
            return "medium"
    
    def generate_flights(self, count: int = 60):
        """Generate flight data."""
        aircraft_types = ["Boeing 737", "Boeing 777", "Boeing 787", "Airbus A320", "Airbus A330", "Airbus A350"]
        
        flight_id_counter = 1
        
        # Generate popular routes
        popular_routes = [
            ("JFK", "LAX"), ("LAX", "JFK"),
            ("JFK", "LHR"), ("LHR", "JFK"),
            ("LAX", "LHR"), ("LHR", "LAX"),
            ("JFK", "CDG"), ("CDG", "JFK"),
            ("LAX", "SYD"), ("SYD", "LAX"),
            ("LHR", "CDG"), ("CDG", "LHR"),
            ("FRA", "JFK"), ("JFK", "FRA"),
            ("DXB", "LHR"), ("LHR", "DXB"),
            ("SIN", "HND"), ("HND", "SIN"),
            ("JFK", "YYZ"), ("YYZ", "JFK"),
            ("LAX", "MEX"), ("MEX", "LAX")
        ]
        
        # Generate flights for popular routes
        for departure, arrival in popular_routes:
            for _ in range(2):  # Multiple flights per route
                airline = random.choice(self.airlines)
                distance_category = self._get_distance_category(departure, arrival)
                duration = self._generate_duration(distance_category)
                
                # Base departure times for different flight types
                if random.random() < 0.5:  # Morning flights
                    departure_time = self._generate_time(8)
                else:  # Afternoon/evening flights
                    departure_time = self._generate_time(16)
                
                arrival_time = self._calculate_arrival_time(departure_time, duration)
                
                flight = {
                    "flight_id": f"FL{flight_id_counter:04d}",
                    "airline": airline["code"],
                    "flight_number": self._generate_flight_number(airline["code"]),
                    "departure_airport": departure,
                    "arrival_airport": arrival,
                    "departure_time": departure_time,
                    "arrival_time": arrival_time,
                    "duration": duration,
                    "price": round(random.uniform(150, 1200), 2),
                    "available_seats": random.randint(5, 200),
                    "aircraft_type": random.choice(aircraft_types)
                }
                
                self.flights.append(flight)
                flight_id_counter += 1
        
        # Generate additional random flights to reach count
        while len(self.flights) < count:
            departure = random.choice(self.airports)["code"]
            arrival = random.choice([a for a in self.airports if a["code"] != departure])["code"]
            
            # Avoid duplicate routes
            if (departure, arrival) not in [(f["departure_airport"], f["arrival_airport"]) for f in self.flights]:
                airline = random.choice(self.airlines)
                distance_category = self._get_distance_category(departure, arrival)
                duration = self._generate_duration(distance_category)
                departure_time = self._generate_time(random.randint(6, 22))
                arrival_time = self._calculate_arrival_time(departure_time, duration)
                
                flight = {
                    "flight_id": f"FL{flight_id_counter:04d}",
                    "airline": airline["code"],
                    "flight_number": self._generate_flight_number(airline["code"]),
                    "departure_airport": departure,
                    "arrival_airport": arrival,
                    "departure_time": departure_time,
                    "arrival_time": arrival_time,
                    "duration": duration,
                    "price": round(random.uniform(100, 1500), 2),
                    "available_seats": random.randint(5, 250),
                    "aircraft_type": random.choice(aircraft_types)
                }
                
                self.flights.append(flight)
                flight_id_counter += 1
    
    def generate_bookings(self, count: int = 30):
        """Generate booking data."""
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa", "James", "Maria"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
        
        booking_id_counter = 1
        
        for _ in range(count):
            flight = random.choice(self.flights)
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            booking = {
                "booking_id": f"BK{booking_id_counter:04d}",
                "flight_id": flight["flight_id"],
                "passenger_name": f"{first_name} {last_name}",
                "passenger_email": f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}",
                "seat_number": f"{random.randint(1, 30)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}",
                "booking_status": random.choice(["confirmed", "confirmed", "confirmed", "pending", "cancelled"]),
                "booking_date": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
            }
            
            self.bookings.append(booking)
            booking_id_counter += 1
    
    def generate_database(self, flights_count: int = 60, bookings_count: int = 30) -> Dict[str, Any]:
        """Generate complete database."""
        self.generate_flights(flights_count)
        self.generate_bookings(bookings_count)
        
        return {
            "flights": self.flights,
            "airports": self.airports,
            "airlines": self.airlines,
            "bookings": self.bookings
        }


def generate_flight_database(
    seed: int = 42,
    flights_count: int = 60,
    bookings_count: int = 30,
    output_path: str = None
) -> Dict[str, Any]:
    """
    Generate a deterministic flight search database.
    
    Args:
        seed: Random seed for deterministic generation
        flights_count: Number of flights to generate
        bookings_count: Number of bookings to generate
        output_path: Optional path to write JSON output
    
    Returns:
        Dictionary containing the complete database
    """
    generator = FlightDatabaseGenerator(seed)
    database = generator.generate_database(flights_count, bookings_count)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
    
    return database


if __name__ == "__main__":
    # Generate and save the database
    database = generate_flight_database(
        seed=42,
        flights_count=60,
        bookings_count=30,
        output_path="flight_search_service_database.json"
    )
    
    print(f"Generated database with:")
    print(f"- {len(database['flights'])} flights")
    print(f"- {len(database['airports'])} airports")
    print(f"- {len(database['airlines'])} airlines")
    print(f"- {len(database['bookings'])} bookings")