#!/usr/bin/env python3
"""
Test script to verify file upload functionality.
"""

import requests
import json
import os

# Test file content
test_code = '''
def calculate_sum(a, b):
    """Calculate the sum of two numbers."""
    return a + b

def main():
    result = calculate_sum(5, 3)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
'''

def test_file_upload():
    """Test the file upload endpoint."""
    
    # API endpoint
    url = "http://localhost:8000/api/review"
    
    # Create a test file
    files = {
        'file': ('test_code.py', test_code, 'text/plain')
    }
    
    # No authentication headers needed when authentication is disabled
    headers = {}
    
    try:
        print("Testing file upload...")
        response = requests.post(url, files=files, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"Report ID: {result.get('report_id')}")
            print(f"Status: {result.get('status')}")
            print(f"Filename: {result.get('filename')}")
            print(f"Language: {result.get('language')}")
            
            # If processing is complete, try to get the report
            if result.get('status') == 'completed':
                report_id = result.get('report_id')
                report_url = f"http://localhost:8000/api/review/{report_id}"
                report_response = requests.get(report_url, headers=headers)
                
                if report_response.status_code == 200:
                    report_data = report_response.json()
                    print(f"\n📊 Analysis Results:")
                    print(f"Summary: {report_data.get('summary', 'No summary')}")
                    print(f"Issues found: {len(report_data.get('issues', []))}")
                    print(f"Recommendations: {len(report_data.get('recommendations', []))}")
                else:
                    print(f"❌ Failed to get report: {report_response.status_code}")
                    print(report_response.text)
            
        else:
            print("❌ Upload failed!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is the server running?")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_limits_endpoint():
    """Test the limits endpoint."""
    try:
        response = requests.get("http://localhost:8000/api/limits", timeout=10)
        if response.status_code == 200:
            limits = response.json()
            print(f"\n📋 System Limits:")
            print(f"Max file size: {limits.get('max_file_size_mb')}MB")
            print(f"Supported languages: {limits.get('supported_languages')}")
            print(f"Supported extensions: {limits.get('supported_extensions')}")
        else:
            print(f"❌ Failed to get limits: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting limits: {e}")

if __name__ == "__main__":
    print("🧪 Testing Code Review Assistant File Upload")
    print("=" * 50)
    
    # Test system limits first
    test_limits_endpoint()
    
    # Test file upload
    test_file_upload()