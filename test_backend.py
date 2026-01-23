import requests
import json
import time

# Test the backend
print("Testing backend endpoints...")

# Test /stats
try:
    response = requests.get("http://127.0.0.1:8000/stats")
    print(f"\n/stats endpoint: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error calling /stats: {e}")

# Test /scans
try:
    response = requests.get("http://127.0.0.1:8000/scans")
    print(f"\n/scans endpoint: {response.status_code}")
    if response.status_code == 200:
        print(f"Number of scans: {len(response.json())}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error calling /scans: {e}")

# Test /scan (POST)
try:
    response = requests.post(
        "http://127.0.0.1:8000/scan",
        json={"url": "https://google.com"}
    )
    print(f"\n/scan endpoint (POST): {response.status_code}")
    if response.status_code == 200:
        scan_data = response.json()
        scan_id = scan_data['id']
        print(f"Scan initiated: {scan_id}")
        
        # Poll for results
        for i in range(15):
            time.sleep(1)
            check = requests.get(f"http://127.0.0.1:8000/scan/{scan_id}")
            if check.status_code == 200:
                data = check.json()
                print(f"Status: {data['status']}, Logs: {len(data.get('logs', []))}")
                if data['status'] == 'completed':
                    print(f"Scan completed! Found {len(data['vulnerabilities'])} vulnerabilities")
                    print(f"ML Score: {data['ml_severity_score']}")
                    break
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error calling /scan: {e}")
