import streamlit as st
from component.navbar import navbar_utils as utl
from views import home,about



st.set_page_config(layout="wide", page_title='PMBD')
def navigation():
    utl.inject_custom_css()
    st.set_option('deprecation.showPyplotGlobalUse', False)
    utl.navbar_component()
    route = utl.get_current_route()
    if route == "home":
        home.load_view()
    elif route == "about":
        about.load_view()
    elif route == None:
        home.load_view()
        


utl.inject_custom_js()
