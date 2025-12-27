#!/usr/bin/env python3
"""
AI Movie Recommender - Setup Script

This script helps set up the project environment and dependencies.
Run this first before using the application.
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has API key"""
    print("\n🔑 Checking API configuration...")
    env_file = ".env"
    if not os.path.exists(env_file):
        print("⚠️  .env file not found. Creating one...")
        with open(env_file, "w") as f:
            f.write("# TMDB API Key for Movie Recommendation System\n")
            f.write("# REQUIRED: Get your free API key from: https://www.themoviedb.org/settings/api\n")
            f.write("# Free tier: Unlimited requests\n")
            f.write("# Replace 'your_tmdb_api_key_here' with your actual API key from TMDB\n\n")
            f.write("TMDB_API_KEY=your_tmdb_api_key_here\n")
        print("✅ .env file created! Please add your TMDB API key.")

    # Check if API key is configured
    with open(env_file, "r") as f:
        content = f.read()
        if "your_tmdb_api_key_here" in content:
            print("⚠️  TMDB API key not configured yet.")
            print("   Please edit the .env file and replace 'your_tmdb_api_key_here' with your actual API key.")
            print("   Get your free API key from: https://www.themoviedb.org/settings/api")
        else:
            print("✅ TMDB API key appears to be configured!")

def test_import():
    """Test if all required modules can be imported"""
    print("\n🧪 Testing imports...")
    try:
        import streamlit
        import requests
        import pandas
        import sentence_transformers
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup function"""
    print("🎬 AI Movie Recommender - Setup")
    print("=" * 50)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        sys.exit(1)

    # Test imports
    if not test_import():
        sys.exit(1)

    # Check environment file
    check_env_file()

    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Get your TMDB API key from: https://www.themoviedb.org/settings/api")
    print("2. Edit the .env file and add your API key")
    print("3. Run the app with: python run.py")
    print("4. Open browser to: http://localhost:8501")
    print("\n🚀 Happy movie recommending!")

if __name__ == "__main__":
    main()
