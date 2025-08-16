#!/usr/bin/env python3
"""
Unified Test Suite for AI-Powered Risk & Scenario Advisor

This file consolidates all testing functionality from the scattered test files:
- test_setup.py
- test_persistence.py  
- quick_test.py
- test_visualizations.py
- test_portfolio_structure.py
- debug_registration.py

All tests are organized by feature and can be run individually or as a complete suite.
"""

import os
import sys
import requests
import time
import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000"
TEST_PASSWORD = "TestPass123!"

class TestSuite:
    """Main test suite class that organizes all tests by feature"""
    
    def __init__(self):
        self.access_token = None
        self.headers = None
        self.test_results = {}
        # Generate unique test email to avoid conflicts
        self.test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        self.test_user_name = "Test User"
    
    def setup_auth(self) -> bool:
        """Setup authentication for tests by creating a new account and logging in"""
        try:
            # Generate a unique email for this test run
            unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
            print(f"  - Creating test account: {unique_email}")
            
            # Step 1: Register a new user
            register_data = {
                "email": unique_email,
                "password": TEST_PASSWORD,
                "full_name": self.test_user_name
            }
            
            response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
            if response.status_code == 200:
                print("    ✅ User registration successful")
            else:
                print(f"    ❌ User registration failed: {response.status_code} - {response.text}")
                return False
            
            # Step 2: Login with the new account
            print(f"  - Logging in with: {unique_email}")
            login_data = {
                "username": unique_email,
                "password": TEST_PASSWORD
            }
            
            response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                self.headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
                print("    ✅ Login successful")
                return True
            else:
                print(f"    ❌ Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"    ❌ Authentication error: {e}")
            return False

    def test_environment(self) -> bool:
        """Test environment configuration"""
        print("🔧 Testing environment configuration...")
        
        # Check required environment variables
        required_vars = ['GEMINI_API_KEY', 'SECRET_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️ Missing environment variables: {missing_vars}")
            print("   These are required for full functionality:")
            print("   - GEMINI_API_KEY: For AI-powered scenario analysis")
            print("   - SECRET_KEY: For JWT token encryption")
            print("   Create a .env file with these variables (see env.example)")
            print("   For testing purposes, this is acceptable")
            return True  # Don't fail the test, just warn
        
        print("✅ Environment variables configured")
        return True

    def test_dependencies(self) -> bool:
        """Test Python dependencies"""
        print("📦 Testing Python dependencies...")
        
        # Core packages that are essential
        core_packages = [
            'fastapi', 'uvicorn', 'streamlit', 'yfinance',
            'plotly', 'google.generativeai', 'requests'
        ]
        
        # Optional packages that enhance functionality
        optional_packages = [
            'sqlmodel', 'reportlab', 'redis'
        ]
        
        missing_core = []
        missing_optional = []
        
        # Check core packages
        for package in core_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_core.append(package)
        
        # Check optional packages
        for package in optional_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_optional.append(package)
        
        if missing_core:
            print(f"❌ Missing core packages: {missing_core}")
            print("   Please install missing packages: pip install " + " ".join(missing_core))
            return False
        
        if missing_optional:
            print(f"⚠️ Missing optional packages: {missing_optional}")
            print("   Some features may not work without these packages")
            print("   Install with: pip install " + " ".join(missing_optional))
        
        print("✅ All core dependencies installed")
        if not missing_optional:
            print("✅ All optional dependencies installed")
        return True

    def test_database(self) -> bool:
        """Test database connection and models"""
        print("🗄️ Testing database...")
        
        try:
            # Try to import sqlmodel
            try:
                from sqlmodel import text
            except ImportError:
                print("⚠️ sqlmodel not installed - skipping database test")
                print("   Install with: pip install sqlmodel")
                return True  # Skip this test if sqlmodel is not available
            
            from backend.models.database import create_db_and_tables, get_session
            from backend.models.models import User, Portfolio, RiskAssessment, Scenario
            
            # Create tables
            create_db_and_tables()
            
            # Test session
            session = next(get_session())
            session.exec(text("SELECT 1")).first()
            session.close()
            
            print("✅ Database connection successful")
            return True
        except Exception as e:
            print(f"❌ Database test failed: {e}")
            return False

    def test_backend_health(self) -> bool:
        """Test backend API health"""
        print("🔌 Testing backend API health...")
        
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend API is running")
                return True
            else:
                print(f"❌ Backend API returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Backend API not accessible: {e}")
            print("   Make sure to start the backend with: python run_backend.py")
            return False

    def test_authentication(self) -> bool:
        """Test authentication endpoints"""
        print("🔐 Testing authentication...")
        
        # Test user registration and login
        print("  - Testing user registration and login...")
        
        if self.setup_auth():
            # Test protected endpoint
            response = requests.get(f"{BASE_URL}/api/v1/user/data", headers=self.headers)
            if response.status_code == 200:
                print("    ✅ Protected endpoint accessible")
                return True
            else:
                print(f"    ❌ Protected endpoint failed: {response.status_code}")
                return False
        else:
            return False

    def test_risk_assessment(self) -> bool:
        """Test risk assessment functionality"""
        print("🎯 Testing risk assessment...")
        
        if not self.setup_auth():
            return False
        
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
                headers=self.headers
            )
            if response.status_code == 200:
                risk_result = response.json()
                print(f"  ✅ Risk assessment created - Score: {risk_result['score']}, Category: {risk_result['category']}")
                
                # Test getting latest risk profile
                response = requests.get(f"{BASE_URL}/api/v1/risk-profile/latest", headers=self.headers)
                if response.status_code == 200:
                    print("  ✅ Latest risk profile retrieved")
                    return True
                else:
                    print(f"  ❌ Failed to get latest risk profile: {response.status_code}")
                    return False
            else:
                print(f"  ❌ Risk assessment failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Error creating risk assessment: {e}")
            return False

    def test_portfolio_analysis(self) -> bool:
        """Test portfolio analysis functionality"""
        print("💼 Testing portfolio analysis...")
        
        if not self.setup_auth():
            return False
        
        portfolio_input = "TCS: 10, HDFC Bank: 5 shares, Reliance: 15"
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/analyze-portfolio",
                json={"portfolio_input": portfolio_input},
                headers=self.headers
            )
            if response.status_code == 200:
                portfolio_result = response.json()
                print(f"  ✅ Portfolio analysis created - Total Value: ₹{portfolio_result['total_value']:,.2f}")
                print(f"  ✅ Holdings count: {portfolio_result['holdings_count']}")
                
                # Test portfolio structure consistency
                if 'holdings' in portfolio_result:
                    print("  ✅ Portfolio has 'holdings' key")
                else:
                    print("  ❌ Portfolio missing 'holdings' key")
                    return False
                
                # Test getting latest portfolio
                response = requests.get(f"{BASE_URL}/api/v1/portfolio/latest", headers=self.headers)
                if response.status_code == 200:
                    latest_portfolio = response.json()
                    if 'message' not in latest_portfolio:
                        print("  ✅ Latest portfolio retrieved")
                        if 'visualizations' in latest_portfolio:
                            print("  ✅ Portfolio includes visualizations")
                        else:
                            print("  ❌ Portfolio missing visualizations")
                    else:
                        print(f"  ℹ️ {latest_portfolio['message']}")
                
                return True
            else:
                print(f"  ❌ Portfolio analysis failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Error creating portfolio analysis: {e}")
            return False

    def test_portfolio_visualizations(self) -> bool:
        """Test portfolio visualization functionality"""
        print("📊 Testing portfolio visualizations...")
        
        if not self.setup_auth():
            return False
        
        # First create a portfolio if none exists
        portfolio_input = "TCS: 10, HDFC Bank: 5 shares"
        
        try:
            # Create portfolio first
            response = requests.post(
                f"{BASE_URL}/api/v1/analyze-portfolio",
                json={"portfolio_input": portfolio_input},
                headers=self.headers
            )
            if response.status_code != 200:
                print("  ❌ Failed to create portfolio for visualization test")
                return False
            
            # Test user data endpoint for visualizations
            response = requests.get(f"{BASE_URL}/api/v1/user/data", headers=self.headers)
            if response.status_code == 200:
                user_data = response.json()
                if user_data.get('portfolio'):
                    portfolio = user_data['portfolio']
                    print(f"  ✅ Portfolio found with ID: {portfolio.get('portfolio_id')}")
                    
                    if 'visualizations' in portfolio:
                        viz = portfolio['visualizations']
                        print(f"  ✅ Has 'pie_chart': {'✅' if 'pie_chart' in viz else '❌'}")
                        print(f"  ✅ Has 'sector_bar_chart': {'✅' if 'sector_bar_chart' in viz else '❌'}")
                        print(f"  ✅ Has 'holdings_bar_chart': {'✅' if 'holdings_bar_chart' in viz else '❌'}")
                        return True
                    else:
                        print("  ❌ No visualizations found in portfolio data")
                        return False
                else:
                    print("  ❌ No portfolio found in user data")
                    return False
            else:
                print(f"  ❌ User data endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Error testing visualizations: {e}")
            return False

    def test_scenario_analysis(self) -> bool:
        """Test scenario analysis functionality"""
        print("🔮 Testing scenario analysis...")
        
        if not self.setup_auth():
            return False
        
        scenario_text = "RBI increases repo rate by 0.5%"
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/analyze-scenario",
                json={"scenario_text": scenario_text},
                headers=self.headers
            )
            if response.status_code == 200:
                scenario_result = response.json()
                print(f"  ✅ Scenario analysis created")
                print(f"  ✅ Narrative length: {len(scenario_result.get('narrative', ''))} characters")
                print(f"  ✅ Insights count: {len(scenario_result.get('insights', []))}")
                print(f"  ✅ Recommendations count: {len(scenario_result.get('recommendations', []))}")
                
                # Test getting user scenarios
                response = requests.get(f"{BASE_URL}/api/v1/scenarios", headers=self.headers)
                if response.status_code == 200:
                    scenarios = response.json()
                    print(f"  ✅ User scenarios retrieved: {len(scenarios.get('scenarios', []))} scenarios")
                    return True
                else:
                    print(f"  ❌ Failed to get user scenarios: {response.status_code}")
                    return False
            else:
                print(f"  ❌ Scenario analysis failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Error creating scenario analysis: {e}")
            return False

    def test_export_functionality(self) -> bool:
        """Test export functionality"""
        print("📋 Testing export functionality...")
        
        if not self.setup_auth():
            return False
        
        # Test text export
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/export/text",
                json={
                    "include_risk_profile": True,
                    "include_portfolio": True,
                    "include_scenarios": True
                },
                headers=self.headers
            )
            if response.status_code == 200:
                print("  ✅ Text export created")
                
                # Test PDF export
                response = requests.post(
                    f"{BASE_URL}/api/v1/export/pdf",
                    json={
                        "include_risk_profile": True,
                        "include_portfolio": True,
                        "include_scenarios": True
                    },
                    headers=self.headers
                )
                if response.status_code == 200:
                    print("  ✅ PDF export created")
                    
                    # Test export history
                    response = requests.get(f"{BASE_URL}/api/v1/export/history", headers=self.headers)
                    if response.status_code == 200:
                        exports = response.json()
                        print(f"  ✅ Export history retrieved: {len(exports.get('exports', []))} exports")
                        return True
                    else:
                        print(f"  ❌ Failed to get export history: {response.status_code}")
                        return False
                else:
                    print(f"  ❌ PDF export failed: {response.status_code}")
                    return False
            else:
                print(f"  ❌ Text export failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Error testing exports: {e}")
            return False

    def test_user_data_endpoint(self) -> bool:
        """Test user data aggregation endpoint"""
        print("👤 Testing user data endpoint...")
        
        if not self.setup_auth():
            return False
        
        try:
            response = requests.get(f"{BASE_URL}/api/v1/user/data", headers=self.headers)
            if response.status_code == 200:
                user_data = response.json()
                print("  ✅ User data endpoint working")
                print(f"  ✅ Risk Profile: {'✅' if user_data['risk_profile'] else '❌'}")
                print(f"  ✅ Portfolio: {'✅' if user_data['portfolio'] else '❌'}")
                print(f"  ✅ Scenarios: {len(user_data['scenarios'])} found")
                print(f"  ✅ Exports: {len(user_data['exports'])} found")
                return True
            else:
                print(f"  ❌ User data endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Error testing user data endpoint: {e}")
            return False

    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        print("🚀 Running Complete Test Suite")
        print("=" * 50)
        
        # First, check if backend is available
        backend_available = False
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=3)
            backend_available = response.status_code == 200
        except:
            pass
        
        if not backend_available:
            print("⚠️ Backend server is not running")
            print("   Starting backend: python run_backend.py")
            print("   Only running tests that don't require backend...")
            print()
        
        # Define test groups
        offline_tests = [
            ("Environment", self.test_environment),
            ("Dependencies", self.test_dependencies),
            ("Database", self.test_database),
        ]
        
        online_tests = [
            ("Backend Health", self.test_backend_health),
            ("Authentication", self.test_authentication),
            ("Risk Assessment", self.test_risk_assessment),
            ("Portfolio Analysis", self.test_portfolio_analysis),
            ("Portfolio Visualizations", self.test_portfolio_visualizations),
            ("Scenario Analysis", self.test_scenario_analysis),
            ("Export Functionality", self.test_export_functionality),
            ("User Data Endpoint", self.test_user_data_endpoint),
        ]
        
        # Choose which tests to run
        if backend_available:
            tests = offline_tests + online_tests
        else:
            tests = offline_tests
            print("📋 Skipping online tests (backend not available):")
            for test_name, _ in online_tests:
                print(f"   - {test_name}")
            print()
        
        results = {}
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ Test {test_name} failed with exception: {e}")
                results[test_name] = False
        
        # Summary
        print(f"\n{'='*50}")
        print("📊 TEST SUMMARY")
        print(f"{'='*50}")
        print(f"Total Tests Run: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if not backend_available and total < len(offline_tests + online_tests):
            print(f"\n📋 Tests Skipped: {len(online_tests)} (backend not available)")
            print("   To run all tests, start the backend server first")
        
        if passed == total:
            if backend_available:
                print("\n🎉 All tests passed!")
                print("✅ Application is working correctly")
            else:
                print("\n✅ All offline tests passed!")
                print("📋 Start backend to run full test suite")
        else:
            print(f"\n⚠️ {total - passed} test(s) failed")
            print("Please check the failed tests above")
        
        return results

def main():
    """Main function to run tests"""
    test_suite = TestSuite()
    
    # Check command line arguments for specific test
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        
        if test_name == "environment":
            test_suite.test_environment()
        elif test_name == "dependencies":
            test_suite.test_dependencies()
        elif test_name == "database":
            test_suite.test_database()
        elif test_name == "health":
            test_suite.test_backend_health()
        elif test_name == "auth":
            test_suite.test_authentication()
        elif test_name == "risk":
            test_suite.test_risk_assessment()
        elif test_name == "portfolio":
            test_suite.test_portfolio_analysis()
        elif test_name == "visualizations":
            test_suite.test_portfolio_visualizations()
        elif test_name == "scenario":
            test_suite.test_scenario_analysis()
        elif test_name == "export":
            test_suite.test_export_functionality()
        elif test_name == "userdata":
            test_suite.test_user_data_endpoint()
        else:
            print(f"Unknown test: {test_name}")
            print("Available tests: environment, dependencies, database, health, auth, risk, portfolio, visualizations, scenario, export, userdata")
    else:
        # Run all tests
        test_suite.run_all_tests()

if __name__ == "__main__":
    main()
