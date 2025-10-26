import streamlit as st


def render_home_page():
    """Render the home page"""
    st.title("🎓 REFLECT - Classroom Observation Tool")
    st.markdown("Welcome to REFLECT! Choose your observation method:")
    
    st.markdown("---")
    
    # Navigation buttons in a grid layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Interval Observation")
        st.markdown("Record behaviors in timed intervals (e.g., every 2 minutes)")
        if st.button("🕐 Start Interval Observation", use_container_width=True, type="primary"):
            st.session_state.page = "observation"
            st.session_state.observation_type = "interval"
            st.rerun()
    
    with col2:
        st.markdown("### ⏱️ Timepoint Observation")
        st.markdown("Record behaviors as they occur in real-time")
        if st.button("⚡ Start Timepoint Observation", use_container_width=True, type="primary"):
            st.session_state.page = "observation"
            st.session_state.observation_type = "timepoint"
            st.rerun()
    
    st.markdown("---")
    
    # Additional navigation options
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("📈 Data Analysis", use_container_width=True):
            st.session_state.page = "analysis"
            st.rerun()
    
    with col4:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.page = "settings"
            st.rerun()
    
    # Information section
    st.markdown("---")
    st.markdown("### ℹ️ About REFLECT")
    st.markdown("""
    REFLECT is a classroom observation tool designed to help educators:
    - **Observe** classroom behaviors systematically
    - **Analyze** teaching patterns and student engagement
    - **Reflect** on instructional effectiveness
    - **Improve** teaching practices through data-driven insights
    """)
    
    # Quick start guide
    with st.expander("🚀 Quick Start Guide"):
        st.markdown("""
        1. **Choose Observation Method**: Select interval or timepoint observation
        2. **Start Recording**: Click the appropriate button to begin
        3. **Record Behaviors**: Use the interface to log student and instructor actions
        4. **Save Data**: Download your observations as CSV files
        5. **Analyze Results**: Upload CSV files to view plots and statistics
        """)
