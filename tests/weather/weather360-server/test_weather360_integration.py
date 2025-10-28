"""
Integration tests for Weather360 FastMCP server.

These tests validate the server module structure and basic functionality
without requiring the fastmcp dependency to be installed.
"""

import json
import pytest
import sys
from pathlib import Path


class TestWeather360Integration:
    """Integration test suite for Weather360 FastMCP server."""
    
    @pytest.fixture
    def server_module_path(self):
        """Return the path to the server module."""
        return Path(__file__).parent.parent.parent.parent / "generated" / "weather" / "weather360-server" / "weather360_server_server.py"
    
    def test_server_module_exists(self, server_module_path):
        """Test that the server module file exists."""
        assert server_module_path.exists(), f"Server module not found: {server_module_path}"
        assert server_module_path.is_file(), f"Server module path is not a file: {server_module_path}"
    
    def test_server_module_structure(self, server_module_path):
        """Test that the server module has expected structure."""
        with open(server_module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required components
        assert "FastMCP" in content, "Server module missing FastMCP import"
        assert "@mcp.tool()" in content, "Server module missing tool decorator"
        assert "def get_live_weather" in content, "Server module missing get_live_weather function"
        assert "def load_database" in content, "Server module missing load_database function"
        assert "mcp.run()" in content, "Server module missing mcp.run() call"
    
    def test_server_module_docstring(self, server_module_path):
        """Test that the server module has proper documentation."""
        with open(server_module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for module docstring
        assert '"""' in content, "Server module missing docstring"
        assert "Weather360 Server" in content, "Server module docstring missing server name"
    
    def test_server_function_signatures(self, server_module_path):
        """Test that server functions have correct signatures."""
        with open(server_module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check get_live_weather signature
        assert "def get_live_weather(latitude: float, longitude: float)" in content, \
            "get_live_weather function has incorrect signature"
        
        # Check load_database signature
        assert "def load_database()" in content, \
            "load_database function has incorrect signature"
    
    def test_server_error_handling(self, server_module_path):
        """Test that server has proper error handling."""
        with open(server_module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for error handling
        assert "try:" in content, "Server module missing try blocks"
        assert "except" in content, "Server module missing except blocks"
        assert "ValueError" in content, "Server module missing ValueError handling"
        assert "FileNotFoundError" in content, "Server module missing FileNotFoundError handling"
    
    def test_server_logging(self, server_module_path):
        """Test that server has proper logging."""
        with open(server_module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for logging
        assert "import logging" in content, "Server module missing logging import"
        assert "logger" in content, "Server module missing logger usage"
    
    def test_server_database_config(self, server_module_path):
        """Test that server has database configuration."""
        with open(server_module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for database configuration
        assert "DATABASE_PATH" in content, "Server module missing DATABASE_PATH configuration"
        assert "weather360_server_database.json" in content, "Server module missing database filename"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])