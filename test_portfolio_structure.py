#!/usr/bin/env python3
"""
Test script to verify portfolio data structure consistency
"""

import requests
import json

def test_portfolio_structure():
    """Test portfolio data structure consistency"""
    
    print("🧪 Testing Portfolio Data Structure")
    print("=" * 40)
    
    try:
        # Login
        login_data = {
            "username": "alokagarwal629@gmail.com",
            "password": "TestPass123!"
        }
        
        response = requests.post("http://localhost:8000/auth/token", data=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return False
        
        token_data = response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        
        print("✅ Login successful")
        
        # Test 1: Get user data (existing portfolio)
        print("\n1. Testing user data endpoint...")
        response = requests.get("http://localhost:8000/api/v1/user/data", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get('portfolio'):
                portfolio = user_data['portfolio']
                print(f"✅ Portfolio found with ID: {portfolio.get('portfolio_id')}")
                print(f"   - Has 'holdings' key: {'✅' if 'holdings' in portfolio else '❌'}")
                print(f"   - Has 'valid_holdings' key: {'✅' if 'valid_holdings' in portfolio else '❌'}")
                print(f"   - Holdings count: {len(portfolio.get('holdings', []))}")
            else:
                print("ℹ️ No portfolio found in user data")
        else:
            print(f"❌ User data endpoint failed: {response.status_code}")
        
        # Test 2: Get latest portfolio directly
        print("\n2. Testing latest portfolio endpoint...")
        response = requests.get("http://localhost:8000/api/v1/portfolio/latest", headers=headers)
        if response.status_code == 200:
            portfolio_data = response.json()
            if 'message' not in portfolio_data:
                print(f"✅ Latest portfolio found with ID: {portfolio_data.get('portfolio_id')}")
                print(f"   - Has 'holdings' key: {'✅' if 'holdings' in portfolio_data else '❌'}")
                print(f"   - Has 'valid_holdings' key: {'✅' if 'valid_holdings' in portfolio_data else '❌'}")
                print(f"   - Holdings count: {len(portfolio_data.get('holdings', []))}")
            else:
                print(f"ℹ️ {portfolio_data['message']}")
        else:
            print(f"❌ Latest portfolio endpoint failed: {response.status_code}")
        
        # Test 3: Create new portfolio analysis
        print("\n3. Testing new portfolio analysis...")
        portfolio_input = "TCS: 5, HDFC Bank: 3 shares"
        
        response = requests.post(
            "http://localhost:8000/api/v1/analyze-portfolio",
            json={"portfolio_input": portfolio_input},
            headers=headers
        )
        if response.status_code == 200:
            new_portfolio = response.json()
            print(f"✅ New portfolio analysis created")
            print(f"   - Has 'holdings' key: {'✅' if 'holdings' in new_portfolio else '❌'}")
            print(f"   - Has 'valid_holdings' key: {'✅' if 'valid_holdings' in new_portfolio else '❌'}")
            print(f"   - Holdings count: {len(new_portfolio.get('holdings', []))}")
            print(f"   - Total value: ₹{new_portfolio.get('total_value', 0):,.2f}")
        else:
            print(f"❌ Portfolio analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
        
        print("\n🎉 Portfolio structure test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_portfolio_structure()
