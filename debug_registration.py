#!/usr/bin/env python3
"""
Debug script to check registration error
"""

import requests
import json

def debug_registration():
    """Debug the registration issue"""
    
    print("🔍 Debugging Registration Issue")
    print("=" * 40)
    
    # Test registration with detailed error
    register_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post("http://localhost:8000/auth/register", json=register_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            # Try with a different email
            register_data["email"] = "test2@example.com"
            response2 = requests.post("http://localhost:8000/auth/register", json=register_data)
            print(f"\nTrying with different email:")
            print(f"Status Code: {response2.status_code}")
            print(f"Response: {response2.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_registration()
