import streamlit as st
import requests
import json
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import os
from datetime import datetime
import time
import random
from PIL import Image
import base64
from io import BytesIO

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, will use environment variables directly

# Page configuration
st.set_page_config(
    page_title="AI Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: black;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .recommendation-card {
        background: white;
        color: black;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #667eea;
        transition: transform 0.2s;
    }
    .recommendation-card:hover {
        transform: translateY(-2px);
    }
    .mood-selector {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 1rem 0;
    }
    .mood-button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: black;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.3s;
    }
    .mood-button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .content-type-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: black;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
    }
    .content-type-card:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: black;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .sidebar-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: black;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        color: black;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []
if 'user_mood' not in st.session_state:
    st.session_state.user_mood = None
if 'future_goals' not in st.session_state:
    st.session_state.future_goals = []
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'last_api_call' not in st.session_state:
    st.session_state.last_api_call = 0

# API Keys (will ask user if needed)
TMDB_API_KEY = os.getenv('TMDB_API_KEY', '636ffddba24c162a08a1cf34ad3dc5f1')

# Content type configurations
CONTENT_TYPES = {
    'Movies': {
        'icon': '🎬',
        'description': 'Discover amazing movies based on your mood and future goals',
        'api': 'TMDB'
    }
}

MOODS = {
    'Happy': {'emoji': '😊', 'color': '#FFD700', 'keywords': ['comedy', 'fun', 'happy', 'feel good', 'lighthearted']},
    'Sad': {'emoji': '😢', 'color': '#4169E1', 'keywords': ['drama', 'emotional', 'moving', 'touching', 'heartfelt']},
    'Excited': {'emoji': '🤩', 'color': '#FF6347', 'keywords': ['action', 'thriller', 'adventure', 'exciting', 'intense']},
    'Relaxed': {'emoji': '😌', 'color': '#98FB98', 'keywords': ['documentary', 'nature', 'calm', 'peaceful', 'relaxing']},
    'Curious': {'emoji': '🤔', 'color': '#DDA0DD', 'keywords': ['educational', 'science', 'history', 'discovery', 'documentary']},
    'Romantic': {'emoji': '💕', 'color': '#FFB6C1', 'keywords': ['romance', 'love', 'romantic', 'relationship', 'love story']}
}

FUTURE_GOALS = [
    'Become more knowledgeable', 'Improve physical health', 'Learn new skills',
    'Build better relationships', 'Achieve career success', 'Travel the world',
    'Start a business', 'Help others', 'Create art', 'Live sustainably'
]

class ContentRecommender:
    def __init__(self):
        self.model = None
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except:
            st.warning("Sentence transformer model not loaded. Some features may be limited.")

    def get_movie_recommendations(self, mood, future_goal=None, limit=5):
        """Get movie recommendations from TMDB based on mood and future goals"""
        try:
            # Try keywords in sequence until we get good results
            headers = {
                'User-Agent': 'AI-Movie-Recommender/1.0 (Educational Project)',
                'Accept': 'application/json'
            }

            results = []
            mood_keywords = MOODS[mood]['keywords'][:3]  # Try up to 3 keywords

            for search_query in mood_keywords:
                print(f"[SEARCH] Looking for movies with: '{search_query}'")

                url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={search_query}&sort_by=popularity.desc"
                response = requests.get(url, headers=headers, timeout=20)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])

                    # If we got at least 2 results, use this query
                    if len(results) >= 2:
                        print(f"[SUCCESS] Found {len(results)} movies with '{search_query}'")

                        # Process the results
                        recommendations = []
                        for movie in results[:limit]:
                            recommendations.append({
                                'title': movie['title'],
                                'description': movie.get('overview', 'No description available'),
                                'image': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path', '')}" if movie.get('poster_path') else None,
                                'link': f"https://www.themoviedb.org/movie/{movie['id']}",
                                'rating': movie.get('vote_average', 0),
                                'year': movie.get('release_date', '')[:4] if movie.get('release_date') else '',
                                'type': 'Movie'
                            })

                        print(f"[SUCCESS] Returning {len(recommendations)} movie recommendations")
                        return recommendations
                    else:
                        print(f"[INFO] Only {len(results)} movies found with '{search_query}', trying next keyword...")

                # Handle API errors
                elif response.status_code == 429:
                    print("[WARNING] Rate limited, stopping search")
                    st.error("⚠️ TMDB API rate limit exceeded. Please wait a few minutes and try again.")
                    return []
                elif response.status_code == 401:
                    print("[ERROR] Invalid API key")
                    st.error("❌ Invalid TMDB API key. Please check your .env file.")
                    return []
                else:
                    print(f"[ERROR] HTTP {response.status_code} with '{search_query}'")

            # If we get here, no keywords worked
            print("[ERROR] No movies found with any keywords")
            st.error("❌ No movies found for this mood. Try selecting a different mood.")
            return []

        except requests.exceptions.ConnectionError:
            st.error("❌ Network connection error. Please check your internet connection and try again.")
            return []
        except requests.exceptions.Timeout:
            st.error("❌ Request timed out. TMDB servers may be busy. Please try again.")
            return []
        except Exception as e:
            st.error(f"❌ Error fetching movie recommendations: {str(e)}")
            return []




    def _goal_to_keywords(self, goal):
        """Convert future goals to relevant keywords"""
        goal_keywords = {
            'Become more knowledgeable': ['education', 'science', 'learning', 'knowledge'],
            'Improve physical health': ['fitness', 'health', 'exercise', 'wellness'],
            'Learn new skills': ['tutorial', 'skill', 'learning', 'education'],
            'Build better relationships': ['relationships', 'communication', 'social', 'psychology'],
            'Achieve career success': ['career', 'business', 'leadership', 'success'],
            'Travel the world': ['travel', 'adventure', 'culture', 'exploration'],
            'Start a business': ['entrepreneurship', 'business', 'startup', 'finance'],
            'Help others': ['volunteer', 'charity', 'community', 'social impact'],
            'Create art': ['art', 'creativity', 'design', 'inspiration'],
            'Live sustainably': ['environment', 'sustainability', 'nature', 'eco-friendly']
        }
        return goal_keywords.get(goal, [])

def main():
    st.markdown('<div class="main-header"><h1>🎬 AI Movie Recommender</h1><p>Discover personalized movies that match your mood and future aspirations</p></div>', unsafe_allow_html=True)

    # Initialize recommender
    recommender = ContentRecommender()

    # Sidebar for configuration
    with st.sidebar:
        st.markdown('<div class="sidebar-content"><h3>🎬 Movie Preferences</h3></div>', unsafe_allow_html=True)

        # Mood selection
        st.markdown("### 😊 Current Mood")
        mood_cols = st.columns(2)
        for i, (mood, info) in enumerate(MOODS.items()):
            col_idx = i % 2
            with mood_cols[col_idx]:
                if st.button(f"{info['emoji']} {mood}", key=f"mood_{mood}"):
                    st.session_state.user_mood = mood
                    st.success(f"Mood set to {mood}!")

        # Future goals
        st.markdown("### 🎯 Future Goals")
        selected_goals = st.multiselect(
            "What are your aspirations?",
            FUTURE_GOALS,
            default=st.session_state.future_goals
        )
        st.session_state.future_goals = selected_goals

    # Main content area
    if not st.session_state.user_mood:
        # Welcome screen
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("## 🌟 Welcome to AI Movie Recommender!")
            st.markdown("### How it works:")
            st.markdown("1. **Select your current mood** from the sidebar")
            st.markdown("2. **Choose your future aspirations** (optional)")
            st.markdown("3. **Get personalized movie recommendations** instantly!")

            st.markdown("---")
            st.markdown("### 🎬 Movie Recommendations")

            st.markdown("""
            <div class="content-type-card">
                <h3>🎬 Movies</h3>
                <p>Discover amazing movies based on your mood and future goals using TMDB API</p>
                <small>Powered by TMDB (Free API)</small>
            </div>
            """, unsafe_allow_html=True)

    else:
        # Recommendations screen
        st.markdown(f"## {MOODS[st.session_state.user_mood]['emoji']} Recommendations for '{st.session_state.user_mood}' mood")

        if st.session_state.future_goals:
            st.markdown(f"**Future Goals:** {', '.join(st.session_state.future_goals)}")

        # Get recommendations button
        if st.button("🎯 Get Personalized Recommendations", type="primary"):
            # Rate limiting: prevent API calls more often than every 5 seconds
            import time
            current_time = time.time()
            if current_time - st.session_state.last_api_call < 5:
                st.warning("⚠️ Please wait a few seconds before making another request.")
                st.stop()

            st.session_state.last_api_call = current_time

            with st.spinner("Finding the perfect movies for you..."):
                progress_bar = st.progress(0)
                all_recommendations = []

                # Get movie recommendations (only content type available)
                progress_bar.progress(1.0)
                recs = recommender.get_movie_recommendations(
                    st.session_state.user_mood,
                    st.session_state.future_goals[0] if st.session_state.future_goals else None,
                    limit=15  # Get more movies since it's the only option
                )

                all_recommendations.extend(recs)

                progress_bar.progress(100)
                time.sleep(0.5)
                progress_bar.empty()

                # Shuffle and limit recommendations
                random.shuffle(all_recommendations)
                st.session_state.recommendations = all_recommendations[:12]  # Show up to 12 recommendations

        # Display recommendations
        if st.session_state.recommendations:
            st.markdown(f"### 🎬 Found {len(st.session_state.recommendations)} Movie Recommendations")

            cols = st.columns(2)
            for i, rec in enumerate(st.session_state.recommendations):
                col_idx = i % 2
                with cols[col_idx]:
                    st.markdown(f"""
                    <div class="recommendation-card">
                        <h4>{rec['title']}</h4>
                        {"<p><strong>Rating:</strong> ⭐ " + str(rec.get('rating', 'N/A')) + "</p>" if rec.get('rating') else ""}
                        {"<p><strong>Year:</strong> " + rec.get('year', '') + "</p>" if rec.get('year') else ""}
                        <p>{rec['description']}</p>
                        <a href="{rec['link']}" target="_blank" style="text-decoration: none;">
                            <button style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: black; border: none; padding: 0.5rem 1rem; border-radius: 20px; cursor: pointer;">🔗 View Movie</button>
                        </a>
                    </div>
                    """, unsafe_allow_html=True)

                    # Display image if available
                    if rec.get('image'):
                        try:
                            st.image(rec['image'], width=200)
                        except:
                            pass

            # Clear recommendations button
            if st.button("🗑️ Clear Recommendations"):
                st.session_state.recommendations = []
                st.experimental_rerun()

    # Footer
    st.markdown("---")
    st.markdown("### 📊 Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="metric-card"><h4>🎭 Moods</h4><h2>6</h2></div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card"><h4>🎬 Movies</h4><h2>TMDB</h2></div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card"><h4>🎯 Goals</h4><h2>10</h2></div>', unsafe_allow_html=True)

    with col4:
        st.markdown(f'<div class="metric-card"><h4>📋 Recommendations</h4><h2>{len(st.session_state.recommendations)}</h2></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Built with ❤️ using Streamlit and TMDB API**")

if __name__ == "__main__":
    main()
