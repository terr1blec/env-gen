"""
GeoPal Travel and Logistics Server - Offline Database Generator

This module generates deterministic synthetic data for the GeoPal travel and logistics
server, following the DATA CONTRACT schema exactly.
"""

import json
import random
from pathlib import Path
from typing import Dict, Any, Optional, List


class GeoPalDatabaseGenerator:
    """Generator for deterministic synthetic travel and logistics data."""
    
    def __init__(self, seed: Optional[int] = 42):
        """Initialize generator with optional seed for deterministic output."""
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        
        # European city coordinates for realistic data
        self.cities = {
            'berlin': [13.4050, 52.5200],
            'paris': [2.3522, 48.8566],
            'london': [-0.1276, 51.5074],
            'rome': [12.4964, 41.9028],
            'madrid': [-3.7038, 40.4168],
            'amsterdam': [4.9041, 52.3676],
            'brussels': [4.3517, 50.8503],
            'vienna': [16.3738, 48.2082],
            'prague': [14.4378, 50.0755],
            'budapest': [19.0402, 47.4979]
        }
        
        self.profiles = ['driving', 'cycling', 'walking', 'truck']
        self.poi_categories = ['restaurant', 'hotel', 'gas_station', 'parking', 'shopping']
    
    def generate_geocoding_results(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate geocoding results for major cities and landmarks."""
        results = []
        city_names = list(self.cities.keys())
        
        for i in range(count):
            city = city_names[i % len(city_names)]
            coords = self.cities[city]
            
            # Add slight variation to coordinates for realism
            variation = random.uniform(-0.01, 0.01)
            coords_varied = [coords[0] + variation, coords[1] + variation]
            
            result = {
                'query': f"{city.capitalize()} Central Station",
                'coordinates': coords_varied,
                'properties': {
                    'city': city.capitalize(),
                    'country': 'Germany' if city == 'berlin' else 'France' if city == 'paris' else 'UK' if city == 'london' else 'Italy' if city == 'rome' else 'Spain' if city == 'madrid' else 'Netherlands' if city == 'amsterdam' else 'Belgium' if city == 'brussels' else 'Austria' if city == 'vienna' else 'Czech Republic' if city == 'prague' else 'Hungary',
                    'type': 'station',
                    'postcode': f"{10000 + i}"
                },
                'confidence': random.uniform(0.85, 0.98)
            }
            results.append(result)
        
        return results
    
    def generate_isochrone_data(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generate isochrone data for different locations and profiles."""
        results = []
        city_names = list(self.cities.keys())
        
        for i in range(count):
            city = city_names[i % len(city_names)]
            coords = self.cities[city]
            profile = self.profiles[i % len(self.profiles)]
            
            # Different range types and values
            if profile == 'driving':
                ranges = [300, 600, 900, 1200]  # 5, 10, 15, 20 minutes
            elif profile == 'cycling':
                ranges = [600, 1200, 1800, 2400]  # 10, 20, 30, 40 minutes
            else:
                ranges = [900, 1800, 2700, 3600]  # 15, 30, 45, 60 minutes
            
            # Generate simple polygon around location
            base_lon, base_lat = coords
            polygon_coords = [
                [base_lon - 0.01, base_lat - 0.01],
                [base_lon + 0.01, base_lat - 0.01],
                [base_lon + 0.01, base_lat + 0.01],
                [base_lon - 0.01, base_lat + 0.01],
                [base_lon - 0.01, base_lat - 0.01]
            ]
            
            result = {
                'locations': [coords],
                'profile': profile,
                'range': ranges,
                'range_type': 'time',
                'polygons': [
                    {
                        'type': 'Feature',
                        'properties': {'range': range_val},
                        'geometry': {
                            'type': 'Polygon',
                            'coordinates': [polygon_coords]
                        }
                    }
                    for range_val in ranges
                ]
            }
            results.append(result)
        
        return results
    
    def generate_poi_data(self, count: int = 100) -> List[Dict[str, Any]]:
        """Generate POI data across different categories."""
        results = []
        city_names = list(self.cities.keys())
        
        for i in range(count):
            city = city_names[i % len(city_names)]
            coords = self.cities[city]
            
            # Add variation for different POIs
            variation_lon = random.uniform(-0.02, 0.02)
            variation_lat = random.uniform(-0.02, 0.02)
            poi_coords = [coords[0] + variation_lon, coords[1] + variation_lat]
            
            category = self.poi_categories[i % len(self.poi_categories)]
            
            result = {
                'coordinates': coords,
                'buffer': random.choice([500, 1000, 2000]),
                'limit': random.choice([5, 10, 20]),
                'filters': {
                    'category': category,
                    'subcategory': f'{category}_sub_{i % 3}'
                },
                'features': [
                    {
                        'id': f'poi_{i}_{j}',
                        'type': 'Feature',
                        'properties': {
                            'name': f'{category.capitalize()} {i}_{j}',
                            'category': category,
                            'subcategory': f'{category}_sub_{i % 3}',
                            'rating': round(random.uniform(3.0, 5.0), 1),
                            'address': f'Street {i}, {city.capitalize()}'
                        },
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [poi_coords[0] + j * 0.001, poi_coords[1] + j * 0.001]
                        }
                    }
                    for j in range(random.randint(1, 5))
                ]
            }
            results.append(result)
        
        return results
    
    def generate_route_data(self, count: int = 30) -> List[Dict[str, Any]]:
        """Generate route data between major locations."""
        results = []
        city_names = list(self.cities.keys())
        
        for i in range(count):
            start_city = city_names[i % len(city_names)]
            end_city = city_names[(i + 1) % len(city_names)]
            
            start_coords = self.cities[start_city]
            end_coords = self.cities[end_city]
            profile = self.profiles[i % len(self.profiles)]
            
            # Calculate approximate distance and duration
            lat_diff = abs(start_coords[1] - end_coords[1])
            lon_diff = abs(start_coords[0] - end_coords[0])
            
            # Rough approximation: 1 degree ≈ 111km
            distance_km = int((lat_diff + lon_diff) * 111 * 1000)  # meters
            
            if profile == 'driving':
                duration = int(distance_km / 1000 * 60 * 60 / 80)  # 80 km/h average
            elif profile == 'cycling':
                duration = int(distance_km / 1000 * 60 * 60 / 15)  # 15 km/h average
            elif profile == 'walking':
                duration = int(distance_km / 1000 * 60 * 60 / 5)   # 5 km/h average
            else:  # truck
                duration = int(distance_km / 1000 * 60 * 60 / 60)  # 60 km/h average
            
            result = {
                'start': start_coords,
                'end': end_coords,
                'profile': profile,
                'distance': distance_km,
                'duration': duration,
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [start_coords, end_coords]
                }
            }
            results.append(result)
        
        return results
    
    def generate_optimization_data(self, count: int = 15) -> List[Dict[str, Any]]:
        """Generate vehicle routing optimization data."""
        results = []
        city_names = list(self.cities.keys())
        
        for i in range(count):
            num_jobs = random.randint(2, 5)
            num_vehicles = random.randint(1, 2)
            
            jobs = []
            for j in range(num_jobs):
                city_idx = (i + j) % len(city_names)
                coords = self.cities[city_names[city_idx]]
                
                job = {
                    'id': j,
                    'location': coords,
                    'service': random.choice([300, 600, 900]),  # 5, 10, 15 minutes
                    'delivery': [random.randint(1, 10)],
                    'time_windows': [[28800, 43200], [46800, 61200]]  # 8-12, 13-17
                }
                jobs.append(job)
            
            vehicles = []
            for v in range(num_vehicles):
                start_city = city_names[i % len(city_names)]
                end_city = city_names[(i + 1) % len(city_names)]
                
                vehicle = {
                    'id': v,
                    'start': self.cities[start_city],
                    'end': self.cities[end_city],
                    'capacity': [random.choice([20, 50, 100])],
                    'skills': [1],
                    'time_window': [25200, 68400]  # 7-19
                }
                vehicles.append(vehicle)
            
            shipments = []
            for s in range(random.randint(1, 3)):
                pickup_city = city_names[(i + s) % len(city_names)]
                delivery_city = city_names[(i + s + 1) % len(city_names)]
                
                shipment = {
                    'pickup': {
                        'id': f'p{s}',
                        'location': self.cities[pickup_city],
                        'service': 300
                    },
                    'delivery': {
                        'id': f'd{s}',
                        'location': self.cities[delivery_city],
                        'service': 300
                    }
                }
                shipments.append(shipment)
            
            # Calculate solution metrics
            total_distance = sum(job['service'] * 100 for job in jobs)  # rough estimate
            total_time = total_distance // 10  # rough estimate
            
            solution = {
                'total_distance': total_distance,
                'total_time': total_time,
                'routes': [
                    {
                        'vehicle': v,
                        'activities': [
                            {'type': 'start', 'location': vehicles[v]['start']},
                            *[{'type': 'job', 'job_id': j} for j in range(num_jobs)],
                            {'type': 'end', 'location': vehicles[v]['end']}
                        ]
                    }
                    for v in range(num_vehicles)
                ]
            }
            
            result = {
                'jobs': jobs,
                'vehicles': vehicles,
                'shipments': shipments,
                'solution': solution
            }
            results.append(result)
        
        return results
    
    def generate_traveling_salesman_data(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate traveling salesman problem data."""
        results = []
        city_names = list(self.cities.keys())
        
        for i in range(count):
            num_locations = random.randint(3, 6)
            locations = []
            
            for j in range(num_locations):
                city_idx = (i + j) % len(city_names)
                locations.append(self.cities[city_names[city_idx]])
            
            start_location = locations[0]
            return_to_start = random.choice([True, False])
            
            # Calculate solution metrics
            total_distance = num_locations * 100000  # rough estimate
            total_time = total_distance // 25  # rough estimate
            
            solution = {
                'total_distance': total_distance,
                'total_time': total_time,
                'route': locations if not return_to_start else locations + [locations[0]]
            }
            
            result = {
                'locations': locations,
                'start_location': start_location,
                'return_to_start': return_to_start,
                'solution': solution
            }
            results.append(result)
        
        return results
    
    def generate_database(self) -> Dict[str, Any]:
        """Generate complete database with all data types."""
        return {
            'geocoding_results': self.generate_geocoding_results(50),
            'isochrone_data': self.generate_isochrone_data(20),
            'poi_data': self.generate_poi_data(100),
            'route_data': self.generate_route_data(30),
            'optimization_data': self.generate_optimization_data(15),
            'traveling_salesman_data': self.generate_traveling_salesman_data(10)
        }