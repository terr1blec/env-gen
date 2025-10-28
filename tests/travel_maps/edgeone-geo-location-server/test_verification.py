#!/usr/bin/env python3
"""
Verification script to ensure all review feedback items have been addressed.
"""

import json
import os
import sys

def verify_metadata_name():
    """Verify metadata name is 'edgeone-geo-location-server' (lowercase with hyphens)."""
    metadata_path = os.path.join(
        'generated', 'travel_maps', 'edgeone-geo-location-server',
        'edgeone_geo_location_server_metadata.json'
    )
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    expected_name = "edgeone-geo-location-server"
    actual_name = metadata.get('name')
    
    if actual_name == expected_name:
        print(f"✅ Metadata name: '{actual_name}' (correct)")
        return True
    else:
        print(f"❌ Metadata name: '{actual_name}' (expected: '{expected_name}')")
        return False

def verify_metadata_schema_fields():
    """Verify metadata uses camelCase for inputSchema/outputSchema."""
    metadata_path = os.path.join(
        'generated', 'travel_maps', 'edgeone-geo-location-server',
        'edgeone_geo_location_server_metadata.json'
    )
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    tool = metadata['tools'][0]
    
    # Check for camelCase fields
    has_input_schema = 'inputSchema' in tool
    has_output_schema = 'outputSchema' in tool
    
    # Check for underscore fields (should not exist)
    has_input_schema_underscore = 'input_schema' in tool
    has_output_schema_underscore = 'output_schema' in tool
    
    if has_input_schema and has_output_schema and not has_input_schema_underscore and not has_output_schema_underscore:
        print("✅ Metadata schema fields: camelCase (inputSchema/outputSchema)")
        return True
    else:
        print("❌ Metadata schema fields: incorrect format")
        print(f"   inputSchema: {has_input_schema}, outputSchema: {has_output_schema}")
        print(f"   input_schema: {has_input_schema_underscore}, output_schema: {has_output_schema_underscore}")
        return False

def verify_test_files():
    """Verify test files exist in the tests directory."""
    test_dir = 'tests/travel_maps/edgeone-geo-location-server'
    
    expected_files = [
        'test_edgeone_geo_location_server.py',
        'test_dataset_generator.py',
        'run_tests.py',
        'README.md'
    ]
    
    all_exist = True
    for file in expected_files:
        file_path = os.path.join(test_dir, file)
        if os.path.exists(file_path):
            print(f"✅ Test file: {file}")
        else:
            print(f"❌ Missing test file: {file}")
            all_exist = False
    
    return all_exist

def verify_transcripts():
    """Verify transcripts exist in the transcripts directory."""
    transcript_dir = 'transcripts/travel_maps/edgeone-geo-location-server'
    
    expected_files = [
        'dataset_implementation_explanation.md',
        'example_usage.md',
        'comprehensive_solution.md'
    ]
    
    all_exist = True
    for file in expected_files:
        file_path = os.path.join(transcript_dir, file)
        if os.path.exists(file_path):
            print(f"✅ Transcript: {file}")
        else:
            print(f"❌ Missing transcript: {file}")
            all_exist = False
    
    return all_exist

def verify_dataset_integrity():
    """Verify the dataset JSON file has correct structure and data."""
    dataset_path = os.path.join(
        'generated', 'travel_maps', 'edgeone-geo-location-server',
        'edgeone_geo_location_server_dataset.json'
    )
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    # Check top-level structure
    if 'geolocation_data' not in dataset:
        print("❌ Dataset missing top-level 'geolocation_data' key")
        return False
    
    locations = dataset['geolocation_data']
    
    if not isinstance(locations, list):
        print("❌ Dataset 'geolocation_data' is not a list")
        return False
    
    if len(locations) != 8:
        print(f"❌ Dataset has {len(locations)} locations (expected 8)")
        return False
    
    # Check each location
    required_fields = [
        'ip', 'country', 'country_code', 'region', 'region_name', 
        'city', 'zip', 'lat', 'lon', 'timezone', 'isp', 'org', 'as'
    ]
    
    all_valid = True
    for i, location in enumerate(locations):
        for field in required_fields:
            if field not in location:
                print(f"❌ Location {i} missing field: {field}")
                all_valid = False
    
    if all_valid:
        print(f"✅ Dataset integrity: {len(locations)} locations with all required fields")
    
    return all_valid

def main():
    """Run all verification checks."""
    print("EdgeOne Geo Location Server - Review Feedback Verification")
    print("=" * 60)
    
    checks = [
        ("Metadata name format", verify_metadata_name),
        ("Metadata schema field names", verify_metadata_schema_fields),
        ("Test files presence", verify_test_files),
        ("Transcripts presence", verify_transcripts),
        ("Dataset integrity", verify_dataset_integrity)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL REVIEW FEEDBACK ITEMS ADDRESSED SUCCESSFULLY")
        print("\nThe implementation now includes:")
        print("  • Correct metadata name: 'edgeone-geo-location-server'")
        print("  • camelCase schema fields: inputSchema/outputSchema")
        print("  • Comprehensive test suite")
        print("  • Detailed usage transcripts")
        print("  • Valid dataset structure")
    else:
        print("❌ SOME REVIEW FEEDBACK ITEMS NEED ATTENTION")
        sys.exit(1)

if __name__ == '__main__':
    main()