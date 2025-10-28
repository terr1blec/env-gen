# Database Generation Process

## Overview
Generated synthetic dog shelter data for San Francisco using deterministic random generation with seed 42.

## Data Characteristics
- 18 dog shelters across different SF neighborhoods
- Realistic coordinates within neighborhood boundaries
- Services: adoption, boarding, grooming, training, emergency
- Capacity: 20-100 dogs per shelter
- Occupancy: 30-95% of capacity
- Contact information: phone, website, hours

## Schema Compliance
Data follows the DATA CONTRACT exactly:
- Top-level key: "shelters"
- Required fields: id, name, address, neighborhood, latitude, longitude
- Optional fields: hours, phone, website, services, capacity, current_occupancy

## Generation Method
Used Python's random module with fixed seed for reproducibility. Neighborhood coordinates are based on approximate SF neighborhood centers with slight variations.