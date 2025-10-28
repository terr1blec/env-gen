"""
Weather360 Server - FastMCP server for weather data queries.

This server provides access to weather data from the offline database.
It exposes tools to query weather information by geographic coordinates.
"""

import json
import logging
from typing import Optional, Dict, Any
from fastmcp import FastMCP

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(name="Weather360 Server")

# Database configuration
DATABASE_PATH = "weather360_server_database.json"


def load_database() -> Dict[str, Any]:
    """
    Load the weather database from JSON file.
    
    Returns:
        Dict containing the weather data
        
    Raises:
        FileNotFoundError: If database file doesn't exist
        json.JSONDecodeError: If database file is malformed
    """
    try:
        with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
            database = json.load(f)
        
        # Validate database structure
        if "weather_data" not in database:
            raise ValueError("Database missing required 'weather_data' key")
        
        if not isinstance(database["weather_data"], list):
            raise ValueError("Database 'weather_data' must be a list")
        
        # Validate each record has required fields
        required_fields = {"latitude", "longitude", "temperature", "humidity", 
                          "wind_speed", "description", "timestamp"}
        
        for i, record in enumerate(database["weather_data"]):
            missing_fields = required_fields - set(record.keys())
            if missing_fields:
                raise ValueError(f"Record {i} missing required fields: {missing_fields}")
        
        logger.info(f"Successfully loaded database with {len(database['weather_data'])} records")
        return database
        
    except FileNotFoundError:
        logger.error(f"Database file not found: {DATABASE_PATH}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in database file: {e}")
        raise
    except ValueError as e:
        logger.error(f"Database validation failed: {e}")
        raise


@mcp.tool()
def get_live_weather(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Get live weather details for a given latitude and longitude.
    
    This tool queries the offline weather database to find weather data
    matching the specified geographic coordinates. If no exact match is found,
    it returns the closest available weather data point.
    
    Args:
        latitude (float): The latitude coordinate (decimal degrees)
        longitude (float): The longitude coordinate (decimal degrees)
        
    Returns:
        Dict containing weather data with the following fields:
            temperature (float): Temperature in Celsius
            humidity (float): Relative humidity percentage
            wind_speed (float): Wind speed in meters per second
            description (str): Weather condition description
            timestamp (str): ISO 8601 timestamp of the data
            
    Raises:
        ValueError: If no weather data is available for the given coordinates
    """
    try:
        database = load_database()
        weather_data = database["weather_data"]
        
        # Find exact match first
        for record in weather_data:
            if (abs(record["latitude"] - latitude) < 0.0001 and 
                abs(record["longitude"] - longitude) < 0.0001):
                logger.info(f"Found exact weather match for coordinates ({latitude}, {longitude})")
                return {
                    "temperature": record["temperature"],
                    "humidity": record["humidity"],
                    "wind_speed": record["wind_speed"],
                    "description": record["description"],
                    "timestamp": record["timestamp"]
                }
        
        # If no exact match, find closest location
        closest_record = None
        min_distance = float('inf')
        
        for record in weather_data:
            distance = ((record["latitude"] - latitude) ** 2 + 
                       (record["longitude"] - longitude) ** 2)
            if distance < min_distance:
                min_distance = distance
                closest_record = record
        
        if closest_record:
            logger.info(f"Found closest weather data for coordinates ({latitude}, {longitude})")
            return {
                "temperature": closest_record["temperature"],
                "humidity": closest_record["humidity"],
                "wind_speed": closest_record["wind_speed"],
                "description": closest_record["description"],
                "timestamp": closest_record["timestamp"]
            }
        else:
            raise ValueError("No weather data available in the database")
            
    except Exception as e:
        logger.error(f"Error retrieving weather data: {e}")
        raise ValueError(f"Failed to retrieve weather data: {str(e)}")


if __name__ == "__main__":
    mcp.run()