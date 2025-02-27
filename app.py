import pickle
import streamlit as st
import requests
import gdown
import os

# --- Google Drive File ID ---
file_id = "1yR5Eru616dl54-G5OXlFhEghM19Pgv2L"
output = "movie_data.pkl"
drive_link = f"https://drive.google.com/uc?id={file_id}"

# --- Download Movie Data if Not Present ---
if not os.path.exists(output):
    st.info("Downloading movie_data.pkl from Google Drive...")
    gdown.download(drive_link, output, quiet=False)

# --- Load Data ---
try:
    with open(output, "rb") as file:
        movies, cosine_sim = pickle.load(file)
except FileNotFoundError:
    st.error("Error: Could not load movie_data.pkl. Check the file link and try again.")
    st.stop()

# --- Function to Get Movie Recommendations ---
def get_recommendations(title):
    idx = movies[movies['title'] == title].index[0]
    sim_scores = sorted(enumerate(cosine_sim[idx]), key=lambda x: x[1], reverse=True)[1:11]
    movie_indices = [i[0] for i in sim_scores]
    return movies[['title', 'movie_id']].iloc[movie_indices]

# --- Fetch Movie Poster ---
def fetch_poster(movie_id):
    api_key = 'a91225c05461f4d2027ca90443335bb5'
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    response = requests.get(url)
    data = response.json()
    return f"https://image.tmdb.org/t/p/w500{data.get('poster_path', '')}" if data.get('poster_path') else "https://i.postimg.cc/0QNxYz4V/social.png"

# --- Streamlit UI ---
st.title("Movie Recommendation System")

selected_movie = st.selectbox("Select a movie:", movies['title'].values)

if st.button('Recommend'):
    recommendations = get_recommendations(selected_movie)
    st.write("Top 10 recommended movies:")

    cols = st.columns(5)  # Two rows of 5 movies
    for i, col in enumerate(cols * 2):  # Loop over 10 movies
        if i < len(recommendations):
            movie_title = recommendations.iloc[i]['title']
            movie_id = recommendations.iloc[i]['movie_id']
            poster_url = fetch_poster(movie_id)
            with col:
                st.image(poster_url, width=130)
                st.write(movie_title)
