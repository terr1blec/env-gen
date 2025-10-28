# Amadeus MCP Server - Implementation Notes

## Architecture Overview

The Amadeus MCP Server is a FastMCP-compliant server that provides flight search capabilities using an offline database. The implementation follows the MCP (Model Context Protocol) specification and exposes tools via the MCP protocol.

## Components

### 1. Server Module (`amadeus_mcp_server_server.py`)

**Key Features:**
- FastMCP server implementation with `search_flight_offers` tool
- Cross-platform path handling using `Path` objects and forward slashes
- Robust database loading with fallback mechanism
- Comprehensive input validation and filtering

**Database Loading:**
- Uses `Path("generated/travel_maps/amadeus-mcp-server/amadeus_mcp_server_database.json")` for cross-platform compatibility
- Validates required `flight_offers` top-level key
- Provides fallback database structure if JSON file is missing or corrupted

**Search Algorithm:**
- Exact matching on origin, destination, and departure date
- Optional filtering on return date, travel class, currency, and passenger capacity
- Returns matching flight offers as a structured response

### 2. Database Structure

The database follows the DATA CONTRACT schema:

```json
{
  "flight_offers": [
    {
      "id": "string",
      "origin": "string",
      "destination": "string", 
      "departure_date": "string",
      "return_date": "string",
      "adults": "integer",
      "children": "integer",
      "infants": "integer",
      "travel_class": "string",
      "currency": "string",
      "price": "number",
      "airline": "string",
      "flight_number": "string",
      "departure_time": "string",
      "arrival_time": "string",
      "duration": "string",
      "stops": "integer"
    }
  ]
}
```

### 3. Metadata (`amadeus_mcp_server_metadata.json`)

**Enhanced Output Schema:**
- Complete description of flight offer object structure
- Detailed field descriptions matching DATA CONTRACT
- Proper type definitions for all fields
- Required field validation in input schema

## Cross-Platform Compatibility

### Path Handling Improvements

**Before (Issue):**
```python
# Hardcoded Windows-style paths
DATABASE_PATH = "generated\\travel_maps\\amadeus-mcp-server\\amadeus_mcp_server_database.json"
```

**After (Fixed):**
```python
# Cross-platform Path objects with forward slashes
from pathlib import Path
DATABASE_PATH = Path("generated/travel_maps/amadeus-mcp-server/amadeus_mcp_server_database.json")
```

### Benefits:
- Works on Windows, Linux, and macOS
- No hardcoded path separators
- Uses standard library `Path` objects for robust path manipulation

## Testing Strategy

### Unit Tests (`test_database_generation.py`)
- Database file existence and structure validation
- Required field presence and data type checking
- Airport code validation
- Schema compliance verification

### Integration Tests (`test_server_integration.py`)
- Database loading functionality
- Search with exact matches
- Round-trip flight searches
- Travel class filtering
- Passenger capacity validation
- Edge cases (no results)

## Error Handling

### Database Loading:
- Graceful fallback to empty structure if file missing
- Validation of required top-level keys
- UTF-8 encoding support for international characters

### Search Operations:
- Type validation for all parameters
- Safe access to optional fields with defaults
- Empty results for non-matching queries (not errors)

## Performance Considerations

- Database loaded once per server instance
- In-memory filtering for fast search operations
- No network requests or external API calls
- Deterministic search results based on offline data

## Deployment Notes

### Requirements:
- Python 3.7+
- FastMCP library
- Access to generated database JSON file

### Running the Server:
```bash
python amadeus_mcp_server_server.py
```

### Testing:
```bash
# Run database tests
python test_database_generation.py

# Run integration tests  
python test_server_integration.py
```

## Data Contract Compliance

The implementation strictly adheres to the DATA CONTRACT:

- ✅ Top-level `flight_offers` key present
- ✅ All required fields in flight offer objects
- ✅ Correct data types for all fields
- ✅ No additional fields beyond contract
- ✅ Proper validation and error handling

## Future Enhancements

Potential improvements for production use:

1. **Search Optimization**: Indexing for faster searches
2. **Date Range Support**: Flexible date matching
3. **Price Filtering**: Min/max price constraints
4. **Airline Preferences**: Airline-specific filtering
5. **Caching**: Response caching for repeated queries
6. **Metrics**: Search performance monitoring

## Security Considerations

- No external network access
- Input validation for all parameters
- No sensitive data exposure
- Read-only database operations