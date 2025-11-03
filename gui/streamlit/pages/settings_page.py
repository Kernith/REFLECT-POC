import streamlit as st
from backend.config.config_manager import ConfigManager


def _initialize_config_manager():
    """Initialize config manager in session state if needed."""
    if 'config_manager' not in st.session_state:
        st.session_state.config_manager = ConfigManager()
    return st.session_state.config_manager


def _render_header():
    """Render page header with title and navigation."""
    col1, col2 = st.columns(2)
    with col1:
        st.title("Protocol Information")
    with col2:
        if st.button("Back to Home"):
            st.session_state.page = "home"
            st.rerun()
    st.markdown("---")


def _render_protocol_selection(config_manager, observation_configs):
    """Handle protocol selection logic and UI."""
    protocol_names = [config['name'] for config in observation_configs]
    
    # Initialize selected protocol if needed
    if 'selected_protocol' not in st.session_state:
        st.session_state.selected_protocol = 0
    
    # Render selectbox
    selected_protocol = st.selectbox(
        "Choose observation protocol:",
        range(len(protocol_names)),
        format_func=lambda x: protocol_names[x],
        index=st.session_state.selected_protocol
    )
    
    # Update session state if selection changed
    if selected_protocol != st.session_state.selected_protocol:
        st.session_state.selected_protocol = selected_protocol
        st.session_state.current_config = config_manager.get_config_by_index(selected_protocol)
        st.rerun()
    
    return config_manager.get_config_by_index(selected_protocol)


def _render_protocol_overview(config):
    """Display basic protocol information."""
    if not config:
        return
    
    st.subheader(f"{config.get('description', 'No description available')}")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Timer Method:** {config.get('timer_method', 'Unknown')}")
    with col2:
        if config.get('timer_interval'):
            st.markdown(f"**Timer Interval:** {config.get('timer_interval')} seconds")


def _render_color_scheme(colors):
    """Render color scheme display."""
    st.markdown("**Color Preview:**")
    cols = st.columns(len(colors))
    for idx, (category, color) in enumerate(colors.items()):
        cols[idx].markdown(
            f"<div style='text-align:center;'>"
            f"<span style='display:inline-block;width:36px;height:24px;background:{color};border-radius:6px;border:1px solid #888;margin-bottom:6px;'></span><br>"
            f"<span style='font-weight:bold;'>{category.title()}</span>"
            f"</div>",
            unsafe_allow_html=True
        )


def _render_actions_section(config):
    """Render student and instructor actions."""
    if not config:
        return
    
    # Student actions
    if config.get('student_actions'):
        st.markdown("### Student Actions")
        student_actions_md = "\n".join([f"- **{action['label']}:** {action['text']}" for action in config['student_actions']])
        st.markdown(student_actions_md)

    # Instructor actions
    if config.get('instructor_actions'):
        st.markdown("### Instructor Actions")
        instructor_actions_md = "\n".join([f"- **{action['label']}:** {action['text']}" for action in config['instructor_actions']])
        st.markdown(instructor_actions_md)

    # Engagement levels
    if config.get('engagement_images'):
        st.markdown("### Engagement Levels")
        engagement_md = "\n".join([f"- **{level['label']}:** {level['text']}" for level in config['engagement_images']])
        st.markdown(engagement_md)


def _render_instructions(config):
    """Render protocol instructions."""
    if not config:
        return
    
    instructions = config.get('instructions', '')
    if instructions:
        st.subheader("Instructions")
        st.markdown(instructions)


def _render_session_info():
    """Render debug session state information."""
    with st.expander("Session State Information"):
        st.markdown("**Current session state:**")
        for key, value in st.session_state.items():
            if key not in ['config_manager', 'current_config']:
                str_value = str(value)
                truncated = str_value[:100] + ('...' if len(str_value) > 100 else '')
                st.markdown(f"- **{key}:** {truncated}")


def _render_reset_section():
    """Render session reset functionality."""
    st.subheader("Session Manager")
    st.markdown("Clear all session data and start fresh.")
    
    if st.button("Clear Session State", type="secondary"):
        keys_to_keep = ['config_manager']
        keys_to_remove = [key for key in st.session_state.keys() if key not in keys_to_keep]
        
        for key in keys_to_remove:
            del st.session_state[key]
        
        st.success("Session state cleared!")
        st.rerun()


def render_settings_page():
    """Render the settings page."""
    # Initialization
    config_manager = _initialize_config_manager()
    observation_configs = config_manager.get_observation_configs()
    colors = config_manager.get_colors()
    
    # Header
    _render_header()
    
    # Protocol selection and overview
    selected_protocol = _render_protocol_selection(config_manager, observation_configs)
    
    col1, col2 = st.columns(2)
    with col1:
        _render_protocol_overview(selected_protocol)
        _render_instructions(selected_protocol)
    with col2:
        _render_actions_section(selected_protocol)
    
    _render_color_scheme(colors)
    
    st.markdown("---")
    _render_reset_section()
    _render_session_info()
