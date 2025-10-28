"""
AMap MCP Server - FastMCP-compliant server for offline map services.
Provides 16 tools for location services, routing, and POI search using offline database.
"""

import json
import os
from typing import Dict, List, Optional, Any
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(name="高德地图 MCP Server")

# Database loading and validation
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "amap_mcp_server_database.json")

# Default fallback data structure
default_database = {
    "regeocode_data": [],
    "geocoding_data": [],
    "ip_location_data": [],
    "weather_data": [],
    "bicycle_routes_by_address": [],
    "bicycle_routes_by_coordinates": [],
    "walking_routes_by_address": [],
    "walking_routes_by_coordinates": [],
    "driving_routes_by_address": [],
    "driving_routes_by_coordinates": [],
    "transit_routes_by_address": [],
    "transit_routes_by_coordinates": [],
    "distance_data": [],
    "text_search_results": [],
    "around_search_results": [],
    "poi_details": []
}

# Load database
try:
    with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
        database = json.load(f)
    
    # Validate required keys exist
    for key in default_database.keys():
        if key not in database:
            print(f"Warning: Missing key '{key}' in database, using default")
            database[key] = default_database[key]
            
except Exception as e:
    print(f"Warning: Failed to load database from {DATABASE_PATH}: {e}")
    print("Using default empty database")
    database = default_database.copy()

# Helper function to find matching data
def find_matching_data(data_list: List[Dict], **kwargs) -> Optional[Dict]:
    """Find first matching record in data list based on provided criteria."""
    for item in data_list:
        match = True
        for key, value in kwargs.items():
            if key not in item or item[key] != value:
                match = False
                break
        if match:
            return item
    return None

# Tool implementations
@mcp.tool()
def maps_regeocode(location: str) -> Dict[str, Any]:
    """根据坐标获取逆地理编码信息
    
    Args:
        location (str): 坐标字符串，格式为"经度,纬度"
        
    Returns:
        dict: 逆地理编码结果，包含位置信息、格式化地址、地址组件和POI列表
    """
    result = find_matching_data(database["regeocode_data"], location=location)
    if result:
        return result
    else:
        return {
            "location": location,
            "formatted_address": "未知地址",
            "address_components": {
                "province": "",
                "city": "",
                "district": "",
                "street": "",
                "street_number": ""
            },
            "pois": []
        }

@mcp.tool()
def maps_geo(address: str, city: str) -> Dict[str, Any]:
    """根据地址获取地理编码信息
    
    Args:
        address (str): 详细地址
        city (str): 城市名称
        
    Returns:
        dict: 地理编码结果，包含地址、城市、坐标和格式化地址
    """
    result = find_matching_data(database["geocoding_data"], address=address, city=city)
    if result:
        return result
    else:
        return {
            "address": address,
            "city": city,
            "coordinates": "",
            "formatted_address": address
        }

@mcp.tool()
def maps_ip_location(ip: str) -> Dict[str, Any]:
    """根据IP地址获取地理位置信息
    
    Args:
        ip (str): IP地址
        
    Returns:
        dict: IP定位结果，包含IP、省份、城市、区域和坐标
    """
    result = find_matching_data(database["ip_location_data"], ip=ip)
    if result:
        return result
    else:
        return {
            "ip": ip,
            "province": "",
            "city": "",
            "district": "",
            "coordinates": ""
        }

@mcp.tool()
def maps_weather(city: str) -> Dict[str, Any]:
    """获取城市天气信息
    
    Args:
        city (str): 城市名称
        
    Returns:
        dict: 天气信息，包含城市、天气状况、温度、湿度、风向和风力
    """
    result = find_matching_data(database["weather_data"], city=city)
    if result:
        return result
    else:
        return {
            "city": city,
            "weather": "未知",
            "temperature": "",
            "humidity": "",
            "wind_direction": "",
            "wind_power": ""
        }

@mcp.tool()
def maps_bicycling_by_address(origin: str, destination: str) -> Dict[str, Any]:
    """根据地址获取自行车路线规划
    
    Args:
        origin (str): 起点地址
        destination (str): 终点地址
        
    Returns:
        dict: 自行车路线规划结果，包含距离、时长、步骤和起终点
    """
    result = find_matching_data(
        database["bicycle_routes_by_address"], 
        origin=origin, 
        destination=destination
    )
    if result:
        return result
    else:
        return {
            "distance": "",
            "duration": "",
            "steps": [],
            "origin": origin,
            "destination": destination
        }

@mcp.tool()
def maps_bicycling_by_coordinates(origin: str, destination: str) -> Dict[str, Any]:
    """根据坐标获取自行车路线规划
    
    Args:
        origin (str): 起点坐标，格式为"经度,纬度"
        destination (str): 终点坐标，格式为"经度,纬度"
        
    Returns:
        dict: 自行车路线规划结果，包含距离、时长、步骤和起终点
    """
    result = find_matching_data(
        database["bicycle_routes_by_coordinates"], 
        origin=origin, 
        destination=destination
    )
    if result:
        return result
    else:
        return {
            "distance": "",
            "duration": "",
            "steps": [],
            "origin": origin,
            "destination": destination
        }

@mcp.tool()
def maps_direction_walking_by_address(origin: str, destination: str) -> Dict[str, Any]:
    """根据地址获取步行路线规划
    
    Args:
        origin (str): 起点地址
        destination (str): 终点地址
        
    Returns:
        dict: 步行路线规划结果，包含距离、时长、步骤和起终点
    """
    result = find_matching_data(
        database["walking_routes_by_address"], 
        origin=origin, 
        destination=destination
    )
    if result:
        return result
    else:
        return {
            "distance": "",
            "duration": "",
            "steps": [],
            "origin": origin,
            "destination": destination
        }

@mcp.tool()
def maps_direction_walking_by_coordinates(origin: str, destination: str) -> Dict[str, Any]:
    """根据坐标获取步行路线规划
    
    Args:
        origin (str): 起点坐标，格式为"经度,纬度"
        destination (str): 终点坐标，格式为"经度,纬度"
        
    Returns:
        dict: 步行路线规划结果，包含距离、时长、步骤和起终点
    """
    result = find_matching_data(
        database["walking_routes_by_coordinates"], 
        origin=origin, 
        destination=destination
    )
    if result:
        return result
    else:
        return {
            "distance": "",
            "duration": "",
            "steps": [],
            "origin": origin,
            "destination": destination
        }

@mcp.tool()
def maps_direction_driving_by_address(origin: str, destination: str) -> Dict[str, Any]:
    """根据地址获取驾车路线规划
    
    Args:
        origin (str): 起点地址
        destination (str): 终点地址
        
    Returns:
        dict: 驾车路线规划结果，包含距离、时长、步骤和起终点
    """
    result = find_matching_data(
        database["driving_routes_by_address"], 
        origin=origin, 
        destination=destination
    )
    if result:
        return result
    else:
        return {
            "distance": "",
            "duration": "",
            "steps": [],
            "origin": origin,
            "destination": destination
        }

@mcp.tool()
def maps_direction_driving_by_coordinates(origin: str, destination: str) -> Dict[str, Any]:
    """根据坐标获取驾车路线规划
    
    Args:
        origin (str): 起点坐标，格式为"经度,纬度"
        destination (str): 终点坐标，格式为"经度,纬度"
        
    Returns:
        dict: 驾车路线规划结果，包含距离、时长、步骤和起终点
    """
    result = find_matching_data(
        database["driving_routes_by_coordinates"], 
        origin=origin, 
        destination=destination
    )
    if result:
        return result
    else:
        return {
            "distance": "",
            "duration": "",
            "steps": [],
            "origin": origin,
            "destination": destination
        }

@mcp.tool()
def maps_direction_transit_integrated_by_address(origin: str, destination: str) -> Dict[str, Any]:
    """根据地址获取公交路线规划
    
    Args:
        origin (str): 起点地址
        destination (str): 终点地址
        
    Returns:
        dict: 公交路线规划结果，包含距离、时长、步骤和起终点
    """
    result = find_matching_data(
        database["transit_routes_by_address"], 
        origin=origin, 
        destination=destination
    )
    if result:
        return result
    else:
        return {
            "distance": "",
            "duration": "",
            "steps": [],
            "origin": origin,
            "destination": destination
        }

@mcp.tool()
def maps_direction_transit_integrated_by_coordinates(origin: str, destination: str) -> Dict[str, Any]:
    """根据坐标获取公交路线规划
    
    Args:
        origin (str): 起点坐标，格式为"经度,纬度"
        destination (str): 终点坐标，格式为"经度,纬度"
        
    Returns:
        dict: 公交路线规划结果，包含距离、时长、步骤和起终点
    """
    result = find_matching_data(
        database["transit_routes_by_coordinates"], 
        origin=origin, 
        destination=destination
    )
    if result:
        return result
    else:
        return {
            "distance": "",
            "duration": "",
            "steps": [],
            "origin": origin,
            "destination": destination
        }

@mcp.tool()
def maps_distance(origins: str, destination: str, type: str = "0") -> Dict[str, Any]:
    """计算多点距离
    
    Args:
        origins (str): 起点坐标集合，多个坐标用分号分隔
        destination (str): 终点坐标
        type (str): 距离计算类型，默认"0"
        
    Returns:
        dict: 距离计算结果，包含起点、终点、距离、时长和类型
    """
    result = find_matching_data(
        database["distance_data"], 
        origins=origins, 
        destination=destination,
        type=type
    )
    if result:
        return result
    else:
        return {
            "origins": origins,
            "destination": destination,
            "distance": "",
            "duration": "",
            "type": type
        }

@mcp.tool()
def maps_text_search(keywords: str, city: str) -> Dict[str, Any]:
    """根据关键词搜索POI
    
    Args:
        keywords (str): 搜索关键词
        city (str): 城市名称
        
    Returns:
        dict: 文本搜索结果，包含关键词、城市、结果列表和总数
    """
    result = find_matching_data(
        database["text_search_results"], 
        keywords=keywords, 
        city=city
    )
    if result:
        return result
    else:
        return {
            "keywords": keywords,
            "city": city,
            "results": [],
            "total_count": 0
        }

@mcp.tool()
def maps_around_search(keywords: str, city: str) -> Dict[str, Any]:
    """根据关键词搜索周边POI
    
    Args:
        keywords (str): 搜索关键词
        city (str): 城市名称
        
    Returns:
        dict: 周边搜索结果，包含关键词、城市、结果列表和总数
    """
    result = find_matching_data(
        database["around_search_results"], 
        keywords=keywords, 
        city=city
    )
    if result:
        return result
    else:
        return {
            "keywords": keywords,
            "city": city,
            "results": [],
            "total_count": 0
        }

@mcp.tool()
def maps_search_detail(id: str) -> Dict[str, Any]:
    """根据POI ID获取详细信息
    
    Args:
        id (str): POI ID
        
    Returns:
        dict: POI详细信息，包含ID、名称、类型、地址、坐标、评分和营业时间
    """
    result = find_matching_data(database["poi_details"], id=id)
    if result:
        return result
    else:
        return {
            "id": id,
            "name": "",
            "type": "",
            "address": "",
            "coordinates": "",
            "rating": 0.0,
            "business_hours": ""
        }

if __name__ == "__main__":
    mcp.run()