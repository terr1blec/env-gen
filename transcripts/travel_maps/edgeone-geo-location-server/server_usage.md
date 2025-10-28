# EdgeOne Geo Location Server - Usage Transcript

## Overview
The EdgeOne Geo Location Server provides geolocation information through a single MCP tool called `get_geolocation`. The server loads data from an offline database containing synthetic but realistic geolocation records.

## Tool: get_geolocation

### Description
Retrieves comprehensive geolocation information including IP address, geographic location, coordinates, timezone, and ISP details.

### Input Parameters
- None (no parameters required)

### Output Fields
- `ip` (string): IP address
- `country` (string): Country name
- `country_code` (string): 2-letter country code
- `region` (string): Region/state code
- `region_name` (string): Region/state name
- `city` (string): City name
- `zip` (string): ZIP/postal code
- `lat` (number): Latitude coordinate
- `lon` (number): Longitude coordinate
- `timezone` (string): Timezone identifier
- `isp` (string): Internet Service Provider
- `org` (string): Organization name
- `as` (string): Autonomous System number

### Example Usage

```python
# Using the MCP client
result = await client.call_tool("get_geolocation", {})

# Expected response structure:
{
  "ip": "164.57.12.190",
  "country": "United States",
  "country_code": "US",
  "region": "IL",
  "region_name": "IL State",
  "city": "Houston",
  "zip": "98696",
  "lat": 30.357058,
  "lon": -82.28467,
  "timezone": "America/New_York",
  "isp": "Windstream",
  "org": "Windstream Communications",
  "as": "AS7029"
}
```

## Data Source
The server loads data from `edgeone_geo_location_server_database.json` which contains 10 synthetic geolocation records covering:
- United States
- United Kingdom
- Germany
- Japan
- Australia
- Canada
- France
- Brazil
- India
- Singapore

## Error Handling
- If the database file is missing or corrupted, the server falls back to default data
- All database structure validation follows the DATA CONTRACT specification
- Comprehensive logging is implemented for troubleshooting

## Implementation Notes
- The server currently returns the first record from the database as the default response
- Future enhancements could include IP-based record selection or random record selection
- The database structure strictly follows the DATA CONTRACT with all required fields