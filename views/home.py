
from importlib.metadata import metadata
from math import e
import streamlit as st
import pickle
import pandas as pd
import requests
from streamlit.components.v1 import html
from streamlit_tags import st_tags,st_tags_sidebar

movies_rating=[]
movies_dict = pickle.load(open('./assets/data/movies.pkl','rb'))
movies=pd.DataFrame(movies_dict) 
isPosterFetch=0

genres_with_movieId=pickle.load(open('./assets/data/genres_rating.pkl','rb'))
cast_with_movieId=pickle.load(open('./assets/data/cast_rating.pkl','rb'))
cast_names=pickle.load(open('./assets/data/cast_names.pkl','rb'))
genres_name=pickle.load(open('./assets/data/genres_name.pkl','rb'))

tf_idf_sim_mat=pickle.load(open('./assets/data/tf_idf_sim_mat.pkl','rb'))
bag_of_words_sim_mat=pickle.load(open('./assets/data/bag_of_words_sim_mat.pkl','rb'))
user_collaborative_sim_mat=pickle.load(open('./assets/data/user-user_collaborative_sim_mat.pkl','rb')).T
item_collaborative_sim_mat=pickle.load(open('./assets/data/item_item_collaborative_sim_mat.pkl','rb'))

# by default tf_idf_sim_mat is selected as similarity matrix

similarity=tf_idf_sim_mat



# Fetch poster from API 
def fetch_poster_and_title(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=b8fda3e150ab7fcabe257624516ee5f3&append_to_response=videos".format(movie_id)
    # st.text(url)

    res = requests.get(url)
    data = res.json()
    res.close()
    utube_vid_link='https://youtu.be/'
    is_Utube_vid_Found=0
    for vid_dict in data['videos']['results']:
        name_list=vid_dict['name'].split(" ")
        for elm in name_list:
            if (elm)=='Trailer' or elm=='Teaser':
                utube_vid_link+=vid_dict['key']
                is_Utube_vid_Found=1
                break
        if is_Utube_vid_Found==1:
            break
    
    poster_title=data['title']
    path = data['poster_path']
    description=data['overview']
    release_date=data['release_date']
    isAdult=data['adult']
    rating=data['vote_average']
    metadata_of_movie={"genres":data['genres'],
                        "tagline":data['tagline'],
                        "utube_vid_link":utube_vid_link,
                        "rating":rating,
                        "description":data['overview'],
                        "release_date":release_date
                        }
    genres_string=""
    for genre in data['genres']:
        genres_string+=genre['name']+", "
    genres_string=genres_string[:len(genres_string)-2]
    text_overview=description+"\n\n"+"Genres : "+genres_string+"\n\n"+"Rating : "+str(rating)+"\n\n"+"Release Date : "+str(release_date)
    if isAdult==True:
        text=text+"\n\n"+"DISCLAIMER : This is 18+ Rated movie"
    if isPosterFetch:
        poster_path = "https://image.tmdb.org/t/p/w500/" + str(path)
    else:
        poster_path='./assets/images/noimage.png'
    return poster_title,poster_path,text_overview,metadata_of_movie

def f7_noHash(seq):
    seen = set()
    return [ x for x in seq if str( x ) not in seen and not seen.add( str( x ) )]
# Function for recommendation of next k movies by cast name
def recommend_movies_by_cast_name(cast_name,no_of_recommendations):
    list_of_highest_rating_movies=[]
    first_movie_id=''
    first_movie_title=''
    loader=st.image('./assets/gif/96x96.gif')
    loding_text=st.text("loading.....")
    for idx in (cast_with_movieId[cast_name].sort_values(ascending=False)).index:
        if cast_with_movieId[cast_name][idx]==0.0:
            for i in movies.index:
                if(movies['id'][i]==first_movie_id):
                    first_movie_title=movies['title'][i]
                    break
            index=0
            for idx in movies.index: 
                if movies['title'][idx]==first_movie_title:
                    index=idx
                    break
            nearest_vectors = sorted(list(enumerate(tf_idf_sim_mat[index])),reverse=True,key = lambda x: x[1])
            list_of_movies=[]
            for i in nearest_vectors:
                list_of_movies.append(movies['id'][i[0]] )
            list_of_highest_rating_movies+=list_of_highest_rating_movies+list_of_movies[1:]
            list_of_highest_rating_movies=f7_noHash(list_of_highest_rating_movies)
            break
        else:
            if len(list_of_highest_rating_movies)==0:
                first_movie_id= idx
            list_of_highest_rating_movies.append(idx)
    # st.write(list_of_highest_rating_movies)
    
    movie_posters=[]
    recommended_movies=[]
    text_strings=[]

    counter=0
    for i in list_of_highest_rating_movies:
        if(counter==no_of_recommendations+1):
            break
        title,path,text,metadata_of_movie=(fetch_poster_and_title(i))
        movie_posters.append(path)
        recommended_movies.append(title)
        text_strings.append(text)
        counter=counter+1
    loader.empty()
    loding_text.empty()
    return recommended_movies,movie_posters,text_strings

# Function for recommendation of next k movies by genres name
def recommend_movies_by_genres_name(genres_name,no_of_recommendations):
    moviesIds_list=genres_with_movieId[genres_name]
    moviesIds_list=moviesIds_list.sort_values(ascending=False)
    movie_posters=[]
    recommended_movies=[]
    text_strings=[]
    counter=0
    loader=st.image('./assets/gif/96x96.gif')
    loding_text=st.text("loading.....")
    for i in moviesIds_list.index:
        if(counter==no_of_recommendations+1):
            break
        title,path,text,metadata_of_movie=(fetch_poster_and_title(i))
        movie_posters.append(path)
        recommended_movies.append(title)
        text_strings.append(text)
        counter=counter+1
    loader.empty()
    loding_text.empty()
    return recommended_movies,movie_posters,text_strings

def recommend_movies_by_movie_name_for_collaborative_based_helper(movie,user_rarting):
    index=0
    for idx in movies.index: 
        if movies['title'][idx]==movie:
            index=movies['id'][idx]
            break
    global similarity

    similar_score=similarity[index]*(user_rarting-5)
    similar_score=similar_score.sort_values(ascending=False)
    return similar_score
# Function for recommendation of next k movies by movie name (collaborative based)
def recommend_movies_by_movie_name_for_collaborative_based(movie_list,no_of_recommendations):
    similar_movies=pd.DataFrame()
    for elm in movie_list:
        similar_movies=similar_movies.append(recommend_movies_by_movie_name_for_collaborative_based_helper(elm['name'],elm['rating']),ignore_index=True)
    similar_movies=similar_movies.sum().sort_values(ascending=False)
    similar_movies=list(similar_movies.index)
    
    movie_posters=[]
    recommended_movies=[]
    text_strings=[]
    counter=0
    loader=st.image('./assets/gif/96x96.gif')
    loding_text=st.text("loading.....")
    for id in similar_movies:
        if(counter==no_of_recommendations+1):
            break
        title,path,text,metadata_of_movie=(fetch_poster_and_title(id))
        movie_posters.append(path)
        recommended_movies.append(title)
        text_strings.append(text)
        counter=counter+1
    loader.empty()
    loding_text.empty()
    return recommended_movies,movie_posters,text_strings
    
# Function for recommendation of next k movies by movie name (content based)
def recommend_movies_by_movie_name_for_content_based(movie,no_of_movies):
    index=0
    
    for idx in movies.index: 
        if movies['title'][idx]==movie:
            index=idx
            break
    global similarity
    nearest_vectors = sorted(list(enumerate(similarity[index])),reverse=True,key = lambda x: x[1])
    recommended_movies=[]
    movie_posters = []
    text_strings=[]
    loader=st.image('./assets/gif/96x96.gif')
    loding_text=st.text("loading.....")
    counter=0
    for i in nearest_vectors[0:no_of_movies+2]:
        movie_id = movies['id'][i[0]]
        title,path,text,metadata_of_movie=(fetch_poster_and_title(movie_id))
        if counter==0:
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

    st.title(first_movie_title)
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

def generate_cards(name,no_of_movies,type,algo_type):
    if type=="Movie based":
        if algo_type=='Item-Item Collaborative Based':

            movies_Names,movies_Poster,text_strings=recommend_movies_by_movie_name_for_collaborative_based(movies_rating,no_of_movies)
        else:
             movies_Names,movies_Poster,text_strings=recommend_movies_by_movie_name_for_content_based(name,no_of_movies)
    elif type=="genres based":
        movies_Names,movies_Poster,text_strings=recommend_movies_by_genres_name(name,no_of_movies)
    else :
        movies_Names,movies_Poster,text_strings=recommend_movies_by_cast_name(name,no_of_movies)

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
def helper(this):
    st.text(this)
def load_view():
    st.title("See what's Next")
    category = ['--Select--', 'Movie based', 'Person based(cast Member)','genres based']

    category_opt = st.selectbox('Select Recommendation Type', category)

    global slected_opt
    global option_for_algo_type
    option_for_algo_type=None
    if category_opt==category[1]:
        # user_input = st.text_input("label goes here",keywords)
        option_for_algo_type = st.selectbox(
        'Select Searchin    g Algorithm',
        ['Content Based (TF-IDF)','Content Based (Bag Of Words)','Item-Item Collaborative Based'])
        
        global similarity
        global movies_rating
        
        if option_for_algo_type=="Content Based (Bag Of Words)":
            similarity=bag_of_words_sim_mat
            slected_opt = st.selectbox(
            'How would you like to be search?',
            movies['title'].values)
            movies_rating.clear()
        elif option_for_algo_type=="Item-Item Collaborative Based":
            movies_selected_by_user=st.sidebar.multiselect(label="Select Your Favorite Movies",options=movies['title'].values)
            if len(movies_selected_by_user)==0:
                movies_rating.clear()
            if len(movies_selected_by_user)!=len(movies_rating):
                new_list=[]
                for idx in range (0,len(movies_selected_by_user)):
                    for i in range(0,len(movies_rating)):
                        if(movies_selected_by_user[idx]==movies_rating[i]['name']):
                            new_list.append(movies_rating[i])
                    
                movies_rating=new_list  
            if movies_selected_by_user:
                rating_by_user = st.sidebar.selectbox(
                'How You Rate {}?'.format(movies_selected_by_user[-1]),
                (1,2,3,4,5,6,7,8,9,10)
                )
                
                if rating_by_user:
                    isCurrentMoviePresent=0
                    for elm in movies_rating:
                        if elm['name']==movies_selected_by_user[-1]:
                            isCurrentMoviePresent=1
                            elm['rating']=rating_by_user
                            break
                    if isCurrentMoviePresent==0:
                        movies_rating.append({'name':movies_selected_by_user[-1],'rating':rating_by_user})
            st.sidebar.write('Your Favorite Movies:', movies_rating)
            similarity=item_collaborative_sim_mat
        else :
            movies_rating.clear()

            slected_opt = st.selectbox(
            'How would you like to be search?',
            movies['title'].values)
            
            similarity=tf_idf_sim_mat

    elif category_opt==category[2]:
        movies_rating.clear()
        slected_opt = st.selectbox(
        'How would you like to be search?',
        cast_names)
    else:
        movies_rating.clear()
        slected_opt = st.selectbox(
        'How would you like to be search?',
        genres_name)

    global isPosterFetch
    isPosterFetch = st.checkbox('Do You Want Poster (⚠️ It takes some time to fetch poster )')

    
    no_of_movies = st.slider('Number of movies you want Recommended:', min_value=5, max_value=20, step=1)
    if st.button('Search'):
        if category_opt!='--Select--' :
            if category_opt=='Movie based' and option_for_algo_type=='Item-Item Collaborative Based' :

                if len(movies_rating)<2:
                   st.warning('Please Select At-least 2 Movies (❗Select movies from sidebar)') 
                else:
                    generate_cards(slected_opt,no_of_movies,category_opt,option_for_algo_type)
            else:
                generate_cards(slected_opt,no_of_movies,category_opt,option_for_algo_type)
        else:
            st.warning('Please Select First Recommendation Type')
    

        

