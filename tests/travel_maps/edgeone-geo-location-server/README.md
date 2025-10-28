# EdgeOne Geo Location Server - Tests

This directory contains unit tests for the edgeone-geo-location-server implementation.

## Test Files

- `test_edgeone_geo_location_server.py` - Tests for the server implementation
- `test_dataset_generator.py` - Tests for the dataset generator
- `run_tests.py` - Test runner script

## Running Tests

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test File
```bash
python -m unittest test_edgeone_geo_location_server.py
python -m unittest test_dataset_generator.py
```

### Run with Verbose Output
```bash
python -m unittest discover -v
```

## Test Coverage

### Server Tests (`test_edgeone_geo_location_server.py`)
- ✅ `get_geolocation` returns valid structure
- ✅ All required fields are present
- ✅ Field types are correct
- ✅ Data comes from the generated dataset
- ✅ Round-robin behavior works correctly
- ✅ No parameters required
- ✅ Dataset structure compliance

### Dataset Generator Tests (`test_dataset_generator.py`)
- ✅ Generator initialization
- ✅ Deterministic generation with seeds
- ✅ Different seeds produce different variations
- ✅ All location access methods work
- ✅ JSON dataset structure compliance
- ✅ Required fields presence
- ✅ Field type correctness
- ✅ Realistic value validation

## Test Data

The tests use the generated dataset from:
`generated/travel_maps/edgeone-geo-location-server/edgeone_geo_location_server_dataset.json`

## Test Environment

Tests automatically add the generated module path to Python's import path, so they can import the server and dataset modules directly.

## Continuous Integration

These tests can be integrated into CI/CD pipelines to ensure the server implementation remains compliant with the DATA CONTRACT.