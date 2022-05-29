# Module
import streamlit as st
import pandas as pd


# fucntion which takes movie name and rating whcih is give by user and then according to that calcualte list of similar movies
def recommend_movies_by_movie_name_for_item_to_item_collaborative_based_helper(movie,user_rarting,movies,similarity):
    index=0
    for idx in movies.index: 
        if movies['title'][idx]==movie:
            index=movies['id'][idx]
            break
     

    # if user rating is less than 5 than all movies related to has low priority in recommendation or vice-versa
    similar_score=similarity[index]*(user_rarting-5)
    similar_score=similar_score.sort_values(ascending=False)
    return similar_score

# Function for recommendation of next k movies by movie name (collaborative based)
def recommend_movies_by_movie_name_for_item_to_item_collaborative_based(movie_list,no_of_recommendations,daily_facts,fetch_metadata_of_movie,similarity,movies):
    similar_movies=pd.DataFrame()


    for elm in movie_list:
        # find out similarity movies  for each movies rated by user
        similar_movies=similar_movies.append(recommend_movies_by_movie_name_for_item_to_item_collaborative_based_helper( elm['name'],elm['rating'],movies,similarity),ignore_index=True)

    # sum them all and sort them into a list in descending order
    similar_movies=similar_movies.sum().sort_values(ascending=False)
    similar_movies=list(similar_movies.index)
    
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

        # inject a fun fact text
        fact_string=daily_facts()
        daily_fact_container=st.empty()
        if fact_string!=-1:
            daily_fact_container.write("FACT :"+"\n\n"+fact_string)

    # fetching all movise metadata one by one       
    for id in similar_movies:
        if(counter==no_of_recommendations+1):
            # if counter becomes equal to no of recommendations+1 then it comes out of for loop
            break
        title,path,text,metadata_of_movie=(fetch_metadata_of_movie(id))
        movie_posters.append(path)
        recommended_movies.append(title)
        text_strings.append(text)
        counter=counter+1

    # remove loader , loader text and daily fact container (whcih contains daily fact text)
    loader.empty()
    loding_text.empty()
    daily_fact_container.empty()

    return recommended_movies,movie_posters,text_strings