#!/usr/bin/env python3
"""
Setup script for AI-Powered Risk & Scenario Advisor
"""
import os
import sys
import subprocess
import shutil
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
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your API keys")
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
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Start the backend: python run_backend.py")
    print("3. Start the frontend: python run_frontend.py")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()
