    def generate_place_details_data(self, count: int) -> List[Dict[str, Any]]:
        """Generate place details data."""
        results = []
        
        for i in range(count):
            business_type = self.random.choice(self.business_types)
            business_name = f"{self.random.choice(self.business_names)} {business_type.title()}"
            location = self.generate_coordinates()
            address = self.generate_address()
            
            result = {
                "input": f"ChIJ{self.random.randint(1000000000000000000, 9999999999999999999)}",
                "output": {
                    "status": "OK",
                    "result": {
                        "address_components": [
                            {"long_name": address.split(",")[0].split()[0], "short_name": address.split(",")[0].split()[0], "types": ["street_number"]},
                            {"long_name": " ".join(address.split(",")[0].split()[1:]), "short_name": " ".join(address.split(",")[0].split()[1:]), "types": ["route"]},
                            {"long_name": address.split(",")[1].strip(), "short_name": address.split(",")[1].strip(), "types": ["locality", "political"]},
                            {"long_name": address.split(",")[2].split()[0].strip(), "short_name": address.split(",")[2].split()[0].strip(), "types": ["administrative_area_level_1", "political"]},
                            {"long_name": "United States", "short_name": "US", "types": ["country", "political"]},
                            {"long_name": address.split()[-1], "short_name": address.split()[-1], "types": ["postal_code"]}
                        ],
                        "adr_address": f"<span class=\"street-address\">{address.split(',')[0]}</span>, <span class=\"locality\">{address.split(',')[1].strip()}</span>, <span class=\"region\">{address.split(',')[2].split()[0].strip()}</span> <span class=\"postal-code\">{address.split()[-1]}</span>, <span class=\"country-name\">USA</span>",
                        "business_status": "OPERATIONAL",
                        "formatted_address": address,
                        "formatted_phone_number": f"({self.random.randint(200, 999)}) {self.random.randint(200, 999)}-{self.random.randint(1000, 9999)}",
                        "geometry": {
                            "location": location,
                            "viewport": {
                                "northeast": {"lat": location["lat"] + 0.01, "lng": location["lng"] + 0.01},
                                "southwest": {"lat": location["lat"] - 0.01, "lng": location["lng"] - 0.01}
                            }
                        },
                        "icon": f"https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/{business_type}-71.png",
                        "name": business_name,
                        "opening_hours": {
                            "open_now": self.random.choice([True, False]),
                            "periods": [
                                {
                                    "close": {"day": 0, "time": "2100"},
                                    "open": {"day": 0, "time": "0900"}
                                }
                            ],
                            "weekday_text": [
                                "Monday: 9:00 AM – 9:00 PM",
                                "Tuesday: 9:00 AM – 9:00 PM",
                                "Wednesday: 9:00 AM – 9:00 PM",
                                "Thursday: 9:00 AM – 9:00 PM",
                                "Friday: 9:00 AM – 9:00 PM",
                                "Saturday: 9:00 AM – 9:00 PM",
                                "Sunday: 9:00 AM – 9:00 PM"
                            ]
                        },
                        "photos": [
                            {
                                "height": 3024,
                                "html_attributions": ["<a href=\"https://maps.google.com/maps/contrib/123456789\">A Google User</a>"],
                                "photo_reference": f"Aap_uEDO{self.random.randint(1000000000000000000, 9999999999999999999)}",
                                "width": 4032
                            }
                        ],
                        "place_id": f"ChIJ{self.random.randint(1000000000000000000, 9999999999999999999)}",
                        "rating": round(self.random.uniform(3.0, 5.0), 1),
                        "types": [business_type, "point_of_interest", "establishment"],
                        "url": f"https://maps.google.com/?q={business_name.replace(' ', '+')}&ftid=0x89c259abcdef1234:0x56789def01234567",
                        "user_ratings_total": self.random.randint(10, 1000),
                        "vicinity": address,
                        "website": f"https://www.{business_name.lower().replace(' ', '')}.com"
                    }
                }
            }
            results.append(result)
        
        return results
    
    def generate_distance_matrix_data(self, count: int) -> List[Dict[str, Any]]:
        """Generate distance matrix data."""
        results = []
        
        for i in range(count):
            origin = self.generate_coordinates()
            destination = self.generate_coordinates()
            distance_meters = self.random.randint(1000, 50000)
            duration_seconds = self.random.randint(300, 3600)
            
            result = {
                "input": {
                    "origins": [origin],
                    "destinations": [destination],
                    "mode": "driving"
                },
                "output": {
                    "status": "OK",
                    "origin_addresses": [self.generate_address()],
                    "destination_addresses": [self.generate_address()],
                    "rows": [
                        {
                            "elements": [
                                {
                                    "status": "OK",
                                    "distance": {
                                        "text": f"{round(distance_meters / 1609.34, 1)} mi",
                                        "value": distance_meters
                                    },
                                    "duration": {
                                        "text": f"{duration_seconds // 60} mins",
                                        "value": duration_seconds
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
            results.append(result)
        
        return results
    
    def generate_elevation_data(self, count: int) -> List[Dict[str, Any]]:
        """Generate elevation data."""
        results = []
        
        for i in range(count):
            location = self.generate_coordinates()
            elevation = self.random.uniform(-100, 3000)
            
            result = {
                "input": [location],
                "output": {
                    "status": "OK",
                    "results": [
                        {
                            "elevation": round(elevation, 2),
                            "location": location,
                            "resolution": self.random.choice([1.0, 4.0, 19.0, 76.0])
                        }
                    ]
                }
            }
            results.append(result)
        
        return results
    
    def generate_timezone_data(self, count: int) -> List[Dict[str, Any]]:
        """Generate timezone data."""
        results = []
        
        for i in range(count):
            location = self.generate_coordinates()
            timestamp = int(datetime.now().timestamp())
            timezone_id = self.random.choice([
                "America/New_York", "America/Los_Angeles", "America/Chicago",
                "America/Denver", "America/Phoenix", "America/Anchorage"
            ])
            
            result = {
                "input": {
                    "location": location,
                    "timestamp": timestamp
                },
                "output": {
                    "status": "OK",
                    "dstOffset": 3600,
                    "rawOffset": self.random.choice([-18000, -21600, -25200, -28800]),
                    "timeZoneId": timezone_id,
                    "timeZoneName": timezone_id.replace("America/", "").replace("_", " ") + " Time"
                }
            }
            results.append(result)
        
        return results
    
    def generate_roads_data(self, count: int) -> List[Dict[str, Any]]:
        """Generate roads data (nearest roads and snap to roads)."""
        results = []
        
        for i in range(count):
            points = [self.generate_coordinates() for _ in range(3)]
            
            result = {
                "input": points,
                "output": {
                    "status": "OK",
                    "snappedPoints": [
                        {
                            "location": {
                                "latitude": point["lat"],
                                "longitude": point["lng"]
                            },
                            "originalIndex": idx,
                            "placeId": f"ChIJ{self.random.randint(1000000000000000000, 9999999999999999999)}"
                        }
                        for idx, point in enumerate(points)
                    ]
                }
            }
            results.append(result)
        
        return results
    
    def generate_dataset(self, count: int = 10) -> Dict[str, Any]:
        """Generate complete dataset for all endpoints."""
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "seed": self.seed,
                "count_per_endpoint": count,
                "description": "Deterministic mock dataset for Google Maps MCP server"
            },
            "geocoding": self.generate_geocoding_data(count),
            "reverse_geocoding": self.generate_reverse_geocoding_data(count),
            "places": self.generate_places_data(count),
            "place_details": self.generate_place_details_data(count),
            "distance_matrix": self.generate_distance_matrix_data(count),
            "elevation": self.generate_elevation_data(count),
            "timezone": self.generate_timezone_data(count),
            "roads": self.generate_roads_data(count)
        }


def main():
    """Main function to generate and save dataset."""
    parser = argparse.ArgumentParser(description="Generate Google Maps mock dataset")
    parser.add_argument("--count", type=int, default=10, help="Number of records per endpoint")
    parser.add_argument("--seed", type=int, help="Random seed for deterministic generation")
    parser.add_argument("--output", type=str, default="generated/google-maps_dataset.json", 
                       help="Output JSON file path")
    
    args = parser.parse_args()
    
    # Generate dataset
    generator = GoogleMapsDatasetGenerator(seed=args.seed)
    dataset = generator.generate_dataset(count=args.count)
    
    # Save to file
    with open(args.output, 'w') as f:
        json.dump(dataset, f, indent=2)
    
    print(f"Dataset generated successfully!")
    print(f"Records per endpoint: {args.count}")
    print(f"Seed: {args.seed}")
    print(f"Output file: {args.output}")
    print(f"Total records: {sum(len(dataset[key]) for key in dataset if key != 'metadata')}")


if __name__ == "__main__":
    main()