#!/usr/bin/env python3
"""
Run script for Resume Analysis Platform
This script starts the Streamlit application with proper error handling.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_virtual_environment():
    """Check if virtual environment is activated."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is activated!")
        return True
    else:
        print("⚠️  Virtual environment not detected.")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = ['streamlit', 'pandas', 'plotly', 'pdfplumber','nltk','spacy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required dependencies are installed!")
        return True

def start_streamlit():
    """Start the Streamlit application."""
    print("\n🚀 Starting Resume Analysis Platform...")
    print("📱 The application will open in your default browser")
    print("🌐 URL: http://localhost:8501")
    print("\n💡 To stop the application, press Ctrl+C")
    print("=" * 50)
    
    try:
        # Start Streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Streamlit: {e}")
        return False
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
        return True
    
    return True

def display_instructions():
    """Display setup instructions if environment is not ready."""
    print("""
🔧 Setup Instructions:

1. Create and activate virtual environment:
   python setup.py

2. Or manually:
   python -m venv venv
   
   # Activate virtual environment:
   Windows: venv\\Scripts\\activate
   macOS/Linux: source venv/bin/activate
   
   # Install dependencies:
   pip install -r requirements.txt

3. Then run this script again:
   python run.py

📖 For detailed instructions, see README.md
""")

def main():
    """Main run function."""
    print("🏗️  Resume Analysis Platform")
    print("=" * 50)
    
    # Check if app.py exists
    if not Path("app.py").exists():
        print("❌ app.py not found. Please ensure you're in the correct directory.")
        sys.exit(1)
    
    # Check virtual environment (optional warning)
    venv_active = check_virtual_environment()
    
    # Check dependencies
    if not check_dependencies():
        if not venv_active:
            print("\n💡 It looks like the virtual environment is not activated or dependencies are missing.")
            display_instructions()
        sys.exit(1)
    
    # Start the application
    if not start_streamlit():
        sys.exit(1)

if __name__ == "__main__":
    main() 