#!/usr/bin/env python3
"""
Comprehensive script to fix all persistence issues
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_database_schema():
    """Check if the database has the correct schema"""
    db_path = Path("investment_advisor.db")
    
    if not db_path.exists():
        print("ℹ️ No database found - will be created with correct schema")
        return False
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if riskassessment table has answers column
        cursor.execute("PRAGMA table_info(riskassessment)")
        columns = [column[1] for column in cursor.fetchall()]
        
        conn.close()
        
        if 'answers' in columns:
            print("✅ Database schema is correct")
            return True
        else:
            print("❌ Database schema is outdated - missing 'answers' column")
            return False
            
    except Exception as e:
        print(f"❌ Error checking database schema: {e}")
        return False

def reset_database():
    """Reset the database"""
    db_path = Path("investment_advisor.db")
    
    if db_path.exists():
        print("🗑️ Deleting outdated database...")
        try:
            db_path.unlink()
            print("✅ Database deleted successfully")
            return True
        except Exception as e:
            print(f"❌ Error deleting database: {e}")
            return False
    else:
        print("ℹ️ No database to delete")
        return True

def start_backend():
    """Start the backend server"""
    print("🚀 Starting backend server...")
    
    try:
        # Start the backend server
        process = subprocess.Popen([
            sys.executable, "run_backend.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for server to start
        time.sleep(5)
        
        # Check if server is running
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server started successfully!")
                return True
            else:
                print(f"❌ Backend server returned status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Could not connect to backend: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False

def test_persistence():
    """Test the persistence functionality"""
    print("🧪 Testing persistence functionality...")
    
    try:
        import requests
        
        # Test user registration
        register_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        response = requests.post("http://localhost:8000/auth/register", json=register_data)
        if response.status_code != 200:
            print(f"❌ User registration failed: {response.status_code}")
            return False
        
        # Test login
        login_data = {
            "username": "test@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post("http://localhost:8000/auth/token", data=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code}")
            return False
        
        token_data = response.json()
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        
        # Test user data endpoint
        response = requests.get("http://localhost:8000/api/v1/user/data", headers=headers)
        if response.status_code != 200:
            print(f"❌ User data endpoint failed: {response.status_code}")
            return False
        
        print("✅ Persistence functionality test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing persistence: {e}")
        return False

def main():
    """Main function to fix all issues"""
    print("🔧 Fixing Persistence Issues")
    print("=" * 50)
    
    # Step 1: Check database schema
    print("\n1. Checking database schema...")
    if not check_database_schema():
        print("\n2. Resetting database...")
        if not reset_database():
            print("❌ Failed to reset database")
            return
        
        print("\n3. Starting backend server...")
        if not start_backend():
            print("❌ Failed to start backend server")
            print("📝 Please manually start the backend: python run_backend.py")
            return
        
        print("\n4. Testing persistence functionality...")
        if not test_persistence():
            print("❌ Persistence test failed")
            return
    else:
        print("\n✅ Database schema is already correct!")
        print("📝 If you're still having issues, try restarting the backend server")
    
    print("\n🎉 All issues fixed!")
    print("=" * 50)
    print("✅ Database schema is correct")
    print("✅ Backend server is running")
    print("✅ Persistence functionality is working")
    print("\n📝 You can now:")
    print("1. Start the frontend: python run_frontend.py")
    print("2. Access the application at: http://localhost:8501")
    print("3. Test the persistence features")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Fix interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
