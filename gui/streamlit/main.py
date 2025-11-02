import streamlit as st
from backend.config.config_manager import ConfigManager
from backend.config.app_state import AppState
from .pages import home_page, observation_page, analysis_page, settings_page
import os


def main():
    """Main Streamlit application"""
    # Configure page
    st.set_page_config(
        page_title="REFLECT - Classroom Observation Tool",
        page_icon="images/icon.png",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize configuration
    if 'config_manager' not in st.session_state:
        st.session_state.config_manager = ConfigManager()
        st.session_state.app_state = AppState(st.session_state.config_manager)
        
        # Load initial configuration
        config = st.session_state.app_state.get_current_config()
        st.session_state.current_config = config
        st.session_state.colors = config.get('colors', {})
        
        # Initialize page state
        st.session_state.page = "home"
    
    # Initialize page state if not exists
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    
    # Add custom CSS for better styling
    add_custom_css()
    
    # Render current page
    if st.session_state.page == "home":
        home_page.render_home_page()
    elif st.session_state.page == "observation":
        observation_page.render_observation_page()
    elif st.session_state.page == "analysis":
        analysis_page.render_analysis_page()
    elif st.session_state.page == "settings":
        settings_page.render_settings_page()
    else:
        st.error("Unknown page. Redirecting to home...")
        st.session_state.page = "home"
        st.rerun()


def add_custom_css():
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    css_file_path = os.path.join(current_dir, 'assets', 'styles.css')
    
    try:
        with open(css_file_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Get colors from session state
        colors = st.session_state.get('colors', {})
        
        # Generate CSS variables
        css_variables = f"""
        :root {{
            --student-color: {colors.get('student', '#F46715')};
            --instructor-color: {colors.get('instructor', '#0C8346')};
            --engagement-color: {colors.get('engagement', '#4169E1')};
            --toggled-color: {colors.get('toggled', '#FFDF00')};
        }}
        """
        
        # Combine CSS variables with the rest of the CSS
        full_css = css_variables + css_content
        st.markdown(f"<style>{full_css}</style>", unsafe_allow_html=True)
        
    except FileNotFoundError:
        st.error(f"CSS file not found at: {css_file_path}")
    except Exception as e:
        st.error(f"Error loading CSS: {str(e)}")
