@echo off
echo 🎬 AI Movie Recommender - Windows Setup
echo ======================================
echo.

echo 🐍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
echo ✅ Python found!

echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed!

echo.
echo 🔑 Checking API configuration...
if not exist .env (
    echo ⚠️  Creating .env file...
    echo # TMDB API Key for Movie Recommendation System > .env
    echo # REQUIRED: Get your free API key from: https://www.themoviedb.org/settings/api >> .env
    echo # Free tier: Unlimited requests >> .env
    echo # Replace 'your_tmdb_api_key_here' with your actual API key from TMDB >> .env
    echo. >> .env
    echo TMDB_API_KEY=your_tmdb_api_key_here >> .env
    echo ✅ .env file created!
)

echo.
echo 🎯 Setup Complete!
echo.
echo 📋 Next Steps:
echo 1. Get your TMDB API key from: https://www.themoviedb.org/settings/api
echo 2. Edit the .env file and add your API key
echo 3. Run: python run.py
echo 4. Open browser to: http://localhost:8501
echo.
echo 🚀 Happy movie recommending!
echo.
pause
