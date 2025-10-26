import streamlit as st
import pandas as pd
import io
import time
from backend.data.collectors.observation_collector import ObservationCollector
from backend.data.collectors.timer_service import TimerService
from backend.data.exporters.csv_exporter import CSVExporter
from gui.streamlit.adapters.timer_adapter import StreamlitTimerAdapter


def render_observation_page():
    """Render the observation page"""
    st.title("📝 Classroom Observation")
    
    # Navigation
    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"
        st.rerun()
    
    st.markdown("---")
    
    # Get observation type
    observation_type = st.session_state.get('observation_type', 'interval')
    
    # Initialize services
    if 'observation_collector' not in st.session_state:
        config = st.session_state.get('current_config', {})
        st.session_state.observation_collector = ObservationCollector(config)
        st.session_state.timer_service = TimerService()
        st.session_state.timer_adapter = StreamlitTimerAdapter(st.session_state.timer_service)
        st.session_state.csv_exporter = CSVExporter()
        st.session_state.button_states = {}
    
    collector = st.session_state.observation_collector
    timer_adapter = st.session_state.timer_adapter
    
    # Timer display and controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.metric("⏱️ Timer", timer_adapter.format_time())
    
    with col2:
        if not timer_adapter.is_running():
            if st.button("▶️ Start Observation", type="primary"):
                collector.start_observation()
                timer_adapter.start()
                st.session_state.button_states = {}
                st.rerun()
        else:
            if st.button("⏹️ Stop & Save", type="secondary"):
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
    
    with col3:
        if st.button("🔄 Reset"):
            timer_adapter.reset()
            collector.clear_responses()
            st.session_state.button_states = {}
            st.session_state.show_download = False
            st.rerun()
    
    # Show download button if data is available
    if st.session_state.get('show_download', False):
        st.success("✅ Observation completed! Download your data below.")
        csv_data = st.session_state.get('csv_data', '')
        if csv_data:
            st.download_button(
                label="📥 Download Observation Data",
                data=csv_data,
                file_name=f"observation_{int(time.time())}.csv",
                mime="text/csv",
                help="Download your observation data as CSV"
            )
    
    st.markdown("---")
    
    # Observation interface
    if timer_adapter.is_running():
        st.markdown(f"### 📊 Recording: {observation_type.title()} Mode")
        
        # Get current config
        config = st.session_state.get('current_config', {})
        
        # Create observation interface
        col1, col2, col3 = st.columns(3)
        
        with col1:
            render_student_actions(config, collector, observation_type)
        
        with col2:
            render_engagement_section(config, collector, observation_type)
        
        with col3:
            render_instructor_actions(config, collector, observation_type)
        
        # Comments section
        st.markdown("---")
        render_comments_section(collector)
        
        # Current observation summary
        st.markdown("---")
        render_observation_summary(collector)
    
    else:
        st.info("👆 Click 'Start Observation' to begin recording classroom behaviors")


def render_student_actions(config, collector, observation_type):
    """Render student actions section"""
    st.markdown("### 👨‍🎓 Student Actions")
    
    student_actions = config.get('student_actions', [])
    if not student_actions:
        st.info("No student actions configured")
        return
    
    for action in student_actions:
        label = action['label']
        text = action['text']
        key = f"student_{label}"
        
        if observation_type == "interval":
            # Toggle buttons for interval mode
            checked = st.session_state.button_states.get(key, False)
            if st.checkbox(f"**{label}**", value=checked, key=f"cb_{key}"):
                st.session_state.button_states[key] = True
            else:
                st.session_state.button_states[key] = False
            
            st.caption(text)
        else:
            # Click buttons for timepoint mode
            if st.button(f"**{label}**", key=f"btn_{key}", help=text):
                collector.record_response("Student", label, 1)
                st.success(f"Recorded: {label}")


def render_instructor_actions(config, collector, observation_type):
    """Render instructor actions section"""
    st.markdown("### 👨‍🏫 Instructor Actions")
    
    instructor_actions = config.get('instructor_actions', [])
    if not instructor_actions:
        st.info("No instructor actions configured")
        return
    
    for action in instructor_actions:
        label = action['label']
        text = action['text']
        key = f"instructor_{label}"
        
        if observation_type == "interval":
            # Toggle buttons for interval mode
            checked = st.session_state.button_states.get(key, False)
            if st.checkbox(f"**{label}**", value=checked, key=f"cb_{key}"):
                st.session_state.button_states[key] = True
            else:
                st.session_state.button_states[key] = False
            
            st.caption(text)
        else:
            # Click buttons for timepoint mode
            if st.button(f"**{label}**", key=f"btn_{key}", help=text):
                collector.record_response("Instructor", label, 1)
                st.success(f"Recorded: {label}")


def render_engagement_section(config, collector, observation_type):
    """Render engagement section"""
    st.markdown("### 📊 Student Engagement")
    
    engagement_levels = config.get('engagement_images', [])
    if not engagement_levels:
        st.info("No engagement levels configured")
        return
    
    if observation_type == "interval":
        # Radio buttons for interval mode (only one selection)
        selected_engagement = st.session_state.get('selected_engagement', None)
        
        for level in engagement_levels:
            label = level['label']
            text = level['text']
            key = f"engagement_{label}"
            
            if st.radio(f"**{label}**", [False, True], key=f"radio_{key}", 
                       format_func=lambda x: "Selected" if x else "Not Selected"):
                # Unselect others
                for other_level in engagement_levels:
                    if other_level['label'] != label:
                        st.session_state[f"radio_engagement_{other_level['label']}"] = False
                st.session_state['selected_engagement'] = label
                st.session_state.button_states[key] = True
            else:
                st.session_state.button_states[key] = False
            
            st.caption(text)
    else:
        # Click buttons for timepoint mode
        for level in engagement_levels:
            label = level['label']
            text = level['text']
            key = f"engagement_{label}"
            
            if st.button(f"**{label}**", key=f"btn_{key}", help=text):
                collector.record_response("Engagement", label, get_engagement_value(label))
                st.success(f"Recorded: {label}")


def render_comments_section(collector):
    """Render comments section"""
    st.markdown("### 💬 Comments")
    
    comment = st.text_area("Add a comment:", key="comment_field", height=100)
    
    if st.button("💾 Save Comment"):
        if comment.strip():
            collector.record_response("Comment", comment.strip())
            st.success("Comment saved!")
            st.session_state.comment_field = ""  # Clear the field
            st.rerun()
        else:
            st.warning("Please enter a comment before saving.")


def render_observation_summary(collector):
    """Render current observation summary"""
    st.markdown("### 📈 Current Observation Summary")
    
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
