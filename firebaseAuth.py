# Modules
import pyrebase
import streamlit as st
from main import navigation
from localStoragePy import localStoragePy



localStorage = localStoragePy('pmdb', 'json')

welcome_text_block=st.empty()
login_signup_image_block=st.empty()

def handle_login_and_logout(username):
    welcome_text_block=st.sidebar.empty()
    welcome_text_block.write(f'Welcome {username} 🤠 !')
    logout_block=st.sidebar.empty()
    logout_btn=logout_block.button("Logout")
    if logout_btn:
        localStorage.removeItem('email')
        localStorage.removeItem('password')
        localStorage.removeItem('username')
        welcome_text_block.empty()
        logout_block.empty()
        authenticate()
        return 
    navigation()

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

    

    email =localStorage.getItem('email')
    password = localStorage.getItem('password')
    username=localStorage.getItem('username')

    if email and password and username:
        welcome_text_block.empty()
        login_signup_image_block.empty()
        handle_login_and_logout(username)
        return

    else :
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
            
            if login:
                try:
                    user = auth.sign_in_with_email_and_password(email,password)
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
                    st.error('Please Enter Correct Credentials 🤔!')

    

                

if __name__ == "__main__":
    
    authenticate()