"""
Configuration settings for the Movie Recommendation System
"""

# API Configuration
TMDB_API_KEY = "Enter your API URL here"
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie"
TMDB_IMAGE_BASE_URL = "http://image.tmdb.org/t/p/w500/"
PLACEHOLDER_IMAGE_URL = "https://via.placeholder.com/500x750?text=No+Image"

# OpenAI Configuration
OPENAI_API_KEY = "Enter your API URL here"  

# API Settings
API_TIMEOUT = 5  # seconds
API_LANGUAGE = "en-US"

# Data Files
MOVIES_DATA_FILE = "./pickle/movies_dict.pkl"
SIMILARITY_DATA_FILE = "./pickle/similarity.pkl"

# UI Configuration
APP_TITLE = "Movie Recommendation System"
APP_LAYOUT = "wide"
SIDEBAR_STATE = "expanded"

# Genre Configuration
ALL_GENRES = [
    'Action', 
    'Adventure', 
    'Comedy', 
    'Drama', 
    'Horror', 
    'Thriller', 
    'Animation', 
    'Fantasy', 
    'Romance', 
    'Sci-Fi'
]

# Display Settings
MOVIES_PER_BATCH = 24
MOVIES_PER_ROW = 6
ROWS_PER_BATCH = 4
MAX_RECOMMENDATIONS = 12
TOP_CAST_COUNT = 5
MAX_GENRE_BADGES = 2

# Visualization Settings
VIZ_SAMPLE_SIZE = 500
VIZ_RANDOM_STATE = 42
MIN_YEAR_FILTER = 1980
MAX_RUNTIME_FILTER = 250
MIN_VOTE_COUNT_TOP_MOVIES = 100
TOP_MOVIES_COUNT = 10

# Color Scheme (Netflix Theme)
COLORS = {
    'primary': '#e50914',
    'secondary': '#b20710',
    'accent': '#ff0a1a',
    'gold': '#ffd700',
    'background_dark': '#000000',
    'background_mid': '#141414',
    'text_light': '#ffffff',
    'text_muted': '#999999'
}

# Chart Settings
CHART_HEIGHT = 400
CHART_HEIGHT_LARGE = 500