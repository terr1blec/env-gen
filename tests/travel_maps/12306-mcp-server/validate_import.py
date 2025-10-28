"""
Simple validation script to ensure the server module can be imported correctly.
"""

import sys
import os

# Add the generated directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'generated', 'travel_maps', '12306-mcp-server'))

try:
    # Try to import the server module
    from 12306_mcp_server_server import search, load_database
    print("✓ Successfully imported 12306 MCP Server module")
    
    # Test database loading
    database = load_database()
    if "train_tickets" in database:
        print(f"✓ Successfully loaded database with {len(database['train_tickets'])} tickets")
    else:
        print("✗ Database structure invalid")
        
    # Test search function signature
    import inspect
    sig = inspect.signature(search)
    expected_params = ['departure_station', 'arrival_station', 'date']
    actual_params = list(sig.parameters.keys())
    
    if actual_params == expected_params:
        print("✓ Search function has correct parameters")
    else:
        print(f"✗ Search function parameters mismatch. Expected: {expected_params}, Got: {actual_params}")
        
    print("\nValidation completed successfully!")
    
except ImportError as e:
    print(f"✗ Failed to import server module: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Validation error: {e}")
    sys.exit(1)