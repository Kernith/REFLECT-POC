import streamlit as st
from backend.config.config_manager import ConfigManager


def render_settings_page():
    """Render the settings page"""
    st.title("⚙️ Settings")
    
    # Navigation
    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"
        st.rerun()
    
    st.markdown("---")
    
    # Initialize config manager if not already done
    if 'config_manager' not in st.session_state:
        st.session_state.config_manager = ConfigManager()
    
    config_manager = st.session_state.config_manager
    
    # Display current configuration
    st.subheader("📋 Current Configuration")
    
    # Get observation configs
    observation_configs = config_manager.get_observation_configs()
    colors = config_manager.get_colors()
    
    # Protocol selection
    st.markdown("### 🎯 Observation Protocol")
    protocol_names = [config['name'] for config in observation_configs]
    
    if 'selected_protocol' not in st.session_state:
        st.session_state.selected_protocol = 0
    
    selected_protocol = st.selectbox(
        "Choose observation protocol:",
        range(len(protocol_names)),
        format_func=lambda x: protocol_names[x],
        index=st.session_state.selected_protocol
    )
    
    if selected_protocol != st.session_state.selected_protocol:
        st.session_state.selected_protocol = selected_protocol
        st.session_state.current_config = config_manager.get_config_by_index(selected_protocol)
        st.rerun()
    
    # Display selected protocol details
    if st.session_state.get('current_config'):
        config = st.session_state.current_config
        st.markdown(f"**Selected Protocol:** {config.get('name', 'Unknown')}")
        st.markdown(f"**Description:** {config.get('description', 'No description available')}")
        st.markdown(f"**Timer Method:** {config.get('timer_method', 'Unknown')}")
        if config.get('timer_interval'):
            st.markdown(f"**Timer Interval:** {config.get('timer_interval')} seconds")
    
    st.markdown("---")
    
    # Color scheme
    st.subheader("🎨 Color Scheme")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Current Colors:**")
        for category, color in colors.items():
            st.markdown(f"- **{category.title()}:** {color}")
    
    with col2:
        st.markdown("**Color Preview:**")
        for category, color in colors.items():
            st.markdown(f"<span style='color: {color}; font-weight: bold;'>{category.title()}</span>", 
                       unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Protocol details
    if st.session_state.get('current_config'):
        config = st.session_state.current_config
        
        # Student actions
        if config.get('student_actions'):
            with st.expander("👨‍🎓 Student Actions"):
                for action in config['student_actions']:
                    st.markdown(f"**{action['label']}:** {action['text']}")
        
        # Instructor actions
        if config.get('instructor_actions'):
            with st.expander("👨‍🏫 Instructor Actions"):
                for action in config['instructor_actions']:
                    st.markdown(f"**{action['label']}:** {action['text']}")
        
        # Engagement levels
        if config.get('engagement_images'):
            with st.expander("📊 Engagement Levels"):
                for level in config['engagement_images']:
                    st.markdown(f"**{level['label']}:** {level['text']}")
    
    st.markdown("---")
    
    # Instructions
    if st.session_state.get('current_config'):
        config = st.session_state.current_config
        instructions = config.get('instructions', '')
        if instructions:
            st.subheader("📖 Instructions")
            st.markdown(instructions)
    
    st.markdown("---")
    
    # Session state info
    with st.expander("🔧 Session State Information"):
        st.markdown("**Current session state:**")
        for key, value in st.session_state.items():
            if key not in ['config_manager', 'current_config']:  # Skip large objects
                st.markdown(f"- **{key}:** {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
    
    # Reset session
    st.markdown("---")
    st.subheader("🔄 Reset Session")
    st.markdown("Clear all session data and start fresh.")
    
    if st.button("🗑️ Clear Session State", type="secondary"):
        # Clear session state except for essential items
        keys_to_keep = ['config_manager']
        keys_to_remove = [key for key in st.session_state.keys() if key not in keys_to_keep]
        
        for key in keys_to_remove:
            del st.session_state[key]
        
        st.success("Session state cleared!")
        st.rerun()
