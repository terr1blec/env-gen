"""
SNCF API Server Database Generator

Generates deterministic synthetic data for French train stations, journeys, disruptions, and schedules.
Exports data following the DATA CONTRACT structure.
"""

import json
import random
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class SNCFDatabaseGenerator:
    """Generates deterministic synthetic SNCF data."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize with optional seed for deterministic generation."""
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        
        # Major French cities and their coordinates
        self.cities = {
            "Paris": {"lat": 48.8566, "lon": 2.3522},
            "Lyon": {"lat": 45.7640, "lon": 4.8357},
            "Marseille": {"lat": 43.2965, "lon": 5.3698},
            "Bordeaux": {"lat": 44.8378, "lon": -0.5792},
            "Lille": {"lat": 50.6292, "lon": 3.0573}
        }
        
        # Transport types
        self.transport_types = ["TGV", "TER", "Intercités", "RER", "Transilien"]
        
        # Common nearby places
        self.nearby_places = [
            "Shopping Center", "Hotel", "Restaurant", "Tourist Information", 
            "Car Rental", "Bus Station", "Taxi Stand", "Parking", "Bike Rental"
        ]
        
        # Train lines
        self.train_lines = [
            "TGV Atlantique", "TGV Est", "TGV Nord", "TGV Sud-Est", 
            "TER Auvergne-Rhône-Alpes", "TER Hauts-de-France"
        ]
        
        # Disruption severities
        self.severities = ["low", "medium", "high", "critical"]
        
        # Disruption messages
        self.disruption_messages = [
            "Signal failure causing delays",
            "Track maintenance work",
            "Staff strike affecting services",
            "Weather conditions causing disruptions"
        ]

    def generate_stations(self) -> List[Dict[str, Any]]:
        """Generate synthetic station data."""
        stations = []
        station_id = 1
        
        for city_name, coords in self.cities.items():
            # Main station for each city
            stations.append({
                "id": f"station_{station_id:03d}",
                "name": f"{city_name} Gare Centrale",
                "city": city_name,
                "coordinates": {
                    "lat": coords["lat"],
                    "lon": coords["lon"]
                },
                "transport_types": random.sample(self.transport_types, random.randint(2, 4)),
                "nearby_places": random.sample(self.nearby_places, random.randint(3, 6))
            })
            station_id += 1
        
        return stations

    def generate_journeys(self, stations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate synthetic journey data between cities."""
        journeys = []
        journey_id = 1
        
        # Create city to station mapping
        city_stations = {}
        for station in stations:
            city = station["city"]
            if city not in city_stations:
                city_stations[city] = []
            city_stations[city].append(station["id"])
        
        cities = list(city_stations.keys())
        
        # Generate journeys between different city pairs
        for i, from_city in enumerate(cities):
            for j, to_city in enumerate(cities):
                if from_city != to_city and random.random() < 0.5:  # 50% chance for connection
                    # Generate 1-2 journey options
                    for _ in range(random.randint(1, 2)):
                        base_duration = self._calculate_base_duration(from_city, to_city)
                        duration = base_duration + random.randint(-15, 30)  # Some variation
                        
                        # Generate realistic departure/arrival times
                        departure_hour = random.randint(6, 22)
                        departure_minute = random.choice([0, 15, 30, 45])
                        departure_time = f"2024-01-15T{departure_hour:02d}:{departure_minute:02d}:00Z"
                        
                        arrival_time_dt = datetime.fromisoformat(departure_time.replace('Z', '+00:00')) + timedelta(minutes=duration)
                        arrival_time = arrival_time_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                        
                        journeys.append({
                            "id": f"journey_{journey_id:03d}",
                            "from_city": from_city,
                            "to_city": to_city,
                            "departure_time": departure_time,
                            "arrival_time": arrival_time,
                            "duration": duration,
                            "transfers": random.randint(0, 1),
                            "price": round(random.uniform(25, 150), 2)
                        })
                        journey_id += 1
        
        return journeys

    def _calculate_base_duration(self, from_city: str, to_city: str) -> int:
        """Calculate base journey duration between cities (in minutes)."""
        # Approximate travel times between major French cities
        distances = {
            ("Paris", "Lyon"): 120,
            ("Paris", "Marseille"): 210,
            ("Paris", "Bordeaux"): 150,
            ("Paris", "Lille"): 60,
            ("Lyon", "Marseille"): 105,
            ("Lyon", "Bordeaux"): 240
        }
        
        # Look for exact match or reverse
        key = (from_city, to_city)
        reverse_key = (to_city, from_city)
        
        if key in distances:
            return distances[key]
        elif reverse_key in distances:
            return distances[reverse_key]
        else:
            # Default duration for other connections
            return random.randint(90, 300)

    def generate_disruptions(self, stations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate synthetic disruption data."""
        disruptions = []
        disruption_id = 1
        
        # Get station IDs and cities
        station_ids = [s["id"] for s in stations]
        
        # Generate 3-5 disruptions
        for _ in range(random.randint(3, 5)):
            severity = random.choice(self.severities)
            message = random.choice(self.disruption_messages)
            
            # Determine affected stations (1-2 stations)
            affected_stations = random.sample(station_ids, random.randint(1, 2))
            
            # Determine affected lines (1-2 lines)
            affected_lines = random.sample(self.train_lines, random.randint(1, 2))
            
            # Generate time range (starting today, lasting 2-24 hours)
            start_time = datetime.now().replace(hour=random.randint(0, 23), minute=0, second=0, microsecond=0)
            duration_hours = random.randint(2, 24)
            end_time = start_time + timedelta(hours=duration_hours)
            
            disruptions.append({
                "id": f"disruption_{disruption_id:03d}",
                "severity": severity,
                "message": message,
                "affected_stations": affected_stations,
                "affected_lines": affected_lines,
                "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            })
            disruption_id += 1
        
        return disruptions

    def generate_schedules(self, stations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate synthetic schedule data."""
        schedules = []
        
        # Generate schedules for each station for the next 2 hours
        base_time = datetime.now().replace(minute=0, second=0, microsecond=0)
        
        for station in stations:
            station_id = station["id"]
            
            # Generate schedule for current hour and next hour
            for hour_offset in range(2):
                schedule_time = base_time + timedelta(hours=hour_offset)
                
                departures = self._generate_departures_arrivals(station_id, "departure", schedule_time)
                arrivals = self._generate_departures_arrivals(station_id, "arrival", schedule_time)
                
                schedules.append({
                    "station_id": station_id,
                    "datetime": schedule_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "departures": departures,
                    "arrivals": arrivals
                })
        
        return schedules

    def _generate_departures_arrivals(self, station_id: str, type_: str, base_time: datetime) -> List[Dict[str, Any]]:
        """Generate departure or arrival data for a station."""
        items = []
        
        # Generate 2-4 departures/arrivals per hour
        for _ in range(random.randint(2, 4)):
            minute = random.choice([0, 15, 30, 45])
            time = base_time.replace(minute=minute)
            
            # Determine destination/origin
            if type_ == "departure":
                destination = random.choice([city for city in self.cities.keys() if city != "Paris"])  # Avoid Paris for variety
                status = random.choice(["on time", "delayed", "cancelled"])
                platform = random.randint(1, 12)
            else:  # arrival
                origin = random.choice([city for city in self.cities.keys() if city != "Paris"])  # Avoid Paris for variety
                status = random.choice(["on time", "delayed", "arrived"])
                platform = random.randint(1, 12)
            
            item = {
                "time": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "train_type": random.choice(self.transport_types),
                "train_number": f"{random.randint(5000, 9999)}",
                "status": status,
                "platform": platform
            }
            
            if type_ == "departure":
                item["destination"] = destination
            else:
                item["origin"] = origin
            
            items.append(item)
        
        return items

    def generate_database(self) -> Dict[str, Any]:
        """Generate complete database following DATA CONTRACT."""
        stations = self.generate_stations()
        journeys = self.generate_journeys(stations)
        disruptions = self.generate_disruptions(stations)
        schedules = self.generate_schedules(stations)
        
        return {
            "stations": stations,
            "journeys": journeys,
            "disruptions": disruptions,
            "schedules": schedules
        }


def generate_database(seed: Optional[int] = 42) -> Dict[str, Any]:
    """
    Generate deterministic synthetic SNCF database.
    
    Args:
        seed: Random seed for deterministic generation (default: 42)
        
    Returns:
        Dictionary containing stations, journeys, disruptions, and schedules
    """
    generator = SNCFDatabaseGenerator(seed=seed)
    return generator.generate_database()


def write_database_to_file(database: Dict[str, Any], filepath: str) -> None:
    """Write database to JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # Generate and write database when run directly
    import os
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "sncf_api_server_database.json")
    
    # Generate database with deterministic seed
    database = generate_database(seed=42)
    
    # Write to file
    write_database_to_file(database, output_path)
    
    print(f"Database generated with:")
    print(f"  - {len(database['stations'])} stations")
    print(f"  - {len(database['journeys'])} journeys")
    print(f"  - {len(database['disruptions'])} disruptions")
    print(f"  - {len(database['schedules'])} schedules")
    print(f"Written to: {output_path}")