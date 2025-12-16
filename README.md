# 🎬 CINEMATE - AI-Powered Movie Recommendation System

A sophisticated movie recommendation system built with Streamlit, featuring AI-powered recommendations, interactive visualizations, and a Netflix-inspired UI.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- **🎯 Content-Based Recommendations**: Get personalized movie suggestions using TF-IDF vectorization and cosine similarity
- **🤖 AI Chatbot**: Interactive assistant powered by OpenAI GPT-4 for natural language movie queries
- **📊 Advanced Analytics**: Comprehensive visualizations of movie trends, ratings, and genre distributions
- **🎨 Netflix-Style UI**: Modern, responsive interface with smooth animations and hover effects
- **🔍 Smart Search**: Fuzzy search with autocomplete for easy movie discovery
- **🎬 Rich Movie Details**: Trailers, cast information, ratings, and comprehensive metadata
- **⚡ Performance Optimized**: Lazy loading, caching, and parallel API calls for fast response times

## 🌐 Live Demo

**[🚀 Try the Live Application](https://movie-recommender.meetgoel.de/)**

Experience CINEMATE in action! The application is fully deployed and ready to use.

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Machine Learning**: scikit-learn (TF-IDF, Cosine Similarity)
- **AI Integration**: OpenAI GPT-4
- **Data Visualization**: Plotly
- **APIs**: TMDB API, OpenAI API
- **Data Processing**: pandas, numpy

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package manager)
- Git

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Business-Project-in-Big-Data-AI.git
cd Business-Project-in-Big-Data-AI
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install the following packages:

```bash
pip install streamlit pandas numpy scikit-learn plotly requests openai
```

### 4. Set Up API Keys

You'll need API keys from two services:

#### 4.1 TMDB API Key

1. Go to [The Movie Database (TMDB)](https://www.themoviedb.org/)
2. Create a free account
3. Navigate to Settings → API
4. Request an API key (choose "Developer" option)
5. Copy your API key

#### 4.2 OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new secret key
5. Copy your API key (you won't be able to see it again!)

#### 4.3 Configure API Keys

Open `config.py` and replace the placeholder values:

```python
# API Configuration
TMDB_API_KEY = "your_tmdb_api_key_here"

# OpenAI Configuration
OPENAI_API_KEY = "your_openai_api_key_here"
```

> ⚠️ **Important**: Never commit your API keys to GitHub! Add `config.py` to `.gitignore` or use environment variables.

### 5. Prepare Data Files

Ensure you have the required pickle files in the `pickle/` directory:
- `movies_dict.pkl` - Contains movie metadata

If these files are not present, you'll need to generate them from your movie dataset.

## 🎮 Running the Application

Once installation is complete, run the application with:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📖 Usage Guide

### Home Tab
- **Browse Movies**: Explore movies by genre with lazy loading
- **Search**: Use the search bar to find specific movies
- **Get Recommendations**: Click on any movie to see similar recommendations

### Visualizations Tab
- View comprehensive analytics about the movie database
- Choose between Quick Overview or Detailed Analysis
- Explore distribution charts, trends, and insights

### AI Recommendations Tab
- Chat with the AI assistant about movie preferences
- Ask questions like:
  - "What sci-fi movies do you recommend?"
  - "Movies similar to Inception"
  - "Best Christopher Nolan films"
  - "I want a comedy for tonight"
- Receive recommendations from both the database and external sources

## 📁 Project Structure

```
Business-Project-in-Big-Data-AI/
│
├── app.py                  # Main application entry point
├── ai_chatbot.py          # AI chatbot implementation
├── components.py          # UI components (hero, movie grid, etc.)
├── config.py              # Configuration and API keys
├── search.py              # Search functionality
├── styles.py              # Custom CSS styling
├── utils.py               # Utility functions (API calls, recommendations)
├── visualizations.py      # Data visualization components
│
├── pickle/                # Data files
│   └── movies_dict.pkl    # Movie metadata
│
└── requirements.txt       # Python dependencies
```

## 🔧 Configuration

You can customize the application by modifying `config.py`:

- **Display Settings**: Movies per row, batch sizes
- **Visualization Settings**: Sample sizes, chart heights
- **API Settings**: Timeouts, language preferences
- **UI Theme**: Netflix color scheme customization

## 🐛 Troubleshooting

### Common Issues

**Issue**: "OpenAI API key not configured"
- **Solution**: Ensure you've added your OpenAI API key to `config.py`

**Issue**: "No module named 'streamlit'"
- **Solution**: Activate your virtual environment and run `pip install -r requirements.txt`

**Issue**: Posters not loading
- **Solution**: Verify your TMDB API key is correct and you have internet connectivity

**Issue**: Slow performance
- **Solution**: Choose "Quick Overview" in Visualizations tab or reduce sample size in `config.py`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Movie data provided by [The Movie Database (TMDB)](https://www.themoviedb.org/)
- AI capabilities powered by [OpenAI](https://openai.com/)
- UI inspiration from [Netflix](https://www.netflix.com/)

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

⭐ If you find this project useful, please consider giving it a star!
