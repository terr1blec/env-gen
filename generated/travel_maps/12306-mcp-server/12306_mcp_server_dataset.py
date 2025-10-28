"""
12306 MCP Server Dataset Synthesis Module

Generates deterministic mock datasets for Chinese railway train schedules.
Supports parameters for controlling data generation and seed for reproducibility.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class TrainDatasetGenerator:
    """Generates synthetic train schedule data for 12306 railway system."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize generator with optional seed for deterministic results."""
        if seed is not None:
            random.seed(seed)
        
        # Major Chinese railway stations
        self.stations = [
            "北京", "上海", "广州", "深圳", "杭州", "南京", "武汉", "成都", 
            "重庆", "西安", "天津", "苏州", "郑州", "长沙", "合肥", "宁波",
            "青岛", "沈阳", "大连", "厦门", "福州", "南昌", "石家庄", "太原"
        ]
        
        # Common train routes (departure -> arrival)
        self.common_routes = [
            ("北京", "上海"), ("上海", "北京"), ("北京", "广州"), ("广州", "北京"),
            ("上海", "深圳"), ("深圳", "上海"), ("北京", "武汉"), ("武汉", "北京"),
            ("上海", "杭州"), ("杭州", "上海"), ("广州", "深圳"), ("深圳", "广州"),
            ("北京", "天津"), ("天津", "北京"), ("上海", "南京"), ("南京", "上海")
        ]
        
        # Train types and their characteristics
        self.train_types = {
            "G": {"name": "高速动车", "speed": "high", "base_price_multiplier": 1.0},
            "D": {"name": "动车组", "speed": "medium", "base_price_multiplier": 0.8},
            "C": {"name": "城际列车", "speed": "medium", "base_price_multiplier": 0.7},
            "K": {"name": "快速列车", "speed": "low", "base_price_multiplier": 0.5}
        }
        
        # Base distances between major cities (in km)
        self.distances = {
            ("北京", "上海"): 1318, ("北京", "广州"): 2294, ("上海", "深圳"): 1454,
            ("北京", "武汉"): 1229, ("上海", "杭州"): 173, ("广州", "深圳"): 147,
            ("北京", "天津"): 137, ("上海", "南京"): 301
        }
    
    def _get_distance(self, departure: str, arrival: str) -> int:
        """Get approximate distance between stations."""
        key = (departure, arrival)
        if key in self.distances:
            return self.distances[key]
        
        # Estimate distance for other routes
        return random.randint(500, 2000)
    
    def _generate_train_number(self, train_type: str) -> str:
        """Generate realistic train number."""
        if train_type == "G":
            return f"G{random.randint(1, 9999):04d}"
        elif train_type == "D":
            return f"D{random.randint(1, 9999):04d}"
        elif train_type == "C":
            return f"C{random.randint(1, 9999):04d}"
        else:  # K series
            return f"K{random.randint(1, 9999):04d}"
    
    def _calculate_duration(self, distance: int, train_type: str) -> str:
        """Calculate travel duration based on distance and train type."""
        if train_type == "G":
            hours = distance / 300  # ~300 km/h
        elif train_type in ["D", "C"]:
            hours = distance / 200  # ~200 km/h
        else:  # K series
            hours = distance / 120  # ~120 km/h
        
        # Add some variance
        hours *= random.uniform(0.9, 1.1)
        
        total_minutes = int(hours * 60)
        duration_hours = total_minutes // 60
        duration_minutes = total_minutes % 60
        
        return f"{duration_hours:02d}:{duration_minutes:02d}"
    
    def _generate_time_schedule(self, duration: str) -> tuple:
        """Generate departure and arrival times."""
        # Parse duration
        duration_hours, duration_minutes = map(int, duration.split(":"))
        
        # Generate departure time (between 06:00 and 22:00)
        departure_hour = random.randint(6, 22)
        departure_minute = random.choice([0, 15, 30, 45])
        departure_time = f"{departure_hour:02d}:{departure_minute:02d}"
        
        # Calculate arrival time
        arrival_hour = departure_hour + duration_hours
        arrival_minute = departure_minute + duration_minutes
        
        if arrival_minute >= 60:
            arrival_hour += 1
            arrival_minute -= 60
        
        # Handle next day arrival
        if arrival_hour >= 24:
            arrival_hour -= 24
        
        arrival_time = f"{arrival_hour:02d}:{arrival_minute:02d}"
        
        return departure_time, arrival_time
    
    def _generate_prices(self, distance: int, train_type: str) -> Dict[str, str]:
        """Generate realistic prices for different seat types."""
        base_price_per_km = 0.5
        multiplier = self.train_types[train_type]["base_price_multiplier"]
        
        base_price = distance * base_price_per_km * multiplier
        
        prices = {
            "business_class": f"¥{int(base_price * 2.5 + random.randint(100, 300))}",
            "first_class": f"¥{int(base_price * 1.8 + random.randint(50, 200))}",
            "second_class": f"¥{int(base_price * 1.2 + random.randint(20, 100))}",
            "hard_seat": f"¥{int(base_price * 0.6 + random.randint(10, 50))}"
        }
        
        return prices
    
    def _generate_available_seats(self) -> Dict[str, str]:
        """Generate available seat counts."""
        return {
            "business_class": str(random.randint(0, 20)),
            "first_class": str(random.randint(0, 50)),
            "second_class": str(random.randint(0, 100)),
            "hard_seat": str(random.randint(0, 200))
        }
    
    def generate_dataset(
        self, 
        num_trains: int = 100,
        start_date: str = "2024-01-01",
        end_date: str = "2024-12-31",
        include_random_routes: bool = True
    ) -> Dict[str, List[Dict]]:
        """
        Generate a synthetic dataset of train schedules.
        
        Args:
            num_trains: Number of train schedules to generate
            start_date: Start date for schedules (YYYY-MM-DD)
            end_date: End date for schedules (YYYY-MM-DD)
            include_random_routes: Whether to include random station combinations
            
        Returns:
            Dictionary with 'search_results' key containing train schedules
        """
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        search_results = []
        
        for _ in range(num_trains):
            # Choose route
            if include_random_routes and random.random() < 0.3:
                departure = random.choice(self.stations)
                arrival = random.choice([s for s in self.stations if s != departure])
            else:
                departure, arrival = random.choice(self.common_routes)
            
            # Choose train type
            train_type = random.choice(list(self.train_types.keys()))
            
            # Generate train details
            train_number = self._generate_train_number(train_type)
            distance = self._get_distance(departure, arrival)
            duration = self._calculate_duration(distance, train_type)
            departure_time, arrival_time = self._generate_time_schedule(duration)
            
            # Generate date
            days_diff = (end_dt - start_dt).days
            random_days = random.randint(0, days_diff)
            date = (start_dt + timedelta(days=random_days)).strftime("%Y-%m-%d")
            
            # Generate additional details
            prices = self._generate_prices(distance, train_type)
            available_seats = self._generate_available_seats()
            
            train_schedule = {
                "train_number": train_number,
                "departure_station": departure,
                "arrival_station": arrival,
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "duration": duration,
                "date": date,
                "seat_types": {
                    "business_class": "商务座",
                    "first_class": "一等座",
                    "second_class": "二等座",
                    "hard_seat": "硬座"
                },
                "prices": prices,
                "available_seats": available_seats
            }
            
            search_results.append(train_schedule)
        
        return {"search_results": search_results}


def generate_dataset(
    output_path: str,
    num_trains: int = 100,
    seed: Optional[int] = 42,
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-31"
) -> None:
    """
    Generate and save synthetic train schedule dataset.
    
    Args:
        output_path: Path to save the JSON dataset
        num_trains: Number of train schedules to generate
        seed: Random seed for deterministic generation
        start_date: Start date for schedules (YYYY-MM-DD)
        end_date: End date for schedules (YYYY-MM-DD)
    """
    generator = TrainDatasetGenerator(seed=seed)
    dataset = generator.generate_dataset(
        num_trains=num_trains,
        start_date=start_date,
        end_date=end_date
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"Dataset generated with {num_trains} train schedules")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    # Example usage
    import os
    
    # Get the default output path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "12306_mcp_server_dataset.json")
    
    # Generate dataset with default parameters
    generate_dataset(output_file, num_trains=150, seed=42)