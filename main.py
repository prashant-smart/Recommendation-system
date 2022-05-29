from setup import navigation
import streamlit as st
from localStoragePy import localStoragePy

# initalisation of localStoragePy for saving user credentials
localStorage = localStoragePy('pmdb', 'json')

welcome_text_block=st.empty()
login_signup_image_block=st.empty()


# importing database function 

from database.database_connection import add_userdata,login_user,view_all_users




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
					result=add_userdata(new_user,make_hashes(new_password))
					if result:
						st.balloons()
						st.sidebar.success("You have succesfully created valid Account")
						st.sidebar.info("Go to Login Menu to login")
					else:
						st.sidebar.warning("{} already exists try another username".format(new_user))    
					
			if choice == 'Login':
				title_block=st.sidebar.empty()
				title_block.header("Login")
				
				username_block =st.sidebar.empty()
				password_block =st.sidebar.empty()


				username=username_block.text_input("User Name")
				password=password_block.text_input("Password",type='password')	
						
				checkbox_block =st.sidebar.empty()
				if checkbox_block.checkbox("Login"):
					user_id=login_user(username,make_hashes(password))
					if user_id:
							
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
							st.balloons()

					else:
							# if user has not enter valid credentials
							st.error('Please Enter Correct Credentials 🤔!')


	

if __name__ == "__main__":
    
    authenticate()