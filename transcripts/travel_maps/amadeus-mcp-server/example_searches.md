# Amadeus MCP Server - Example Search Transcripts

This document contains example search scenarios and expected responses from the Amadeus MCP Server.

## Example 1: Basic One-Way Flight Search

**Request:**
```json
{
  "origin": "JFK",
  "destination": "LAX", 
  "departure_date": "2025-11-17"
}
```

**Expected Response:**
```json
{
  "flight_offers": [
    {
      "id": "FL017",
      "origin": "JFK",
      "destination": "LAX",
      "departure_date": "2025-11-17",
      "return_date": "2025-11-18",
      "adults": 3,
      "children": 0,
      "infants": 0,
      "travel_class": "ECONOMY",
      "currency": "USD",
      "price": 615.28,
      "airline": "American Airlines",
      "flight_number": "AM158",
      "departure_time": "08:00",
      "arrival_time": "11:15",
      "duration": "3h 15m",
      "stops": 0
    }
  ]
}
```

## Example 2: Round-Trip Flight Search

**Request:**
```json
{
  "origin": "LHR",
  "destination": "CDG",
  "departure_date": "2025-10-30",
  "return_date": "2025-11-03"
}
```

**Expected Response:**
```json
{
  "flight_offers": [
    {
      "id": "FL001",
      "origin": "LHR",
      "destination": "CDG",
      "departure_date": "2025-10-30",
      "return_date": "2025-11-03",
      "adults": 2,
      "children": 0,
      "infants": 0,
      "travel_class": "ECONOMY",
      "currency": "USD",
      "price": 939.41,
      "airline": "Emirates",
      "flight_number": "EM132",
      "departure_time": "12:15",
      "arrival_time": "18:15",
      "duration": "6h 0m",
      "stops": 0
    }
  ]
}
```

## Example 3: Business Class Search

**Request:**
```json
{
  "origin": "LAX",
  "destination": "LHR",
  "departure_date": "2025-11-09",
  "travel_class": "BUSINESS"
}
```

**Expected Response:**
```json
{
  "flight_offers": [
    {
      "id": "FL085",
      "origin": "LAX",
      "destination": "LHR",
      "departure_date": "2025-11-09",
      "return_date": "2025-11-11",
      "adults": 1,
      "children": 0,
      "infants": 0,
      "travel_class": "BUSINESS",
      "currency": "USD",
      "price": 3192.36,
      "airline": "American Airlines",
      "flight_number": "AM341",
      "departure_time": "14:15",
      "arrival_time": "23:30",
      "duration": "9h 15m",
      "stops": 0
    }
  ]
}
```

## Example 4: Family Travel Search

**Request:**
```json
{
  "origin": "LAX",
  "destination": "CDG",
  "departure_date": "2025-11-27",
  "adults": 4,
  "children": 1,
  "infants": 0
}
```

**Expected Response:**
```json
{
  "flight_offers": [
    {
      "id": "FL031",
      "origin": "LAX",
      "destination": "CDG",
      "departure_date": "2025-11-27",
      "return_date": "2025-12-08",
      "adults": 4,
      "children": 1,
      "infants": 0,
      "travel_class": "ECONOMY",
      "currency": "USD",
      "price": 1519.1,
      "airline": "United Airlines",
      "flight_number": "UN897",
      "departure_time": "11:45",
      "arrival_time": "02:00",
      "duration": "14h 15m",
      "stops": 0
    }
  ]
}
```

## Example 5: No Results Search

**Request:**
```json
{
  "origin": "JFK",
  "destination": "CDG",
  "departure_date": "2025-12-31"
}
```

**Expected Response:**
```json
{
  "flight_offers": []
}
```

## Example 6: Premium Economy Search

**Request:**
```json
{
  "origin": "JFK",
  "destination": "SFO",
  "departure_date": "2025-11-02",
  "travel_class": "PREMIUM_ECONOMY"
}
```

**Expected Response:**
```json
{
  "flight_offers": [
    {
      "id": "FL027",
      "origin": "JFK",
      "destination": "SFO",
      "departure_date": "2025-11-02",
      "return_date": "",
      "adults": 2,
      "children": 1,
      "infants": 0,
      "travel_class": "PREMIUM_ECONOMY",
      "currency": "USD",
      "price": 456.91,
      "airline": "Singapore Airlines",
      "flight_number": "SI803",
      "departure_time": "19:00",
      "arrival_time": "23:30",
      "duration": "4h 30m",
      "stops": 1
    }
  ]
}
```

## Search Parameters Summary

- **Required Parameters**: `origin`, `destination`, `departure_date`
- **Optional Parameters**: `return_date`, `adults`, `children`, `infants`, `travel_class`, `currency`
- **Supported Travel Classes**: `ECONOMY`, `PREMIUM_ECONOMY`, `BUSINESS`, `FIRST`
- **Supported Currencies**: Primarily `USD` in the current database
- **Supported Airports**: JFK, LAX, LHR, CDG, SFO, DXB, FRA, ORD, ATL, DFW

## Notes

- The server performs exact matching on all search criteria
- Passenger capacity filtering ensures flights have sufficient seats
- All searches are case-sensitive for airport codes and travel classes
- Empty results are returned as an empty array, not an error