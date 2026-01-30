
import sys
import os

# Ensure we can import from backend
sys.path.append(os.getcwd())

from backend.processor import process_video_crossfade

input_file = os.path.abspath("uploads/Waterfall 8 (30s).mov")

print(f"Testing with: {input_file}")

try:
    output = process_video_crossfade(input_file, 1.0, "hap", "outputs")
    print(f"Success: {output}")
    print(f"Size: {os.path.getsize(output)} bytes")
except Exception as e:
    print(f"Error: {e}")
