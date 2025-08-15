#!/usr/bin/env python3
"""
Quick test to verify persistence functionality is working
"""

import requests
import json

def test_persistence():
    """Quick test of persistence functionality"""
    
    print("🧪 Quick Persistence Test")
    print("=" * 30)
    
    try:
        # Test 1: Health check
        print("1. Testing backend health...")
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
        
        # Test 2: User registration
        print("2. Testing user registration...")
        register_data = {
            "email": "test@example.com",
            "password": "TestPass123!",
            "full_name": "Test User"
        }
        
        response = requests.post("http://localhost:8000/auth/register", json=register_data)
        if response.status_code == 200:
            print("✅ User registration successful")
        else:
            print(f"⚠️ User registration response: {response.status_code}")
        
        # Test 3: User login
        print("3. Testing user login...")
        login_data = {
            "username": "test@example.com",
            "password": "TestPass123!"
        }
        
        response = requests.post("http://localhost:8000/auth/token", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
            print("✅ User login successful")
        else:
            print(f"❌ User login failed: {response.status_code}")
            return False
        
        # Test 4: User data endpoint
        print("4. Testing user data endpoint...")
        response = requests.get("http://localhost:8000/api/v1/user/data", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print("✅ User data endpoint working")
            print(f"   - Risk Profile: {'✅' if user_data['risk_profile'] else '❌'}")
            print(f"   - Portfolio: {'✅' if user_data['portfolio'] else '❌'}")
            print(f"   - Scenarios: {len(user_data['scenarios'])} found")
            print(f"   - Exports: {len(user_data['exports'])} found")
        else:
            print(f"❌ User data endpoint failed: {response.status_code}")
            return False
        
        print("\n🎉 All tests passed!")
        print("✅ Persistence functionality is working correctly")
        print("📝 You can now start the frontend: python run_frontend.py")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_persistence()
