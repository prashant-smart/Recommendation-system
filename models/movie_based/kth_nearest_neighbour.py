# Module
import streamlit as st


# Function for recommendation of next k movies by listmovie name (Kth Nearest Neighbor)
def recommend_movies_by_movie_name_for_k_Nearest_Neighbor(movie_name,no_of_movies,movies_metadata_for_k_nearest_neighbor_recommendation,daily_facts,k_nearest_neighbor_recommendation_with_movies_id,fetch_metadata_of_movie):
    index_of_movie=0
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

    # finding  index of the movie in movie dictonary
    for idx in movies_metadata_for_k_nearest_neighbor_recommendation.index: 
        if movies_metadata_for_k_nearest_neighbor_recommendation['title'][idx]==movie_name:
            index_of_movie=movies_metadata_for_k_nearest_neighbor_recommendation['id'][idx]
            break
    list_of_recommended_movies=[]

    # iterate over all movies id  which is in pair  of index and list of index , if first elment is equal to index_of_movie then its second elm is the list of movies is going to be recommended to user
    for pairs in k_nearest_neighbor_recommendation_with_movies_id:
        if pairs[0]==str(index_of_movie):
            for movie_id in pairs[1]:
                list_of_recommended_movies.append(movie_id)

    # container for movies poster path , recommended movies title and overview text
    recommended_movies=[]
    movie_posters = []
    text_strings=[]
    counter=0

    # interate over all movie ids
    for i in range(0,no_of_movies+1):
        title,path,text,metadata_of_movie=(fetch_metadata_of_movie(list_of_recommended_movies[i]))
        if counter==0:
            # this contains fist movise metadata
            first_movie_title=title
            first_movie_path=path
            first_movie_metadata=metadata_of_movie
            counter+=1
            continue
        movie_posters.append(path)
        recommended_movies.append(title)
        text_strings.append(text)
    
    loader.empty()
    loding_text.empty()
    daily_fact_container.empty()

    # first movie before recommendation 
    st.title(first_movie_title)

    # impliment two columns grid container with ration 1:1
    col1,col2=st.columns([1,1])
    with col1:
        st.image(first_movie_path)
    with col2:   
        st.markdown('<h3>Overview</h3>',unsafe_allow_html=True)
        st.markdown('<i>{}</i>'.format(first_movie_metadata['tagline']),unsafe_allow_html=True)
        st.markdown('<p>{}</p>'.format(first_movie_metadata['description']),unsafe_allow_html=True)
        st.markdown('<b>Rating : </b><span>{}</span>'.format(first_movie_metadata['rating']),unsafe_allow_html=True)
        st.progress(int(first_movie_metadata['rating']*10))
        st.markdown('<b>Release Date : </b><span>{}</span>'.format(first_movie_metadata['release_date']),unsafe_allow_html=True)
        for elm in first_movie_metadata['genres']:
            st.info(elm['name'])

    st.success('Recommended movies for you')
        
    return recommended_movies,movie_posters,text_strings