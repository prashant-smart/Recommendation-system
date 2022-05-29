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



# importing models 
from models.movie_based.content_based_tf_idf_or_bag_of_words_filtering import recommend_movies_by_movie_name_for_content_based
from models.movie_based.Item_Item_collaborative_filtering import recommend_movies_by_movie_name_for_item_to_item_collaborative_based
from models.movie_based.kth_nearest_neighbour import recommend_movies_by_movie_name_for_k_Nearest_Neighbor

from models.genres_based.genres_based_filtering import recommend_movies_by_genres_name

from models.person_based.person_based_filtering import recommend_movies_by_cast_name





# function to genrates daily facts (this is because user have to wait unitl all posters are fetched and in that period of time user can read fun facts) 
def daily_facts():
    limit = 1
    api_url = 'https://api.api-ninjas.com/v1/facts?limit={}'.format(limit)
    response = requests.get(api_url, headers={'X-Api-Key': 'mo3xJ0PIXgIZb4Cv2T/QPA==7Y85a7L0BKhjVkb2'})
    if response.status_code == requests.codes.ok:
        data=(ast.literal_eval(response.text)[0]['fact']) 
        return data
    return -1

# function for fetching trailer
def fetch_trailer(movie_name):
        # finding movie id from movie name
        movie_id=0
        for idx in movies.index: 
            if movies['title'][idx]==movie_name:
                movie_id=movies['id'][idx]
                break
        # tmbd url for get requests
        url = "https://api.themoviedb.org/3/movie/{}/videos?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
        data = requests.get(url)    
        data = data.json()
        data_list=data['results']
        key=""
        for i in data_list:
            if i['type']=="Trailer":
                key=i['key']
        if key=="":
            return ""
        trailer ="https://www.youtube.com/watch?v={}".format(key)
        return trailer

# Fetch metadata of movie from API 
def fetch_metadata_of_movie(movie_id):
    # tmbd url for get requests
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




    



# fucntion which is used to generate cards for movies
def generate_cards(name,no_of_movies,type,algo_type):
    
    if type=="Movie based":
        
        if algo_type=='Item-Item Collaborative Based':
            movies_Names,movies_Poster,text_strings=recommend_movies_by_movie_name_for_item_to_item_collaborative_based(movies_rating,no_of_movies,daily_facts,fetch_metadata_of_movie,item_collaborative_sim_mat,movies)

        elif algo_type=='K Nearest Neighbor (Item Based)':
             movies_Names,movies_Poster,text_strings=recommend_movies_by_movie_name_for_k_Nearest_Neighbor(name,no_of_movies,movies_metadata_for_k_nearest_neighbor_recommendation,daily_facts,k_nearest_neighbor_recommendation_with_movies_id,fetch_metadata_of_movie)

        elif algo_type=='Content Based (Bag Of Words)':
             movies_Names,movies_Poster,text_strings=recommend_movies_by_movie_name_for_content_based(name,no_of_movies,movies,daily_facts,fetch_metadata_of_movie,fetch_trailer,bag_of_words_sim_mat)
        else:
            movies_Names,movies_Poster,text_strings=recommend_movies_by_movie_name_for_content_based(name,no_of_movies,movies,daily_facts,fetch_metadata_of_movie,fetch_trailer,tf_idf_sim_mat)

    elif type=="genres based":
        movies_Names,movies_Poster,text_strings=recommend_movies_by_genres_name(name,no_of_movies,genres_with_movieId,daily_facts,fetch_metadata_of_movie)

    else :
        movies_Names,movies_Poster,text_strings=recommend_movies_by_cast_name(name,no_of_movies,daily_facts,cast_with_movieId,movies,tf_idf_sim_mat,fetch_metadata_of_movie)

    counter=0

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

    slected_opt="nan"
    global option_for_algo_type
    option_for_algo_type=None
    if category_opt==category[1]:

        # select box for sleceting algorithm type
        option_for_algo_type = st.selectbox(
        'Select Searching Algorithm',
        ['Content Based (TF-IDF)','Content Based (Bag Of Words)','Item-Item Collaborative Based','K Nearest Neighbor (Item Based)'])
        
        global similarity
        global movies_rating
        # global slected_opt
        
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
        # global slected_opt
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
    

        

