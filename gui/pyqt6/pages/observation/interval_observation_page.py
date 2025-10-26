from PyQt6.QtWidgets import QPushButton, QMessageBox
from PyQt6.QtCore import QTimer
from gui.pyqt6.pages.observation.base_observation_page import BaseObservationPage
from gui.pyqt6.pages.observation.components.button_behaviors import ToggleButtonBehavior
from core.util_functions import get_current_time

class ObservationIntervalPage(BaseObservationPage):
    def __init__(self, switch_page, app_state):
        """run some additional init before running base init"""
        # Track button states for toggle functionality
        self.button_states = {}
        self.interval_timer = QTimer()
        self.interval_timer.timeout.connect(self.save_interval_data)
        
        super().__init__(switch_page, app_state)

    def get_button_behavior(self):
        """Return toggle button behavior for interval observations"""
        return ToggleButtonBehavior()
    
    def load_config(self):
        """Override to load timer interval from config"""
        super().load_config()
        # Get timer interval from config (convert to milliseconds, default 2 minutes)
        self.timer_interval = self.config.get("timer_interval", 120) * 1000

    def toggle_button(self, category, label, checked):
        """Handle button toggle state"""
        if not self.observation_collector.is_observation_active():
            return
        
        key = f"{category}_{label}"
        if checked:
            self.button_states[key] = True
            print(f"Toggled ON: {category} - {label}")
        else:
            self.button_states[key] = False
            print(f"Toggled OFF: {category} - {label}")

    def toggle_engagement_button(self, label, checked, clicked_button):
        """Handle engagement button toggle with radio button behavior"""
        if not self.observation_collector.is_observation_active():
            return
        
        if checked:
            # Uncheck all other engagement buttons
            for btn in self.engagement_buttons:
                if btn != clicked_button and btn.isChecked():
                    btn.setChecked(False)
            
            # Update button states
            self.button_states[f"Engagement_{label}"] = True
            print(f"Engagement selected: {label}")
        else:
            # If this button was unchecked, remove it from states
            key = f"Engagement_{label}"
            if key in self.button_states:
                del self.button_states[key]
            print(f"Engagement deselected: {label}")

    def save_comment(self):
        """Save the current comment and clear the field"""
        comment = self.comment_field.toPlainText().strip()
        if comment:
            self.record_response("Comment", comment)  # The value will be set automatically in record_response
            self.comment_field.clear()

    def start_observation(self):
        """Override to start interval timer"""
        super().start_observation()
        self.button_states = {}
        self.interval_timer.start(self.timer_interval)  # Start interval timer

    def save_interval_data(self):
        """Save data for all toggled buttons and reset them"""
        if not self.observation_collector.is_observation_active():
            return
        
        # Save data for all toggled buttons
        for key, is_toggled in self.button_states.items():
            if is_toggled:
                category, label = key.split("_", 1)
                # Determine value based on category
                if category == "Engagement":
                    engagement_values = {"Low": 1, "Medium": 2, "High": 3}
                    value = engagement_values.get(label, 1)
                else:  # Student and Instructor categories
                    value = 1
                
                self.observation_collector.record_response(category, label, value)
                print(f"Interval save: {category} - {label} (value: {value})")
        
        # Reset all buttons
        self.reset_all_buttons()
        
        # Clear button states
        self.button_states = {}

    def reset_all_buttons(self):
        """Reset all toggle buttons to unchecked state"""
        # Find all toggle buttons and uncheck them
        for widget in self.findChildren(QPushButton):
            if widget.isCheckable():
                widget.setChecked(False)

    def stop_observation(self):
        """Override to handle interval timer and save remaining data"""
        self.timer_adapter.stop()
        self.interval_timer.stop()
        
        # Save any remaining toggled buttons before stopping
        if self.observation_collector.is_observation_active():
            for key, is_toggled in self.button_states.items():
                if is_toggled:
                    category, label = key.split("_", 1)
                    # Determine value based on category
                    if category == "Engagement":
                        engagement_values = {"Low": 1, "Medium": 2, "High": 3}
                        value = engagement_values.get(label, 1)
                    else:  # Student and Instructor categories
                        value = 1
                    self.observation_collector.record_response(category, label, value)
        
        # Call parent stop_observation to handle the rest
        super().stop_observation()

    def handle_back_to_home(self):
        """Handle back to home button with confirmation if timer is running"""
        if self.observation_collector.is_observation_active():
            # Timer is running, show confirmation dialog
            reply = QMessageBox.question(
                self, 
                "Confirm Navigation", 
                "An observation is currently running. Are you sure you want to go back to home? This will stop the current observation.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                # Stop the observation and go back
                self.timer_adapter.stop()
                self.interval_timer.stop()
                self.observation_collector.stop_observation()
                self.switch_page(0)
        else:
            # Timer is not running, go back directly
            self.switch_page(0)
