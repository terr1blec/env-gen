# Geolocation Dataset Implementation

## Overview
This implementation provides a synthetic geolocation dataset generator for the edgeone-geo-location-server. The dataset contains realistic geolocation data for major cities around the world, formatted according to the DATA CONTRACT specification.

## Key Features

### 1. Deterministic Generation
- Uses random seeds for reproducible results
- Same seed always produces identical data
- Useful for testing and debugging

### 2. Realistic Data
- 8 major cities across different continents
- Realistic IP addresses (using RFC 1918 and documentation ranges)
- Accurate geographic coordinates
- Real ISP and organization names
- Proper timezone assignments

### 3. Data Structure Compliance
All generated data matches the exact schema from the DATA CONTRACT:
- `ip` (string): IP address
- `country` (string): Full country name
- `country_code` (string): 2-letter country code
- `region` (string): Region/state code
- `region_name` (string): Full region name
- `city` (string): City name
- `zip` (string): Postal/ZIP code
- `lat` (number): Latitude coordinate
- `lon` (number): Longitude coordinate
- `timezone` (string): Timezone identifier
- `isp` (string): Internet Service Provider
- `org` (string): Organization name
- `as` (string): Autonomous System information

## Included Locations
1. San Francisco, USA
2. London, UK
3. Tokyo, Japan
4. Berlin, Germany
5. Sydney, Australia
6. Toronto, Canada
7. Paris, France
8. São Paulo, Brazil

## Usage

### Python Module
```python
from edgeone_geo_location_server_dataset import GeolocationDatasetGenerator

# Create generator with seed for determinism
generator = GeolocationDatasetGenerator(seed=42)

# Get all locations
all_locations = generator.get_all_locations()

# Get random location
random_location = generator.get_random_location()

# Get specific location by index
location = generator.get_location_by_index(0)
```

### JSON File
The dataset is also available as a JSON file at `edgeone_geo_location_server_dataset.json` with the structure:
```json
{
  "geolocation_data": [
    { /* location object */ },
    // ... more locations
  ]
}
```

## Testing
The `test_dataset.py` script verifies:
- Data structure compliance
- Required field presence
- Type correctness
- JSON file integrity

## Notes
- IP addresses use RFC 1918 private ranges and documentation ranges (203.0.113.0/24, 198.51.100.0/24)
- Coordinates are approximate to major city centers
- ISP and organization data is based on real providers but uses synthetic details
- The dataset is designed for testing and development, not production use