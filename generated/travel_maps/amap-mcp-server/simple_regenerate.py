import json
import random

class AMapDatabaseGenerator:
    def __init__(self, seed=42):
        self.random = random.Random(seed)
        self.cities = {
            "北京市": {"province": "北京市", "districts": ["朝阳区", "海淀区", "西城区", "东城区"]},
            "上海市": {"province": "上海市", "districts": ["浦东新区", "徐汇区", "黄浦区", "静安区"]},
            "广州市": {"province": "广东省", "districts": ["天河区", "越秀区", "海珠区", "荔湾区"]},
            "深圳市": {"province": "广东省", "districts": ["福田区", "南山区", "罗湖区", "宝安区"]},
            "成都市": {"province": "四川省", "districts": ["武侯区", "锦江区", "青羊区", "金牛区"]}
        }
        self.streets = ["中山路", "南京路", "长安街", "人民路", "解放路"]
        self.poi_types = ["银行", "餐饮", "购物", "酒店", "景点"]
        self.poi_suffixes = ["店", "中心", "广场", "大厦"]
    
    def generate_poi_id(self, index):
        return f"B0FF{index:04d}"
    
    def generate_poi_name(self):
        return f"{self.random.choice(self.poi_types)}{self.random.choice(self.poi_suffixes)}"
    
    def generate_address(self, city, district):
        return f"{city}{district}{self.random.choice(self.streets)}{self.random.randint(1, 100)}号"
    
    def generate_regeocode_data(self, count=10):
        results = []
        for i in range(count):
            city = self.random.choice(list(self.cities.keys()))
            district = self.random.choice(self.cities[city]["districts"])
            results.append({
                "location": f"116.{self.random.randint(350000, 450000)},{39}.{self.random.randint(850000, 950000)}",
                "formatted_address": self.generate_address(city, district),
                "address_components": {
                    "province": self.cities[city]["province"],
                    "city": city,
                    "district": district,
                    "street": f"{self.random.choice(self.streets)}{self.random.randint(1, 100)}号",
                    "street_number": ""
                },
                "pois": [{
                    "id": self.generate_poi_id(i * 3 + j),
                    "name": self.generate_poi_name(),
                    "type": self.random.choice(self.poi_types),
                    "address": self.generate_address(city, self.random.choice(self.cities[city]["districts"])),
                    "coordinates": f"116.{self.random.randint(350000, 450000)},{39}.{self.random.randint(850000, 950000)}",
                    "distance": f"{self.random.randint(50, 2000)}米"
                } for j in range(3)]
            })
        return results
    
    def generate_ip_location_data(self, count=5):
        results = []
        ips = ["202.96.153.53", "202.96.79.139", "116.228.250.128", "180.168.141.22", "180.168.218.4"]
        for i in range(min(count, len(ips))):
            city = self.random.choice(list(self.cities.keys()))
            district = self.random.choice(self.cities[city]["districts"])
            results.append({
                "ip": ips[i],
                "province": self.cities[city]["province"],
                "city": city,
                "district": district,
                "coordinates": f"116.{self.random.randint(350000, 450000)},{39}.{self.random.randint(850000, 950000)}"
            })
        return results
    
    def generate_route_data(self, route_type, count=5):
        results = []
        for i in range(count):
            city = self.random.choice(list(self.cities.keys()))
            districts = self.cities[city]["districts"]
            distance = self.random.randint(1000, 10000)
            duration = distance // 200
            step_count = 2 if route_type == "bicycle" else 3
            steps = []
            remaining_distance = distance
            for step_idx in range(step_count):
                if step_idx == step_count - 1:
                    step_distance = remaining_distance
                else:
                    step_distance = self.random.randint(50, min(500, remaining_distance // 2))
                    remaining_distance -= step_distance
                step_duration = max(1, step_distance // 200)
                instruction = f"沿道路{step_distance}米"
                steps.append({
                    "instruction": instruction,
                    "distance": f"{step_distance}米",
                    "duration": f"{step_duration}分钟"
                })
            origin_district = self.random.choice(districts)
            destination_district = self.random.choice([d for d in districts if d != origin_district])
            results.append({
                "distance": f"{distance}米",
                "duration": f"{duration}分钟",
                "steps": steps,
                "origin": self.generate_address(city, origin_district),
                "destination": self.generate_address(city, destination_district)
            })
        return results
    
    def generate_poi_details(self, count=10):
        results = []
        for i in range(count):
            city = self.random.choice(list(self.cities.keys()))
            district = self.random.choice(self.cities[city]["districts"])
            results.append({
                "id": self.generate_poi_id(1000 + i),
                "name": self.generate_poi_name(),
                "type": self.random.choice(self.poi_types),
                "address": self.generate_address(city, district),
                "coordinates": f"116.{self.random.randint(350000, 450000)},{39}.{self.random.randint(850000, 950000)}",
                "rating": round(self.random.uniform(3.0, 5.0), 1),
                "business_hours": "09:00-22:00"
            })
        return results
    
    def generate_database(self):
        return {
            "regeocode_data": self.generate_regeocode_data(10),
            "geocoding_data": [{"address": "北京市朝阳区中山路1号", "city": "北京市", "coordinates": "116.397685,39.944572", "formatted_address": "北京市朝阳区中山路1号"} for _ in range(10)],
            "ip_location_data": self.generate_ip_location_data(5),
            "weather_data": [{"city": "北京市", "weather": "晴", "temperature": "25℃", "humidity": "50%", "wind_direction": "东风", "wind_power": "3级"} for _ in range(8)],
            "bicycle_routes_by_address": self.generate_route_data("bicycle", 5),
            "bicycle_routes_by_coordinates": self.generate_route_data("bicycle", 5),
            "walking_routes_by_address": self.generate_route_data("walking", 5),
            "walking_routes_by_coordinates": self.generate_route_data("walking", 5),
            "driving_routes_by_address": self.generate_route_data("driving", 5),
            "driving_routes_by_coordinates": self.generate_route_data("driving", 5),
            "transit_routes_by_address": self.generate_route_data("transit", 5),
            "transit_routes_by_coordinates": self.generate_route_data("transit", 5),
            "distance_data": [{"origins": "116.397685,39.944572", "destination": "116.397685,39.944572", "distance": "1000米", "duration": "5分钟", "type": "0"} for _ in range(5)],
            "text_search_results": [{"keywords": "餐厅", "city": "北京市", "results": [{"id": self.generate_poi_id(2000 + i), "name": self.generate_poi_name(), "type": "餐饮", "address": "北京市朝阳区中山路1号", "coordinates": "116.397685,39.944572", "distance": "100米"} for i in range(8)], "total_count": 8} for _ in range(5)],
            "around_search_results": [{"keywords": "餐厅", "city": "北京市", "results": [{"id": self.generate_poi_id(3000 + i), "name": self.generate_poi_name(), "type": "餐饮", "address": "北京市朝阳区中山路1号", "coordinates": "116.397685,39.944572", "distance": "100米"} for i in range(8)], "total_count": 8} for _ in range(5)],
            "poi_details": self.generate_poi_details(10)
        }

# Generate and save
generator = AMapDatabaseGenerator(seed=42)
database = generator.generate_database()

with open("amap_mcp_server_database.json", "w", encoding="utf-8") as f:
    json.dump(database, f, ensure_ascii=False, indent=2)

print("Database regenerated successfully!")
print(f"POI IDs in poi_details: {[poi['id'] for poi in database['poi_details']]}")
print(f"Provinces in regeocode_data: {set([record['address_components']['province'] for record in database['regeocode_data']])}")
print(f"Provinces in ip_location_data: {set([record['province'] for record in database['ip_location_data']])}")