"""
Quick start script for Nassau Candy Analytics Dashboard
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🍬 Starting Nassau Candy Analytics Dashboard...\n")
    
    # Check if in virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not activated")
        print("   Recommended: Activate .venv first\n")
    
    # Check if requirements are installed
    try:
        import streamlit
        import pandas
        import plotly
    except ImportError:
        print("❌ Missing dependencies. Installing...\n")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Launch dashboard
    dashboard_path = Path("dashboard/app.py")
    if not dashboard_path.exists():
        print("❌ Dashboard file not found!")
        return
    
    print("✅ Launching dashboard at http://localhost:8501\n")
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(dashboard_path)])

if __name__ == "__main__":
    main()
