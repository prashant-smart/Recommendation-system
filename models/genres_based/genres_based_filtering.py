import streamlit as st
import pandas as pd




# Function for recommendation of next k movies by genres name
def recommend_movies_by_genres_name(genres_name,no_of_recommendations,genres_with_movieId,daily_facts,fetch_metadata_of_movie):

    # this container all movies wchih is under a specific genres
    moviesIds_list=genres_with_movieId[genres_name]

    # sort all then movies according to ratings
    moviesIds_list=moviesIds_list.sort_values(ascending=False)

    # container for movies poster path , recommended movies title and overview text
    movie_posters=[]
    recommended_movies=[]
    text_strings=[]
    counter=0

    # create a columns grid continer of ratio 1:3
    loading_column,daily_fact_column=st.columns([1,3])

    with loading_column:
        # inject a loader and loading text
        loader=st.image('./assets/gif/loading_gif.gif')
        loding_text=st.text("loading.....")
    with daily_fact_column:

        # inject fun fact text
        fact_string=daily_facts()
        daily_fact_container=st.empty()
        if fact_string!=-1:
            daily_fact_container.write("FACT :"+"\n\n"+fact_string)

    # fetching all movise metadata one by one      
    for idx in moviesIds_list.index:
        if(counter==no_of_recommendations+1):
            break
        title,path,text,metadata_of_movie=(fetch_metadata_of_movie(idx))
        movie_posters.append(path)
        recommended_movies.append(title)
        text_strings.append(text)
        counter=counter+1

    # remove loader , loader text and daily fact container (whcih contains daily fact text)
    loader.empty()
    loding_text.empty()
    daily_fact_container.empty()

    return recommended_movies,movie_posters,text_strings
