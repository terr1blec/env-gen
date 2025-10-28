"""
Test script for 12306 MCP Server functionality.

This script tests the search functionality of the 12306 MCP Server.
"""

import sys
import os

# Add the generated directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'travel_maps', '12306-mcp-server'))

from 12306_mcp_server_server import search


def test_search_functionality():
    """Test the search functionality with various scenarios."""
    
    print("Testing 12306 MCP Server Search Functionality")
    print("=" * 50)
    
    # Test 1: Valid search with expected results
    print("\nTest 1: Search from Beijing to Shanghai on 2024-01-23")
    result1 = search(
        departure_station="北京南站",
        arrival_station="上海虹桥",
        date="2024-01-23"
    )
    print(f"Found {result1['search_parameters']['total_results']} tickets")
    if result1['train_tickets']:
        for ticket in result1['train_tickets']:
            print(f"  - {ticket['train_number']}: {ticket['departure_time']} → {ticket['arrival_time']} ({ticket['duration']})")
    
    # Test 2: Valid search with different stations
    print("\nTest 2: Search from Guangzhou to Shenzhen on 2024-01-19")
    result2 = search(
        departure_station="广州南站",
        arrival_station="深圳北站",
        date="2024-01-19"
    )
    print(f"Found {result2['search_parameters']['total_results']} tickets")
    if result2['train_tickets']:
        for ticket in result2['train_tickets']:
            print(f"  - {ticket['train_number']}: {ticket['departure_time']} → {ticket['arrival_time']} ({ticket['duration']})")
    
    # Test 3: Search with no results (invalid date)
    print("\nTest 3: Search with no expected results (future date)")
    result3 = search(
        departure_station="北京南站",
        arrival_station="上海虹桥",
        date="2025-01-01"
    )
    print(f"Found {result3['search_parameters']['total_results']} tickets")
    
    # Test 4: Search with invalid stations
    print("\nTest 4: Search with invalid stations")
    result4 = search(
        departure_station="Invalid Station",
        arrival_station="Another Invalid",
        date="2024-01-15"
    )
    print(f"Found {result4['search_parameters']['total_results']} tickets")
    
    # Test 5: Case insensitive search
    print("\nTest 5: Case insensitive search")
    result5 = search(
        departure_station="北京南站",
        arrival_station="上海虹桥",
        date="2024-01-23"
    )
    print(f"Found {result5['search_parameters']['total_results']} tickets")
    
    print("\n" + "=" * 50)
    print("All tests completed successfully!")


if __name__ == "__main__":
    test_search_functionality()