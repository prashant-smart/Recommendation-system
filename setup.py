# Modules
import streamlit as st
from component.navbar import navbar_utils as utl
from views import home,about


# set title of webpage
st.set_page_config(layout="wide", page_title='PMBD')

# function for handle navigation 
def navigation():
    # inject css
    utl.inject_custom_css()
    st.set_option('deprecation.showPyplotGlobalUse', False)
    
    # inject navbar to webpage
    utl.navbar_component()
    route = utl.get_current_route()
    
    if route == "home":
        # if user selected home on navbar
        home.load_view()
    elif route == "about":
        # if user selected about on navbar
        about.load_view()
    elif route == None:
        # if user has't selected any option on navbar( by defalut )
        home.load_view()
        


