"""
AMap MCP Server Database Generator
Generates deterministic synthetic test data for offline map services.
"""

import json
import random
from typing import Dict, List, Any


class AMapDatabaseGenerator:
    """Generate deterministic synthetic AMap data for offline testing."""
    
    def __init__(self, seed: int = 42):
        """Initialize with seed for deterministic generation."""
        self.seed = seed
        self.random = random.Random(seed)
        
        # City data with correct province names
        self.cities = {
            "北京市": {"province": "北京市", "districts": ["朝阳区", "海淀区", "西城区", "东城区"]},
            "上海市": {"province": "上海市", "districts": ["浦东新区", "徐汇区", "黄浦区", "静安区"]},
            "广州市": {"province": "广东省", "districts": ["天河区", "越秀区", "海珠区", "荔湾区"]},
            "深圳市": {"province": "广东省", "districts": ["福田区", "南山区", "罗湖区", "宝安区"]},
            "成都市": {"province": "四川省", "districts": ["武侯区", "锦江区", "青羊区", "金牛区"]}
        }
        
        # Street names
        self.streets = ["中山路", "南京路", "长安街", "人民路", "解放路"]
        
        # POI types and names
        self.poi_types = ["银行", "餐饮", "购物", "酒店", "景点"]
        self.poi_suffixes = ["店", "中心", "广场", "大厦"]
        
        # Weather conditions
        self.weather_conditions = ["晴", "多云", "阴", "小雨", "阵雨"]
        self.wind_directions = ["东风", "南风", "西风", "北风", "东南风", "西南风"]
        
    def generate_coordinates(self, city: str) -> str:
        """Generate realistic coordinates for a city."""
        if city == "北京市":
            return f"116.{self.random.randint(350000, 450000)},{39}.{self.random.randint(850000, 950000)}"
        elif city == "上海市":
            return f"121.{self.random.randint(450000, 550000)},{31}.{self.random.randint(180000, 280000)}"
        elif city == "广州市":
            return f"113.{self.random.randint(200000, 320000)},{23}.{self.random.randint(80000, 180000)}"
        elif city == "深圳市":
            return f"114.{self.random.randint(0, 120000)},{22}.{self.random.randint(480000, 580000)}"
        elif city == "成都市":
            return f"104.{self.random.randint(0, 120000)},{30}.{self.random.randint(520000, 620000)}"
        else:
            return f"116.{self.random.randint(350000, 450000)},{39}.{self.random.randint(850000, 950000)}"
    
    def generate_poi_id(self, index: int) -> str:
        """Generate unique POI ID for each record."""
        return f"B0FF{index:04d}"
    
    def generate_poi_name(self) -> str:
        """Generate POI name."""
        poi_type = self.random.choice(self.poi_types)
        suffix = self.random.choice(self.poi_suffixes)
        return f"{poi_type}{suffix}"
    
    def generate_address(self, city: str, district: str) -> str:
        """Generate realistic address."""
        street = self.random.choice(self.streets)
        number = self.random.randint(1, 100)
        return f"{city}{district}{street}{number}号"
    
    def generate_regeocode_data(self, count: int = 10) -> List[Dict]:
        """Generate regeocode data with correct province names."""
        results = []
        for i in range(count):
            city = self.random.choice(list(self.cities.keys()))
            district = self.random.choice(self.cities[city]["districts"])
            location = self.generate_coordinates(city)
            
            results.append({
                "location": location,
                "formatted_address": self.generate_address(city, district),
                "address_components": {
                    "province": self.cities[city]["province"],  # Use correct province name
                    "city": city,
                    "district": district,
                    "street": f"{self.random.choice(self.streets)}{self.random.randint(1, 100)}号",
                    "street_number": ""
                },
                "pois": [
                    {
                        "id": self.generate_poi_id(i * 3 + j),
                        "name": self.generate_poi_name(),
                        "type": self.random.choice(self.poi_types),
                        "address": self.generate_address(city, self.random.choice(self.cities[city]["districts"])),
                        "coordinates": self.generate_coordinates(city),
                        "distance": f"{self.random.randint(50, 2000)}米"
                    }
                    for j in range(3)
                ]
            })
        return results
    
    def generate_geocoding_data(self, count: int = 10) -> List[Dict]:
        """Generate geocoding data."""
        results = []
        for i in range(count):
            city = self.random.choice(list(self.cities.keys()))
            district = self.random.choice(self.cities[city]["districts"])
            address = self.generate_address(city, district)
            
            results.append({
                "address": address,
                "city": city,
                "coordinates": self.generate_coordinates(city),
                "formatted_address": address
            })
        return results
    
    def generate_ip_location_data(self, count: int = 5) -> List[Dict]:
        """Generate IP location data with correct province names."""
        results = []
        ips = ["202.96.153.53", "202.96.79.139", "116.228.250.128", "180.168.141.22", "180.168.218.4"]
        
        for i in range(min(count, len(ips))):
            city = self.random.choice(list(self.cities.keys()))
            district = self.random.choice(self.cities[city]["districts"])
            
            results.append({
                "ip": ips[i],
                "province": self.cities[city]["province"],  # Use correct province name
                "city": city,
                "district": district,
                "coordinates": self.generate_coordinates(city)
            })
        return results
    
    def generate_weather_data(self, count: int = 8) -> List[Dict]:
        """Generate weather data."""
        results = []
        cities = list(self.cities.keys())
        
        for i in range(count):
            city = cities[i % len(cities)]
            temperature = self.random.randint(5, 35)
            
            results.append({
                "city": city,
                "weather": self.random.choice(self.weather_conditions),
                "temperature": f"{temperature}℃",
                "humidity": f"{self.random.randint(30, 90)}%",
                "wind_direction": self.random.choice(self.wind_directions),
                "wind_power": f"{self.random.randint(1, 6)}级"
            })
        return results
    
    def generate_route_data(self, route_type: str, count: int = 5) -> List[Dict]:
        """Generate route data for different transportation modes with consistent step values."""
        results = []
        
        for i in range(count):
            city = self.random.choice(list(self.cities.keys()))
            districts = self.cities[city]["districts"]
            
            if route_type in ["bicycle", "walking"]:
                distance = self.random.randint(1000, 10000)
                duration = distance // 200  # Approximate minutes
                step_count = 2 if route_type == "bicycle" else 3
            else:
                distance = self.random.randint(1000, 20000)
                duration = distance // 500  # Approximate minutes
                step_count = 4
            
            # Generate steps with consistent distance/duration values
            steps = []
            remaining_distance = distance
            remaining_duration = duration
            
            for step_idx in range(step_count):
                if step_idx == step_count - 1:
                    step_distance = remaining_distance
                    step_duration = remaining_duration
                else:
                    step_distance = self.random.randint(50, min(500, remaining_distance // 2))
                    step_duration = max(1, step_distance // (200 if route_type in ["bicycle", "walking"] else 500))
                    remaining_distance -= step_distance
                    remaining_duration -= step_duration
                
                # Ensure consistency between instruction text and actual values
                if route_type == "bicycle":
                    instruction = f"沿自行车道骑行{step_distance}米"
                elif route_type == "walking":
                    instruction = f"沿道路步行{step_distance}米"
                elif route_type == "driving":
                    instruction = f"沿道路行驶{step_distance}米"
                else:  # transit
                    modes = ["地铁", "公交", "步行"]
                    instruction = f"乘坐{self.random.choice(modes)}，{self.random.randint(3, 8)}站"
                
                steps.append({
                    "instruction": instruction,
                    "distance": f"{step_distance}米",  # Use same distance as in instruction
                    "duration": f"{step_duration}分钟"  # Use calculated duration
                })
            
            origin_district = self.random.choice(districts)
            destination_district = self.random.choice([d for d in districts if d != origin_district])
            
            if "coordinates" in route_type:
                origin = self.generate_coordinates(city)
                destination = self.generate_coordinates(city)
            else:
                origin = self.generate_address(city, origin_district)
                destination = self.generate_address(city, destination_district)
            
            results.append({
                "distance": f"{distance}米",
                "duration": f"{duration}分钟",
                "steps": steps,
                "origin": origin,
                "destination": destination
            })
        
        return results
    
    def generate_distance_data(self, count: int = 5) -> List[Dict]:
        """Generate distance calculation data."""
        results = []
        
        for i in range(count):
            city = self.random.choice(list(self.cities.keys()))
            
            origins = ";".join([self.generate_coordinates(city) for _ in range(2)])
            destination = self.generate_coordinates(city)
            distance = self.random.randint(1000, 10000)
            duration = distance // 500
            
            results.append({
                "origins": origins,
                "destination": destination,
                "distance": f"{distance}米",
                "duration": f"{duration}分钟",
                "type": "0"
            })
        return results
    
    def generate_search_results(self, search_type: str, count: int = 5) -> List[Dict]:
        """Generate search results data with unique POI IDs."""
        results = []
        keywords_list = ["商场", "餐厅", "银行", "酒店"]
        
        for i in range(count):
            keyword = keywords_list[i % len(keywords_list)]
            city = self.random.choice(list(self.cities.keys()))
            
            result_count = self.random.randint(8, 15)
            search_results = []
            
            for j in range(min(8, result_count)):
                search_results.append({
                    "id": self.generate_poi_id(i * 8 + j + 2000),  # Start from 2000 to avoid conflicts
                    "name": self.generate_poi_name(),
                    "type": self.random.choice(self.poi_types),
                    "address": self.generate_address(city, self.random.choice(self.cities[city]["districts"])),
                    "coordinates": self.generate_coordinates(city),
                    "distance": f"{self.random.randint(50, 2000)}米"
                })
            
            results.append({
                "keywords": keyword,
                "city": city,
                "results": search_results,
                "total_count": result_count
            })
        return results
    
    def generate_poi_details(self, count: int = 10) -> List[Dict]:
        """Generate POI details with unique IDs."""
        results = []
        
        for i in range(count):
            city = self.random.choice(list(self.cities.keys()))
            district = self.random.choice(self.cities[city]["districts"])
            
            results.append({
                "id": self.generate_poi_id(1000 + i),  # Use unique IDs starting from 1000
                "name": self.generate_poi_name(),
                "type": self.random.choice(self.poi_types),
                "address": self.generate_address(city, district),
                "coordinates": self.generate_coordinates(city),
                "rating": round(self.random.uniform(3.0, 5.0), 1),
                "business_hours": "09:00-22:00"
            })
        return results
    
    def generate_database(self) -> Dict[str, Any]:
        """Generate complete database with all data types."""
        return {
            "regeocode_data": self.generate_regeocode_data(10),
            "geocoding_data": self.generate_geocoding_data(10),
            "ip_location_data": self.generate_ip_location_data(5),
            "weather_data": self.generate_weather_data(8),
            "bicycle_routes_by_address": self.generate_route_data("bicycle", 5),
            "bicycle_routes_by_coordinates": self.generate_route_data("bicycle_coordinates", 5),
            "walking_routes_by_address": self.generate_route_data("walking", 5),
            "walking_routes_by_coordinates": self.generate_route_data("walking_coordinates", 5),
            "driving_routes_by_address": self.generate_route_data("driving", 5),
            "driving_routes_by_coordinates": self.generate_route_data("driving_coordinates", 5),
            "transit_routes_by_address": self.generate_route_data("transit", 5),
            "transit_routes_by_coordinates": self.generate_route_data("transit_coordinates", 5),
            "distance_data": self.generate_distance_data(5),
            "text_search_results": self.generate_search_results("text", 5),
            "around_search_results": self.generate_search_results("around", 5),
            "poi_details": self.generate_poi_details(10)
        }


if __name__ == "__main__":
    generator = AMapDatabaseGenerator(seed=42)
    database = generator.generate_database()
    
    # Save to JSON file
    with open("amap_mcp_server_database.json", "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    
    print("Database generated successfully!")
    print(f"Generated {len(database)} data types:")
    for key, value in database.items():
        print(f"  - {key}: {len(value)} records")