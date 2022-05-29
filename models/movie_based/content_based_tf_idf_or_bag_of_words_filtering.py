import streamlit as st


    
# Function for recommendation of next k movies by movie name (content based)
def recommend_movies_by_movie_name_for_content_based(movie_name,no_of_movies,movies,daily_facts,fetch_metadata_of_movie,fetch_trailer,similarity):

    # At first index is 0( index will store index of movie name selected by user in movie directory)
    index=0
    
    # iterate movue directory and finding tmbdId when title match with movie_name
    for idx in movies.index: 
        if movies['title'][idx]==movie_name:
            index=idx
            break
    
     

    # finding all vectors and sort them in increasing order of cosine angle between them 
    nearest_vectors = sorted(list(enumerate(similarity[index])),reverse=True,key = lambda x: x[1])
    recommended_movies=[]
    movie_posters = []
    text_strings=[]

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
   
    counter=0
    
    # fetching all movise metadata one by one  
    for i in nearest_vectors[0:no_of_movies+2]:
        movie_id = movies['id'][i[0]]
        title,path,text,metadata_of_movie=(fetch_metadata_of_movie(movie_id))
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

    # impliment two columns grid container with ration 1:1
    col1,col2=st.columns([1,1])
    with col1:
        # inject first movie image 
        st.image(first_movie_path)

    with col2:  

        # inject first movie metadata
        st.title(first_movie_title)
        st.markdown('<h4>Overview</h4>',unsafe_allow_html=True)
        st.markdown('<i>{}</i>'.format(first_movie_metadata['tagline']),unsafe_allow_html=True)
        st.markdown('<p>{}</p>'.format(first_movie_metadata['description']),unsafe_allow_html=True)
        st.markdown('<b>Rating : </b><span>{}</span>'.format(first_movie_metadata['rating']),unsafe_allow_html=True)
        st.progress(int(first_movie_metadata['rating']*10))
        st.markdown('<b>Release Date : </b><span>{}</span>'.format(first_movie_metadata['release_date']),unsafe_allow_html=True)
        st.write("Click here for [Trailer]({})".format(fetch_trailer(movie_name)))
        for elm in first_movie_metadata['genres']:
            st.info(elm['name'])

        
        
        
    st.success('Recommended movies for you')
        
    return recommended_movies,movie_posters,text_strings
