import streamlit as st
import pandas as pd
import pickle
from datetime import datetime

# Import custom modules
from styles import apply_custom_styles
from utils import load_movies_and_vectorizer, fetch_poster, fetch_movie_details, display_stars, recommend
from components import display_hero_section, display_movie_grid, display_recommendations
from visualizations import render_visualizations
from ai_chatbot import render_chat_interface

# --------------------------
# Page config
# --------------------------
st.set_page_config(
    layout="wide", 
    page_title="Movie Recommendation System", 
    initial_sidebar_state="expanded"
)

# Hide Streamlit branding
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# Apply custom Netflix-style CSS
apply_custom_styles()

# --------------------------
# Dashboard title
# --------------------------
st.markdown('<div class="netflix-title">CINEMATE</div>', unsafe_allow_html=True)

# --------------------------
# Load data with progress indicator
# --------------------------
@st.cache_resource
def load_app_data():
    """Load application data with caching"""
    with st.spinner('Loading movie database...'):
        movies_df, tfidf_matrix = load_movies_and_vectorizer()
    return movies_df, tfidf_matrix

movies_df, tfidf_matrix = load_app_data()

# --------------------------
# Initialize session state
# --------------------------
if "selected_movie" not in st.session_state:
    st.session_state["selected_movie"] = None
if "genre_batches" not in st.session_state:
    st.session_state["genre_batches"] = {}
if "search_text" not in st.session_state:
    st.session_state["search_text"] = ""
if "back_clicked" not in st.session_state:
    st.session_state["back_clicked"] = False
if "genres_shown" not in st.session_state:
    st.session_state["genres_shown"] = 3
if "rec_batch" not in st.session_state:
    st.session_state["rec_batch"] = 1

# --------------------------
# Handle query param for clickable posters
# --------------------------
query_params = st.query_params

# Only process the query param if back button wasn't just clicked
if "selected" in query_params and not st.session_state["back_clicked"]:
    movie_id_param = query_params["selected"]
    movies_df["movie_id"] = movies_df["movie_id"].astype(int)

    try:
        movie_id = int(movie_id_param)
    except ValueError:
        st.warning(f"Invalid movie ID: {movie_id_param}")
        movie_id = None

    if movie_id is not None:
        filtered_movie = movies_df[movies_df["movie_id"] == movie_id]
        if not filtered_movie.empty:
            selected_movie = filtered_movie.iloc[0].title
            st.session_state["selected_movie"] = selected_movie
            st.session_state["search_text"] = ""
            # Reset recommendation batch
            st.session_state["rec_batch"] = 1

# Reset back_clicked flag after processing
if st.session_state["back_clicked"]:
    st.session_state["back_clicked"] = False

# --------------------------
# Tabs
# --------------------------
tab1, tab2, tab3 = st.tabs(["🏠 Home", "📊 Visualizations", "🤖 AI Recommendations"])

# --------------------------
# Tab 1: Home / Movie Recommender
# --------------------------
with tab1:
    # Hero Section
    if st.session_state["selected_movie"] is None:
        display_hero_section()

    # Search functionality
    from search import handle_search
    handle_search(movies_df)

    all_genres = ['Action', 'Adventure', 'Comedy', 'Drama', 'Horror', 'Thriller', 'Animation', 'Fantasy', 'Romance', 'Sci-Fi']

    if st.session_state["selected_movie"] is None:
        # Display movies by genre with lazy loading
        display_movie_grid(movies_df, all_genres)
    else:
        # Show recommendations
        display_recommendations(movies_df, tfidf_matrix)

# --------------------------
# Tab 2: Visualizations
# --------------------------
with tab2:
    # Lazy load visualizations only when tab is active
    with st.spinner('Loading analytics...'):
        render_visualizations(movies_df, all_genres)

# --------------------------
# Tab 3: AI Recommendations
# --------------------------
with tab3:
    # Render AI chatbot interface
    render_chat_interface(movies_df, tfidf_matrix)