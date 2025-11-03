import streamlit as st


def render_home_page():
    """Render the home page"""
    # Get current config from app state
    app_state = st.session_state.get('app_state')
    current_config = app_state.get_current_config() if app_state else {}
    timer_method = current_config.get('timer_method', 'timepoint')  # Default to timepoint if not found
    
    # set custom width in css
    st.markdown("""
    <style>
    .stApp {
        max-width: 50%;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)
    
    title_col, icon_col = st.columns([3, 1])
    with title_col:
        st.markdown("# <span style='color: var(--highlight-color);'>REFLECT</span>", unsafe_allow_html=True)
        st.markdown("### <span style='color: var(--highlight-color);'>R</span>esearch & <span style='color: var(--highlight-color);'>E</span>valuation <span style='color: var(--highlight-color);'>F</span>ramework for <span style='color: var(--highlight-color);'>L</span>earning, <span style='color: var(--highlight-color);'>E</span>ngagement, <span style='color: var(--highlight-color);'>C</span>ollaboration, and <span style='color: var(--highlight-color);'>T</span>racking", unsafe_allow_html=True)
    with icon_col:
        st.image("images/hero_image.png", use_container_width=True)
        
    st.markdown("---")
    
    # Navigation buttons in a grid layout
    left_col, right_col = st.columns([1, 2])
    
    with left_col:
        if st.button(f"Start Observation ({current_config.get('name', 'Unknown')})", use_container_width=True, type="primary"):
            st.session_state.page = "observation"
            st.session_state.observation_type = timer_method
            st.rerun()

        with st.expander("### Select Protocol"):
            # Get config manager and app state from session
            config_manager = st.session_state.get('config_manager')
            app_state = st.session_state.get('app_state')
            
            if config_manager and app_state:
                # Get available observation configs
                observation_configs = config_manager.get_observation_configs()
                
                if observation_configs:
                    # Create list of config names
                    config_names = [config['name'] for config in observation_configs]
                    
                    # Get current config index from app state
                    current_config = app_state.get_current_config()
                    current_index = 0
                    
                    # Find the index of the current config
                    for i, config in enumerate(observation_configs):
                        if config['name'] == current_config.get('name'):
                            current_index = i
                            break
                    
                    # Radio buttons for protocol selection
                    selected = st.radio(
                        "Choose an observation protocol:",
                        options=range(len(config_names)),
                        format_func=lambda x: config_names[x],
                        index=current_index,
                        horizontal=True
                    )
                    
                    # Update app state if selection changed
                    if selected != current_index:
                        app_state.update_config(selected)
                        
                        # Update session state to reflect the change
                        st.session_state.current_config = app_state.get_current_config()
                        st.session_state.colors = st.session_state.current_config.get('colors', {})
                        
                        # Trigger rerun to update the UI
                        st.rerun()
                else:
                    st.error("No observation protocols found in configuration")
            else:
                st.error("Configuration system not initialized")
        
        if st.button("Data Analysis", use_container_width=True, type="primary"):
            st.session_state.page = "analysis"
            st.rerun()
        
        if st.button("Protocol Information", use_container_width=True, type="primary"):
            st.session_state.page = "settings"
            st.rerun()

        
    
    with right_col:
        # Quick start guide
        st.markdown("""
        REFLECT Quick Start Guide:
        1. **Select Protocol**: Select an observation protocol from the dropdown menu
        2. **Start Recording**: Click the appropriate button to begin
        3. **Record Behaviors**: Use the interface to log student and instructor actions
        4. **Save Data**: Download your observations as CSV files
        5. **Analyze Results**: Upload CSV files to view plots and statistics
        """)

