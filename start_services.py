#!/usr/bin/env python3
"""
Start Services Script for AI-Powered Risk & Scenario Advisor

This script opens two separate terminal windows:
1. Backend terminal - activates venv and runs backend
2. Frontend terminal - activates venv and runs frontend

Usage:
    python start_services.py
"""

import os
import sys
import subprocess
import time
import platform
from pathlib import Path

def get_venv_activate_command():
    """Get the appropriate venv activation command based on OS"""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def get_cd_command():
    """Get the appropriate cd command based on OS"""
    if platform.system() == "Windows":
        # Use Set-Location for PowerShell compatibility
        return f"Set-Location '{os.getcwd()}'"
    else:
        return f"cd '{os.getcwd()}'"

def open_backend_terminal():
    """Open a new terminal window and start the backend"""
    venv_activate = get_venv_activate_command()
    cd_command = get_cd_command()
    
    if platform.system() == "Windows":
        # Windows - use PowerShell with proper commands
        backend_commands = [
            cd_command,
            f"& '{venv_activate}'",
            "python run_backend.py"
        ]
        
        # Join commands with semicolons for PowerShell
        command_string = "; ".join(backend_commands)
        
        # Create a PowerShell script file for better reliability
        script_content = f"""# Backend Server Startup Script
Write-Host "🚀 Starting Backend Server..." -ForegroundColor Green
Write-Host "📍 Working Directory: {os.getcwd()}" -ForegroundColor Cyan
Write-Host "🔧 Activating Virtual Environment..." -ForegroundColor Yellow

{cd_command}
& '{venv_activate}'

Write-Host "✅ Virtual Environment Activated" -ForegroundColor Green
Write-Host "🚀 Starting FastAPI Backend..." -ForegroundColor Yellow
Write-Host "📡 Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs will be available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

python run_backend.py

Write-Host "=" * 60 -ForegroundColor Gray
Write-Host "🛑 Backend Server Stopped" -ForegroundColor Red
Read-Host "Press Enter to close this window..."
"""
        
        # Write script to temporary file
        script_path = Path("temp_backend_startup.ps1")
        script_path.parent.mkdir(exist_ok=True)
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Execute PowerShell script
        try:
            subprocess.Popen([
                "powershell", 
                "-ExecutionPolicy", "Bypass",
                "-File", str(script_path)
            ])
            print(f"✅ Backend terminal opened with script: {script_path}")
        except Exception as e:
            print(f"❌ Failed to open backend terminal: {e}")
            print("   Please run manually:")
            print(f"   cd {os.getcwd()}")
            print(f"   {venv_activate}")
            print("   python run_backend.py")
        
    else:
        # Linux/Mac - use gnome-terminal or xterm
        backend_commands = [
            cd_command,
            f"{venv_activate}",
            "python run_backend.py"
        ]
        
        command_string = " && ".join(backend_commands)
        
        try:
            # Try gnome-terminal first
            subprocess.Popen([
                "gnome-terminal", 
                "--title=Backend Server", 
                "--", "bash", "-c", command_string
            ])
        except FileNotFoundError:
            try:
                # Try xterm as fallback
                subprocess.Popen([
                    "xterm", 
                    "-title", "Backend Server", 
                    "-e", "bash", "-c", command_string
                ])
            except FileNotFoundError:
                print("❌ No suitable terminal emulator found. Please start backend manually:")
                print(f"   {cd_command}")
                print(f"   {venv_activate}")
                print("   python run_backend.py")

def open_frontend_terminal():
    """Open a new terminal window and start the frontend"""
    venv_activate = get_venv_activate_command()
    cd_command = get_cd_command()
    
    if platform.system() == "Windows":
        # Windows - use PowerShell with proper commands
        frontend_commands = [
            cd_command,
            f"& '{venv_activate}'",
            "python run_frontend.py"
        ]
        
        # Create a PowerShell script file for better reliability
        script_content = f"""# Frontend Server Startup Script
Write-Host "🎨 Starting Frontend Server..." -ForegroundColor Green
Write-Host "📍 Working Directory: {os.getcwd()}" -ForegroundColor Cyan
Write-Host "🔧 Activating Virtual Environment..." -ForegroundColor Yellow

{cd_command}
& '{venv_activate}'

Write-Host "✅ Virtual Environment Activated" -ForegroundColor Green
Write-Host "🎨 Starting Streamlit Frontend..." -ForegroundColor Yellow
Write-Host "🌐 Frontend will be available at: http://localhost:8501" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

python run_frontend.py

Write-Host "=" * 60 -ForegroundColor Gray
Write-Host "🛑 Frontend Server Stopped" -ForegroundColor Red
Read-Host "Press Enter to close this window..."
"""
        
        # Write script to temporary file
        script_path = Path("temp_frontend_startup.ps1")
        script_path.parent.mkdir(exist_ok=True)
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Execute PowerShell script
        try:
            subprocess.Popen([
                "powershell", 
                "-ExecutionPolicy", "Bypass",
                "-File", str(script_path)
            ])
            print(f"✅ Frontend terminal opened with script: {script_path}")
        except Exception as e:
            print(f"❌ Failed to open frontend terminal: {e}")
            print("   Please run manually:")
            print(f"   cd {os.getcwd()}")
            print(f"   {venv_activate}")
            print("   python run_frontend.py")
        
    else:
        # Linux/Mac - use gnome-terminal or xterm
        frontend_commands = [
            cd_command,
            f"{venv_activate}",
            "python run_frontend.py"
        ]
        
        command_string = " && ".join(frontend_commands)
        
        try:
            # Try gnome-terminal first
            subprocess.Popen([
                "gnome-terminal", 
                "--title=Frontend Server", 
                "--", "bash", "-c", command_string
            ])
        except FileNotFoundError:
            try:
                # Try xterm as fallback
                subprocess.Popen([
                    "xterm", 
                    "-title", "Frontend Server", 
                    "-e", "bash", "-c", command_string
                ])
            except FileNotFoundError:
                print("❌ No suitable terminal emulator found. Please start frontend manually:")
                print(f"   {cd_command}")
                print(f"   {venv_activate}")
                print("   python run_frontend.py")

def check_venv_exists():
    """Check if virtual environment exists"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("❌ Virtual environment 'venv' not found!")
        print("   Please run 'python setup.py' first to create the virtual environment.")
        return False
    return True

def check_redis_status():
    """Check Redis status and provide guidance"""
    print("🔍 Checking Redis status...")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=2)
        r.ping()
        print("✅ Redis is running and accessible")
        return True
    except ImportError:
        print("⚠️  Redis Python package not installed")
        print("   Rate limiting will be disabled (this is OK for development)")
        return False
    except Exception as e:
        print("⚠️  Redis is not running or not accessible")
        print("   Error:", str(e))
        print("   Rate limiting will be disabled (this is OK for development)")
        print()
        print("💡 To enable Redis (optional):")
        if platform.system() == "Windows":
            print("   1. Install Redis for Windows: https://github.com/microsoftarchive/redis/releases")
            print("   2. Or use Docker: docker run -d -p 6379:6379 redis:alpine")
        else:
            print("   1. Install Redis: sudo apt-get install redis-server (Ubuntu/Debian)")
            print("   2. Or use Docker: docker run -d -p 6379:6379 redis:alpine")
        print("   3. Start Redis service")
        print()
        return False

def cleanup_temp_files():
    """Clean up temporary PowerShell script files"""
    temp_files = ["temp_backend_startup.ps1", "temp_frontend_startup.ps1"]
    for temp_file in temp_files:
        try:
            if Path(temp_file).exists():
                Path(temp_file).unlink()
                print(f"🧹 Cleaned up temporary file: {temp_file}")
        except Exception:
            pass

def main():
    """Main function to start both services"""
    print("🚀 Starting AI-Powered Risk & Scenario Advisor Services")
    print("=" * 60)
    
    # Check if virtual environment exists
    if not check_venv_exists():
        return
    
    # Check Redis status (informational only)
    check_redis_status()
    print()
    
    print("📋 Starting services in separate terminals...")
    print("   This will open two new terminal windows:")
    print("   1. Backend Server (FastAPI) - Port 8000")
    print("   2. Frontend Server (Streamlit) - Port 8501")
    print()
    
    # Start backend terminal
    print("🔧 Opening backend terminal...")
    open_backend_terminal()
    
    # Wait a moment for backend terminal to open
    time.sleep(3)
    
    # Start frontend terminal
    print("🎨 Opening frontend terminal...")
    open_frontend_terminal()
    
    print()
    print("✅ Both terminals have been opened!")
    print()
    print("📱 Services will be available at:")
    print("   • Backend API: http://localhost:8000")
    print("   • Frontend App: http://localhost:8501")
    print("   • API Documentation: http://localhost:8000/docs")
    print()
    print("💡 Tips:")
    print("   • Backend terminal will show API logs and requests")
    print("   • Frontend terminal will show Streamlit app logs")
    print("   • Redis is optional - rate limiting will be disabled if not available")
    print("   • Close the terminals to stop the services")
    print("   • You can also use 'python run_backend.py' and 'python run_frontend.py' directly")
    print()
    print("🔄 Waiting for services to start...")
    print("   Check the terminal windows for startup progress")
    
    # Clean up temporary files after a delay
    time.sleep(5)
    cleanup_temp_files()
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Startup interrupted by user")
        cleanup_temp_files()
    except Exception as e:
        print(f"\n❌ Error during startup: {e}")
        cleanup_temp_files()
        sys.exit(1)
