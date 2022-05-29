import streamlit as st
import pandas as pd


# fucntion for convert string to hash and return unique items ( like sets in cpp stl )
def f7_noHash(seq):
    seen = set()
    return [ x for x in seq if str( x ) not in seen and not seen.add( str( x ) )]

# Function for recommendation of next k movies by cast name
def recommend_movies_by_cast_name(cast_name,no_of_recommendations,daily_facts,cast_with_movieId,movies,tf_idf_sim_mat,fetch_metadata_of_movie):
    # this contains list of movies has high rating 
    list_of_highest_rating_movies=[]

    # this contains title and tmdbId of first movie which is recommended to user
    first_movie_id=''
    first_movie_title=''

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
    
    # iteration for take out all movies (sorted according to average ratings ) in whcih person( lead actors and director ) is casted 
    
    for idx in (cast_with_movieId[cast_name].sort_values(ascending=False)).index:
        
        # if values is 0.0 means person is not casted in that movie so in this case user get recommendations according to first high rated movie (which tmbdId sotre in first_movie_id)
        if cast_with_movieId[cast_name][idx]==0.0:
            for i in movies.index:
                # finding first movie for title
                if(movies['id'][i]==first_movie_id):
                    first_movie_title=movies['title'][i]
                    break
            index=0
            for idx in movies.index: 
                # finding index of first movie title
                if movies['title'][idx]==first_movie_title:
                    index=idx
                    break
            # it contains list of vector whcih having smallest cosine diffrence between them (i.e nearest vectors to first movie)
            nearest_vectors = sorted(list(enumerate(tf_idf_sim_mat[index])),reverse=True,key = lambda x: x[1])

            # this contains tmbdId of nearest vectors
            list_of_movies=[]
            for i in nearest_vectors:
                list_of_movies.append(movies['id'][i[0]] )

            # merge all list to one list
            list_of_highest_rating_movies+=list_of_highest_rating_movies+list_of_movies[1:]

            # filter out unique movies tmbdIds 
            list_of_highest_rating_movies=f7_noHash(list_of_highest_rating_movies)
            break
        else:
            if len(list_of_highest_rating_movies)==0:
                first_movie_id= idx

            # append all movies which having non zero values
            list_of_highest_rating_movies.append(idx)

    # container for movies poster path , recommended movies title and overview text
    movie_posters=[]
    recommended_movies=[]
    text_strings=[]

    counter=0
    # fetching all movise metadata one by one
    for i in list_of_highest_rating_movies:
        if(counter==no_of_recommendations+1):
            break
        title,path,text,metadata_of_movie=(fetch_metadata_of_movie(i))
        movie_posters.append(path)
        recommended_movies.append(title)
        text_strings.append(text)
        counter=counter+1

    # remove loader , loader text and daily fact container (whcih contains daily fact text)
    loader.empty()
    loding_text.empty()
    daily_fact_container.empty()

    return recommended_movies,movie_posters,text_strings
