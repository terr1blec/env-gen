#!/usr/bin/env python3
"""
Quick validation script to test the Weather360 Server module.
This script tests the database loading and basic functionality.
"""

import sys
import os

# Add the generated directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'weather', 'weather360-server'))

try:
    # Import and test the server module
    from weather360_server_server import load_database, get_live_weather
    
    print("Testing Weather360 Server module...")
    
    # Test database loading
    print("\n1. Testing database loading...")
    database = load_database()
    print(f"✓ Database loaded successfully with {len(database['weather_data'])} records")
    
    # Test get_live_weather with known coordinates
    print("\n2. Testing get_live_weather with known coordinates...")
    
    # Test with New York coordinates (from the database)
    result = get_live_weather(40.7128, -74.006)
    print(f"✓ Weather data retrieved for New York:")
    print(f"  Temperature: {result['temperature']}°C")
    print(f"  Humidity: {result['humidity']}%")
    print(f"  Wind Speed: {result['wind_speed']} m/s")
    print(f"  Description: {result['description']}")
    print(f"  Timestamp: {result['timestamp']}")
    
    # Test with coordinates that don't have exact match
    print("\n3. Testing get_live_weather with approximate coordinates...")
    result = get_live_weather(40.7, -74.0)
    print(f"✓ Weather data retrieved for approximate coordinates:")
    print(f"  Temperature: {result['temperature']}°C")
    print(f"  Humidity: {result['humidity']}%")
    print(f"  Description: {result['description']}")
    
    print("\n✅ All tests passed! Server module is working correctly.")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)