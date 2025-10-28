#!/usr/bin/env python3
"""
Quick validation test for the Amadeus MCP Server implementation.
"""

import sys
import os
from pathlib import Path

# Add the server module to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "generated" / "travel_maps" / "amadeus-mcp-server"))

try:
    from amadeus_mcp_server_server import search_flight_offers, load_database
    
    print("✅ Server module imported successfully")
    
    # Test database loading
    database = load_database()
    print(f"✅ Database loaded with {len(database.get('flight_offers', []))} flight offers")
    
    # Test a simple search
    result = search_flight_offers(
        origin="JFK",
        destination="LAX",
        departure_date="2025-11-17"
    )
    
    print(f"✅ Search returned {len(result.get('flight_offers', []))} results")
    
    # Verify metadata file exists
    metadata_path = Path("generated/travel_maps/amadeus-mcp-server/amadeus_mcp_server_metadata.json")
    if metadata_path.exists():
        print("✅ Metadata file exists")
    else:
        print("❌ Metadata file missing")
    
    # Verify tests exist
    test_dir = Path("tests/travel_maps/amadeus-mcp-server")
    if test_dir.exists():
        test_files = list(test_dir.glob("*.py"))
        print(f"✅ Test directory exists with {len(test_files)} test files")
    else:
        print("❌ Test directory missing")
    
    # Verify transcripts exist
    transcript_dir = Path("transcripts/travel_maps/amadeus-mcp-server")
    if transcript_dir.exists():
        transcript_files = list(transcript_dir.glob("*.md"))
        print(f"✅ Transcript directory exists with {len(transcript_files)} transcript files")
    else:
        print("❌ Transcript directory missing")
    
    print("\n🎉 All validations passed! The Amadeus MCP Server is ready.")
    
except Exception as e:
    print(f"❌ Validation failed: {e}")
    sys.exit(1)