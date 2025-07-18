#!/usr/bin/env python3
"""
Setup script for Meta Ad Library Scraper
This script handles the installation and setup of dependencies
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and handle errors"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running: {command}")
        print(f"Error output: {e.stderr}")
        return None

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    run_command(f"{sys.executable} -m pip install --upgrade pip")
    run_command(f"{sys.executable} -m pip install -r requirements.txt")

def install_browser():
    """Install Chrome/Chromium browser"""
    print("🌐 Installing Chromium browser...")
    
    # Check if we're on a Debian/Ubuntu system
    try:
        result = subprocess.run(['which', 'apt'], capture_output=True)
        if result.returncode == 0:
            # Install Chromium on Debian/Ubuntu
            run_command("sudo apt update")
            run_command("sudo apt install -y chromium-browser")
        else:
            print("⚠️  Could not automatically install browser. Please install Chrome or Chromium manually:")
            print("   - On Ubuntu/Debian: sudo apt install chromium-browser")
            print("   - On CentOS/RHEL: sudo yum install chromium")
            print("   - On macOS: brew install --cask google-chrome")
    except Exception as e:
        print(f"⚠️  Could not install browser automatically: {e}")
        print("Please install Chrome or Chromium manually for full functionality.")

def check_requirements():
    """Check if all requirements are satisfied"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    # Check if pip is available
    try:
        import pip
        print("✅ pip is available")
    except ImportError:
        print("❌ pip is not available")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    print("✅ Directories created")

def create_virtual_environment():
    """Create Python virtual environment"""
    print("🐍 Creating virtual environment...")
    run_command(f"{sys.executable} -m venv venv")
    
    # Activate virtual environment and upgrade pip
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    run_command(f"{pip_cmd} install --upgrade pip")
    print("✅ Virtual environment created")

def main():
    """Main setup function"""
    print("🚀 Setting up Meta Ad Library Scraper...")
    print("=" * 50)
    
    if not check_requirements():
        print("❌ Setup failed: Requirements not met")
        sys.exit(1)
    
    create_directories()
    create_virtual_environment()
    
    # Install dependencies in virtual environment
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip"
    
    print("📦 Installing Python dependencies in virtual environment...")
    run_command(f"{pip_cmd} install -r requirements.txt")
    
    install_browser()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nTo run the application:")
    print("  ./run.sh")
    print("  # or")
    print("  source venv/bin/activate && python app.py")
    print("\nThe app will be available at: http://localhost:5000")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()