#!/usr/bin/env python3
"""
Simple test script to verify authentication functionality.
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_API_KEY = "test-admin-key-12345"  # Default admin key from user store

def test_auth_endpoints():
    """Test authentication endpoints."""
    print("Testing Code Review Assistant Authentication...")
    
    # Test 1: Create API key (no auth required)
    print("\n1. Testing API key creation...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/api-key", json={
            "email": "test@example.com",
            "rate_limit_tier": "standard"
        })
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Created API key: {data['api_key'][:20]}...")
            new_api_key = data['api_key']
        else:
            print(f"Error: {response.text}")
            new_api_key = None
    except Exception as e:
        print(f"Error: {e}")
        new_api_key = None
    
    # Test 2: Get current user info (with auth)
    print("\n2. Testing authenticated endpoint...")
    headers = {"Authorization": f"Bearer {TEST_API_KEY}"}
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"User ID: {data['id']}")
            print(f"Rate limit tier: {data['rate_limit_tier']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Test rate limit info
    print("\n3. Testing rate limit endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/rate-limit", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Rate limit: {data['requests_per_minute']}/min")
            print(f"Current usage: {data['current_usage']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Test unauthorized access
    print("\n4. Testing unauthorized access...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me")
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✓ Correctly rejected unauthorized request")
        else:
            print(f"✗ Unexpected response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Test invalid API key
    print("\n5. Testing invalid API key...")
    invalid_headers = {"Authorization": "Bearer invalid-key-12345"}
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=invalid_headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✓ Correctly rejected invalid API key")
        else:
            print(f"✗ Unexpected response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 6: Test X-API-Key header format
    print("\n6. Testing X-API-Key header format...")
    api_key_headers = {"X-API-Key": TEST_API_KEY}
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=api_key_headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✓ X-API-Key header format works")
        else:
            print(f"✗ X-API-Key failed: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_security_headers():
    """Test security headers."""
    print("\n\nTesting Security Headers...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        
        # Check for security headers
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Content-Security-Policy",
            "Referrer-Policy"
        ]
        
        for header in security_headers:
            if header in response.headers:
                print(f"✓ {header}: {response.headers[header]}")
            else:
                print(f"✗ Missing {header}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Make sure the server is running on http://localhost:8000")
    print("You can start it with: python main.py")
    
    test_auth_endpoints()
    test_security_headers()
    
    print("\n" + "="*50)
    print("Authentication and Security Test Complete!")
    print("="*50)