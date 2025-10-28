#!/usr/bin/env python3
"""
China Railway MCP Server

A FastMCP-compliant server that provides Chinese railway ticket search functionality
using an offline database of train schedules, prices, and availability.
"""

import json
import os
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(name="chinarailway MCP 服务端")

# Database file path
DATABASE_FILE = os.path.join(os.path.dirname(__file__), "chinarailway_mcp__database.json")


def load_database() -> Dict[str, Any]:
    """
    Load the train database from JSON file.
    
    Returns:
        Dict containing train data or empty dict if file not found
    """
    try:
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load database file: {e}")
        return {"trains": []}


def validate_database_structure(database: Dict[str, Any]) -> bool:
    """
    Validate that the database structure matches the DATA CONTRACT.
    
    Args:
        database: The loaded database dictionary
        
    Returns:
        bool: True if structure is valid, False otherwise
    """
    if not isinstance(database, dict):
        return False
    
    if "trains" not in database:
        return False
    
    if not isinstance(database["trains"], list):
        return False
    
    # Check required fields in each train
    required_fields = [
        "train_number", "departure_station", "arrival_station", 
        "departure_time", "arrival_time", "duration", "date"
    ]
    
    for train in database["trains"]:
        if not isinstance(train, dict):
            return False
        
        for field in required_fields:
            if field not in train:
                return False
        
        # Check nested structures
        for nested_field in ["seat_types", "prices", "available_seats"]:
            if nested_field not in train or not isinstance(train[nested_field], dict):
                return False
    
    return True


@mcp.tool()
def search(from_station: str, to_station: str, date: str) -> Dict[str, Any]:
    """
    查询12306火车票
    
    Args:
        from_station (str): 出发站名称
        to_station (str): 到达站名称  
        date (str): 出发日期 (YYYY-MM-DD格式)
        
    Returns:
        Dict containing matching train information
    """
    # Load database
    database = load_database()
    
    # Validate database structure
    if not validate_database_structure(database):
        return {
            "error": "数据库结构无效",
            "trains": []
        }
    
    # Filter trains based on search criteria
    matching_trains = []
    
    for train in database["trains"]:
        # Case-insensitive matching for station names
        if (train["departure_station"].lower() == from_station.lower() and 
            train["arrival_station"].lower() == to_station.lower() and
            train["date"] == date):
            
            matching_trains.append(train)
    
    return {
        "trains": matching_trains
    }


if __name__ == "__main__":
    mcp.run()