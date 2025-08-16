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

def open_backend_terminal():
    """Open a new terminal window and start the backend"""
    venv_activate = get_venv_activate_command()
    
    if platform.system() == "Windows":
        # Windows - use PowerShell
        backend_commands = [
            f"cd /d {os.getcwd()}",
            f"{venv_activate}",
            "python run_backend.py"
        ]
        
        # Join commands with semicolons for PowerShell
        command_string = "; ".join(backend_commands)
        
        # Open new PowerShell window
        subprocess.Popen([
            "powershell", 
            "-Command", 
            f"Start-Process powershell -ArgumentList '-Command', '{command_string}; Read-Host \"Press Enter to close...\"' -WindowStyle Normal"
        ])
        
    else:
        # Linux/Mac - use gnome-terminal or xterm
        backend_commands = [
            f"cd {os.getcwd()}",
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
                print(f"   cd {os.getcwd()}")
                print(f"   {venv_activate}")
                print("   python run_backend.py")

def open_frontend_terminal():
    """Open a new terminal window and start the frontend"""
    venv_activate = get_venv_activate_command()
    
    if platform.system() == "Windows":
        # Windows - use PowerShell
        frontend_commands = [
            f"cd /d {os.getcwd()}",
            f"{venv_activate}",
            "python run_frontend.py"
        ]
        
        # Join commands with semicolons for PowerShell
        command_string = "; ".join(frontend_commands)
        
        # Open new PowerShell window
        subprocess.Popen([
            "powershell", 
            "-Command", 
            f"Start-Process powershell -ArgumentList '-Command', '{command_string}; Read-Host \"Press Enter to close...\"' -WindowStyle Normal"
        ])
        
    else:
        # Linux/Mac - use gnome-terminal or xterm
        frontend_commands = [
            f"cd {os.getcwd()}",
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
                print(f"   cd {os.getcwd()}")
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

def main():
    """Main function to start both services"""
    print("🚀 Starting AI-Powered Risk & Scenario Advisor Services")
    print("=" * 60)
    
    # Check if virtual environment exists
    if not check_venv_exists():
        return
    
    print("📋 Starting services in separate terminals...")
    print("   This will open two new terminal windows:")
    print("   1. Backend Server (FastAPI)")
    print("   2. Frontend Server (Streamlit)")
    print()
    
    # Start backend terminal
    print("🔧 Opening backend terminal...")
    open_backend_terminal()
    
    # Wait a moment for backend terminal to open
    time.sleep(2)
    
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
    print("   • Close the terminals to stop the services")
    print("   • You can also use 'python run_backend.py' and 'python run_frontend.py' directly")
    
    return True

if __name__ == "__main__":
    main()
