import subprocess
import sys

# Run the regeneration script
result = subprocess.run([sys.executable, "regenerate_database.py"], capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)

print(f"Return code: {result.returncode}")