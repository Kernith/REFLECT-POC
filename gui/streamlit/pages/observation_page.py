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
        st.session_state.last_interval_save = None
        st.session_state.interval_start_time = None
    
    collector = st.session_state.observation_collector
    timer_adapter = st.session_state.timer_adapter
    
    # Handle periodic interval saving for interval mode
    if observation_type == "interval" and timer_adapter.is_running() and collector.is_observation_active():
        timer_interval = config.get('timer_interval', 120)  # Default 2 minutes
        current_time = time.time()
        
        # Initialize interval tracking
        if st.session_state.interval_start_time is None:
            st.session_state.interval_start_time = current_time
            st.session_state.last_interval_save = current_time
        
        # Check if interval has elapsed
        elapsed_since_last_save = current_time - st.session_state.last_interval_save
        if elapsed_since_last_save >= timer_interval:
            save_interval_data(collector, config)
            st.session_state.last_interval_save = current_time
            st.rerun()
    
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
    
    # Check if there's saved data
    has_saved_data = st.session_state.get('show_download', False) and st.session_state.get('csv_data', '')
    
    with col2:
        # Only show timer if there's no saved data
        if not has_saved_data:
            # Create a placeholder for the timer that will auto-refresh
            timer_placeholder = st.empty()
            
            # Display the current timer value
            timer_placeholder.metric("Timer", timer_adapter.format_time())
            
            # Auto-refresh only when timer is running
            if timer_adapter.is_running():
                st_autorefresh(interval=1000, key="timer_refresh")
    
    with col3:
        timer_running = timer_adapter.is_running()
        
        if timer_running:
            # State 3: Timer is running -> "Finish Observation" button
            if st.button("Finish Observation", type="primary"):
                timer_adapter.stop()
                
                # Save any remaining button states for interval mode
                if observation_type == "interval":
                    save_interval_data(collector, config)
                
                responses = collector.get_responses()
                
                if responses:
                    # Use CSVExporter to create CSV data with metadata
                    csv_exporter = st.session_state.csv_exporter
                    start_time = collector.start_time
                    duration = collector.get_elapsed_time()
                    metadata = csv_exporter.create_metadata(config, start_time, duration)
                    
                    # Create CSV data string
                    csv_data = create_csv_data_with_metadata(responses, metadata)
                    st.session_state.csv_data = csv_data
                    st.session_state.show_download = True
                else:
                    st.warning("No observations recorded.")
                
                # Reset interval tracking
                st.session_state.last_interval_save = None
                st.session_state.interval_start_time = None
                st.rerun()
        elif has_saved_data:
            # State 2: Timer not running and data is saved -> "Download Data" button
            csv_data = st.session_state.get('csv_data', '')
            if csv_data:
                st.download_button(
                    label="Download Data",
                    data=csv_data,
                    file_name=f"observation_{int(time.time())}.csv",
                    mime="text/csv",
                    help="Download your observation data as CSV",
                    type="primary"
                )
        else:
            # State 1: Timer not running and no data saved -> "Start Observation" button
            if st.button("Start Observation", type="primary"):
                collector.start_observation()
                timer_adapter.start()
                st.session_state.button_states = {}
                st.session_state.last_interval_save = None
                st.session_state.interval_start_time = None
                # Clear any previous download state when starting new observation
                st.session_state.show_download = False
                st.session_state.csv_data = None
                st.rerun()
        
    with col4:
        # Check if we're showing confirmation dialog
        show_confirmation = st.session_state.get('show_back_confirmation', False)
        
        if show_confirmation:
            # Show confirmation UI when timer is running
            st.warning("⚠️ An observation is currently running. Leaving will stop the timer and clear all data.")
            confirm_col, cancel_col = st.columns(2)
            
            with confirm_col:
                if st.button("Yes, Go Back", type="primary", key="confirm_back"):
                    # Reset confirmation state
                    st.session_state.show_back_confirmation = False
                    
                    # Reset all observation state
                    collector = st.session_state.observation_collector
                    timer_adapter = st.session_state.timer_adapter
                    
                    # Stop timer if running
                    if timer_adapter.is_running():
                        timer_adapter.stop()
                    
                    # Stop observation and clear data
                    if collector.is_observation_active():
                        collector.stop_observation()
                    collector.clear_responses()
                    
                    # Reset timer
                    timer_adapter.reset()
                    
                    # Clear all button states and toggles
                    st.session_state.button_states = {}
                    
                    # Clear interval tracking
                    st.session_state.last_interval_save = None
                    st.session_state.interval_start_time = None
                    
                    # Clear download state
                    st.session_state.show_download = False
                    st.session_state.csv_data = None
                    
                    # Clear comment field
                    if 'comment_field' in st.session_state:
                        del st.session_state.comment_field
                    
                    # Navigate to home
                    st.session_state.page = "home"
                    st.rerun()
            
            with cancel_col:
                if st.button("Cancel", key="cancel_back"):
                    st.session_state.show_back_confirmation = False
                    st.rerun()
        else:
            # Normal "Back to Home" button
            if st.button("Back to Home"):
                collector = st.session_state.observation_collector
                timer_adapter = st.session_state.timer_adapter
                
                # Check if timer is running - show confirmation if so
                if timer_adapter.is_running():
                    st.session_state.show_back_confirmation = True
                    st.rerun()
                else:
                    # Timer not running - proceed directly with reset
                    # Stop observation and clear data
                    if collector.is_observation_active():
                        collector.stop_observation()
                    collector.clear_responses()
                    
                    # Reset timer
                    timer_adapter.reset()
                    
                    # Clear all button states and toggles
                    st.session_state.button_states = {}
                    
                    # Clear interval tracking
                    st.session_state.last_interval_save = None
                    st.session_state.interval_start_time = None
                    
                    # Clear download state
                    st.session_state.show_download = False
                    st.session_state.csv_data = None
                    
                    # Clear comment field
                    if 'comment_field' in st.session_state:
                        del st.session_state.comment_field
                    
                    # Navigate to home
                    st.session_state.page = "home"
                    st.rerun()


def save_interval_data(collector, config):
    """Save data for all toggled buttons and reset them (similar to PyQt6)"""
    if not collector.is_observation_active():
        return
    
    button_states = st.session_state.get('button_states', {})
    
    # Save data for all toggled buttons
    for key, is_toggled in button_states.items():
        if is_toggled:
            # Parse category and label from key
            if key.startswith("student_"):
                category = "Student"
                label = key.replace("student_", "", 1)
                value = 1
            elif key.startswith("instructor_"):
                category = "Instructor"
                label = key.replace("instructor_", "", 1)
                value = 1
            elif key.startswith("engagement_"):
                category = "Engagement"
                label = key.replace("engagement_", "", 1)
                value = get_engagement_value(label)
            else:
                continue
            
            collector.record_response(category, label, value)
    
    # Clear button states after saving
    st.session_state.button_states = {}


def render_student_actions(config, collector, observation_type):
    """Render student actions section"""
    st.markdown("### Student Actions")
    
    student_actions = config.get('student_actions', [])
    if not student_actions:
        st.info("No student actions configured")
        return
    
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
                
                # Modify button key to include checked state for CSS targeting
                button_key = f"btn_{key}{'_checked' if checked else ''}"
                
                if st.button(label, key=button_key, help=text):
                    # Toggle the state
                    st.session_state.button_states[key] = not checked
                    st.rerun()
            else:
                # Click buttons for timepoint mode
                if st.button(f"**{label}**", key=f"btn_{key}", help=text):
                    collector.record_response("Student", label, 1)
                    st.success(f"Recorded: {label}")


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
                
                # Modify button key to include checked state for CSS targeting
                button_key = f"btn_{key}{'_checked' if checked else ''}"
                
                if st.button(label, key=button_key, help=text):
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
                
                # Modify button key to include checked state for CSS targeting
                button_key = f"btn_{key}{'_checked' if checked else ''}"
                
                if st.button(label, key=button_key, help=text):
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
            # Clear the field by deleting the key
            if 'comment_field' in st.session_state:
                del st.session_state.comment_field
            st.rerun()
        else:
            st.warning("Please enter a comment before saving.")


def get_engagement_value(label):
    """Get numeric value for engagement level"""
    engagement_values = {"Low": 1, "Medium": 2, "High": 3}
    return engagement_values.get(label, 1)


def create_csv_data_with_metadata(responses, metadata):
    """Create CSV data string with metadata using CSVExporter format"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Add metadata as comment lines (matching CSVExporter format)
    for key, value in metadata.items():
        writer.writerow([f"# {key}: {value}"])
    
    # Add empty line separator
    writer.writerow([])
    
    # Add data header and rows
    writer.writerow(["time_s", "category", "response", "value"])
    writer.writerows(responses)
    
    return output.getvalue()
