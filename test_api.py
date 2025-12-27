#!/usr/bin/env python3
"""
Test TMDB API Key
"""

import requests
import os
from dotenv import load_dotenv

def test_api_key():
    # Load environment variables
    load_dotenv()

    # Get API key
    api_key = os.getenv('TMDB_API_KEY')
    if not api_key:
        print('❌ No API key found in .env file')
        return False

    print(f'🔑 Testing API key: {api_key[:8]}...')

    try:
        # Test API call
        url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query=happy'
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            movie_count = len(data.get('results', []))
            print(f'✅ API key works! Found {movie_count} movies for "happy"')
            return True
        else:
            print(f'❌ API key invalid. Status: {response.status_code}')
            print(f'Response: {response.text[:200]}')
            return False

    except requests.exceptions.RequestException as e:
        print(f'❌ Connection error: {e}')
        return False

if __name__ == "__main__":
    test_api_key()
