# Flight Search Server Database Generation

## Overview
This database generator creates synthetic flight data that strictly follows the DATA CONTRACT structure for testing flight search functionality.

## Key Features

### Deterministic Generation
- Uses random seed (default: 42) for reproducible results
- Consistent flight IDs based on departure/arrival/date combinations
- Realistic pricing and timing patterns

### Data Coverage
- **Airports**: 30+ common IATA codes (YYZ, YVR, JFK, LAX, LHR, etc.)
- **Airlines**: 20+ IATA codes (AC, WS, AA, UA, etc.)
- **Alliances**: All major alliances covered (STAR_ALLIANCE, ONE_WORLD, SKY_TEAM, VALUE_ALLIANCE)
- **Cabin Classes**: All types (economy, premium, business, first)
- **Sort Options**: All 13 supported sort options
- **Passenger Types**: Adults, students, and children (11, 1S, 1L)

### Realistic Flight Data
- Mix of one-way and round-trip flights
- Various stop configurations (nonstop, 1-stop, 2-stops)
- Realistic pricing ranges ($200-$5000)
- Proper time formatting and stop details
- Optional parameters randomly included/excluded

## Database Structure Validation
The generated database has been validated to ensure:
- All required fields are present
- Airport codes follow IATA 3-letter format
- Dates follow ISO 8601 format (YYYY-MM-DD)
- Results arrays contain properly structured flight options
- All enum values are from allowed sets
- Numeric fields have appropriate ranges

## Usage
```python
from flight_search_server_database import generate_flight_database

# Generate database with custom parameters
generate_flight_database(
    output_path="flight_search_server_database.json",
    num_flights=100,  # Number of flight entries
    seed=42           # Random seed for determinism
)
```

## Integration with Server
The server implementation can load this database and filter flights based on search parameters, applying pagination and sorting as specified in the tool input schema.