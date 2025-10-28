"""
12306 MCP Server Usage Examples

This script demonstrates realistic usage scenarios for the 12306 MCP Server,
including successful searches and error handling.
"""

import json
import os
import sys

# Add the server module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "generated", "travel_maps", "12306-mcp-server"))

from 12306_mcp_server_server import search, validate_date_format, load_dataset


def print_search_result(result):
    """Pretty print search results"""
    print(f"Found {len(result['search_results'])} train(s)")
    for train in result["search_results"]:
        print(f"\nTrain: {train['train_number']}")
        print(f"  Route: {train['departure_station']} → {train['arrival_station']}")
        print(f"  Time: {train['departure_time']} - {train['arrival_time']} ({train['duration']})")
        print(f"  Date: {train['date']}")
        
        if "prices" in train:
            print("  Prices:")
            for seat_type, price in train["prices"].items():
                print(f"    {seat_type}: {price}")
        
        if "available_seats" in train:
            print("  Available Seats:")
            for seat_type, seats in train["available_seats"].items():
                print(f"    {seat_type}: {seats}")


def example_1_successful_search():
    """Example 1: Successful search for Beijing to Shanghai"""
    print("=" * 60)
    print("EXAMPLE 1: Successful Search - Beijing to Shanghai")
    print("=" * 60)
    
    try:
        result = search("北京", "上海", "2024-03-15")
        print_search_result(result)
    except Exception as e:
        print(f"Error: {e}")


def example_2_successful_search_reverse():
    """Example 2: Successful search for Shanghai to Beijing"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Successful Search - Shanghai to Beijing")
    print("=" * 60)
    
    try:
        result = search("上海", "北京", "2024-03-15")
        print_search_result(result)
    except Exception as e:
        print(f"Error: {e}")


def example_3_no_results():
    """Example 3: Search with no matching results"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: No Results - Beijing to Guangzhou on different date")
    print("=" * 60)
    
    try:
        result = search("北京", "广州", "2024-03-20")
        print_search_result(result)
    except Exception as e:
        print(f"Error: {e}")


def example_4_invalid_date_format():
    """Example 4: Invalid date format"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Invalid Date Format")
    print("=" * 60)
    
    try:
        result = search("北京", "上海", "2024/03/15")
        print_search_result(result)
    except Exception as e:
        print(f"Error: {e}")


def example_5_empty_stations():
    """Example 5: Empty station names"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Empty Station Names")
    print("=" * 60)
    
    try:
        result = search("", "上海", "2024-03-15")
        print_search_result(result)
    except Exception as e:
        print(f"Error: {e}")


def example_6_multiple_routes():
    """Example 6: Search for multiple routes"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Multiple Route Search")
    print("=" * 60)
    
    routes = [
        ("北京", "上海", "2024-03-15"),
        ("上海", "深圳", "2024-03-17"),
        ("广州", "深圳", "2024-03-18"),
        ("北京", "天津", "2024-03-19")
    ]
    
    for departure, arrival, date in routes:
        print(f"\nSearching: {departure} → {arrival} on {date}")
        try:
            result = search(departure, arrival, date)
            print_search_result(result)
        except Exception as e:
            print(f"Error: {e}")


def example_7_date_validation():
    """Example 7: Date format validation examples"""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Date Format Validation")
    print("=" * 60)
    
    test_dates = [
        ("2024-03-15", True),    # Valid
        ("2024-12-31", True),    # Valid
        ("2025-01-01", True),    # Valid
        ("2024/03/15", False),   # Invalid separator
        ("15-03-2024", False),   # Wrong order
        ("2024-3-15", False),    # Single digit month
        ("2024-03-5", False),    # Single digit day
        ("not-a-date", False),   # Not a date
    ]
    
    for date_str, expected_valid in test_dates:
        is_valid = validate_date_format(date_str)
        status = "✓ Valid" if is_valid else "✗ Invalid"
        expected = "✓ Expected" if is_valid == expected_valid else "✗ Unexpected"
        print(f"  {date_str:15} → {status:10} ({expected})")


def example_8_dataset_inspection():
    """Example 8: Dataset structure inspection"""
    print("\n" + "=" * 60)
    print("EXAMPLE 8: Dataset Structure Inspection")
    print("=" * 60)
    
    try:
        dataset = load_dataset()
        print(f"Dataset loaded successfully")
        print(f"Number of train entries: {len(dataset['search_results'])}")
        
        # Show unique routes
        routes = set()
        for train in dataset["search_results"]:
            route = f"{train['departure_station']} → {train['arrival_station']}"
            routes.add(route)
        
        print(f"\nUnique routes in dataset:")
        for route in sorted(routes):
            print(f"  - {route}")
        
        # Show unique dates
        dates = set()
        for train in dataset["search_results"]:
            dates.add(train["date"])
        
        print(f"\nUnique dates in dataset:")
        for date in sorted(dates):
            print(f"  - {date}")
            
    except Exception as e:
        print(f"Error loading dataset: {e}")


if __name__ == "__main__":
    print("12306 MCP Server Usage Examples")
    print("Demonstrating realistic search scenarios and error handling\n")
    
    # Run all examples
    example_1_successful_search()
    example_2_successful_search_reverse()
    example_3_no_results()
    example_4_invalid_date_format()
    example_5_empty_stations()
    example_6_multiple_routes()
    example_7_date_validation()
    example_8_dataset_inspection()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)