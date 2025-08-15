#!/usr/bin/env python3
"""
Test script to verify all components of the AI-Powered Risk & Scenario Advisor
"""
import os
import sys
import requests
import time
import json
from pathlib import Path

def test_environment():
    """Test environment configuration"""
    print("🔧 Testing environment configuration...")
    
    # Check required environment variables
    required_vars = ['GEMINI_API_KEY', 'SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    print("✅ Environment variables configured")
    return True

def test_dependencies():
    """Test Python dependencies"""
    print("📦 Testing Python dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'sqlmodel', 'streamlit', 'yfinance',
        'plotly', 'google.generativeai', 'reportlab', 'redis'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {missing_packages}")
        return False
    
    print("✅ All dependencies installed")
    return True

def test_database():
    """Test database connection and models"""
    print("🗄️ Testing database...")
    
    try:
        from backend.models.database import create_db_and_tables, get_session
        from backend.models.models import User, Portfolio, RiskAssessment, Scenario
        
        # Create tables
        create_db_and_tables()
        
        # Test session
        session = next(get_session())
        session.exec("SELECT 1").first()
        session.close()
        
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_backend_api():
    """Test backend API endpoints"""
    print("🔌 Testing backend API...")
    
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
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

def test_services():
    """Test service components"""
    print("⚙️ Testing services...")
    
    try:
        # Test risk profile service
        from backend.services.risk_profile_service import RiskProfileService
        service = RiskProfileService()
        result = service.assess_risk_tolerance([
            "3-5 years", "Hold and wait", "Moderate growth",
            "3-7 years", "Stable", "3-6 months"
        ])
        
        if result and 'score' in result and 'category' in result:
            print("✅ Risk profile service working")
        else:
            print("❌ Risk profile service failed")
            return False
        
        # Test portfolio service
        from backend.services.portfolio_service import PortfolioService
        portfolio_service = PortfolioService()
        
        # Test symbol mapping
        symbol = portfolio_service.get_stock_symbol("TCS")
        if symbol == "TCS.NS":
            print("✅ Portfolio service symbol mapping working")
        else:
            print("❌ Portfolio service symbol mapping failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        return False

def test_gemini_api():
    """Test Gemini API connection"""
    print("🤖 Testing Gemini API...")
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not set")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Simple test prompt
        response = model.generate_content("Hello, this is a test.")
        
        if response.text:
            print("✅ Gemini API connection successful")
            return True
        else:
            print("❌ Gemini API returned empty response")
            return False
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def test_redis():
    """Test Redis connection (optional)"""
    print("🔴 Testing Redis connection...")
    
    try:
        import redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        r = redis.from_url(redis_url, decode_responses=True)
        r.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"⚠️ Redis not available: {e}")
        print("   Rate limiting will be disabled")
        return True  # Not critical for basic functionality

def test_file_structure():
    """Test file structure and permissions"""
    print("📁 Testing file structure...")
    
    required_files = [
        "backend/main.py",
        "backend/models/models.py",
        "backend/services/portfolio_service.py",
        "app/main.py",
        "requirements.txt",
        "run_backend.py",
        "run_frontend.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ File structure correct")
    return True

def main():
    """Run all tests"""
    print("🧪 Running comprehensive system tests...")
    print("=" * 50)
    
    tests = [
        ("Environment Configuration", test_environment),
        ("Python Dependencies", test_dependencies),
        ("File Structure", test_file_structure),
        ("Database", test_database),
        ("Services", test_services),
        ("Gemini API", test_gemini_api),
        ("Redis", test_redis),
        ("Backend API", test_backend_api),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your system is ready to run.")
        print("\nNext steps:")
        print("1. Start backend: python run_backend.py")
        print("2. Start frontend: python run_frontend.py")
        print("3. Open http://localhost:8501 in your browser")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
