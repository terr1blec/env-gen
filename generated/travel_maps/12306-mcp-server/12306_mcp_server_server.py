"""
12306 MCP Server - FastMCP server for Chinese railway ticket search

This server provides train schedule search functionality using the generated dataset.
It only uses data from the generated JSON file and does not contain any fallback data.
"""

import json
import os
import re
from typing import Dict, List, Optional, Any
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("12306 MCP Server")

# Dataset file path
DATASET_PATH = os.path.join(os.path.dirname(__file__), "12306_mcp_server_dataset.json")

# Date validation pattern (YYYY-MM-DD)
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def load_dataset() -> Dict[str, Any]:
    """
    Load the train dataset from the generated JSON file.
    
    Returns:
        Dictionary containing the train dataset
        
    Raises:
        FileNotFoundError: If the dataset file is not found
        json.JSONDecodeError: If the dataset file contains invalid JSON
        KeyError: If the dataset does not contain required keys
    """
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset file not found: {DATASET_PATH}")
    
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    # Validate dataset structure
    if "search_results" not in dataset:
        raise KeyError("Dataset missing required 'search_results' key")
    
    if not isinstance(dataset["search_results"], list):
        raise ValueError("Dataset 'search_results' must be a list")
    
    return dataset


def validate_date_format(date_str: str) -> bool:
    """
    Validate that the date string is in YYYY-MM-DD format.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid, False otherwise
    """
    return bool(DATE_PATTERN.match(date_str))


@mcp.tool()
def search(departure_station: str, arrival_station: str, date: str) -> Dict[str, Any]:
    """
    查询12306火车票
    
    Search for train tickets between departure and arrival stations on a specific date.
    
    Args:
        departure_station: 出发站 (Departure station)
        arrival_station: 到达站 (Arrival station) 
        date: 日期 (Date in YYYY-MM-DD format)
        
    Returns:
        Dictionary containing search results with train schedules
        
    Raises:
        ValueError: If date format is invalid or stations are empty
        FileNotFoundError: If dataset file is not found
        json.JSONDecodeError: If dataset file contains invalid JSON
        KeyError: If dataset structure is invalid
    """
    # Input validation
    if not departure_station or not arrival_station:
        raise ValueError("Departure and arrival stations cannot be empty")
    
    if not validate_date_format(date):
        raise ValueError("Date must be in YYYY-MM-DD format")
    
    # Load dataset
    dataset = load_dataset()
    
    # Filter results based on input criteria
    search_results = []
    for train in dataset["search_results"]:
        if (train["departure_station"] == departure_station and 
            train["arrival_station"] == arrival_station and 
            train["date"] == date):
            search_results.append(train)
    
    return {"search_results": search_results}


# Server initialization
if __name__ == "__main__":
    # Run the server
    mcp.run(transport="stdio")