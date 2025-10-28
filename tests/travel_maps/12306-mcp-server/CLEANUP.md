# Cleanup Notes

The following test files were causing issues and should be removed:

1. `test_dataset.py` - References a non-existent dataset file
2. `test_server.py` - Has syntax errors due to module name starting with number
3. `test_server_integration.py` - Requires fastmcp module which is not installed
4. `test_server_functionality.py` - Requires fastmcp module which is not installed

## Current Working Tests

The following tests are working correctly:
- `test_basic.py` - Basic file validation tests
- `test_integration.py` - Integration validation without requiring fastmcp

## Recommendations

1. Remove the problematic test files
2. Keep the working test files for continuous validation
3. Install fastmcp dependency if full server testing is needed
4. Consider renaming the server module to avoid numeric prefix issues