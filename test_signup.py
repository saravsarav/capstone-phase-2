import requests
import json

url = "http://127.0.0.1:8000/signup"
data = {
    "email": "saravanan@example.com",
    "password": "password123",
    "full_name": "saravanan"
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
