import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from pages.home_page import HomePage
from pages.observation_interval_page import ObservationIntervalPage
from pages.observation_timepoint_page import ObservationTimepointPage
from pages.analysis_page import AnalysisPage
from pages.settings_page import SettingsPage
import json
from utils.paths import resource_path

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stack = QStackedWidget()
        
        # Load the first observation config as the default
        self.current_observation_config = self.load_default_config()

        self.pages = [
            HomePage(self.switch_page, self.get_current_config),
            ObservationIntervalPage(self.switch_page, self.get_current_config),
            ObservationTimepointPage(self.switch_page, self.get_current_config),
            AnalysisPage(self.switch_page),
            SettingsPage(self.switch_page, self.update_config)
        ]

        for page in self.pages:
            self.stack.addWidget(page)

        self.setCentralWidget(self.stack)
        self.setWindowTitle("REFLECT App")

    def load_default_config(self):
        """Load the first observation config as default"""
        try:
            config_path = resource_path("config.json")
            with open(config_path, "r") as f:
                full_config = json.load(f)
            observation_configs = full_config.get("observation_configs", [])
            if observation_configs:
                config = observation_configs[0].copy()
                # Add colors from the main config
                config["colors"] = full_config.get("colors", {})
                return config
            else:
                return self.get_fallback_config()
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return self.get_fallback_config()
    
    def get_fallback_config(self):
        """Return a fallback configuration"""
        return {
            "name": "Default",
            "timer_method": "timepoint",
            "timer_interval": 0,
            "student_actions": [],
            "instructor_actions": [],
            "engagement_images": [],
            "colors": {
                "student": "#F46715",
                "engagement": "#4169E1", 
                "instructor": "#0C8346",
                "comments": "#808080",
                "carmine": "#931621"
            }
        }
    
    def get_current_config(self):
        """Get the current observation configuration"""
        return self.current_observation_config
    
    def update_config(self, config_index):
        """Update the current observation configuration"""
        try:
            config_path = resource_path("config.json")
            with open(config_path, "r") as f:
                full_config = json.load(f)
            observation_configs = full_config.get("observation_configs", [])
            if 0 <= config_index < len(observation_configs):
                self.current_observation_config = observation_configs[config_index].copy()
                # Add colors from the main config
                self.current_observation_config["colors"] = full_config.get("colors", {})
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass  # Keep current config if loading fails

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())