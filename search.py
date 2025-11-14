import streamlit as st
from difflib import SequenceMatcher

def handle_search(movies_df):
    """Handle movie search functionality with autocomplete"""
    search_col1, search_col2 = st.columns([3, 1])
    
    with search_col1:
        search_input = st.text_input(
            "🔍 Search for a movie...", 
            st.session_state.get("search_text", ""), 
            placeholder="Type a movie name..."
        )
        
    if search_input:
        # Check for exact match first
        exact_match = movies_df[movies_df['title'].str.lower() == search_input.lower()]
        
        if not exact_match.empty:
            movie_title = exact_match.iloc[0].title
            st.session_state["selected_movie"] = movie_title
            st.session_state["search_text"] = search_input
        else:
            # Search for partial matches
            search_results = movies_df[movies_df['title'].str.contains(search_input, case=False, na=False)]
            
            if not search_results.empty:
                search_results = search_results.copy()
                search_results['similarity'] = search_results['title'].apply(
                    lambda x: SequenceMatcher(None, search_input.lower(), x.lower()).ratio()
                )
                search_results = search_results.sort_values('similarity', ascending=False)
                
                with search_col2:
                    if len(search_results) > 1:
                        st.caption(f"Found {len(search_results)} results")
                
                movie_title = search_results.iloc[0].title
                st.session_state["selected_movie"] = movie_title
                st.session_state["search_text"] = search_input
            elif search_input.strip() != "":
                st.warning("🎬 No movie found! Try another title.")