from setup import navigation
import pandas as pd
import streamlit as st
from localStoragePy import localStoragePy

# initalisation of localStoragePy for saving user credentials
localStorage = localStoragePy('pmdb', 'json')

welcome_text_block=st.empty()
login_signup_image_block=st.empty()




def handle_login_and_logout(username):
    welcome_text_block=st.sidebar.empty()
    welcome_text_block.write(f'Welcome {username} 🤠 ! \n\n  You can now access App')
    logout_block=st.sidebar.empty()
    logout_btn=logout_block.button("Logout")
    if logout_btn:

        # if user click logout btn then all text container will remove
        # localStorage.removeItem('email')
        localStorage.removeItem('password')
        localStorage.removeItem('username')
        logout_block.empty()
        welcome_text_block.empty()

        authenticate()
        return 
    # if user only logged in then it redirected to homepage 
    navigation()

# Security
#passlib,hashlib,bcrypt,scrypt
import hashlib
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False
# DB Management
import sqlite3 
conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data


def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data


def authenticate():
		signup_titl_block=st.sidebar.empty()

		signup_titl_block.title("PMBD")

		# check wheater whether user credentials are already saved in localStoragePy or not (if credentials is saved then it means user already logged in)
		username =localStorage.getItem('username')
		password = localStorage.getItem('password')
		# if user already logged in then redirected to home page
		if username and password and login_user(username,make_hashes(password)):
			welcome_text_block.empty()
			signup_titl_block.empty()
			login_signup_image_block.empty()
			handle_login_and_logout(username)
			return    
		else:
			welcome_text_block.title("welcome To PMBD")
			login_signup_image_block.image('./assets/images/login_signup_page_image.png')
			menu=["Login","SignUp"]
			choice_block=st.sidebar.empty()
			choice= choice_block.selectbox("Menu",menu)


			if choice =="SignUp":

				st.sidebar.title("SignUp")
				new_user =st.sidebar.text_input("User Name")
				new_password =st.sidebar.text_input("Password",type='password')

				if st.sidebar.button("SignUp"):
					create_usertable()
					add_userdata(new_user,make_hashes(new_password))
					st.balloons()
					st.success("You have succesfully created valid Account")
					st.info("Go to Login Menu to login")
					
			if choice == 'Login':
				title_block=st.sidebar.empty()
				title_block.header("Login")
				
				username_block =st.sidebar.empty()
				password_block =st.sidebar.empty()


				username=username_block.text_input("User Name")
				password=password_block.text_input("Password",type='password')	
						
				checkbox_block =st.sidebar.empty()
				if checkbox_block.checkbox("Login"):
					create_usertable()
					result=login_user(username,make_hashes(password))
					if result:
							st.balloons()
							user_result=view_all_users()
							clean_db=pd.DataFrame(user_result,columns=['username','password'])

							# saved username and password in localStorage
							localStorage.setItem('password', password)
							localStorage.setItem('username', username)

							# Delete all placeholders
							title_block.empty()
							choice_block.empty()
							username_block.empty()
							password_block.empty()
							checkbox_block.empty()
							signup_titl_block.empty()
							welcome_text_block.empty()
							login_signup_image_block.empty()
							signup_titl_block.empty()
							
							handle_login_and_logout(username)

					else:
							# if user has not enter valid credentials
							st.error('Please Enter Correct Credentials 🤔!')


	

if __name__ == "__main__":
    
    authenticate()