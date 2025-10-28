# Kakao Navigation Database Generation

## Overview
This module generates synthetic Korean navigation data for Kakao Navigation following the DATA CONTRACT schema.

## Data Generation Strategy

### Addresses
- 10 major Seoul landmarks with realistic Korean addresses
- Coordinates within Seoul area (37.5-37.7 latitude, 126.9-127.1 longitude)
- Includes subway stations, landmarks, shopping districts, and tourist attractions

### Directions
- 8 predefined routes between major landmarks
- Realistic distance calculations based on coordinate differences
- Duration estimates with traffic variations
- Route details with traffic condition descriptions

### Future Directions
- 6 routes with specific departure times
- Traffic predictions based on time of day
- Different traffic multipliers for rush hour vs normal times
- Realistic duration adjustments

### Multi-destination Directions
- 4 multi-stop routes for delivery/tour scenarios
- Sequential distance calculations
- Thematic summaries (sightseeing, shopping, night views)
- Total distance and duration calculations

## Deterministic Generation
- Uses random seed 42 for reproducible results
- Consistent coordinate-based distance calculations
- Logical route pairings between nearby locations

## DATA CONTRACT Compliance
- All top-level keys present: addresses, directions, future_directions, multi_destination_directions
- All nested objects follow specified schema
- Korean text in appropriate fields
- Proper coordinate ranges for Seoul area

## Usage
```python
from kakao_navigation_database import generate_database, update_database

# Generate new database
db = generate_database(seed=42)

# Update existing database
updates = {
    "addresses": [new_address],
    "directions": [new_route]
}
updated_db = update_database(updates)
```