# Flight Search Server - Example Usage

## Overview
The Flight Search Server provides flight search functionality using an offline database. It implements the `scrape_flights_tool` to search for flights based on various criteria.

## Basic Usage

### Simple One-Way Search
```python
from flight_search_server_server import scrape_flights_tool

result = scrape_flights_tool(
    departure_airport="YYZ",
    arrival_airport="LAX",
    departure_date="2024-03-15"
)
print(result['content'])
```

### Round-Trip Search
```python
result = scrape_flights_tool(
    departure_airport="YYZ",
    arrival_airport="LAX",
    departure_date="2024-03-15",
    return_date="2024-03-20"
)
```

### Search with Passengers
```python
result = scrape_flights_tool(
    departure_airport="YYZ",
    arrival_airport="LAX",
    departure_date="2024-03-15",
    adults=2,
    students=1,
    children=["11", "1S"]
)
```

## Advanced Filtering

### Price and Stops Filtering
```python
result = scrape_flights_tool(
    departure_airport="YVR",
    arrival_airport="JFK",
    departure_date="2024-03-16",
    max_price=1500.0,
    stops=1
)
```

### Airline and Alliance Filtering
```python
result = scrape_flights_tool(
    departure_airport="LHR",
    arrival_airport="CDG",
    departure_date="2024-03-17",
    include_airlines=["BA", "AF"],
    alliance="STAR_ALLIANCE"
)
```

### Cabin Class and Wi-Fi
```python
result = scrape_flights_tool(
    departure_airport="SFO",
    arrival_airport="HKG",
    departure_date="2024-03-18",
    plane_type="first",
    wifi_only=True
)
```

## Pagination

### Limit Results
```python
result = scrape_flights_tool(
    departure_airport="YYC",
    arrival_airport="YUL",
    departure_date="2024-03-19",
    start_index=0,
    end_index=3
)
```

## Available Parameters

### Required Parameters
- `departure_airport`: 3-letter IATA code (e.g., "YYZ", "LAX")
- `arrival_airport`: 3-letter IATA code (e.g., "JFK", "CDG")
- `departure_date`: ISO 8601 format (YYYY-MM-DD)

### Optional Parameters
- `return_date`: Return date for round-trip flights
- `adults`: Number of adult passengers
- `students`: Number of student passengers
- `children`: List of child types ("11", "1S", "1L")
- `plane_type`: Cabin class ("economy", "premium", "business", "first")
- `sort_option`: Sort order for results
- `carry_on_free`: Minimum free carry-on bags
- `checked_bags_free`: Minimum free checked bags
- `stops`: Maximum number of stops
- `max_price`: Maximum price in CAD
- `alliance`: Airline alliance
- `include_airlines`: Airlines to include
- `exclude_airlines`: Airlines to exclude
- `wifi_only`: Wi-Fi requirement
- `start_index`: Pagination start
- `end_index`: Pagination end

## Output Format
The server returns a dictionary with a `content` key containing formatted flight results separated by "---". Each flight result includes:
- Flight ID and route
- Dates and passenger information
- Filtering criteria used
- Available flights with pricing, times, airlines, and stop details

## Error Handling
- If no flights match the criteria, returns "No flights found matching the specified criteria."
- If database file is missing, falls back to empty database
- Validates required fields in database structure