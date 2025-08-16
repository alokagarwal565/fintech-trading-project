#!/usr/bin/env python3
"""
Setup script for AI-Powered Risk & Scenario Advisor
"""
import os
import sys
import subprocess
import shutil
import time
import httpx
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Environment file created from template")
        print("   Please edit .env with your actual API keys and configuration")
    else:
        print("❌ env.example file not found")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def check_redis():
    """Check if Redis is available"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running")
    except Exception:
        print("⚠️  Redis is not running. Rate limiting will be disabled.")
        print("   To enable rate limiting, install and start Redis")

def create_directories():
    """Create necessary directories"""
    directories = ["logs", "exports", "temp"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Created necessary directories")

def start_backend():
    """Start the backend server"""
    print("🚀 Starting backend server...")
    try:
        # Start backend in background
        process = subprocess.Popen([sys.executable, "run_backend.py"], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
        print("✅ Backend server started")
        return process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def wait_for_backend(api_base_url="http://localhost:8000", max_wait=30):
    """Wait for backend to be ready"""
    print("⏳ Waiting for backend to be ready...")
    for i in range(max_wait):
        try:
            response = httpx.get(f"{api_base_url}/health", timeout=2.0)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                return True
        except:
            pass
        time.sleep(1)
        if (i + 1) % 5 == 0:
            print(f"   Still waiting... ({i + 1}/{max_wait}s)")
    
    print("❌ Backend did not become ready in time")
    return False

def setup_admin_user(api_base_url="http://localhost:8000"):
    """Setup the initial admin user"""
    print("\n🔐 Admin User Setup")
    print("=" * 40)
    
    # Check if admin already exists
    try:
        response = httpx.post(
            f"{api_base_url}/auth/setup-admin",
            json={"email": "test@test.com", "password": "Test123!"},
            timeout=5.0
        )
        if response.status_code == 400 and "already exists" in response.text:
            print("✅ Admin user already exists")
            return True
    except:
        pass
    
    print("📝 Enter Admin User Details:")
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
    
    print("\n🔍 Creating admin user...")
    
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
    """Main setup function"""
    print("🚀 Setting up AI-Powered Risk & Scenario Advisor")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Install dependencies
    install_dependencies()
    
    # Create .env file
    create_env_file()
    
    # Check Redis
    check_redis()
    
    # Ask user if they want to start backend and setup admin
    print("\n🔐 Admin Dashboard Setup:")
    setup_admin = input("Do you want to start the backend and setup admin user now? (y/n): ").strip().lower()
    
    if setup_admin in ['y', 'yes']:
        # Start backend
        backend_process = start_backend()
        if backend_process:
            # Wait for backend to be ready
            if wait_for_backend():
                # Setup admin user
                if setup_admin_user():
                    print("\n🎯 Next Steps:")
                    print("1. Start frontend: python run_frontend.py")
                    print("2. Login with your admin credentials")
                    print("3. You'll be redirected to the Admin Dashboard")
                    print("4. Regular users will see the normal app interface")
                else:
                    print("\n❌ Admin setup failed. You can run this setup again later.")
            else:
                print("\n❌ Backend failed to start properly.")
                print("   You can manually start it with: python run_backend.py")
        else:
            print("\n❌ Failed to start backend automatically.")
            print("   You can manually start it with: python run_backend.py")
    else:
        print("\n⏭️  Skipping backend startup and admin setup.")
        print("   You can do this later manually.")
    
    print("\n🎯 Manual Setup Steps (if needed):")
    print("1. Edit .env file with your configuration")
    print("2. Start backend: python run_backend.py")
    print("3. Setup admin user: python setup.py (and choose 'y' for admin setup)")
    print("4. Start frontend: python run_frontend.py")
    print("5. Access the application at http://localhost:8501")
    
    print("\n📚 For more information, see README.md")
    
    return True

if __name__ == "__main__":
    main()
