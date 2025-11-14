import streamlit as st
from utils import fetch_poster, fetch_movie_details, display_stars, recommend

def display_hero_section():
    """Display hero banner section"""
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">Discover Your Next Favorite Movie</div>
        <div class="hero-subtitle">Powered by AI • Personalized Recommendations • Thousands of Titles</div>
    </div>
    """, unsafe_allow_html=True)

def display_movie_grid(movies_df, all_genres):
    """Display movie grid organized by genres with lazy loading"""
    
    # Add a selectbox to choose which genre to display
    st.markdown("### 🎬 Browse by Genre")
    
    # Option to show all or select specific genre
    genre_options = ["All Genres"] + all_genres
    selected_display = st.selectbox(
        "Select a genre to explore:",
        genre_options,
        key="genre_selector"
    )
    
    # Determine which genres to display
    if selected_display == "All Genres":
        genres_to_display = all_genres[:3]  # Only show first 3 genres initially
        show_load_more_genres = True
    else:
        genres_to_display = [selected_display]
        show_load_more_genres = False
    
    # Display selected genres
    for genre in genres_to_display:
        st.markdown(f'<h3>🎬 {genre}</h3>', unsafe_allow_html=True)
        genre_movies = movies_df[movies_df['tags'].str.contains(genre, case=False, na=False)]
        
        if genre not in st.session_state["genre_batches"]:
            st.session_state["genre_batches"][genre] = 1

        total_batches = st.session_state["genre_batches"][genre]
        
        # Limit to show only first batch initially (12 movies per batch)
        movies_per_batch = 12
        
        for batch_num in range(total_batches):
            start = batch_num * movies_per_batch
            end = start + movies_per_batch
            movies_to_show = genre_movies.iloc[start:end]

            if len(movies_to_show) == 0:
                continue

            # Display in rows of 6
            rows = (len(movies_to_show) + 5) // 6
            for row in range(rows):
                cols = st.columns(6)
                for col_idx in range(6):
                    idx = row * 6 + col_idx
                    if idx < len(movies_to_show):
                        movie = movies_to_show.iloc[idx]
                        
                        # Fetch movie details for overlay
                        details = fetch_movie_details(movie.movie_id)
                        genre_badges = ''.join([f'<span class="genre-badge">{g}</span>' for g in details['genres'][:2]])
                        
                        poster_html = f"""
                        <a href='?selected={movie.movie_id}' target="_self" style="text-decoration: none;">
                            <div class="poster-container">
                                <img src="{fetch_poster(movie.movie_id)}" alt="{movie.title}" loading="lazy"/>
                                <div class="poster-overlay">
                                    <h4>{movie.title}</h4>
                                    <p>{display_stars(details['rating'], details['vote_count'])}</p>
                                    <p style="font-size: 12px; color: #ccc; margin-top: 5px;">{details['release_date'][:4] if details['release_date'] != 'Unknown' else 'N/A'} • {details['runtime']} min</p>
                                    <div style="margin-top: 8px;">{genre_badges}</div>
                                </div>
                            </div>
                        </a>
                        """
                        with cols[col_idx]:
                            st.markdown(poster_html, unsafe_allow_html=True)

        # Show "Load More" button for this genre
        if len(genre_movies) > total_batches * movies_per_batch:
            if st.button(f"⬇️ Load more {genre} movies", key=f"load_{genre}"):
                st.session_state["genre_batches"][genre] += 1
                st.rerun()
    

def display_recommendations(movies_df, tfidf_matrix):
    """Display selected movie details and recommendations"""
    selected_movie = st.session_state["selected_movie"]
    
    st.markdown(f'<h3>🎯 Recommended for: {selected_movie}</h3>', unsafe_allow_html=True)
    
    # Show selected movie details
    selected_movie_data = movies_df[movies_df['title'] == selected_movie].iloc[0]
    
    # Use a spinner for loading
    with st.spinner('Loading movie details...'):
        selected_details = fetch_movie_details(selected_movie_data.movie_id)
    
    detail_col1, detail_col2 = st.columns([1, 2])
    with detail_col1:
        poster_url = fetch_poster(selected_movie_data.movie_id)
        if poster_url:
            st.image(poster_url, width='stretch')
        else:
            st.warning("Poster not available")
    
    with detail_col2:
        st.markdown(f"### {selected_movie}")
        st.markdown(display_stars(selected_details['rating'], selected_details['vote_count']), unsafe_allow_html=True)
        st.markdown(f"**Release:** {selected_details['release_date']} • **Runtime:** {selected_details['runtime']} min")
        st.markdown(f"**Genres:** {', '.join(selected_details['genres'])}")
        if selected_details['cast']:
            st.markdown(f"**Cast:** {', '.join(selected_details['cast'])}")
        
        with st.expander("📖 Overview", expanded=True):
            st.markdown(selected_details['overview'])
        
        # Show trailer if available
        if selected_details['videos']:
            trailer = next((v for v in selected_details['videos'] if v['type'] == 'Trailer'), None)
            if trailer:
                with st.expander("🎬 Watch Trailer"):
                    st.video(f"https://www.youtube.com/watch?v={trailer['key']}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h3>🎬 You might also like</h3>', unsafe_allow_html=True)
    
    # Get recommendations with progress indicator
    with st.spinner('Finding similar movies...'):
        names, posters, ratings, movie_ids = recommend(selected_movie, movies_df, tfidf_matrix, top_n=18)
    
    if not names:
        st.warning("No recommendations found.")
        return
    
    # Display all 18 recommendations in 3 rows of 6
    for i in range(0, 18, 6):
        cols = st.columns(6)
        for j in range(6):
            if i+j < len(names):
                # Fetch details for recommendations
                rec_details = fetch_movie_details(movie_ids[i+j])
                genre_badges = ''.join([f'<span class="genre-badge">{g}</span>' for g in rec_details['genres'][:2]])
                
                poster_html = f"""
                <a href='?selected={movie_ids[i+j]}' target="_self" style="text-decoration: none;">
                    <div class="poster-container">
                        <img src="{posters[i+j]}" alt="{names[i+j]}" loading="lazy"/>
                        <div class="poster-overlay">
                            <h4>{names[i+j]}</h4>
                            <p>{display_stars(rec_details['rating'], rec_details['vote_count'])}</p>
                            <p style="font-size: 12px; color: #ccc; margin-top: 5px;">{rec_details['release_date'][:4] if rec_details['release_date'] != 'N/A' else 'N/A'} • {rec_details['runtime']} min</p>
                            <div style="margin-top: 8px;">{genre_badges}</div>
                        </div>
                    </div>
                </a>
                """
                with cols[j]:
                    st.markdown(poster_html, unsafe_allow_html=True)