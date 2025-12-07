import os
from exporters import export_to_fcpxml
import numpy as np

# Create dummy data
timestamps = np.array([1.0, 2.5, 3.0, 4.2])
output_path = "test_export.fcpxml"

print(f"Testing FCPXML export to {output_path}...")
try:
    export_to_fcpxml(timestamps, output_path, fps=24, duration_seconds=10.0)
    if os.path.exists(output_path):
        print("Success! File created.")
        with open(output_path, 'r') as f:
            print("Content preview:")
            print(f.read()[:200] + "...")
        os.remove(output_path)
    else:
        print("Error: File not created.")
except Exception as e:
    print(f"Error during export: {e}")
