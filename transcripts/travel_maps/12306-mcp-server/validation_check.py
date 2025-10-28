"""
12306 MCP Server Data Contract Validation

This script validates that the server implementation and dataset comply with the data contract.
"""

import json
import os
import sys

# Add the server module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "generated", "travel_maps", "12306-mcp-server"))

from 12306_mcp_server_server import search, validate_date_format, load_dataset


def validate_data_contract():
    """Validate that the dataset follows the data contract schema"""
    print("=" * 60)
    print("DATA CONTRACT VALIDATION")
    print("=" * 60)
    
    try:
        # Load dataset
        dataset = load_dataset()
        print("✓ Dataset loaded successfully")
        
        # Check top-level keys
        required_top_keys = ["search_results"]
        for key in required_top_keys:
            if key not in dataset:
                print(f"✗ Missing required top-level key: {key}")
                return False
            print(f"✓ Required top-level key present: {key}")
        
        # Check search_results is a list
        if not isinstance(dataset["search_results"], list):
            print("✗ 'search_results' must be a list")
            return False
        print("✓ 'search_results' is a list")
        
        # Validate each train entry
        required_train_fields = [
            "train_number", "departure_station", "arrival_station",
            "departure_time", "arrival_time", "duration", "date"
        ]
        
        optional_train_fields = ["seat_types", "prices", "available_seats"]
        
        for i, train in enumerate(dataset["search_results"]):
            print(f"\nValidating train entry {i + 1}:")
            
            # Check required fields
            for field in required_train_fields:
                if field not in train:
                    print(f"  ✗ Missing required field: {field}")
                    return False
                if not isinstance(train[field], str):
                    print(f"  ✗ Field {field} must be a string")
                    return False
                print(f"  ✓ Required field present: {field}")
            
            # Check optional fields
            for field in optional_train_fields:
                if field in train:
                    if not isinstance(train[field], dict):
                        print(f"  ✗ Optional field {field} must be a dictionary")
                        return False
                    print(f"  ✓ Optional field present: {field}")
        
        print("\n✓ All data contract requirements satisfied!")
        return True
        
    except Exception as e:
        print(f"✗ Data contract validation failed: {e}")
        return False


def validate_server_functionality():
    """Validate that the server functions correctly"""
    print("\n" + "=" * 60)
    print("SERVER FUNCTIONALITY VALIDATION")
    print("=" * 60)
    
    test_cases = [
        # (description, departure, arrival, date, should_succeed)
        ("Valid search", "北京", "上海", "2024-03-15", True),
        ("Valid reverse search", "上海", "北京", "2024-03-15", True),
        ("No results", "北京", "广州", "2024-03-20", True),
        ("Invalid date format", "北京", "上海", "2024/03/15", False),
        ("Empty departure", "", "上海", "2024-03-15", False),
        ("Empty arrival", "北京", "", "2024-03-15", False),
    ]
    
    all_passed = True
    
    for description, departure, arrival, date, should_succeed in test_cases:
        print(f"\nTest: {description}")
        print(f"  Input: {departure} → {arrival} on {date}")
        
        try:
            result = search(departure, arrival, date)
            
            if should_succeed:
                print(f"  ✓ Success - Found {len(result['search_results'])} trains")
                if len(result['search_results']) > 0:
                    for train in result['search_results']:
                        print(f"    - {train['train_number']}: {train['departure_time']} → {train['arrival_time']}")
            else:
                print(f"  ✗ Unexpected success (should have failed)")
                all_passed = False
                
        except Exception as e:
            if not should_succeed:
                print(f"  ✓ Expected failure: {e}")
            else:
                print(f"  ✗ Unexpected failure: {e}")
                all_passed = False
    
    return all_passed


def validate_metadata():
    """Validate that the metadata file exists and has correct structure"""
    print("\n" + "=" * 60)
    print("METADATA VALIDATION")
    print("=" * 60)
    
    metadata_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "generated", "travel_maps", "12306-mcp-server", "12306_mcp_server_metadata.json"
    )
    
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print("✓ Metadata file loaded successfully")
        
        # Check required top-level fields
        required_fields = ["name", "description", "tools"]
        for field in required_fields:
            if field not in metadata:
                print(f"✗ Missing required metadata field: {field}")
                return False
            print(f"✓ Required metadata field present: {field}")
        
        # Check server name
        if metadata["name"] != "12306 MCP Server":
            print(f"✗ Server name should be '12306 MCP Server', got: {metadata['name']}")
            return False
        print("✓ Server name is correct")
        
        # Check tools array
        if not isinstance(metadata["tools"], list):
            print("✗ 'tools' must be a list")
            return False
        print(f"✓ Found {len(metadata['tools'])} tool(s)")
        
        # Check each tool
        for tool in metadata["tools"]:
            tool_name = tool.get("name", "unknown")
            print(f"\n  Validating tool: {tool_name}")
            
            # Check tool structure
            tool_fields = ["name", "description", "input_schema", "output_schema"]
            for field in tool_fields:
                if field not in tool:
                    print(f"    ✗ Missing tool field: {field}")
                    return False
                print(f"    ✓ Tool field present: {field}")
            
            # Check input schema
            input_schema = tool["input_schema"]
            if input_schema.get("type") != "object":
                print(f"    ✗ Input schema type should be 'object'")
                return False
            print(f"    ✓ Input schema type is 'object'")
            
            # Check output schema
            output_schema = tool["output_schema"]
            if output_schema.get("type") != "object":
                print(f"    ✗ Output schema type should be 'object'")
                return False
            print(f"    ✓ Output schema type is 'object'")
        
        print("\n✓ All metadata requirements satisfied!")
        return True
        
    except Exception as e:
        print(f"✗ Metadata validation failed: {e}")
        return False


def main():
    """Run all validation checks"""
    print("12306 MCP Server - Comprehensive Validation Check\n")
    
    results = []
    
    # Run validations
    results.append(("Data Contract", validate_data_contract()))
    results.append(("Server Functionality", validate_server_functionality()))
    results.append(("Metadata", validate_metadata()))
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("The 12306 MCP Server implementation is fully compliant.")
    else:
        print("❌ SOME VALIDATIONS FAILED!")
        print("Please review the failed checks above.")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)