import streamlit as st
import pandas as pd
import requests
import pickle
import gdown
import os

# Google Drive File ID for movie_data.pkl
file_id = "1yR5Eru616dl54-G5OXlFhEghM19Pgv2L"
output = "movie_data.pkl"

# Ensure the file exists, otherwise download it
if not os.path.exists(output):
    try:
        st.write("Downloading movie_data.pkl from Google Drive...")
        drive_link = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(drive_link, output, quiet=False)
    except Exception as e:
        st.error(f"Failed to download movie_data.pkl. Error: {e}")

# Load the processed data and similarity matrix
try:
    with open(output, "rb") as file:
        movies, cosine_sim = pickle.load(file)
except FileNotFoundError:
    st.error("Error: The file 'movie_data.pkl' was not found. Make sure the file exists and is accessible.")
    st.stop()

# Function to get movie recommendations
def get_recommendations(title, cosine_sim=cosine_sim):
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]  # Get top 10 similar movies
    movie_indices = [i[0] for i in sim_scores]
    return movies[['title', 'movie_id']].iloc[movie_indices]

# Fetch movie poster from TMDB API
def fetch_poster(movie_id):
    api_key = 'a91225c05461f4d2027ca90443335bb5'  # Replace with your TMDB API key
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    response = requests.get(url)
    data = response.json()
    poster_path = data.get('poster_path', None)
    return f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

# Streamlit UI
st.title("Movie Recommendation System")

selected_movie = st.selectbox("Select a movie:", movies['title'].values)

if st.button('Recommend'):
    recommendations = get_recommendations(selected_movie)
    st.write("Top 10 recommended movies:")

    # Create a 2x5 grid layout
    for i in range(0, 10, 5):  # Loop over rows (2 rows, 5 movies each)
        cols = st.columns(5)  # Create 5 columns for each row
        for col, j in zip(cols, range(i, i+5)):
            if j < len(recommendations):
                movie_title = recommendations.iloc[j]['title']
                movie_id = recommendations.iloc[j]['movie_id']
                poster_url = fetch_poster(movie_id)
                with col:
                    if poster_url:
                        st.image(poster_url, width=130)
                    st.write(movie_title)
