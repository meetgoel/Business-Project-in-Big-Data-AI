import streamlit as st
from openai import OpenAI
from typing import List, Dict
import pandas as pd
import json
import re
import requests
from utils import fetch_movie_details, fetch_poster, display_stars
from config import OPENAI_API_KEY, TMDB_API_KEY

# ---------------- MovieChatbot Class ---------------- #
class MovieChatbot:
    """Hybrid AI chatbot combining OpenAI with local movie database"""

    def __init__(self, api_key: str, movies_df: pd.DataFrame, tfidf_matrix):
        self.client = OpenAI(api_key=api_key)
        self.movies_df = movies_df
        self.tfidf_matrix = tfidf_matrix
        self.system_prompt = """You are a movie recommendation assistant with access to a specific movie database, but you can also recommend movies outside of it.

Role:
1. Help users discover movies from database AND beyond
2. Ask clarifying questions about preferences (genre, mood, actors, themes)
3. Provide thoughtful recommendations with explanations
4. Be conversational and enthusiastic

Response Format:
{
  "message": "Your conversational response here",
  "database_movies": [
    {"title": "Exact Movie Title", "movie_id": 12345, "reason": "Brief explanation"}
  ],
  "external_movies": [
    {"title": "Movie Title", "year": 2020, "reason": "Brief explanation"}
  ]
}

Rules:
- Always include 'message'
- Include 'database_movies' when recommending from database
- Include 'external_movies' when recommending from general knowledge
- Provide 10-15 recommendations, prioritize database movies"""
    
    def search_database(self, query: str, limit: int = 15) -> List[Dict]:
        query_lower = query.lower()
        title_matches = self.movies_df[self.movies_df['title'].str.lower().str.contains(query_lower, na=False, regex=False)]
        tag_matches = self.movies_df[self.movies_df['tags'].str.lower().str.contains(query_lower, na=False, regex=False)]
        all_matches = pd.concat([title_matches, tag_matches]).drop_duplicates(subset=['movie_id'])
        
        results = []
        for _, movie in all_matches.head(limit).iterrows():
            details = fetch_movie_details(movie.movie_id)
            results.append({
                'title': movie.title,
                'movie_id': movie.movie_id,
                'genres': ', '.join(details['genres']) if details['genres'] else 'N/A',
                'rating': details['rating'],
                'year': details['release_date'][:4] if details['release_date'] != 'Unknown' else 'N/A'
            })
        return results
    
    def get_movie_context(self, user_query: str) -> str:
        keywords = ['action', 'comedy', 'drama', 'horror', 'thriller', 'romance', 'sci-fi', 'animation', 'fantasy', 'adventure']
        found_genres = [kw for kw in keywords if kw in user_query.lower()]
        context = f"Database Info: {len(self.movies_df)} movies available.\n\n"
        
        search_results = self.search_database(user_query, limit=15)
        if search_results:
            context += "Movies available in our database (USE EXACT TITLES):\n"
            for movie in search_results:
                context += f"- {movie['title']} (ID: {movie['movie_id']}, {movie['year']}) | Genres: {movie['genres']} | Rating: {movie['rating']:.1f}/10\n"
        elif found_genres:
            genre_movies = self.search_database(found_genres[0], limit=15)
            if genre_movies:
                context += f"\n{found_genres[0].capitalize()} movies in database:\n"
                for movie in genre_movies:
                    context += f"- {movie['title']} (ID: {movie['movie_id']}, {movie['year']}) | Rating: {movie['rating']:.1f}/10\n"
        
        context += "\nNote: Recommend 10-15 movies total. Prioritize database movies."
        return context
    
    def validate_movie_ids(self, parsed_response: Dict) -> Dict:
        if 'database_movies' in parsed_response:
            validated = []
            for movie in parsed_response['database_movies']:
                title = movie.get('title', '')
                matched = self.movies_df[self.movies_df['title'].str.lower() == title.lower()]
                if not matched.empty:
                    validated.append({
                        'title': matched.iloc[0]['title'],
                        'movie_id': matched.iloc[0]['movie_id'],
                        'reason': movie.get('reason', '')
                    })
            parsed_response['database_movies'] = validated
        return parsed_response
    
    def parse_response(self, response_text: str) -> Dict:
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return self.validate_movie_ids(parsed)
            return {"message": response_text, "database_movies": [], "external_movies": []}
        except:
            return {"message": response_text, "database_movies": [], "external_movies": []}
    
    def get_response(self, user_message: str, conversation_history: List[Dict]) -> Dict:
        try:
            db_context = self.get_movie_context(user_message)
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": db_context}
            ]
            messages.extend(conversation_history[-10:])
            messages.append({"role": "user", "content": user_message})
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=1500,
                temperature=0.7,
            )
            response_text = response.choices[0].message.content
            return self.parse_response(response_text)
        
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "api key" in error_msg:
                return {"message": "❌ Invalid API key.", "database_movies": [], "external_movies": []}
            elif "rate limit" in error_msg or "quota" in error_msg:
                return {"message": "⚠️ Rate limit reached. Try again later.", "database_movies": [], "external_movies": []}
            else:
                return {"message": f"❌ Error: {str(e)}", "database_movies": [], "external_movies": []}

# ---------------- TMDB Poster Search ---------------- #
@st.cache_data(show_spinner=False, ttl=3600)
def search_external_movie_poster(title: str, year: int = None) -> Dict:
    try:
        params = {'api_key': TMDB_API_KEY, 'query': title, 'language': 'en-US'}
        if year:
            params['year'] = year
        response = requests.get("https://api.themoviedb.org/3/search/movie", params=params, timeout=3)
        data = response.json()
        if data.get('results'):
            movie = data['results'][0]
            poster_path = movie.get('poster_path')
            return {
                'poster_url': f"http://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750/141414/e50914?text=No+Poster",
                'rating': movie.get('vote_average', 0),
                'release_date': movie.get('release_date', 'Unknown'),
                'overview': movie.get('overview', 'No description available'),
                'tmdb_id': movie.get('id')
            }
        return {'poster_url': "https://via.placeholder.com/500x750/141414/e50914?text=No+Poster", 'rating': 0, 'release_date': 'Unknown', 'overview': 'No description available', 'tmdb_id': None}
    except:
        return {'poster_url': "https://via.placeholder.com/500x750/141414/e50914?text=Error", 'rating': 0, 'release_date': 'Unknown', 'overview': 'Error fetching data', 'tmdb_id': None}

# ---------------- Movie Display Functions ---------------- #
def display_movie_details_modal(movie_id: int):
    details = fetch_movie_details(movie_id)
    poster_url = fetch_poster(movie_id)
    col1, col2 = st.columns([1, 2])
    with col1:
        if poster_url:
            st.image(poster_url, use_container_width=True)
    with col2:
        movie_data = st.session_state.movies_df[st.session_state.movies_df['movie_id'] == movie_id]
        if not movie_data.empty:
            st.markdown(f"### {movie_data.iloc[0].title}")
        st.markdown(display_stars(details['rating'], details['vote_count']), unsafe_allow_html=True)
        st.markdown(f"**Release:** {details['release_date']} • **Runtime:** {details['runtime']} min")
        st.markdown(f"**Genres:** {', '.join(details['genres'])}")
        if details['cast']:
            st.markdown(f"**Cast:** {', '.join(details['cast'])}")
        with st.expander("📖 Overview", expanded=True):
            st.markdown(details['overview'])
        if details['videos']:
            trailer = next((v for v in details['videos'] if v['type'] == 'Trailer'), None)
            if trailer:
                with st.expander("🎬 Watch Trailer"):
                    st.video(f"https://www.youtube.com/watch?v={trailer['key']}")

def render_movie_posters(movies_list: List[Dict], label: str, is_database: bool = True):
    if not movies_list:
        return
    st.markdown(f"### {label}")
    rows = max(3, (len(movies_list) + 4) // 5)
    for row in range(rows):
        cols = st.columns(5)
        for col_idx in range(5):
            idx = row * 5 + col_idx
            if idx < len(movies_list):
                movie = movies_list[idx]
                if is_database:
                    movie_id = movie.get('movie_id')
                    details = fetch_movie_details(movie_id)
                    poster_url = fetch_poster(movie_id)
                    genre_badges = ''.join([f'<span class="genre-badge">{g}</span>' for g in details['genres'][:2]])
                    poster_html = f"""
                    <a href='?selected={movie_id}&tab=ai' target="_self" style="text-decoration: none;">
                        <div class="poster-container">
                            <img src="{poster_url}" alt="{movie['title']}" loading="lazy"/>
                            <div class="poster-overlay">
                                <h4>{movie['title']}</h4>
                                <p>{display_stars(details['rating'], details['vote_count'])}</p>
                                <p style="font-size: 12px; color: #ccc; margin-top: 5px;">
                                    {details['release_date'][:4] if details['release_date'] != 'Unknown' else 'N/A'} • {details['runtime']} min
                                </p>
                                <div style="margin-top: 8px;">{genre_badges}</div>
                                <p style="font-size: 11px; margin-top: 8px; color: #90ee90;">✓ In Database</p>
                            </div>
                        </div>
                    </a>
                    """
                    with cols[col_idx]:
                        st.markdown(poster_html, unsafe_allow_html=True)
                        if movie.get('reason'):
                            st.caption(f"💡 {movie['reason']}")
                else:
                    movie_title = movie.get('title', 'Unknown')
                    year = movie.get('year', None)
                    reason = movie.get('reason', '')
                    external_data = search_external_movie_poster(movie_title, year)
                    poster_url = external_data['poster_url']
                    rating = external_data['rating']
                    release_date = external_data['release_date']
                    display_year = year if year else (release_date[:4] if release_date != 'Unknown' else 'N/A')
                    external_html = f"""
                    <div class="poster-container" style="cursor: default;">
                        <img src="{poster_url}" alt="{movie_title}" loading="lazy"/>
                        <div class="poster-overlay">
                            <h4>{movie_title}</h4>
                            <p>{display_stars(rating, 0) if rating > 0 else '<span style="color: #999;">Rating N/A</span>'}</p>
                            <p style="font-size: 12px; color: #ccc; margin-top: 5px;">{display_year}</p>
                            <p style="font-size: 11px; margin-top: 8px; color: #ff6b6b;">🌐 External Recommendation</p>
                        </div>
                    </div>
                    """
                    with cols[col_idx]:
                        st.markdown(external_html, unsafe_allow_html=True)
                        if reason:
                            st.caption(f"💡 {reason}")
                        with st.expander("ℹ️ More Info", expanded=False):
                            st.markdown(f"**Overview:** {external_data['overview'][:200]}...")
                            if external_data['tmdb_id']:
                                st.markdown(f"[View on TMDB](https://www.themoviedb.org/movie/{external_data['tmdb_id']})")

# ---------------- Chat Interface ---------------- #
def render_chat_interface(movies_df, tfidf_matrix):
    st.session_state.movies_df = movies_df
    
    query_params = st.query_params
    if "selected" in query_params and query_params.get("tab") == "ai":
        try:
            movie_id = int(query_params["selected"])
            st.markdown("### 🎬 Movie Details")
            display_movie_details_modal(movie_id)
            if st.button("⬅️ Back to Chat"):
                st.query_params.clear()
                st.rerun()
            st.markdown("---")
        except ValueError:
            pass
    
    st.markdown('<h3>🤖 AI Movie Recommendation Assistant</h3>', unsafe_allow_html=True)
    st.markdown("Ask me about ANY movie! Click on database posters to see full details and trailers.")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎬 AI Assistant Info")
        if OPENAI_API_KEY and OPENAI_API_KEY != "your-openai-api-key-here":
            st.success("✅ OpenAI API configured")
        else:
            st.error("❌ OpenAI API key not configured in config.py")
            st.info("Please add your OpenAI API key to config.py")
        st.markdown("---")
        st.markdown("**💭 Example questions:**")
        st.markdown("- What sci-fi movies do you recommend?")
        st.markdown("- Movies similar to Inception")
        st.markdown("- Best Christopher Nolan films")
        st.markdown("- I want a comedy for tonight")
        st.markdown("- Show me highly rated thrillers")
    
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your-openai-api-key-here":
        st.error("⚠️ OpenAI API key not configured. Please add your API key to config.py")
        return
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = MovieChatbot(OPENAI_API_KEY, movies_df, tfidf_matrix)
    
    chat_container = st.container()
    with chat_container:
        for msg_idx, msg_data in enumerate(st.session_state.chat_messages):
            if msg_data["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(msg_data["content"])
            else:
                with st.chat_message("assistant"):
                    if isinstance(msg_data["content"], dict):
                        st.markdown(msg_data["content"]["message"])
                        if msg_data["content"].get("database_movies"):
                            render_movie_posters(msg_data["content"]["database_movies"], "🎬 From Our Database", is_database=True)
                        if msg_data["content"].get("external_movies"):
                            render_movie_posters(msg_data["content"]["external_movies"], "🌐 More Recommendations (via TMDB)", is_database=False)
                    else:
                        st.markdown(msg_data["content"])
    
    if prompt := st.chat_input("Ask me for movie recommendations..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.spinner("🎬 Searching movies and generating recommendations..."):
            response = st.session_state.chatbot.get_response(
                prompt,
                [{"role": msg["role"], "content": msg["content"] if isinstance(msg["content"], str) else msg["content"]["message"]} 
                 for msg in st.session_state.chat_messages[:-1]]
            )
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    if st.session_state.chat_messages:
        if st.button("🗑️ Clear Chat", key="clear_chat_btn"):
            st.session_state.chat_messages = []
            st.rerun()
