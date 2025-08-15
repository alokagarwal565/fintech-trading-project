#!/usr/bin/env python3
"""
Script to restart the backend with the new database schema
"""

import subprocess
import sys
import time
import os

def restart_backend():
    """Restart the backend server"""
    
    print("🔄 Restarting Backend Server")
    print("=" * 40)
    
    # Check if backend is running
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("⚠️ Backend is currently running. Please stop it first (Ctrl+C in the backend terminal)")
            print("Then run this script again.")
            return False
    except:
        pass
    
    print("✅ Backend is not running. Starting it now...")
    
    try:
        # Start the backend server
        process = subprocess.Popen([
            sys.executable, "run_backend.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        # Check if the server started successfully
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server started successfully!")
                print("🌐 Backend URL: http://localhost:8000")
                print("📚 API Docs: http://localhost:8000/docs")
                print("💡 Keep this terminal open to run the backend")
                print("📝 Open a new terminal to run the frontend: python run_frontend.py")
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

if __name__ == "__main__":
    print("🚀 Backend Restart Script")
    print("=" * 40)
    
    try:
        success = restart_backend()
        if success:
            print("\n🎉 Backend is ready!")
            print("📝 You can now start the frontend in a new terminal:")
            print("   python run_frontend.py")
        else:
            print("\n❌ Failed to start backend")
            print("📝 Please manually start the backend:")
            print("   python run_backend.py")
    except KeyboardInterrupt:
        print("\n⏹️ Backend restart interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
