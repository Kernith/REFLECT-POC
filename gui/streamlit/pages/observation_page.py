import streamlit as st
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh
from backend.data.collectors.observation_collector import ObservationCollector
from backend.data.collectors.timer_service import TimerService
from backend.data.exporters.csv_exporter import CSVExporter
from gui.streamlit.adapters.timer_adapter import StreamlitTimerAdapter

def render_observation_page():
    """Render the observation page"""
    # Get observation type (interval, timepoint, etc.)
    observation_type = st.session_state.get('observation_type', 'interval')
    
    # Get config from session state
    config = st.session_state.get('current_config', {})
    
    # Initialize services
    if 'observation_collector' not in st.session_state:
        st.session_state.observation_collector = ObservationCollector(config)
        st.session_state.timer_service = TimerService()
        st.session_state.timer_adapter = StreamlitTimerAdapter(st.session_state.timer_service)
        st.session_state.csv_exporter = CSVExporter()
        st.session_state.button_states = {}
    
    collector = st.session_state.observation_collector
    timer_adapter = st.session_state.timer_adapter
    
    # student, engagement, and instructor activities
    student_col, engagement_col, instructor_col = st.columns([3, 2, 3])

    with student_col:
        render_student_actions(config, collector, observation_type)
    
    with engagement_col:
        render_engagement_section(config, collector, observation_type)
        st.markdown("---")
        render_comments_section(collector)
    
    with instructor_col:
        render_instructor_actions(config, collector, observation_type)

    st.markdown("---")

    # Timer display and controls
    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 3])
    
    with col2:
        # Create a placeholder for the timer that will auto-refresh
        timer_placeholder = st.empty()
        
        # Display the current timer value
        timer_placeholder.metric("Timer", timer_adapter.format_time())
        
        # Auto-refresh only when timer is running
        if timer_adapter.is_running():
            st_autorefresh(interval=1000, key="timer_refresh")
    
    with col3:
        if not timer_adapter.is_running():
            if st.button("Start Observation", type="primary"):
                collector.start_observation()
                timer_adapter.start()
                st.session_state.button_states = {}
                st.rerun()
        else:
            if st.button("Stop & Save", type="secondary"):
                timer_adapter.stop()
                responses = collector.get_responses()
                
                if responses:
                    # Create CSV data
                    csv_data = create_csv_data(responses, st.session_state.get('current_config', {}))
                    st.session_state.csv_data = csv_data
                    st.session_state.show_download = True
                else:
                    st.warning("No observations recorded.")
                st.rerun()
        
    with col4:
        if st.button("Back to Home"):
            st.session_state.page = "home"
            st.rerun()
    
    # Show download button if data is available
    if st.session_state.get('show_download', False):
        st.success("Observation completed! Download your data below.")
        csv_data = st.session_state.get('csv_data', '')
        if csv_data:
            st.download_button(
                label="Download Observation Data",
                data=csv_data,
                file_name=f"observation_{int(time.time())}.csv",
                mime="text/csv",
                help="Download your observation data as CSV"
            )
    
    st.markdown("---")
    
    # Observation interface
    if timer_adapter.is_running():
        render_observation_summary(collector)
    

def render_student_actions(config, collector, observation_type):
    """Render student actions section"""
    st.markdown("### Student Actions")
    
    student_actions = config.get('student_actions', [])
    if not student_actions:
        st.info("No student actions configured")
        return
    
    # Custom wrapper for CSS targeting
    st.html('<div class="student-actions-section">')
    
    # Create 4 columns for button grid with equal spacing
    cols = st.columns(4, gap = "small")

    for i, action in enumerate(student_actions):
        label = action['label']
        text = action['text']
        key = f"student_{label}"
        
        # Use modulo to cycle through columns
        col_index = i % 4
        
        with cols[col_index]:
            if observation_type == "interval":
                # Toggle buttons for interval mode
                checked = st.session_state.button_states.get(key, False)
                
                # Create button style based on state
                button_type = "primary" if checked else "secondary"
                button_text = f"{label}" if checked else f"{label}"
                
                if st.button(button_text, key=f"btn_{key}", help=text, type=button_type):
                    # Toggle the state
                    st.session_state.button_states[key] = not checked
                    st.rerun()
            else:
                # Click buttons for timepoint mode
                if st.button(f"**{label}**", key=f"btn_{key}", help=text):
                    collector.record_response("Student", label, 1)
                    st.success(f"Recorded: {label}")

    st.html('</div>')


def render_instructor_actions(config, collector, observation_type):
    """Render instructor actions section"""
    st.markdown("### Instructor Actions")
    
    instructor_actions = config.get('instructor_actions', [])
    if not instructor_actions:
        st.info("No instructor actions configured")
        return
    
    # Create 4 columns for button grid
    cols = st.columns(4, gap = "small")
    
    for i, action in enumerate(instructor_actions):
        label = action['label']
        text = action['text']
        key = f"instructor_{label}"
        
        # Use modulo to cycle through columns
        col_index = i % 4
        
        with cols[col_index]:
            if observation_type == "interval":
                # Toggle buttons for interval mode
                checked = st.session_state.button_states.get(key, False)
                
                # Create button style based on state
                button_type = "primary" if checked else "secondary"
                button_text = f"{label}" if checked else f"{label}"
                
                if st.button(button_text, key=f"btn_{key}", help=text, type=button_type):
                    # Toggle the state
                    st.session_state.button_states[key] = not checked
                    st.rerun()
            else:
                # Click buttons for timepoint mode
                if st.button(f"**{label}**", key=f"btn_{key}", help=text):
                    collector.record_response("Instructor", label, 1)
                    st.success(f"Recorded: {label}")


def render_engagement_section(config, collector, observation_type):
    """Render engagement section"""
    st.markdown("### Student Engagement")
    
    engagement_levels = config.get('engagement_images', [])
    if not engagement_levels:
        st.info("No engagement levels configured")
        return
    
    # Create 3 columns for button grid with equal spacing
    cols = st.columns(3, gap = "small")
    
    for i, level in enumerate(engagement_levels):
        label = level['label']
        text = level['text']
        key = f"engagement_{label}"
        
        # Use modulo to cycle through columns
        col_index = i % 3
        
        with cols[col_index]:
            if observation_type == "interval":
                # Toggle buttons for interval mode
                checked = st.session_state.button_states.get(key, False)
                
                # Create button style based on state
                button_type = "primary" if checked else "secondary"
                button_text = f"{label}" if checked else f"{label}"
                
                if st.button(button_text, key=f"btn_{key}", help=text, type=button_type):
                    # Toggle the state
                    st.session_state.button_states[key] = not checked
                    st.rerun()
            else:
                # Click buttons for timepoint mode
                if st.button(f"**{label}**", key=f"btn_{key}", help=text):
                    collector.record_response("Engagement", label, get_engagement_value(label))
                    st.success(f"Recorded: {label}")


def render_comments_section(collector):
    """Render comments section"""
    st.markdown("### Comments")
    
    comment = st.text_area("Add a comment:", key="comment_field", height=100)
    
    if st.button("Save Comment"):
        if comment.strip():
            collector.record_response("Comment", comment.strip())
            st.success("Comment saved!")
            st.session_state.comment_field = ""  # Clear the field
            st.rerun()
        else:
            st.warning("Please enter a comment before saving.")


def render_observation_summary(collector):
    """Render current observation summary"""
    st.markdown("### Current Observation Summary")
    
    responses = collector.get_responses()
    if responses:
        # Convert to DataFrame for analysis
        df = pd.DataFrame(responses, columns=['time_s', 'category', 'response', 'value'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Responses", len(responses))
        
        with col2:
            categories = df['category'].nunique()
            st.metric("Categories", categories)
        
        with col3:
            if len(responses) > 0:
                duration = responses[-1][0] - responses[0][0]
                st.metric("Duration (s)", f"{duration:.1f}")
        
        # Show recent responses
        st.markdown("**Recent Responses:**")
        recent_responses = responses[-5:] if len(responses) >= 5 else responses
        for response in recent_responses:
            time_s, category, resp, value = response
            minutes = int(time_s // 60)
            seconds = int(time_s % 60)
            st.markdown(f"- **{minutes:02d}:{seconds:02d}** {category}: {resp}")
    else:
        st.info("No responses recorded yet.")


def get_engagement_value(label):
    """Get numeric value for engagement level"""
    engagement_values = {"Low": 1, "Medium": 2, "High": 3}
    return engagement_values.get(label, 1)


def create_csv_data(responses, config):
    """Create CSV data string"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Add metadata
    protocol_name = config.get('name', 'Unknown')
    writer.writerow([f"# Protocol: {protocol_name}"])
    writer.writerow([f"# Generated by: REFLECT Streamlit v1.0"])
    writer.writerow([f"# Total Responses: {len(responses)}"])
    writer.writerow([])  # Empty line
    
    # Add data header and rows
    writer.writerow(["time_s", "category", "response", "value"])
    writer.writerows(responses)
    
    return output.getvalue()
