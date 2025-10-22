    def generate_distance_matrix(self) -> List[Dict[str, Any]]:
        """Generate distance matrix data."""
        distance_matrix = []
        
        # Predefined routes between famous places
        routes = [
            ("1600 Amphitheatre Parkway, Mountain View, CA", "1 Infinite Loop, Cupertino, CA", 13197, 900),
            ("350 5th Ave, New York, NY", "Times Square, New York, NY", 1931, 480),
            ("Eiffel Tower, Paris, France", "Louvre Museum, Paris, France", 3380, 720),
            ("10600 N Tantau Ave, Cupertino, CA", "1600 Amphitheatre Parkway, Mountain View, CA", 13197, 900)
        ]
        
        for origin, destination, distance_meters, duration_seconds in routes:
            distance_matrix.append({
                "origin": origin,
                "destination": destination,
                "distance": {
                    "text": f"{distance_meters // 1609} mi",
                    "value": distance_meters
                },
                "duration": {
                    "text": f"{duration_seconds // 60} mins",
                    "value": duration_seconds
                }
            })
        
        return distance_matrix
    
    def generate_elevation_data(self, geocoding_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate elevation data."""
        elevation_data = []
        
        # Famous locations with known elevations
        famous_elevations = {
            "37.4220656,-122.0840897": 32.0,  # Googleplex
            "37.33182,-122.03118": 68.0,      # Apple Park
            "40.748817,-73.985428": 1250.0,   # Empire State Building area
            "48.8583701,2.2944813": 35.0,     # Eiffel Tower
            "51.523767,-0.158555": 25.0       # London
        }
        
        for entry in geocoding_data:
            location_key = f"{entry['latitude']},{entry['longitude']}"
            if location_key in famous_elevations:
                elevation = famous_elevations[location_key]
            else:
                elevation = round(random.uniform(0.0, 500.0), 1)
            
            elevation_data.append({
                "location": location_key,
                "elevation": elevation
            })
        
        return elevation_data
    
    def generate_directions(self) -> List[Dict[str, Any]]:
        """Generate directions data."""
        directions = []
        
        # Googleplex to Apple Park
        directions.append({
            "origin": "1600 Amphitheatre Parkway, Mountain View, CA",
            "destination": "1 Infinite Loop, Cupertino, CA",
            "summary": "I-280 S",
            "distance": {
                "text": "8.2 mi",
                "value": 13197
            },
            "duration": {
                "text": "15 mins",
                "value": 900
            },
            "steps": [
                {
                    "instruction": "Head northwest on Amphitheatre Pkwy",
                    "distance": {
                        "text": "0.2 mi",
                        "value": 322
                    },
                    "duration": {
                        "text": "1 min",
                        "value": 60
                    }
                },
                {
                    "instruction": "Turn right onto N Shoreline Blvd",
                    "distance": {
                        "text": "0.8 mi",
                        "value": 1287
                    },
                    "duration": {
                        "text": "2 mins",
                        "value": 120
                    }
                },
                {
                    "instruction": "Take the I-280 S ramp",
                    "distance": {
                        "text": "0.3 mi",
                        "value": 483
                    },
                    "duration": {
                        "text": "1 min",
                        "value": 60
                    }
                },
                {
                    "instruction": "Continue on I-280 S",
                    "distance": {
                        "text": "6.2 mi",
                        "value": 9978
                    },
                    "duration": {
                        "text": "9 mins",
                        "value": 540
                    }
                },
                {
                    "instruction": "Take exit 8 for N De Anza Blvd",
                    "distance": {
                        "text": "0.4 mi",
                        "value": 644
                    },
                    "duration": {
                        "text": "1 min",
                        "value": 60
                    }
                },
                {
                    "instruction": "Turn left onto N De Anza Blvd",
                    "distance": {
                        "text": "0.2 mi",
                        "value": 322
                    },
                    "duration": {
                        "text": "1 min",
                        "value": 60
                    }
                },
                {
                    "instruction": "Turn right onto Infinite Loop",
                    "distance": {
                        "text": "0.1 mi",
                        "value": 161
                    },
                    "duration": {
                        "text": "1 min",
                        "value": 60
                    }
                }
            ]
        })
        
        # Empire State Building to Times Square
        directions.append({
            "origin": "350 5th Ave, New York, NY",
            "destination": "Times Square, New York, NY",
            "summary": "7th Ave",
            "distance": {
                "text": "1.2 mi",
                "value": 1931
            },
            "duration": {
                "text": "8 mins",
                "value": 480
            },
            "steps": [
                {
                    "instruction": "Head south on 5th Ave",
                    "distance": {
                        "text": "0.3 mi",
                        "value": 483
                    },
                    "duration": {
                        "text": "2 mins",
                        "value": 120
                    }
                },
                {
                    "instruction": "Turn right onto W 34th St",
                    "distance": {
                        "text": "0.4 mi",
                        "value": 644
                    },
                    "duration": {
                        "text": "2 mins",
                        "value": 120
                    }
                },
                {
                    "instruction": "Turn left onto 7th Ave",
                    "distance": {
                        "text": "0.5 mi",
                        "value": 805
                    },
                    "duration": {
                        "text": "4 mins",
                        "value": 240
                    }
                }
            ]
        })
        
        return directions
    
    def generate_dataset(self, geocode_count: int = 8) -> Dict[str, Any]:
        """Generate complete dataset that matches server structure."""
        
        # Generate base geocoding data
        self.geocoding_data = self.generate_geocoding_data(geocode_count)
        
        # Generate all other data based on geocoding data
        dataset = {
            "geocoding_data": self.geocoding_data,
            "reverse_geocoding_data": self.generate_reverse_geocoding_data(self.geocoding_data),
            "places_data": self.generate_places_data(self.geocoding_data),
            "place_details": self.generate_place_details(self.generate_places_data(self.geocoding_data)),
            "distance_matrix": self.generate_distance_matrix(),
            "elevation_data": self.generate_elevation_data(self.geocoding_data),
            "directions": self.generate_directions()
        }
        
        return dataset


def main():
    """Main function to generate and save dataset."""
    parser = argparse.ArgumentParser(description='Generate Google Maps mock dataset')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for deterministic generation')
    parser.add_argument('--geocode_count', type=int, default=8, help='Number of geocoding entries to generate')
    
    args = parser.parse_args()
    
    # Generate dataset
    generator = GoogleMapsDatasetGenerator(seed=args.seed)
    dataset = generator.generate_dataset(geocode_count=args.geocode_count)
    
    # Save to JSON file
    output_path = "generated/google-maps/google_maps_dataset.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"Dataset generated successfully!")
    print(f"Output: {output_path}")
    print(f"Geocoding entries: {len(dataset['geocoding_data'])}")
    print(f"Places: {len(dataset['places_data'])}")
    print(f"Place details: {len(dataset['place_details'])}")
    print(f"Distance matrix entries: {len(dataset['distance_matrix'])}")
    print(f"Elevation data points: {len(dataset['elevation_data'])}")
    print(f"Directions: {len(dataset['directions'])}")


if __name__ == "__main__":
    main()