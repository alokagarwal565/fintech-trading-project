#!/usr/bin/env python3
"""
Script to run the Streamlit frontend
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    # Change to app directory and run streamlit
    os.chdir("app")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "main.py", "--server.port", "8501"])