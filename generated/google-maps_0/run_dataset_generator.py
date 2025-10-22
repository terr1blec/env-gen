#!/usr/bin/env python3
"""
Simple runner for the Google Maps dataset generator.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from google_maps_dataset import main

if __name__ == "__main__":
    main()