import streamlit as st
import pickle
import pandas as pd
import requests

movies_dict = pickle.load(open('./assets/data/movies.pkl','rb'))
similarity = pickle.load(open('./assets/data/similarity.pkl','rb'))
cast_with_avgrating=pickle.load(open('./assets/data/cast_avgrating.pkl','rb'))
crew_names=pickle.load(open('./assets/data/crew_names.pkl','rb'))
movies=pd.DataFrame(movies_dict) 

# Fetch poster from API 
def fetch_poster_and_title(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=b8fda3e150ab7fcabe257624516ee5f3&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_title=data['original_title']
    path = data['poster_path']
    poster_path = "https://image.tmdb.org/t/p/w500/" + path
    return poster_title,poster_path


# Function for recommendation of next k movies by crew name
def recommend_movies_by_crew_name(crew_name,no_of_recommendations):
    movies_list=cast_with_avgrating[crew_name]
    movies_list=movies_list.sort_values(ascending=False)
    movie_posters=[]
    recommended_movies=[]
    counter=0
    loader=st.image('./assets/gif/96x96.gif')
    loding_text=st.text("loading.....")
    for i in movies_list.index:
        if(counter==no_of_recommendations+1):
            break
        title,path=(fetch_poster_and_title(i))
        movie_posters.append(path)
        recommended_movies.append(title)
        counter=counter+1
    loader.empty()
    loding_text.empty()
    return recommended_movies,movie_posters


# Function for recommendation of next k movies by movie name
def recommend_movies_by_movie_name(movie,no_of_movies):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])),reverse=True,key = lambda x: x[1])
    recommended_movies=[]
    movie_posters = []
    loader=st.image('./assets/gif/96x96.gif')
    loding_text=st.text("loading.....")
    for i in distances[0:no_of_movies+1]:
        movie_id = movies.iloc[i[0]].id
        title,path=(fetch_poster_and_title(movie_id))
        movie_posters.append(path)
        recommended_movies.append(title)
    loader.empty()
    loding_text.empty()
    return recommended_movies,movie_posters

def generate_cards(name,no_of_movies,type):
    if type=="Movie based":
        movies_Names,movies_Poster=recommend_movies_by_movie_name(name,no_of_movies)
    else :
        movies_Names,movies_Poster=recommend_movies_by_crew_name(name,no_of_movies)

    counter=0
    for i in range(1, no_of_movies+1):
        if i%5==1:
            col = st.columns(5)
            counter=0
        with col[counter]:
            st.text(movies_Names[i-1])
            st.image(movies_Poster[i-1])
            counter=counter+1
def load_view():
    st.title("See what's Next")
    category = ['--Select--', 'Movie based', 'Person based(Crew Member)']
    category_opt = st.selectbox('Select Recommendation Type', category)
    if category_opt==category[1]:
        option = st.selectbox(
        'How would you like to be search?',
        movies['title'].values)
    else:
        option = st.selectbox(
        'How would you like to be search?',
        crew_names)
    
    no_of_movies = st.slider('Number of movies you want Recommended:', min_value=5, max_value=20, step=1)
    if st.button('Search'):
        # st.text()
        if category_opt!='--Select--' :
            generate_cards(option,no_of_movies,category_opt)
        else:
            st.warning('Please Select First Recommendation Type')

        

