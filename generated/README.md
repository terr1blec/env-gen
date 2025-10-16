# Google Maps MCP Server

A FastMCP server module that provides offline Google Maps API functionality using a local dataset. This implementation addresses all code review feedback and provides a robust, offline-capable mapping service.

## Features

- **7 Core Google Maps Tools**: All major Google Maps API functionality
- **Offline Operation**: No external API calls required
- **Deterministic Dataset**: Pre-generated test data for reliable testing
- **Error Handling**: Comprehensive validation and error responses
- **MCP Compliance**: Fully compatible with Model Context Protocol

## Tools Available

### 1. `maps_geocode`
Convert addresses to geographic coordinates.

**Parameters:**
- `address` (required): Address to geocode

**Returns:** Geocoding results with coordinates and formatted address

### 2. `maps_reverse_geocode`
Convert geographic coordinates to addresses.

**Parameters:**
- `latitude` (required): Latitude coordinate
- `longitude` (required): Longitude coordinate

**Returns:** Reverse geocoding results with formatted address

### 3. `maps_search_places`
Search for places based on query.

**Parameters:**
- `query` (required): Search query for places
- `radius` (optional): Search radius in meters
- `location` (optional): Location to search around

**Returns:** List of matching places with details

### 4. `maps_place_details`
Get detailed information about a place.

**Parameters:**
- `place_id` (required): Unique identifier for the place

**Returns:** Comprehensive place details including address, phone, hours, etc.

### 5. `maps_distance_matrix`
Calculate travel distance and time between locations.

**Parameters:**
- `origins` (required): Starting locations (comma-separated or pipe-separated)
- `destinations` (required): Destination locations (comma-separated or pipe-separated)
- `mode` (optional): Travel mode (driving, walking, transit, bicycling)

**Returns:** Distance matrix with travel times and distances

### 6. `maps_elevation`
Get elevation data for locations.

**Parameters:**
- `locations` (required): Locations to get elevation for (format: "lat,lng" or "lat,lng|lat,lng")

**Returns:** Elevation data for specified locations

### 7. `maps_directions`
Get directions between two locations.

**Parameters:**
- `origin` (required): Starting location
- `destination` (required): Ending location
- `mode` (optional): Travel mode (driving, walking, transit, bicycling)

**Returns:** Route information with step-by-step directions

## Code Review Improvements

This implementation addresses all identified issues from the code review:

### ✅ Fixed Parameter Naming Inconsistencies
- Removed confusing parameter names that shadowed function names
- Standardized parameter names to follow Google Maps API conventions
- Eliminated `maps_geocode` parameter in `maps_geocode` function
- Eliminated `maps_place_details` parameter in `maps_place_details` function
- Eliminated `maps_distance_matrix` parameter in `maps_distance_matrix` function
- Removed confusing `Add` and `Item` parameters from `maps_elevation`

### ✅ Added Missing Required Parameters
- Added `origins` and `destinations` parameters to `maps_distance_matrix`
- Added proper coordinate parsing for `maps_elevation`
- Ensured all required parameters are properly documented

### ✅ Improved Dataset Structure Alignment
- Enhanced dataset parsing to match Google Maps API response formats
- Added proper coordinate validation and parsing
- Improved error handling for invalid inputs
- Standardized return formats across all tools

### ✅ Enhanced Error Handling
- Added comprehensive input validation
- Improved coordinate parsing with error messages
- Standardized error response formats
- Added graceful fallbacks for missing data

## Dataset Structure

The server uses a JSON dataset with the following structure:

```json
{
  "geocoding": [
    {
      "input": {"address": "..."},
      "output": {"results": [...], "status": "OK"}
    }
  ],
  "reverse_geocoding": [...],
  "places": [...],
  "place_details": [...],
  "distance_matrix": [...],
  "elevation": [...],
  "directions": [...]
}
```

## Usage

### Running the Server

```bash
python generated/google-maps_server.py
```

### Testing

Run the test suite to verify functionality:

```bash
python generated/test_server.py
```

### Integration with MCP Client

The server can be integrated with any MCP-compatible client:

```python
from mcp.client import create_session

async with create_session("google-maps-server") as session:
    result = await session.call_tool("maps_geocode", {"address": "1600 Amphitheatre Parkway, Mountain View, CA"})
    print(result)
```

## Implementation Details

### Key Features
- **FastMCP Integration**: Uses the FastMCP framework for high-performance MCP server
- **Type Annotations**: Full type hints for better development experience
- **Error Resilience**: Graceful handling of missing data and invalid inputs
- **Dataset Abstraction**: Clean separation between data and logic
- **Extensible Design**: Easy to add new tools or modify existing ones

### Data Flow
1. Client sends MCP tool call
2. Server loads dataset from JSON file
3. Function searches for matching data
4. Returns structured response matching Google Maps API format
5. Graceful fallback if no match found

## Dependencies

- `mcp` - Model Context Protocol framework
- `fastmcp` - FastMCP server implementation
- Standard Python libraries: `json`, `os`, `typing`

## License

This implementation is designed for testing and development purposes with offline datasets.