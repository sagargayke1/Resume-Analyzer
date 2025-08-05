#!/usr/bin/env python3
"""
Setup script for Resume Analysis Platform
This script helps with initial setup and installation of dependencies.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible!")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible. Please use Python 3.8 or higher.")
        return False

def create_virtual_environment():
    """Create a virtual environment."""
    venv_path = Path("venv")
    if venv_path.exists():
        print("📁 Virtual environment already exists!")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")

def install_dependencies():
    """Install required dependencies."""
    # Determine the correct pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = "venv\\Scripts\\pip"
    else:  # macOS/Linux
        pip_path = "venv/bin/pip"
    
    commands = [
        (f"{pip_path} install --upgrade pip", "Upgrading pip"),
        (f"{pip_path} install -r requirements.txt", "Installing dependencies")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True

def create_sample_data():
    """Create sample directories if they don't exist."""
    directories = ["data", "models", "uploads"]
    
    print("\n📁 Creating project directories...")
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            print(f"✅ Created {directory}/ directory")
        else:
            print(f"📁 {directory}/ directory already exists")

def display_next_steps():
    """Display next steps for the user."""
    print("""
🎉 Setup Complete! 

🚀 Next Steps:
1. Activate the virtual environment:
   Windows: venv\\Scripts\\activate
   macOS/Linux: source venv/bin/activate

2. Run the application:
   streamlit run app.py

3. Open your browser to: http://localhost:8501

📖 For detailed usage instructions, see README.md

💡 Tips:
- Place your PDF resume files in the uploads/ folder
- The system works best with text-based PDFs
- Supported domains: ML/AI, Frontend, Backend, Data Engineering, DevOps

🆘 Need help? Check the troubleshooting section in README.md
""")

def main():
    """Main setup function."""
    print("🏗️  Resume Analysis Platform Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment. Please create it manually:")
        print("   python -m venv venv")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies. Please install manually:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Create directories
    create_sample_data()
    
    # Display next steps
    display_next_steps()

if __name__ == "__main__":
    main() 