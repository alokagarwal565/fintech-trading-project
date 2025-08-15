#!/usr/bin/env python3
"""
Test script to verify portfolio visualizations are working
"""

import requests
import json

def test_visualizations():
    """Test portfolio visualizations"""
    
    print("🧪 Testing Portfolio Visualizations")
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
        
        # Test 1: Get user data (should include visualizations)
        print("\n1. Testing user data endpoint for visualizations...")
        response = requests.get("http://localhost:8000/api/v1/user/data", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get('portfolio'):
                portfolio = user_data['portfolio']
                print(f"✅ Portfolio found with ID: {portfolio.get('portfolio_id')}")
                print(f"   - Has 'visualizations' key: {'✅' if 'visualizations' in portfolio else '❌'}")
                if 'visualizations' in portfolio:
                    viz = portfolio['visualizations']
                    print(f"   - Has 'pie_chart': {'✅' if 'pie_chart' in viz else '❌'}")
                    print(f"   - Has 'sector_bar_chart': {'✅' if 'sector_bar_chart' in viz else '❌'}")
                    print(f"   - Has 'holdings_bar_chart': {'✅' if 'holdings_bar_chart' in viz else '❌'}")
                else:
                    print("❌ No visualizations found in portfolio data")
            else:
                print("ℹ️ No portfolio found in user data")
        else:
            print(f"❌ User data endpoint failed: {response.status_code}")
        
        # Test 2: Get latest portfolio directly
        print("\n2. Testing latest portfolio endpoint for visualizations...")
        response = requests.get("http://localhost:8000/api/v1/portfolio/latest", headers=headers)
        if response.status_code == 200:
            portfolio_data = response.json()
            if 'message' not in portfolio_data:
                print(f"✅ Latest portfolio found with ID: {portfolio_data.get('portfolio_id')}")
                print(f"   - Has 'visualizations' key: {'✅' if 'visualizations' in portfolio_data else '❌'}")
                if 'visualizations' in portfolio_data:
                    viz = portfolio_data['visualizations']
                    print(f"   - Has 'pie_chart': {'✅' if 'pie_chart' in viz else '❌'}")
                    print(f"   - Has 'sector_bar_chart': {'✅' if 'sector_bar_chart' in viz else '❌'}")
                    print(f"   - Has 'holdings_bar_chart': {'✅' if 'holdings_bar_chart' in viz else '❌'}")
                else:
                    print("❌ No visualizations found in latest portfolio data")
            else:
                print(f"ℹ️ {portfolio_data['message']}")
        else:
            print(f"❌ Latest portfolio endpoint failed: {response.status_code}")
        
        print("\n🎉 Visualization test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_visualizations()
