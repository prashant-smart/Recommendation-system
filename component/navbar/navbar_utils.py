import streamlit as st
from streamlit.components.v1 import html

from .paths_for_navbar import NAVBAR_PATHS


def inject_custom_css():
    with open('assets/css/styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    
       
          
  
  
def inject_custom_js():
    # with open("./assets/js/mobiscroll.javascript.min.js",'rb') as f:
    #     st.markdown(f'<script>{f.read()}</script>', unsafe_allow_html=True)
    with open("assets/js/script.js") as f:
        st.markdown(f'<script>{f.read()}</script>', unsafe_allow_html=True)
    
    



def get_current_route():
    try:
        return st.experimental_get_query_params()['nav'][0]
    except:
        return None


def navbar_component():

    navbar_items = ''
    for key, value in NAVBAR_PATHS.items():
        navbar_items += (f'<a class="navitem" href="/?nav={value}">{key}</a>')


    component = rf'''
            <nav class="container navbar" id="navbar">
                <ul class="navlist">
                <a class="navitem" id="logo" href="#">PMBD</a>
                {navbar_items}
                </ul>
            </nav>
            '''
    st.markdown(component, unsafe_allow_html=True)
    js = '''
    <script>
        // navbar elements
        var navigationTabs = window.parent.document.getElementsByClassName("navitem");
        var cleanNavbar = function(navigation_element) {
            navigation_element.removeAttribute('target')
        }
        
        for (var i = 0; i < navigationTabs.length; i++) {
            cleanNavbar(navigationTabs[i]);
        }
        
        // Dropdown hide / show
        var dropdown = window.parent.document.getElementById("settingsDropDown");
        dropdown.onclick = function() {
            var dropWindow = window.parent.document.getElementById("myDropdown");
            if (dropWindow.style.visibility == "hidden"){
                dropWindow.style.visibility = "visible";
            }else{
                dropWindow.style.visibility = "hidden";
            }
        };
        
        var settingsNavs = window.parent.document.getElementsByClassName("settingsNav");
        var cleanSettings = function(navigation_element) {
            navigation_element.removeAttribute('target')
        }
        
        for (var i = 0; i < settingsNavs.length; i++) {
            cleanSettings(settingsNavs[i]);
        }
    </script>
    '''
    html(js)
