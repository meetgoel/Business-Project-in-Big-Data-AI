import streamlit as st
import pandas as pd
import pickle
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor
import time

# --------------------------
# Data Loading
# --------------------------
@st.cache_data
def load_movies_and_vectorizer():
    """Load movie data and create TF-IDF vectorizer (replaces load_data)"""
    movies_df = pickle.load(open('./pickle/movies_dict.pkl', 'rb'))
    movies_df = pd.DataFrame(movies_df)
    
    # Create and fit the vectorizer
    tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies_df['tags'])
    
    return movies_df, tfidf_matrix

@st.cache_data
def compute_similarity_for_movie(movie_index, _tfidf_matrix):
    """Compute similarity for a specific movie on-demand"""
    # Get the vector for the selected movie
    movie_vector = _tfidf_matrix[movie_index]
    
    # Compute cosine similarity only for this movie
    similarity_scores = cosine_similarity(movie_vector, _tfidf_matrix).flatten()
    
    return similarity_scores

# --------------------------
# API Functions with Rate Limiting
# --------------------------
@st.cache_data(show_spinner=False, ttl=3600)  # Cache for 1 hour
def fetch_poster(movie_id):
    """Fetch movie poster from TMDB API with caching"""
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=a21857dcf47a4fbd3b23169e9af1257b&language=en-US',
            timeout=3  # Reduced timeout
        )
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "http://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"
    except:
        return "https://via.placeholder.com/500x750?text=No+Image"

@st.cache_data(show_spinner=False, ttl=3600)  # Cache for 1 hour
def fetch_movie_details(movie_id):
    """Fetch detailed movie information from TMDB API with caching"""
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=a21857dcf47a4fbd3b23169e9af1257b&language=en-US&append_to_response=videos,credits',
            timeout=3  # Reduced timeout
        )
        data = response.json()
        return {
            'rating': data.get('vote_average', 0),
            'vote_count': data.get('vote_count', 0),
            'overview': data.get('overview', 'No description available.'),
            'runtime': data.get('runtime', 0),
            'release_date': data.get('release_date', 'Unknown'),
            'genres': [g['name'] for g in data.get('genres', [])],
            'videos': data.get('videos', {}).get('results', []),
            'cast': [c['name'] for c in data.get('credits', {}).get('cast', [])[:5]]
        }
    except:
        return {
            'rating': 0,
            'vote_count': 0,
            'overview': 'No description available.',
            'runtime': 0,
            'release_date': 'Unknown',
            'genres': [],
            'videos': [],
            'cast': []
        }

def fetch_multiple_posters(movie_ids):
    """Fetch multiple posters in parallel"""
    with ThreadPoolExecutor(max_workers=5) as executor:
        posters = list(executor.map(fetch_poster, movie_ids))
    return posters

def fetch_multiple_details(movie_ids):
    """Fetch multiple movie details in parallel"""
    with ThreadPoolExecutor(max_workers=5) as executor:
        details = list(executor.map(fetch_movie_details, movie_ids))
    return details

# --------------------------
# Display Functions
# --------------------------
def display_stars(rating, vote_count=None):
    """Generate star rating HTML"""
    full_stars = int(rating / 2)
    half_star = 1 if (rating / 2) - full_stars >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    
    stars = "⭐" * full_stars + "✨" * half_star + "☆" * empty_stars
    if vote_count:
        return f'<span class="star-rating">{stars}</span> <span style="color: #999; font-size: 12px;">({vote_count:,} votes)</span>'
    return f'<span class="star-rating">{stars}</span>'

# --------------------------
# Recommendation Engine (Optimized)
# --------------------------
def recommend(movie, movies_df, tfidf_matrix, top_n=12):
    """Generate movie recommendations using on-demand similarity computation"""
    try:
        movie_index = movies_df[movies_df['title'] == movie].index[0]
        
        # Compute similarity only for this movie
        similarity_scores = compute_similarity_for_movie(movie_index, tfidf_matrix)
        
        # Get top recommendations
        distances = sorted(list(enumerate(similarity_scores)), reverse=True, key=lambda x: x[1])[1:top_n+1]
        
        recommended_movies = []
        recommended_posters = []
        recommended_ratings = []
        recommended_ids = []
        
        # Extract movie IDs first
        movie_ids = [movies_df.iloc[i].movie_id for i, score in distances]
        
        # Fetch details and posters in parallel
        details_list = fetch_multiple_details(movie_ids)
        posters_list = fetch_multiple_posters(movie_ids)
        
        for i, (idx, score) in enumerate(distances):
            recommended_movies.append(movies_df.iloc[idx].title)
            recommended_posters.append(posters_list[i])
            recommended_ratings.append(details_list[i]['rating'])
            recommended_ids.append(movie_ids[i])
        
        return recommended_movies, recommended_posters, recommended_ratings, recommended_ids
    except IndexError:
        st.error(f"Movie '{movie}' not found in database")
        return [], [], [], []
    except Exception as e:
        st.error(f"Error generating recommendations: {str(e)}")
        return [], [], [], []

# --------------------------
# Utility Functions
# --------------------------
@st.cache_data
def get_genre_movie_count(movies_df, genre):
    """Get count of movies for a specific genre (cached)"""
    return len(movies_df[movies_df['tags'].str.contains(genre, case=False, na=False)])

@st.cache_data
def filter_movies_by_genre(movies_df, genre):
    """Filter movies by genre (cached)"""
    return movies_df[movies_df['tags'].str.contains(genre, case=False, na=False)]