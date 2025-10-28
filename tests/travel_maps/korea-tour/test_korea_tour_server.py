"""
Test suite for Korea Tour MCP Server
"""

import json
import os
import sys
from unittest.mock import patch

# Add the server module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "generated", "travel_maps", "korea-tour"))

from korea_tour_server import get_area_code, search_tour_info, get_detail_common, load_database


class TestKoreaTourServer:
    """Test cases for Korea Tour MCP Server tools."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_database = {
            "area_codes": [
                {"areaCode": "1", "name": "Seoul", "rnum": 1, "sub_areas": [
                    {"areaCode": "101", "name": "Gangnam-gu", "rnum": 101}
                ]},
                {"areaCode": "2", "name": "Busan", "rnum": 2, "sub_areas": []}
            ],
            "tour_info": [
                {
                    "contentid": "12000000",
                    "contenttypeid": "12",
                    "title": "Gyeongbokgung Palace",
                    "addr1": "Gyeongbokgung Palace, Seoul",
                    "areacode": "1"
                }
            ],
            "detail_common": [
                {
                    "contentid": "12000000",
                    "contenttypeid": "12",
                    "title": "Gyeongbokgung Palace",
                    "overview": "Test overview"
                }
            ]
        }

    def test_load_database_success(self):
        """Test loading database successfully."""
        with patch('korea_tour_server.json.load') as mock_load:
            mock_load.return_value = self.test_database
            database = load_database()
            
            assert "area_codes" in database
            assert "tour_info" in database
            assert "detail_common" in database

    def test_get_area_code_all(self):
        """Test getting all area codes."""
        with patch('korea_tour_server.DATABASE', self.test_database):
            result = get_area_code()
            
            assert isinstance(result, list)
            assert len(result) == 2

    def test_get_area_code_specific(self):
        """Test getting specific area code."""
        with patch('korea_tour_server.DATABASE', self.test_database):
            result = get_area_code(areaCode="1")
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["areaCode"] == "101"

    def test_search_tour_info_all(self):
        """Test searching all tour info."""
        with patch('korea_tour_server.DATABASE', self.test_database):
            result = search_tour_info()
            
            assert isinstance(result, list)
            assert len(result) == 1

    def test_search_tour_info_by_area(self):
        """Test searching tour info by area code."""
        with patch('korea_tour_server.DATABASE', self.test_database):
            result = search_tour_info(areaCode="1")
            
            assert isinstance(result, list)
            assert len(result) == 1

    def test_get_detail_common_success(self):
        """Test getting detail common information successfully."""
        with patch('korea_tour_server.DATABASE', self.test_database):
            result = get_detail_common(contentId="12000000")
            
            assert isinstance(result, dict)
            assert result["contentid"] == "12000000"

    def test_get_detail_common_not_found(self):
        """Test getting detail common information for non-existent content."""
        with patch('korea_tour_server.DATABASE', self.test_database):
            result = get_detail_common(contentId="99999999")
            
            assert result is None