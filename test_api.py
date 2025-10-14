import requests
import json

# Test the API endpoints
base_url = "http://127.0.0.1:8000"

print("Testing Code Review Assistant API...")
print("=" * 50)

# Test 1: Health endpoint
print("1. Testing health endpoint...")
try:
    response = requests.get(f"{base_url}/api/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

print()

# Test 2: Limits endpoint  
print("2. Testing limits endpoint...")
try:
    response = requests.get(f"{base_url}/api/limits")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

print()

# Test 3: File upload without auth (should fail)
print("3. Testing file upload without authentication...")
try:
    files = {'file': ('test.py', 'print("hello")', 'text/plain')}
    response = requests.post(f"{base_url}/api/review", files=files)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

print()

# Test 4: File upload with auth
print("4. Testing file upload with authentication...")
try:
    headers = {"Authorization": "Bearer test-admin-key-12345"}
    files = {'file': ('test.py', 'print("hello world")', 'text/plain')}
    response = requests.post(f"{base_url}/api/review", files=files, headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

print()

# Test 5: List reports with auth
print("5. Testing list reports with authentication...")
try:
    headers = {"Authorization": "Bearer test-admin-key-12345"}
    response = requests.get(f"{base_url}/api/reviews", headers=headers)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")