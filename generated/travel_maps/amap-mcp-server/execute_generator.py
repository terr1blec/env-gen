import subprocess
import sys

# Run the generator
result = subprocess.run([sys.executable, "run_generator.py"], capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)

print(f"Return code: {result.returncode}")