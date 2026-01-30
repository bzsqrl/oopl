import sys
import os
import subprocess
import glob

# Ensure desktop_app is in path
sys.path.append(os.path.abspath('desktop_app'))

from processor import process_video_crossfade, get_video_duration, get_ffmpeg_path, get_ffprobe_path

# Setup paths
input_file = r'c:/Users/beatf/Documents/Antigravity/uploads/Whorld Cartoon.mp4'
output_dir = r'c:/Users/beatf/Documents/Antigravity/outputs'
target_duration = 5.0
crossfade = 1.0

# Ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print(f"Testing trim logic with input: {input_file}")
print(f"Target duration: {target_duration}s")
print(f"Crossfade duration: {crossfade}s")

try:
    # Process
    output_path = process_video_crossfade(
        input_file,
        crossfade_duration=crossfade,
        output_format='mp4',
        target_output_duration=target_duration
    )
    
    print(f"Processing complete. Output: {output_path}")
    
    # Verify duration
    if os.path.exists(output_path):
        actual_duration = get_video_duration(output_path)
        print(f"Actual output duration: {actual_duration}s")
        
        # Tolerance of 0.5s
        if abs(actual_duration - target_duration) < 0.5:
            print("SUCCESS: Duration is within tolerance.")
        else:
            print("FAILURE: Duration mismatch.")
            sys.exit(1)
    else:
        print("FAILURE: Output file not found.")
        sys.exit(1)

except Exception as e:
    print(f"Error during verification: {e}")
    sys.exit(1)
