import streamlit as st
import pickle
import pandas as pd
import requests
movies_dict = pickle.load(open('./assets/data/movies.pkl','rb'))
similarity = pickle.load(open('./assets/data/similarity.pkl','rb'))
movies=pd.DataFrame(movies_dict) 

import time
import sys



# Fetch poster from API
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=b8fda3e150ab7fcabe257624516ee5f3&language=en-US".format(movie_id)
    data = requests.get(url)

    #long process here
    data = data.json()
    path = data['poster_path']
    poster_path = "https://image.tmdb.org/t/p/w500/" + path
    return poster_path

# Function for recommendation of next 5 movies
def recommend_next_5_Movies(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])),reverse=True,key = lambda x: x[1])
    recommend_movies=[]
    movie_posters = []
    for i in distances[0:7]:
        movie_id = movies.iloc[i[0]].id
        recommend_movies.append(movies.iloc[i[0]].title)
        movie_posters.append(fetch_poster(movie_id))
    return recommend_movies,movie_posters


def load_view():
    
    st.title("See what's Next")
    option = st.selectbox(
     'How would you like to be search?',
     movies['title'].values)
    if st.button('Search'):
        #structure of cards 
        movies_Names,movies_Poster=recommend_next_5_Movies(option)
        col1, col2, col3, col4, col5,col6 = st.columns(6)
        with col1:
            st.text(movies_Names[0])
            st.image(movies_Poster[0])
        with col2:
            st.text(movies_Names[1])
            st.image(movies_Poster[1])

        with col3:
            st.text(movies_Names[2])
            st.image(movies_Poster[2])
        with col4:
            st.text(movies_Names[3])
            st.image(movies_Poster[3])
        with col5:
            st.text(movies_Names[4])
            st.image(movies_Poster[4])
        with col6:
            st.text(movies_Names[5])
            st.image(movies_Poster[5])

