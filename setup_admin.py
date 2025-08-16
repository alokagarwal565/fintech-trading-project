#!/usr/bin/env python3
"""
Admin User Setup Script for AI-Powered Risk & Scenario Advisor

This script creates the initial admin user for the system.
Run this script once after starting the backend server for the first time.

Usage:
    python setup_admin.py
"""

import os
import sys
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_admin_user():
    """Setup the initial admin user"""
    
    # Get configuration from environment
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    print("🔐 Admin User Setup for AI-Powered Risk & Scenario Advisor")
    print("=" * 60)
    
    # Check if backend is running
    try:
        response = httpx.get(f"{api_base_url}/health", timeout=5.0)
        if response.status_code != 200:
            print("❌ Backend API is not responding. Please start the FastAPI server first.")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend API at {api_base_url}")
        print(f"   Error: {e}")
        print("   Please ensure the backend server is running on port 8000")
        return False
    
    print("✅ Backend API is running")
    
    # Get admin credentials
    print("\n📝 Enter Admin User Details:")
    print("-" * 30)
    
    admin_email = input("Admin Email (e.g., admin@finadvisor.com): ").strip()
    if not admin_email:
        print("❌ Email is required")
        return False
    
    admin_password = input("Admin Password: ").strip()
    if not admin_password:
        print("❌ Password is required")
        return False
    
    admin_full_name = input("Admin Full Name (optional): ").strip()
    if not admin_full_name:
        admin_full_name = None
    
    # Validate password strength
    if len(admin_password) < 8:
        print("❌ Password must be at least 8 characters long")
        return False
    
    has_upper = any(c.isupper() for c in admin_password)
    has_lower = any(c.islower() for c in admin_password)
    has_digit = any(c.isdigit() for c in admin_password)
    has_special = any(c in '!@#$%^&*(),.?":{}|<>' for c in admin_password)
    
    if not all([has_upper, has_lower, has_digit, has_special]):
        print("❌ Password must contain uppercase, lowercase, digit, and special character")
        return False
    
    print("\n🔍 Validating credentials...")
    
    # Create admin user
    try:
        data = {
            "email": admin_email,
            "password": admin_password,
            "full_name": admin_full_name
        }
        
        response = httpx.post(
            f"{api_base_url}/auth/setup-admin",
            json=data,
            timeout=30.0
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Admin user created successfully!")
            print(f"   Admin ID: {result.get('admin_id')}")
            print(f"   Email: {admin_email}")
            print("\n🎉 You can now login with these credentials to access the Admin Dashboard")
            return True
        else:
            error_data = response.json()
            if 'detail' in error_data:
                print(f"❌ Error: {error_data['detail']}")
            else:
                print(f"❌ Error: HTTP {response.status_code}")
            return False
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            try:
                error_data = e.response.json()
                if 'detail' in error_data:
                    print(f"❌ Error: {error_data['detail']}")
                else:
                    print(f"❌ Error: {e}")
            except:
                print(f"❌ Error: {e}")
        else:
            print(f"❌ HTTP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Starting Admin Setup...")
    
    success = setup_admin_user()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Start the frontend: python run_frontend.py")
        print("2. Login with your admin credentials")
        print("3. You'll be redirected to the Admin Dashboard")
        print("4. Regular users will see the normal app interface")
    else:
        print("\n❌ Admin setup failed. Please check the errors above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
