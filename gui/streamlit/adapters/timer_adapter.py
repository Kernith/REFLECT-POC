import streamlit as st
from backend.data.collectors.timer_service import TimerService


class StreamlitTimerAdapter:
    """Adapter to use TimerService with Streamlit session state"""
    
    def __init__(self, timer_service: TimerService):
        self.timer_service = timer_service
    
    def start(self):
        """Start the timer"""
        self.timer_service.start()
        st.session_state.timer_running = True
    
    def stop(self):
        """Stop the timer"""
        self.timer_service.stop()
        st.session_state.timer_running = False
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time"""
        return self.timer_service.get_elapsed_time()
    
    def format_time(self) -> str:
        """Format elapsed time"""
        return self.timer_service.format_time()
    
    def is_running(self) -> bool:
        """Check if timer is running"""
        return st.session_state.get('timer_running', False)
    
    def reset(self):
        """Reset the timer"""
        self.timer_service.reset()
        st.session_state.timer_running = False
