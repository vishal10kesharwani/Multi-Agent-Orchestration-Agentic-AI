"""
Setup script for Multi-Agent Orchestration Platform
"""
import os
import sys
import subprocess
import asyncio
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file from example"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        print("Creating .env file...")
        with open(env_example) as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file created")
        print("⚠️  Please review and update the .env file with your specific configuration")
        return True
    elif env_file.exists():
        print("✅ .env file already exists")
        return True
    else:
        print("❌ .env.example not found")
        return False

def setup_database():
    """Setup database"""
    print("Setting up database...")
    try:
        from backend.database.connection import init_database
        asyncio.run(init_database())
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to setup database: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("Multi-Agent Orchestration Platform - Setup")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python version: {sys.version}")
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create .env file
    if not create_env_file():
        return False
    
    # Setup database
    if not setup_database():
        return False
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review and update .env file if needed")
    print("2. Start the platform: python main.py")
    print("3. Run demo: python test_runner.py demo")
    print("4. Run tests: python test_runner.py test")
    print("5. Access web interface: http://localhost:8000")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
