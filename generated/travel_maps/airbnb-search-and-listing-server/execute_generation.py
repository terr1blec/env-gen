#!/usr/bin/env python3
"""
Execute the dataset generation.
"""

import subprocess
import sys

# Execute the create_dataset.py script
result = subprocess.run([sys.executable, "create_dataset.py"], capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)

if result.stderr:
    print("STDERR:")
    print(result.stderr)

print(f"Return code: {result.returncode}")