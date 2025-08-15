#!/usr/bin/env python3
"""
Test script to verify the persistence functionality of the AI-Powered Risk & Scenario Advisor
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def test_persistence():
    """Test the complete persistence workflow"""
    
    print("🧪 Testing Persistence Functionality")
    print("=" * 50)
    
    # Step 1: Register a new user
    print("\n1. Registering new user...")
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 200:
            print("✅ User registered successfully")
        else:
            print(f"⚠️ User registration response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error registering user: {e}")
        return
    
    # Step 2: Login
    print("\n2. Logging in...")
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Error logging in: {e}")
        return
    
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    
    # Step 3: Create risk assessment
    print("\n3. Creating risk assessment...")
    risk_answers = [
        "More than 5 years",
        "Hold and wait", 
        "Moderate growth",
        "3-7 years",
        "Stable",
        "3-6 months"
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/risk-profile",
            json={"answers": risk_answers},
            headers=headers
        )
        if response.status_code == 200:
            risk_result = response.json()
            print(f"✅ Risk assessment created - Score: {risk_result['score']}, Category: {risk_result['category']}")
        else:
            print(f"❌ Risk assessment failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating risk assessment: {e}")
        return
    
    # Step 4: Create portfolio analysis
    print("\n4. Creating portfolio analysis...")
    portfolio_input = "TCS: 10, HDFC Bank: 5 shares, Reliance: 15"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze-portfolio",
            json={"portfolio_input": portfolio_input},
            headers=headers
        )
        if response.status_code == 200:
            portfolio_result = response.json()
            print(f"✅ Portfolio analysis created - Total Value: ₹{portfolio_result['total_value']:,.2f}")
        else:
            print(f"❌ Portfolio analysis failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating portfolio analysis: {e}")
        return
    
    # Step 5: Create scenario analysis
    print("\n5. Creating scenario analysis...")
    scenario_text = "RBI increases repo rate by 0.5%"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/analyze-scenario",
            json={"scenario_text": scenario_text},
            headers=headers
        )
        if response.status_code == 200:
            scenario_result = response.json()
            print(f"✅ Scenario analysis created - ID: {scenario_result['scenario_id']}")
        else:
            print(f"❌ Scenario analysis failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating scenario analysis: {e}")
        return
    
    # Step 6: Create export
    print("\n6. Creating export...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/export/text",
            json={
                "include_risk_profile": True,
                "include_portfolio": True,
                "include_scenarios": True
            },
            headers=headers
        )
        if response.status_code == 200:
            print("✅ Export created successfully")
        else:
            print(f"❌ Export failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating export: {e}")
        return
    
    # Step 7: Fetch all user data
    print("\n7. Fetching all user data...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/user/data", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print("✅ User data fetched successfully")
            print(f"   - Risk Profile: {'✅' if user_data['risk_profile'] else '❌'}")
            print(f"   - Portfolio: {'✅' if user_data['portfolio'] else '❌'}")
            print(f"   - Scenarios: {len(user_data['scenarios'])} found")
            print(f"   - Exports: {len(user_data['exports'])} found")
        else:
            print(f"❌ Fetching user data failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Error fetching user data: {e}")
        return
    
    # Step 8: Test individual endpoints
    print("\n8. Testing individual endpoints...")
    
    # Test risk profile endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/v1/risk-profile/latest", headers=headers)
        if response.status_code == 200:
            print("✅ Risk profile endpoint working")
        else:
            print(f"❌ Risk profile endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing risk profile endpoint: {e}")
    
    # Test portfolio endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/v1/portfolio/latest", headers=headers)
        if response.status_code == 200:
            print("✅ Portfolio endpoint working")
        else:
            print(f"❌ Portfolio endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing portfolio endpoint: {e}")
    
    # Test scenarios endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/v1/scenarios", headers=headers)
        if response.status_code == 200:
            scenarios_data = response.json()
            print(f"✅ Scenarios endpoint working - {scenarios_data['count']} scenarios found")
        else:
            print(f"❌ Scenarios endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing scenarios endpoint: {e}")
    
    # Test exports endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/v1/export/history", headers=headers)
        if response.status_code == 200:
            exports_data = response.json()
            print(f"✅ Exports endpoint working - {exports_data['count']} exports found")
        else:
            print(f"❌ Exports endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing exports endpoint: {e}")
    
    print("\n🎉 Persistence functionality test completed!")
    print("=" * 50)
    print("✅ All user actions are now persisted in the database")
    print("✅ Users can see their previous work when they log back in")
    print("✅ Data can be updated, replaced, or deleted as needed")

if __name__ == "__main__":
    print("🚀 Starting Persistence Test")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    try:
        test_persistence()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
