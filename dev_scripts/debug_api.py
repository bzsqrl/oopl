
import requests
import os
import shutil

# Ensure we have a file to upload
test_file = "uploads/Waterfall 15 (30s).mov"
if not os.path.exists(test_file):
    print("Test file not found")
    exit(1)

api_url = "http://localhost:8000"

# 1. Upload
print("Uploading...")
files = {'files': open(test_file, 'rb')}
res = requests.post(f"{api_url}/upload/", files=files)
if res.status_code != 200:
    print(f"Upload failed: {res.text}")
    exit(1)

uploaded_path = res.json()['uploaded'][0]
print(f"Uploaded to: {uploaded_path}")

# 2. Process with HAP
print("Processing with format='hap'...")
params = {
    'file_path': uploaded_path,
    'crossfade_duration': 1.0,
    'format': 'hap'
}

res = requests.post(f"{api_url}/process/", params=params)
if res.status_code != 200:
    print(f"Process failed: {res.text}")
    print(f"Request url: {res.url}")
    exit(1)

output_file = res.json()['output_file']
print(f"Success: {output_file}")

# Verify file matches expectation
if not output_file.endswith(".mov"):
    print("FAILURE: Output file extension is not .mov")
else:
    print("SUCCESS: Output file extension is .mov")
