"""
Test script to verify user registration works with bcrypt
"""

import requests
import json

# Registration endpoint
url = "http://localhost:8000/api/v1/auth/register"

# Test data
payload = {
    "email": "user@example.com",
    "password": "stringst12$"
}

headers = {
    "Content-Type": "application/json"
}

print("Testing registration endpoint...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("-" * 50)

try:
    response = requests.post(url, json=payload, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("\n✅ Registration successful!")
        print("Check terminal logs for verification code.")
    elif response.status_code == 400:
        print("\n⚠️  User might already exist or validation failed")
    else:
        print(f"\n❌ Registration failed with status {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
