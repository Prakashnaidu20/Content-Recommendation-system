#!/usr/bin/env python3
"""
AI Content Recommender - Launcher Script

This script provides an easy way to run the Streamlit application
with proper environment setup and error handling.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"SUCCESS: Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'requests',
        'pandas',
        'sentence_transformers',
        'python_dotenv'
    ]

    # Map package names to their actual import names
    package_imports = {
        'streamlit': 'streamlit',
        'requests': 'requests',
        'pandas': 'pandas',
        'sentence_transformers': 'sentence_transformers',
        'python_dotenv': 'dotenv'
    }

    missing_packages = []
    for package_name, import_name in package_imports.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)

    if missing_packages:
        print("ERROR: Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall with: pip install -r requirements.txt")
        return False

    print("SUCCESS: All required packages are installed")
    return True

def load_environment():
    """Load environment variables from .env file if it exists"""
    env_file = Path('.env')
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("SUCCESS: Environment variables loaded from .env file")
        except ImportError:
            print("WARNING: python-dotenv not installed, skipping .env file loading")
    else:
        print("INFO: No .env file found, using environment variables or defaults")

def check_api_keys():
    """Check if TMDB API key is configured"""
    tmdb_key = os.getenv('TMDB_API_KEY', '636ffddba24c162a08a1cf34ad3dc5f1')

    if not tmdb_key or tmdb_key == '636ffddba24c162a08a1cf34ad3dc5f1':
        print("WARNING: TMDB API Key not configured!")
        print("   - Get your free API key from: https://www.themoviedb.org/settings/api")
        print("\nYou can still run the app, but movie recommendations won't work.")
        print("Add your TMDB API key to the .env file.")
    else:
        print("SUCCESS: TMDB API key is configured")

def run_streamlit():
    """Run the Streamlit application"""
    print("\nStarting AI Content Recommender...")

    try:
        # Run streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Error running Streamlit: {e}")
        return False
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
        return True
    return True

def main():
    """Main launcher function"""
    print("AI Content Recommender Launcher")
    print("=" * 50)

    # Check system requirements
    if not check_python_version():
        sys.exit(1)

    if not check_dependencies():
        sys.exit(1)

    # Load environment
    load_environment()

    # Check API keys
    check_api_keys()

    print("\n" + "=" * 50)
    print("System check complete!")

    # Run the application
    success = run_streamlit()

    if success:
        print("\nApplication exited successfully")
    else:
        print("\nApplication exited with errors")
        sys.exit(1)

if __name__ == "__main__":
    main()
