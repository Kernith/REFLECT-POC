from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QComboBox, QGroupBox, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt
import json
from utils.util_functions import resource_path

class SettingsPage(QWidget):
    # Constants
    MAX_DETAILS_HEIGHT = 200
    LAYOUT_SPACING = 20
    TITLE_FONT_SIZE = 24
    DESCRIPTION_PADDING = 10
    
    def __init__(self, switch_page, app_state):
        super().__init__()
        self.switch_page = switch_page
        self.app_state = app_state

        self.config_data = {}
        self.load_config()
        self.current_config_index = self.get_current_config_index()

        self.setup_ui()
        
    def get_observation_configs(self):
        """Get the list of observation configurations"""
        return self.config_data.get("observation_configs", [])
    
    def get_current_config_index(self):
        """Get the index of the currently active configuration"""
        current_config = self.app_state.get_current_config()
        current_name = current_config.get("name", "")
        
        configs = self.get_observation_configs()
        for i, config in enumerate(configs):
            if config.get("name", "") == current_name:
                return i
        
        # Fallback to first config if not found
        return 0
        
    def load_config(self):
        """Load configuration from config.json"""
        try:
            config_path = resource_path("config.json")
            with open(config_path, "r") as f:
                self.config_data = json.load(f)
            
            # Validate configuration structure
            if not self.validate_config():
                QMessageBox.warning(self, "Warning", "Configuration file has invalid structure. Using defaults.")
                self.config_data = {"observation_configs": []}
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            QMessageBox.critical(self, "Error", f"Could not load configuration: {e}")
            self.switch_page(0)
            return
    
    def validate_config(self):
        """Validate the loaded configuration structure"""
        if not isinstance(self.config_data, dict):
            return False
        
        observation_configs = self.config_data.get("observation_configs", [])
        if not isinstance(observation_configs, list):
            return False
        
        # Validate each config has required fields
        for config in observation_configs:
            if not isinstance(config, dict) or "name" not in config:
                return False
        
        return True
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(self.LAYOUT_SPACING)
        
        self.add_title(layout)
        self.add_config_selection(layout)
        self.add_config_details(layout)
        self.add_buttons(layout)
        
        self.setLayout(layout)
        
        # Update display with current selection after UI is fully set up
        self.update_config_display()
    
    def add_title(self, layout):
        """Add the page title"""
        title = QLabel("Settings")
        title.setStyleSheet(f"font-size: {self.TITLE_FONT_SIZE}px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
    
    def add_config_selection(self, layout):
        """Add the configuration selection group"""
        config_group = QGroupBox()
        config_layout = QVBoxLayout()
        config_group.setStyleSheet("QGroupBox { border: none; }")
        
        # Config selection dropdown
        config_label = QLabel("Select Observation Protocol:")
        config_layout.addWidget(config_label)
        
        self.config_combo = QComboBox()
        self.populate_config_combo()
        self.config_combo.currentIndexChanged.connect(self.on_config_changed)
        config_layout.addWidget(self.config_combo)
        
        self.set_current_config_selection()
        
        # Config description
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet(f"margin-top: 10px; padding: {self.DESCRIPTION_PADDING}px; background-color: #f0f0f0; border-radius: 5px;")
        config_layout.addWidget(self.description_label)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
    
    def add_config_details(self, layout):
        """Add the configuration details group"""
        details_group = QGroupBox("Configuration Details")
        details_layout = QVBoxLayout()
        
        # Show current config details
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(self.MAX_DETAILS_HEIGHT)
        details_layout.addWidget(self.details_text)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
    
    def add_buttons(self, layout):
        """Add the action buttons"""
        button_layout = QHBoxLayout()
        
        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self.save_settings)
        button_layout.addWidget(btn_save)
        
        btn_back = QPushButton("Back to Home")
        btn_back.clicked.connect(lambda: self.switch_page(0))
        button_layout.addWidget(btn_back)
        
        layout.addLayout(button_layout)
    
    def populate_config_combo(self):
        """Populate the configuration dropdown"""
        configs = self.get_observation_configs()
        for i, config in enumerate(configs):
            self.config_combo.addItem(config.get("name", f"Config {i+1}"))
    
    def set_current_config_selection(self):
        """Set the dropdown to show the currently active configuration"""
        # Use the already-calculated index instead of searching again
        if 0 <= self.current_config_index < self.config_combo.count():
            self.config_combo.setCurrentIndex(self.current_config_index)
        else:
            # Fallback to first item if index is invalid
            self.config_combo.setCurrentIndex(0)
            self.current_config_index = 0
    
    def on_config_changed(self, index):
        """Handle configuration selection change"""
        self.current_config_index = index
        self.update_config_display()
    
    def update_config_display(self):
        """Update the display with current configuration details"""
        configs = self.get_observation_configs()
        if not configs or self.current_config_index >= len(configs):
            return
            
        current_config = configs[self.current_config_index]
        
        # Update description and details (only if UI elements exist)
        description = current_config.get("description", "No description available.")
        if hasattr(self, 'description_label'):
            self.description_label.setText(f"{description}")
        if hasattr(self, 'details_text'):
            details = self.format_config_details(current_config)
            self.details_text.setPlainText(details)
    
    def extract_config_data(self, config):
        """Extract configuration data for formatting"""
        return {
            'timer_method': config.get("timer_method", "No method set"),
            'timer_interval': config.get("timer_interval", "No interval"),
            'student_actions': config.get("student_actions", []),
            'instructor_actions': config.get("instructor_actions", []),
            'engagement_images': config.get("engagement_images", [])
        }
    
    def format_config_details(self, config):
        """Format configuration details for display"""
        data = self.extract_config_data(config)
        details = []
        
        # Timer settings
        details.append(f"Timer Method: {data['timer_method']}")
        details.append(f"Timer Interval: {self.format_timer_interval(data['timer_interval'])}")
        details.append("")

        # Student actions
        details.append(f"Student Actions ({len(data['student_actions'])}):")
        for action in data['student_actions']:
            details.append(f"  • {action.get('label', 'N/A')}: {action.get('text', 'No description')}")
        details.append("")
        
        # Instructor actions
        details.append(f"Instructor Actions ({len(data['instructor_actions'])}):")
        for action in data['instructor_actions']:
            details.append(f"  • {action.get('label', 'N/A')}: {action.get('text', 'No description')}")
        details.append("")
        
        # Engagement levels
        details.append(f"Engagement Levels ({len(data['engagement_images'])}):")
        for level in data['engagement_images']:
            details.append(f"  • {level.get('label', 'N/A')}: {level.get('text', 'No description')}")
        
        return "\n".join(details)
    
    def format_timer_interval(self, interval):
        """Format timer interval for display"""
        if isinstance(interval, (int, float)) and interval < 120:
            return f"{interval} seconds"
        elif isinstance(interval, (int, float)):
            return f"{round(interval/60, 1)} minutes"
        else:
            return str(interval)
    
    def save_settings(self):
        """Save the current settings and update the app state"""
        # Update the app state with the new configuration
        self.app_state.update_config(self.current_config_index)
        self.switch_page(0)
        