# Modules
import streamlit as st
import pickle
import pandas as pd
import requests
import ast


# it contains list of movies whcih is selected by user and also contains rating with respect to each movie rated by user
movies_rating=[]

# import movies dictionary and convert into data frame
movies_dict = pickle.load(open('./assets/data/movies.pkl','rb'))
movies=pd.DataFrame(movies_dict) 

# this is 0 when user don't want poster to be fetch or 1 means user want to fetch movie poster
isPosterFetch=0

# importing files related to genres based search
genres_with_movieId=pickle.load(open('./assets/data/genres_rating.pkl','rb'))
genres_name=pickle.load(open('./assets/data/genres_name.pkl','rb'))

# importing files related to cast based search
cast_with_movieId=pickle.load(open('./assets/data/cast_rating.pkl','rb'))
cast_names=pickle.load(open('./assets/data/cast_names.pkl','rb'))

# importing files related to content based search
tf_idf_sim_mat=pickle.load(open('./assets/data/tf_idf_sim_mat.pkl','rb'))
bag_of_words_sim_mat=pickle.load(open('./assets/data/bag_of_words_sim_mat.pkl','rb'))

# importing files related to item-item collaboratoive based search
item_collaborative_sim_mat=pickle.load(open('./assets/data/item_item_collaborative_sim_mat.pkl','rb'))

# importing files related to Kth Nearest Neighbors based search
k_nearest_neighbor_recommendation_with_movies_id=pickle.load(open('./assets/data/movieId_with_recommedations_kNearestNeighbor.pkl','rb'))
movies_metadata_for_k_nearest_neighbor_recommendation=pickle.load(open('./assets/data/movies_for_kNearestNeighbor.pkl','rb'))

# by default tf_idf_sim_mat is selected as similarity matrix 
similarity=tf_idf_sim_mat


# function to genrates daily facts (this is because user have to wait unitl all posters are fetched and in that period of time user can read fun facts) 
def daily_facts():
    limit = 1
    api_url = 'https://api.api-ninjas.com/v1/facts?limit={}'.format(limit)
    response = requests.get(api_url, headers={'X-Api-Key': 'mo3xJ0PIXgIZb4Cv2T/QPA==7Y85a7L0BKhjVkb2'})
    if response.status_code == requests.codes.ok:
        data=(ast.literal_eval(response.text)[0]['fact']) 
        return data
    print(response.text[0])
    return -1

# Fetch metadata of movie from API 
def fetch_metadata_of_movie(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=b8fda3e150ab7fcabe257624516ee5f3&append_to_response=videos".format(movie_id)

    res = requests.get(url)
    data = res.json()
    res.close()

    # Destructuring valuable related data from array
    poster_title=data['title']
    path = data['poster_path']
    description=data['overview']
    release_date=data['release_date']
    isAdult=data['adult']
    rating=data['vote_average']

    metadata_of_movie={"genres":data['genres'],
                        "tagline":data['tagline'],
                        "rating":rating,
                        "description":data['overview'],
                        "release_date":release_date
                        }
    genres_string=""
    for genre in data['genres']:
        genres_string+=genre['name']+", "
    genres_string=genres_string[:len(genres_string)-2]

    # string which is used to show overview of a movie
    text_overview=description+"\n\n"+"Genres : "+genres_string+"\n\n"+"Rating : "+str(rating)+"\n\n"+"Release Date : "+str(release_date)

    # if movie is 18+ rated then show disclaimer 
    if isAdult==True:
        text=text+"\n\n"+"DISCLAIMER : This is 18+ Rated movie"
    
    # if user don't want any image then at the place of poster users get to see a low quality image (which indicates ther is no image)
    if isPosterFetch:
        poster_path = "https://image.tmdb.org/t/p/w500/" + str(path)
    else:
        poster_path='./assets/images/noimage.png'

    # return poster_title(title of movie) , psoter path , text for overview
    return poster_title,poster_path,text_overview,metadata_of_movie

# fucntion for convert string to hash and return unique items ( like sets in cpp stl )
def f7_noHash(seq):
    seen = set()
    return [ x for x in seq if str( x ) not in seen and not seen.add( str( x ) )]

# Function for recommendation of next k movies by cast name
def recommend_movies_by_cast_name(cast_name,no_of_recommendations):
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

# Function for recommendation of next k movies by genres name
def recommend_movies_by_genres_name(genres_name,no_of_recommendations):

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

# fucntion which takes movie name and rating whcih is give by user and then according to that calcualte list of similar movies
def recommend_movies_by_movie_name_for_item_to_item_collaborative_based_helper(movie,user_rarting):
    index=0
    for idx in movies.index: 
        if movies['title'][idx]==movie:
            index=movies['id'][idx]
            break
    global similarity

    # if user rating is less than 5 than all movies related to has low priority in recommendation or vice-versa
    similar_score=similarity[index]*(user_rarting-5)
    similar_score=similar_score.sort_values(ascending=False)
    return similar_score

# Function for recommendation of next k movies by movie name (collaborative based)
def recommend_movies_by_movie_name_for_item_to_item_collaborative_based(movie_list,no_of_recommendations):
    similar_movies=pd.DataFrame()


    for elm in movie_list:
        # find out similarity movies  for each movies rated by user
        similar_movies=similar_movies.append(recommend_movies_by_movie_name_for_item_to_item_collaborative_based_helper(elm['name'],elm['rating']),ignore_index=True)

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
    
# Function for recommendation of next k movies by movie name (content based)
def recommend_movies_by_movie_name_for_content_based(movie_name,no_of_movies):

    # At first index is 0( index will store index of movie name selected by user in movie directory)
    index=0
    
    # iterate movue directory and finding tmbdId when title match with movie_name
    for idx in movies.index: 
        if movies['title'][idx]==movie_name:
            index=idx
            break
    
    global similarity

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
    st.title(first_movie_title)
    with col1:
        # inject first movie image 
        st.image(first_movie_path)

    with col2:  

        # inject first movie metadata
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

    
# Function for recommendation of next k movies by listmovie name (Kth Nearest Neighbor)
def recommend_movies_by_movie_name_for_k_Nearest_Neighbor(movie_name,no_of_movies):
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


# fucntion which is used to generate cards for movies
def generate_cards(name,no_of_movies,type,algo_type):
    if type=="Movie based":
        
        if algo_type=='Item-Item Collaborative Based':
            movies_Names,movies_Poster,text_strings=recommend_movies_by_movie_name_for_item_to_item_collaborative_based(movies_rating,no_of_movies)

        elif algo_type=='K Nearest Neighbor (Item Based)':
            movies_Names,movies_Poster,text_strings=recommend_movies_by_movie_name_for_k_Nearest_Neighbor(name,no_of_movies)

        else:
             movies_Names,movies_Poster,text_strings=recommend_movies_by_movie_name_for_content_based(name,no_of_movies)

    elif type=="genres based":
        movies_Names,movies_Poster,text_strings=recommend_movies_by_genres_name(name,no_of_movies)

    else :
        movies_Names,movies_Poster,text_strings=recommend_movies_by_cast_name(name,no_of_movies)

    counter=0

    # iterate over all movies and generate cards
    for i in range(1, no_of_movies+1):
        if i%5==1:
            col = st.columns(5)
            counter=0
        with col[counter]:
            st.text(movies_Names[i-1])
            st.image(movies_Poster[i-1])
            expander = st.expander("Read More")
            expander.write(text_strings[i-1])
            counter=counter+1

# it is main fucntion which call after user nvigate to homepage
def load_view():
    st.title("See what's Next")

    category = ['--Select--', 'Movie based', 'Person based(cast Member)','genres based']

    # select box for sleceting category
    category_opt = st.selectbox('Select Recommendation Type', category)

    global slected_opt
    global option_for_algo_type
    option_for_algo_type=None
    if category_opt==category[1]:

        # select box for sleceting algorithm type
        option_for_algo_type = st.selectbox(
        'Select Searching Algorithm',
        ['Content Based (TF-IDF)','Content Based (Bag Of Words)','Item-Item Collaborative Based','K Nearest Neighbor (Item Based)'])
        
        global similarity
        global movies_rating
        
        if option_for_algo_type=="Content Based (Bag Of Words)":

            # set bag_of_words_sim_mat as similarity
            similarity=bag_of_words_sim_mat

            # select box for sleceting movies
            slected_opt = st.selectbox(
            'How would you like to be search?',
            movies['title'].values)

            movies_rating.clear()

        elif option_for_algo_type=="Item-Item Collaborative Based":
            
            # muliselect box for selecting multiple movies
            movies_selected_by_user=st.sidebar.multiselect(label="Select Your Favorite Movies",options=movies['title'])
            
            # if movies selected by user then clear movies_rating 
            if len(movies_selected_by_user)==0:
                movies_rating.clear()
            
            # if movies movies selected by user not equal to movies rating, then reiterate and whole list and update movies_rating
            if len(movies_selected_by_user)!=len(movies_rating):
                new_list=[]
                for idx in range (0,len(movies_selected_by_user)):
                    for i in range(0,len(movies_rating)):
                        if(movies_selected_by_user[idx]==movies_rating[i]['name']):
                            new_list.append(movies_rating[i])
                movies_rating=new_list 

            if movies_selected_by_user:

                # input box for rating given by user to each movies
                rating_by_user = st.sidebar.selectbox(
                'How You Rate {}?'.format(movies_selected_by_user[-1]),
                (1,2,3,4,5,6,7,8,9,10)
                )
                
                # if user rate any movie
                if rating_by_user:

                    isCurrentMoviePresent=0
                    # iterate over each movies in movies_rating and where name is match then update its ratings
                    for elm in movies_rating:
                        if elm['name']==movies_selected_by_user[-1]:
                            isCurrentMoviePresent=1
                            elm['rating']=rating_by_user
                            break
                    if isCurrentMoviePresent==0:
                        # if target movies not present in movies_rating 
                        movies_rating.append({'name':movies_selected_by_user[-1],'rating':rating_by_user})

            # print favorite Movies
            st.sidebar.write('Your Favorite Movies:', movies_rating)

            # set similaritem_collaborative_sim_mat as similarity 
            similarity=item_collaborative_sim_mat

        elif option_for_algo_type=="K Nearest Neighbor (Item Based)":

            # select box for selecting movies
            slected_opt=st.selectbox(label="Select Your Favorite Movies",options=set(movies_metadata_for_k_nearest_neighbor_recommendation['title']))
            movies_rating.clear()
        else :
            movies_rating.clear()
            
            # select box for selecting movies
            slected_opt = st.selectbox(
            'How would you like to be search?',
            movies['title'].values)
            
            # set tf_idf_sim_mat as similarity 
            similarity=tf_idf_sim_mat

    elif category_opt==category[2]:

        movies_rating.clear()

        # select box for selecting movies
        slected_opt = st.selectbox(
        'How would you like to be search?',
        cast_names)
    else:

        movies_rating.clear()

        # select box for selecting movies
        slected_opt = st.selectbox(
        'How would you like to be search?',
        genres_name)

    global isPosterFetch

    # checkbox for confirmation of fecting of posters
    isPosterFetch = st.checkbox('Do You Want Poster (⚠️ It takes some time to fetch poster )')

    #  slider for selcting number of recommendations user wants
    no_of_movies = st.slider('Number of movies you want Recommended:', min_value=5, max_value=20, step=1)

    if st.button('Search'):
        if category_opt!='--Select--' :
            if category_opt=='Movie based' and option_for_algo_type=='Item-Item Collaborative Based' :

                # when algorithm tpye is Item-Item Collaborative Based then user get recommendation only when user rate atleast two movies
                if len(movies_rating)<2:
                   st.warning('Please Select At-least 2 Movies (❗Select movies from sidebar)') 
                else:
                    generate_cards(slected_opt,no_of_movies,category_opt,option_for_algo_type)
            else:
                generate_cards(slected_opt,no_of_movies,category_opt,option_for_algo_type)
        else:
            st.warning('Please Select First Recommendation Type')
    

        

