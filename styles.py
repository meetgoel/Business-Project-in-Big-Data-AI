import streamlit as st

def apply_custom_styles():
    """Apply Netflix-style custom CSS with performance optimizations"""
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto:wght@300;400;700&display=swap');

/* -----------------------------
   App Background & Fonts
----------------------------- */
.stApp {
    background: linear-gradient(to bottom, #000000 0%, #141414 50%, #000000 100%);
    color: white;
    font-family: 'Roboto', sans-serif;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* -----------------------------
   Netflix-style Title
----------------------------- */
.netflix-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 70px;
    color: #e50914;
    text-align: center;
    font-weight: bold;
    margin-bottom: 30px;
    text-shadow: 0 0 20px rgba(229, 9, 20, 0.8), 0 0 40px rgba(229, 9, 20, 0.4);
    animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
    from { text-shadow: 0 0 20px rgba(229, 9, 20, 0.8), 0 0 40px rgba(229, 9, 20, 0.4); }
    to { text-shadow: 0 0 30px rgba(229, 9, 20, 1), 0 0 60px rgba(229, 9, 20, 0.6); }
}

/* -----------------------------
   Search Bar
----------------------------- */
.stTextInput > div > div > input {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
    border: 2px solid rgba(229, 9, 20, 0.5);
    border-radius: 25px;
    padding: 15px 25px;
    font-size: 18px;
    transition: all 0.3s ease;
}

.stTextInput > div > div > input:focus {
    border-color: #e50914;
    box-shadow: 0 0 20px rgba(229, 9, 20, 0.5);
    background-color: rgba(255, 255, 255, 0.15);
}

/* -----------------------------
   Genre Section Headers
----------------------------- */
h3 {
    color: white;
    font-size: 28px;
    font-weight: 700;
    margin: 60px 0 30px 0;
    padding-left: 10px;
    border-left: 4px solid #e50914;
    text-transform: uppercase;
    letter-spacing: 2px;
}

/* Subheaders */
.stSubheader {
    color: white !important;
    font-size: 32px !important;
    font-weight: 700 !important;
    margin-bottom: 20px !important;
}

/* -----------------------------
   Poster Container
----------------------------- */
.poster-container {
    position: relative;
    overflow: hidden;
    border-radius: 8px;
    cursor: pointer;
    text-decoration: none;
    display: block;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    will-change: transform;
    margin-bottom: 20px; /* Gap between poster and button */
}

/* Poster image */
.poster-container img {
    width: 100%;
    transition: transform 0.3s ease;
    display: block;
    will-change: transform;
}

/* Poster hover effect */
.poster-container:hover {
    transform: scale(1.05) translateY(-5px);
    box-shadow: 0 15px 40px rgba(229, 9, 20, 0.6), 0 0 30px rgba(229, 9, 20, 0.4);
    z-index: 10;
}

.poster-container:hover img {
    transform: scale(1.05);
}

/* Overlay */
.poster-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.95) 0%, rgba(0, 0, 0, 0.7) 50%, transparent 100%);
    color: white;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: flex-start;
    opacity: 0;
    transition: opacity 0.3s ease;
    text-align: left;
    padding: 20px;
}

.poster-container:hover .poster-overlay {
    opacity: 1;
}

.poster-overlay h4 {
    font-size: 18px;
    font-weight: 700;
    margin: 0 0 10px 0;
    color: white;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
}

.poster-overlay p {
    font-size: 14px;
    margin: 5px 0;
    color: #ffd700;
}

/* Genre badges */
.genre-badge {
    display: inline-block;
    background: linear-gradient(135deg, #e50914, #b20710);
    color: white;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 11px;
    margin: 2px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* -----------------------------
   Netflix-style Buttons
----------------------------- */
.stButton > button {
    background: linear-gradient(90deg, #e50914, #f6121d);
    color: white;
    border: none;
    border-radius: 30px;
    padding: 14px 36px;
    font-size: 18px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 6px 20px rgba(229, 9, 20, 0.5);
    margin-top: 15px; /* Gap between poster and button */
}

.stButton > button:hover {
    background: linear-gradient(90deg, #ff0a1a, #e50914);
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(229, 9, 20, 0.7);
}

/* -----------------------------
   Hero Section
----------------------------- */
.hero-section {
    position: relative;
    height: 500px;
    background: linear-gradient(rgba(0,0,0,0.4), rgba(20,20,20,0.9)), url('https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1920&h=500&fit=crop');
    background-size: cover;
    background-position: center;
    border-radius: 10px;
    margin-bottom: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    text-align: center;
    padding: 40px;
}

.hero-title {
    font-size: 48px;
    font-weight: 700;
    color: white;
    text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.9);
    margin-bottom: 20px;
}

.hero-subtitle {
    font-size: 20px;
    color: rgba(255, 255, 255, 0.9);
    text-shadow: 1px 1px 4px rgba(0, 0, 0, 0.8);
}

/* Star rating */
.star-rating {
    color: #ffd700;
    font-size: 16px;
    text-shadow: 0 0 5px rgba(255, 215, 0, 0.5);
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 20px;
    background-color: transparent;
}

.stTabs [data-baseweb="tab"] {
    background-color: rgba(255, 255, 255, 0.05);
    color: white;
    border-radius: 10px;
    padding: 15px 30px;
    font-size: 18px;
    font-weight: 600;
    border: 2px solid transparent;
    transition: all 0.3s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: rgba(229, 9, 20, 0.2);
    border-color: rgba(229, 9, 20, 0.5);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #e50914, #b20710) !important;
    border-color: #e50914 !important;
}

/* Selectbox styling */
.stSelectbox > div > div {
    background-color: rgba(255, 255, 255, 0.1);
    color: white;
    border: 2px solid rgba(229, 9, 20, 0.5);
    border-radius: 10px;
}

/* Spinner styling */
.stSpinner > div {
    border-top-color: #e50914 !important;
}

/* Expander styling */
.streamlit-expanderHeader {
    background-color: rgba(229, 9, 20, 0.1);
    border-radius: 10px;
    color: white;
}

.streamlit-expanderHeader:hover {
    background-color: rgba(229, 9, 20, 0.2);
}

/* Performance optimizations */
* {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

img {
    image-rendering: -webkit-optimize-contrast;
}
</style>
""", unsafe_allow_html=True)
