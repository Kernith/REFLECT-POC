from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QComboBox, QGroupBox, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt
import json
from utils.paths import resource_path

class SettingsPage(QWidget):
    def __init__(self, switch_page, update_config):
        super().__init__()
        self.switch_page = switch_page
        self.update_config = update_config
        self.config_data = {}
        self.current_config_index = 0
        
        # Load configuration
        self.load_config()
        
        # Create UI
        self.setup_ui()
        
    def load_config(self):
        """Load configuration from config.json"""
        try:
            config_path = resource_path("config.json")
            with open(config_path, "r") as f:
                self.config_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            QMessageBox.critical(self, "Error", f"Could not load configuration: {e}")
            self.switch_page(0)
            return
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Observation Config Selection
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
        
        # Config description
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("margin-top: 10px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        config_layout.addWidget(self.description_label)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Config Details
        details_group = QGroupBox("Configuration Details")
        details_layout = QVBoxLayout()
        
        # Show current config details
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        details_layout.addWidget(self.details_text)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self.save_settings)
        button_layout.addWidget(btn_save)
        
        btn_back = QPushButton("Back to Home")
        btn_back.clicked.connect(lambda: self.switch_page(0))
        button_layout.addWidget(btn_back)
        
        layout.addLayout(button_layout)
        
        # Update display with current selection
        self.update_config_display()
        
        self.setLayout(layout)
    
    def populate_config_combo(self):
        """Populate the configuration dropdown"""
        configs = self.config_data.get("observation_configs", [])
        for i, config in enumerate(configs):
            self.config_combo.addItem(config.get("name", f"Config {i+1}"))
    
    def on_config_changed(self, index):
        """Handle configuration selection change"""
        self.current_config_index = index
        self.update_config_display()
    
    def update_config_display(self):
        """Update the display with current configuration details"""
        configs = self.config_data.get("observation_configs", [])
        if not configs or self.current_config_index >= len(configs):
            return
            
        current_config = configs[self.current_config_index]
        
        # Update description
        description = current_config.get("description", "No description available.")
        self.description_label.setText(f"{description}")
        
        # Update details
        details = self.format_config_details(current_config)
        self.details_text.setPlainText(details)
    
    def format_config_details(self, config):
        """Format configuration details for display"""
        details = []
        
        # timer settings
        timer_method = config.get("timer_method", "No method set")
        details.append(f"Timer Method: {timer_method}")
        timer_interval = config.get("timer_interval", "No interval")
        if timer_interval < 120:
            interval_string = f"{timer_interval} seconds"
        else:
            interval_string = f"{round(timer_interval/60, 1)} minutes"
        details.append(f"Timer Interval: {interval_string}")
        details.append("")

        # Student actions
        student_actions = config.get("student_actions", [])
        details.append(f"Student Actions ({len(student_actions)}):")
        for action in student_actions:
            details.append(f"  • {action.get('label', 'N/A')}: {action.get('text', 'No description')}")
        details.append("")
        
        # Instructor actions
        instructor_actions = config.get("instructor_actions", [])
        details.append(f"Instructor Actions ({len(instructor_actions)}):")
        for action in instructor_actions:
            details.append(f"  • {action.get('label', 'N/A')}: {action.get('text', 'No description')}")
        details.append("")
        
        # Engagement levels
        engagement = config.get("engagement_images", [])
        details.append(f"Engagement Levels ({len(engagement)}):")
        for level in engagement:
            details.append(f"  • {level.get('label', 'N/A')}: {level.get('text', 'No description')}")
        
        return "\n".join(details)
    
    def save_settings(self):
        """Save the current settings and update the global config"""
        # Update the global configuration
        self.update_config(self.current_config_index)
        