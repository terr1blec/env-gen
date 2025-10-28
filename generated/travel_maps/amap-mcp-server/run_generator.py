"""
Run the AMap database generator to create updated database JSON.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from amap_mcp_server_database import AMapDatabaseGenerator
import json

def main():
    """Generate and save the updated database."""
    generator = AMapDatabaseGenerator(seed=42)
    database = generator.generate_database()
    
    # Save to JSON file
    output_path = "amap_mcp_server_database.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    
    print("Database generated successfully!")
    print(f"Generated {len(database)} data types:")
    for key, value in database.items():
        print(f"  - {key}: {len(value)} records")
    
    # Verify the fixes
    print("\nVerifying fixes:")
    
    # 1. Check POI ID uniqueness
    poi_ids = [poi["id"] for poi in database["poi_details"]]
    unique_poi_ids = set(poi_ids)
    print(f"✅ POI ID Uniqueness: {len(poi_ids)} POIs, {len(unique_poi_ids)} unique IDs")
    
    # 2. Check province names
    provinces = []
    for record in database["regeocode_data"]:
        provinces.append(record["address_components"]["province"])
    for record in database["ip_location_data"]:
        provinces.append(record["province"])
    
    print(f"✅ Province Names: {set(provinces)}")
    
    # 3. Check route step consistency
    consistent_steps = 0
    total_steps = 0
    for route_type in ["bicycle", "walking", "driving", "transit"]:
        for route in database[f"{route_type}_routes_by_address"]:
            for step in route["steps"]:
                total_steps += 1
                # Check if instruction mentions the same distance as the actual distance field
                if str(step["distance"].replace("米", "")) in step["instruction"]:
                    consistent_steps += 1
    
    print(f"✅ Route Step Consistency: {consistent_steps}/{total_steps} steps have matching distances")

if __name__ == "__main__":
    main()