import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils import fetch_movie_details

@st.cache_data(show_spinner=False)
def fetch_visualization_data(movies_df, sample_size=200):  # Reduced from 500 to 200
    """Fetch detailed movie data for visualizations (Optimized)"""
    sample_movies = movies_df.sample(n=min(sample_size, len(movies_df)), random_state=42)
    viz_data = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, (i, movie) in enumerate(sample_movies.iterrows()):
        if idx % 20 == 0:  # Update UI less frequently
            status_text.text(f"Loading movie data... {idx+1}/{len(sample_movies)}")
            progress_bar.progress((idx + 1) / len(sample_movies))
        
        details = fetch_movie_details(movie.movie_id)
        viz_data.append({
            'title': movie.title,
            'rating': details['rating'],
            'vote_count': details['vote_count'],
            'runtime': details['runtime'],
            'release_date': details['release_date'],
            'year': int(details['release_date'][:4]) if details['release_date'] != 'Unknown' and len(details['release_date']) >= 4 else None,
            'genres': details['genres']
        })
    
    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(viz_data)

def render_key_metrics(movies_df, viz_df):
    """Display key metrics cards"""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Movies", f"{len(movies_df):,}")
    with col2:
        avg_rating = viz_df[viz_df['rating'] > 0]['rating'].mean()
        st.metric("Avg Rating", f"{avg_rating:.1f}⭐")
    with col3:
        avg_runtime = viz_df[viz_df['runtime'] > 0]['runtime'].mean()
        st.metric("Avg Runtime", f"{int(avg_runtime)} min")
    with col4:
        total_votes = viz_df['vote_count'].sum()
        st.metric("Total Votes", f"{total_votes:,.0f}")

def render_genre_distribution(movies_df, all_genres):
    """Render genre distribution bar chart"""
    st.markdown("#### 🎭 Genre Distribution")
    genre_data = []
    for genre in all_genres:
        count = len(movies_df[movies_df['tags'].str.contains(genre, case=False, na=False)])
        genre_data.append({"Genre": genre, "Count": count})
    
    fig1 = px.bar(genre_data, x="Genre", y="Count", 
                 color="Count",
                 color_continuous_scale=["#b20710", "#e50914", "#ff0a1a"],
                 title="Movies per Genre")
    fig1.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title="Number of Movies"),
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig1, config={"plotly":{ "responsive": True, "displayModeBar": False}})

def render_rating_distribution(viz_df):
    """Render rating distribution chart"""
    st.markdown("#### ⭐ Rating Distribution")
    rating_bins = pd.cut(viz_df[viz_df['rating'] > 0]['rating'], 
                         bins=[0, 3, 5, 7, 8, 10], 
                         labels=['0-3', '3-5', '5-7', '7-8', '8-10'])
    rating_counts = rating_bins.value_counts().sort_index()
    
    fig2 = go.Figure(data=[go.Bar(
        x=rating_counts.index,
        y=rating_counts.values,
        marker_color=['#ff0a1a', '#e50914', '#ffd700', '#90ee90', '#4169e1'],
        text=rating_counts.values,
        textposition='auto',
    )])
    fig2.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        xaxis=dict(showgrid=False, title="Rating Range"),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title="Number of Movies"),
        title="Distribution of Movie Ratings",
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig2, config={"plotly":{ "responsive": True, "displayModeBar": False}})

def render_year_trends(viz_df):
    """Render movies by release year chart"""
    st.markdown("#### 📅 Movies by Release Year")
    year_df = viz_df[viz_df['year'].notna()].copy()
    year_counts = year_df.groupby('year').size().reset_index(name='count')
    year_counts = year_counts[year_counts['year'] >= 1980]
    
    fig3 = px.area(year_counts, x='year', y='count',
                  title="Movie Releases Over Time (1980+)",
                  color_discrete_sequence=['#e50914'])
    fig3.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        xaxis=dict(showgrid=False, title="Year"),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title="Number of Movies"),
        showlegend=False,
        height=400
    )
    fig3.update_traces(fill='tozeroy', fillcolor='rgba(229, 9, 20, 0.3)')
    st.plotly_chart(fig3, config={"plotly":{ "responsive": True, "displayModeBar": False}})

def render_runtime_distribution(viz_df):
    """Render runtime distribution histogram"""
    st.markdown("#### ⏱️ Runtime Distribution")
    runtime_df = viz_df[(viz_df['runtime'] > 0) & (viz_df['runtime'] < 250)].copy()
    
    fig4 = go.Figure(data=[go.Histogram(
        x=runtime_df['runtime'],
        nbinsx=30,
        marker_color='#e50914',
        opacity=0.8
    )])
    fig4.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        xaxis=dict(showgrid=False, title="Runtime (minutes)"),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title="Frequency"),
        title="Movie Runtime Distribution",
        showlegend=False,
        height=400,
        bargap=0.1
    )
    st.plotly_chart(fig4, config={"plotly":{ "responsive": True, "displayModeBar": False}})

def render_genre_ratings(viz_df, all_genres):
    """Render average rating by genre chart"""
    st.markdown("#### 🏆 Average Rating by Genre")
    genre_ratings = []
    for genre in all_genres:
        genre_movies = viz_df[viz_df['genres'].apply(lambda x: genre in x if isinstance(x, list) else False)]
        if len(genre_movies) > 0:
            avg_rating = genre_movies[genre_movies['rating'] > 0]['rating'].mean()
            genre_ratings.append({"Genre": genre, "Avg Rating": avg_rating})
    
    genre_ratings_df = pd.DataFrame(genre_ratings).sort_values('Avg Rating', ascending=True)
    
    fig5 = go.Figure(go.Bar(
        x=genre_ratings_df['Avg Rating'],
        y=genre_ratings_df['Genre'],
        orientation='h',
        marker=dict(
            color=genre_ratings_df['Avg Rating'],
            colorscale=[[0, '#b20710'], [0.5, '#e50914'], [1, '#ffd700']],
            showscale=False
        ),
        text=genre_ratings_df['Avg Rating'].round(2),
        textposition='auto',
    ))
    fig5.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title="Average Rating", range=[0, 10]),
        yaxis=dict(showgrid=False, title=""),
        title="Which Genres Rate Highest?",
        height=400
    )
    st.plotly_chart(fig5, config={"plotly":{ "responsive": True, "displayModeBar": False}})

def render_top_movies(viz_df):
    """Render top rated movies chart"""
    st.markdown("#### 🌟 Top Rated Movies (Sample)")
    top_movies = viz_df[(viz_df['rating'] > 0) & (viz_df['vote_count'] > 100)].nlargest(10, 'rating')[['title', 'rating', 'vote_count']]
    
    fig6 = go.Figure(data=[go.Bar(
        y=top_movies['title'][::-1],
        x=top_movies['rating'][::-1],
        orientation='h',
        marker_color='#ffd700',
        text=top_movies['rating'][::-1].round(1),
        textposition='auto',
    )])
    fig6.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title="Rating", range=[0, 10]),
        yaxis=dict(showgrid=False, title=""),
        title="Top Rated Movies",
        height=400
    )
    st.plotly_chart(fig6, config={"plotly":{ "responsive": True, "displayModeBar": False}})

def render_insights(movies_df, all_genres, viz_df):
    """Render key insights section"""
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 💡 Key Insights")
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    # Most common genre
    genre_data = []
    for genre in all_genres:
        count = len(movies_df[movies_df['tags'].str.contains(genre, case=False, na=False)])
        genre_data.append({"Genre": genre, "Count": count})
    most_common_genre = pd.DataFrame(genre_data).nlargest(1, 'Count').iloc[0]['Genre']
    
    # Best rated genre
    genre_ratings = []
    for genre in all_genres:
        genre_movies = viz_df[viz_df['genres'].apply(lambda x: genre in x if isinstance(x, list) else False)]
        if len(genre_movies) > 0:
            avg_rating = genre_movies[genre_movies['rating'] > 0]['rating'].mean()
            genre_ratings.append({"Genre": genre, "Avg Rating": avg_rating})
    genre_ratings_df = pd.DataFrame(genre_ratings)
    best_rated_genre = genre_ratings_df.nlargest(1, 'Avg Rating').iloc[0]['Genre']
    best_rating = genre_ratings_df.nlargest(1, 'Avg Rating').iloc[0]['Avg Rating']
    
    # Runtime sweet spot
    runtime_df = viz_df[(viz_df['runtime'] > 0) & (viz_df['runtime'] < 250)].copy()
    sweet_spot = runtime_df['runtime'].mode()[0] if len(runtime_df) > 0 else 0
    
    with insight_col1:
        st.info(f"**Most Popular Genre:** {most_common_genre} dominates the database with the highest number of movies.")
    
    with insight_col2:
        st.success(f"**Highest Rated Genre:** {best_rated_genre} leads with an average rating of {best_rating:.1f}⭐")
    
    with insight_col3:
        st.warning(f"**Sweet Spot Runtime:** Most movies cluster around {int(sweet_spot)} minutes duration.")

def render_visualizations(movies_df, all_genres):
    """Render all visualization charts with lazy loading"""
    st.markdown('<h3>📊 Movie Database Analytics</h3>', unsafe_allow_html=True)
    
    # Option to choose visualization depth
    viz_depth = st.radio(
        "Choose visualization detail level:",
        ["Quick Overview (Faster)", "Detailed Analysis (Slower)"],
        horizontal=True
    )
    
    sample_size = 200 if viz_depth == "Quick Overview (Faster)" else 500
    
    with st.spinner(f'Loading analytics data ({sample_size} movies sample)...'):
        viz_df = fetch_visualization_data(movies_df, sample_size)
    
    # Key Metrics
    render_key_metrics(movies_df, viz_df)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Create tabs for different visualization sections
    viz_tab1, viz_tab2, viz_tab3 = st.tabs(["📈 Distribution", "🎯 Trends", "💡 Insights"])
    
    with viz_tab1:
        # Row 1: Genre Distribution and Rating Distribution
        viz_col1, viz_col2 = st.columns(2)
        with viz_col1:
            render_genre_distribution(movies_df, all_genres)
        with viz_col2:
            render_rating_distribution(viz_df)
    
    with viz_tab2:
        # Row 2: Release Year Trends and Runtime Analysis
        viz_col3, viz_col4 = st.columns(2)
        with viz_col3:
            render_year_trends(viz_df)
        with viz_col4:
            render_runtime_distribution(viz_df)
    
    with viz_tab3:
        # Row 3: Genre vs Rating and Top Rated Movies
        viz_col5, viz_col6 = st.columns(2)
        with viz_col5:
            render_genre_ratings(viz_df, all_genres)
        with viz_col6:
            render_top_movies(viz_df)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Insights Section
        render_insights(movies_df, all_genres, viz_df)