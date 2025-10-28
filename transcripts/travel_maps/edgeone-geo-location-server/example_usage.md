# EdgeOne Geo Location Server - Example Usage

## Overview
This document provides example conversations demonstrating how to use the edgeone-geo-location-server's `get_geolocation` tool.

## Example 1: Basic Location Retrieval

**User:** Where am I located right now?

**Assistant:** I'll check your current geolocation information.

```python
from edgeone_geo_location_server_server import get_geolocation

location = get_geolocation()
print(f"You are currently in {location['city']}, {location['country']}")
print(f"IP Address: {location['ip']}")
print(f"Coordinates: {location['lat']}, {location['lon']}")
print(f"Timezone: {location['timezone']}")
```

**Output:**
```
You are currently in San Francisco, United States
IP Address: 192.168.1.100
Coordinates: 37.77768853596916, -122.42889978489555
Timezone: America/Los_Angeles
```

## Example 2: Multiple Location Checks

**User:** Can you show me different locations I might appear to be in?

**Assistant:** The server provides round-robin location selection. Let me show you a few different locations:

```python
from edgeone_geo_location_server_server import get_geolocation

# Get multiple locations
locations = []
for i in range(3):
    location = get_geolocation()
    locations.append(location)
    print(f"Location {i+1}: {location['city']}, {location['country']} (IP: {location['ip']})")
```

**Output:**
```
Location 1: San Francisco, United States (IP: 192.168.1.100)
Location 2: London, United Kingdom (IP: 203.0.113.45)
Location 3: Tokyo, Japan (IP: 198.51.100.23)
```

## Example 3: Detailed Location Analysis

**User:** Give me detailed information about my current location.

**Assistant:** Here's a comprehensive breakdown of your geolocation data:

```python
from edgeone_geo_location_server_server import get_geolocation

location = get_geolocation()

print("=== Geolocation Details ===")
print(f"IP Address: {location['ip']}")
print(f"Country: {location['country']} ({location['country_code']})")
print(f"Region: {location['region_name']} ({location['region']})")
print(f"City: {location['city']}")
print(f"ZIP Code: {location['zip']}")
print(f"Coordinates: {location['lat']:.4f}, {location['lon']:.4f}")
print(f"Timezone: {location['timezone']}")
print(f"ISP: {location['isp']}")
print(f"Organization: {location['org']}")
print(f"AS: {location['as']}")
```

**Output:**
```
=== Geolocation Details ===
IP Address: 192.168.1.100
Country: United States (US)
Region: California (CA)
City: San Francisco
ZIP Code: 94102
Coordinates: 37.7777, -122.4289
Timezone: America/Los_Angeles
ISP: Comcast Cable
Organization: Comcast Cable Communications, LLC
AS: AS7922 Comcast Cable Communications, LLC
```

## Example 4: Location-Based Content

**User:** What's the weather like where I am?

**Assistant:** Based on your location, I can provide relevant information:

```python
from edgeone_geo_location_server_server import get_geolocation

location = get_geolocation()
city = location['city']
country = location['country']
timezone = location['timezone']

print(f"Since you're in {city}, {country} (Timezone: {timezone}), ")
print("I can help you with:")
print("- Local weather information")
print("- Nearby attractions")
print("- Local time and date")
print("- Regional news and events")
```

**Output:**
```
Since you're in Berlin, Germany (Timezone: Europe/Berlin),
I can help you with:
- Local weather information
- Nearby attractions
- Local time and date
- Regional news and events
```

## Example 5: Network Information

**User:** What network information can you tell me about my connection?

**Assistant:** Here's the network-related information from your geolocation data:

```python
from edgeone_geo_location_server_server import get_geolocation

location = get_geolocation()

print("=== Network Information ===")
print(f"IP Address: {location['ip']}")
print(f"Internet Service Provider: {location['isp']}")
print(f"Organization: {location['org']}")
print(f"Autonomous System: {location['as']}")

# Note about IP ranges
if location['ip'].startswith(('192.168.', '10.', '172.16.', '172.31.')):
    print("Note: This appears to be a private/internal IP address")
elif location['ip'].startswith(('203.0.113.', '198.51.100.')):
    print("Note: This appears to be a documentation/test IP address")
```

**Output:**
```
=== Network Information ===
IP Address: 203.0.113.45
Internet Service Provider: British Telecommunications
Organization: BT Group
Autonomous System: AS2856 British Telecommunications PLC
Note: This appears to be a documentation/test IP address
```

## Example 6: Geographic Distribution

**User:** What locations are available in the dataset?

**Assistant:** The dataset includes locations from around the world. Let me show you the geographic distribution:

```python
from edgeone_geo_location_server_server_dataset import GeolocationDatasetGenerator

# Load the dataset
generator = GeolocationDatasetGenerator()
locations = generator.get_all_locations()

print("=== Available Locations ===")
for i, location in enumerate(locations, 1):
    print(f"{i}. {location['city']}, {location['country']} ({location['country_code']})")
    print(f"   Coordinates: {location['lat']:.2f}, {location['lon']:.2f}")
    print(f"   Timezone: {location['timezone']}")
    print()
```

**Output:**
```
=== Available Locations ===
1. San Francisco, United States (US)
   Coordinates: 37.78, -122.43
   Timezone: America/Los_Angeles

2. London, United Kingdom (GB)
   Coordinates: 51.50, -0.13
   Timezone: Europe/London

3. Tokyo, Japan (JP)
   Coordinates: 35.68, 139.65
   Timezone: Asia/Tokyo

4. Berlin, Germany (DE)
   Coordinates: 52.53, 13.40
   Timezone: Europe/Berlin

5. Sydney, Australia (AU)
   Coordinates: -33.87, 151.20
   Timezone: Australia/Sydney

6. Toronto, Canada (CA)
   Coordinates: 43.65, -79.38
   Timezone: America/Toronto

7. Paris, France (FR)
   Coordinates: 48.85, 2.35
   Timezone: Europe/Paris

8. São Paulo, Brazil (BR)
   Coordinates: -23.55, -46.63
   Timezone: America/Sao_Paulo
```

## Key Features Demonstrated

1. **Simple Integration**: The `get_geolocation()` function requires no parameters
2. **Complete Data**: Returns all required geolocation fields
3. **Round-Robin Selection**: Consecutive calls return different locations
4. **Realistic Data**: Uses realistic IP addresses, coordinates, and ISP information
5. **Global Coverage**: Includes major cities from multiple continents
6. **Type Safety**: All fields have proper data types (strings, numbers)

## Notes
- The server uses synthetic data for testing and development
- IP addresses use RFC 1918 private ranges and documentation ranges
- Locations are approximate to major city centers
- The round-robin behavior ensures variety in consecutive calls