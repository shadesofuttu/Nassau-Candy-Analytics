"""
Setup script for Nassau Candy Analytics Platform
"""
import subprocess
import sys
from pathlib import Path

def setup_environment():
    """
    Setup the project environment
    """
    print("🍬 Nassau Candy Analytics - Setup")
    print("=" * 50)
    
    # Check Python version
    print(f"\n✓ Python version: {sys.version}")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        return False
    
    # Generate sample data
    print("\n📊 Generating sample data...")
    try:
        subprocess.check_call([sys.executable, "data/sample_data_generator.py"])
        print("✓ Sample data generated")
    except subprocess.CalledProcessError as e:
        print(f"⚠ Could not generate sample data: {e}")
        print("  You can upload your own data through the dashboard")
    
    # Run tests
    print("\n🧪 Running tests...")
    try:
        subprocess.check_call([sys.executable, "-m", "pytest", "tests/", "-v"])
        print("✓ All tests passed")
    except subprocess.CalledProcessError as e:
        print(f"⚠ Some tests failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\nTo start the dashboard, run:")
    print("  streamlit run dashboard/app.py")
    print("\nOr on Windows:")
    print("  .venv\\Scripts\\activate && streamlit run dashboard/app.py")
    
    return True

if __name__ == "__main__":
    setup_environment()
