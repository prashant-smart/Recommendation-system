# Modules

import pyrebase
import streamlit as st
from setup import navigation
from localStoragePy import localStoragePy


# initalisation of localStoragePy for saving user credentials
localStorage = localStoragePy('pmdb', 'json')

welcome_text_block=st.empty()
login_signup_image_block=st.empty()


# Function for handle logout and login

def handle_login_and_logout(username):
    welcome_text_block=st.sidebar.empty()
    welcome_text_block.write(f'Welcome {username} 🤠 !')
    logout_block=st.sidebar.empty()
    logout_btn=logout_block.button("Logout")
    if logout_btn:

        # if user click logout btn then all text container will remove
        localStorage.removeItem('email')
        localStorage.removeItem('password')
        localStorage.removeItem('username')
        welcome_text_block.empty()
        logout_block.empty()
        authenticate()
        return 
    # if user only logged in then it redirected to homepage 
    navigation()

# function for Authentication of user (using firebase)
def authenticate():

    firebaseConfig = {
    "apiKey": "AIzaSyACfmH5Tsfe-y7qz8ewrVc1nF2Qjm0kotk",
    "authDomain": "pmbd-firebase-streamlit.firebaseapp.com",
    "projectId": "pmbd-firebase-streamlit",
    "storageBucket": "pmbd-firebase-streamlit.appspot.com",
    "messagingSenderId": "308716710258",
    "databaseURL":'https://pmbd-firebase-streamlit-default-rtdb.firebaseio.com/',
    "appId": "1:308716710258:web:33481c6a7230603cca15eb",
    "measurementId": "G-JTJ7CYYRE7"
    }

    
    # check wheater whether user credentials are already saved in localStoragePy or not (if credentials is saved then it means user already logged in)
    email =localStorage.getItem('email')
    password = localStorage.getItem('password')
    username=localStorage.getItem('username')

    # if user already logged in then redirected to home page
    if email and password and username:
        welcome_text_block.empty()
        login_signup_image_block.empty()
        handle_login_and_logout(username)
        return

    else :
        # if user not logged in then redirected to login/signup page

        welcome_text_block.title("welcome To PMBD")
        login_signup_image_block.image('./assets/images/login_signup_page_image.png')

        # Firebase Authentication
        firebase = pyrebase.initialize_app(firebaseConfig)
        auth = firebase.auth()

        # Database
        db = firebase.database()
        storage = firebase.storage()

        # Authentication
        choice_block = st.sidebar.empty()
        choice = choice_block.radio('Login / Signup', ['Login', 'Sign up'])

        # E-mail input
        email_block = st.sidebar.empty()
        email = email_block.text_input('Please enter your email address')

        # Password input
        password_block = st.sidebar.empty()
        password = password_block.text_input('Please enter your password',type = 'password')

        # Sign up block
        if choice == 'Sign up':
            username_block = st.sidebar.empty()
            username = username_block.text_input('Please input your app user name', value='Default')

            sign_up_block = st.sidebar.empty()
            sign_up = sign_up_block.button('Sign Up')

            # Sign Up button is clicked
            if sign_up:
                try:
                    user = auth.create_user_with_email_and_password(email, password)
                    st.success('Your account was created successfully!')
                    st.balloons()
                    
                    # Sign in
                    user = auth.sign_in_with_email_and_password(email, password)
                    db.child(user['localId']).child("Username").set(username)
                    db.child(user['localId']).child("ID").set(user['localId'])
                    st.info(f"Welcome {username}, you can now login to the system.")
                    sign_up_block.empty()

                except:
                    st.error('Account already exists!')

        # Login block
        elif choice == 'Login':

            # Login button
            login_block = st.sidebar.empty()
            login = login_block.button('Login')
            
            # Login button is clicked
            if login:
                try:
                    user = auth.sign_in_with_email_and_password(email,password)

                    # if user has enter valid credentials
                    if user:
                        welcome_text_block.empty()
                        login_signup_image_block.empty()
                        st.balloons()
                        username = db.child(user['localId']).child("Username").get().val()
                        localStorage.setItem('email', email)
                        localStorage.setItem('password', password)
                        localStorage.setItem('username', username)

                        # Delete all placeholders
                        choice_block.empty()
                        email_block.empty()
                        password_block.empty()
                        login_block.empty()
                        handle_login_and_logout(username)
                except :
                    # if user has not enter valid credentials
                    st.error('Please Enter Correct Credentials 🤔!')

                

if __name__ == "__main__":
    
    authenticate()