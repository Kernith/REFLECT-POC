import streamlit as st
from backend.config.config_manager import ConfigManager
from backend.config.app_state import AppState
from .pages import home_page, observation_page, analysis_page, settings_page


def main():
    """Main Streamlit application"""
    # Configure page
    st.set_page_config(
        page_title="REFLECT - Classroom Observation Tool",
        page_icon="🎓",
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
    """Add custom CSS styling"""
    st.markdown("""
    <style>
    /* Main title styling */
    .main-title {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 10px;
        border: 2px solid #1f77b4;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #1f77b4;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Metric styling */
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Success message styling */
    .stSuccess {
        border-radius: 10px;
        border-left: 4px solid #28a745;
    }
    
    /* Error message styling */
    .stError {
        border-radius: 10px;
        border-left: 4px solid #dc3545;
    }
    
    /* Info message styling */
    .stInfo {
        border-radius: 10px;
        border-left: 4px solid #17a2b8;
    }
    
    /* Warning message styling */
    .stWarning {
        border-radius: 10px;
        border-left: 4px solid #ffc107;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        border-radius: 10px;
        border: 2px dashed #1f77b4;
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background-color: #28a745;
        color: white;
        border: none;
        border-radius: 10px;
    }
    
    .stDownloadButton > button:hover {
        background-color: #218838;
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)
