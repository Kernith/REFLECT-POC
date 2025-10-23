# core/app_state.py
import json
from typing import Dict, Any, Optional
from core.util_functions import resource_path

class AppState:
    """Centralized application state manager"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._state = {
                'username': '',
                'current_observation_config': None,
                'user_settings': {},
                'app_settings': {}
            }
            self.load_initial_state()
            AppState._initialized = True
    
    def load_initial_state(self):
        """Load initial state from config files"""
        try:
            config_path = resource_path("config.json")
            with open(config_path, "r") as f:
                full_config = json.load(f)
            
            observation_configs = full_config.get("observation_configs", [])
            if observation_configs:
                self._state['current_observation_config'] = observation_configs[0].copy()
                self._state['current_observation_config']['colors'] = full_config.get("colors", {})
            else:
                self._state['current_observation_config'] = self.get_fallback_config()
                
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            self._state['current_observation_config'] = self.get_fallback_config()
    
    def get_fallback_config(self):
        """Return fallback configuration"""
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
    
    # Property getters
    def get_username(self) -> str:
        return self._state.get('username', '')
    
    def get_current_config(self) -> Dict[str, Any]:
        return self._state.get('current_observation_config', {})
    
    def get_user_settings(self) -> Dict[str, Any]:
        return self._state.get('user_settings', {})
    
    def get_app_settings(self) -> Dict[str, Any]:
        return self._state.get('app_settings', {})
    
    # Property setters
    def set_username(self, username: str):
        self._state['username'] = username
    
    def set_current_config(self, config: Dict[str, Any]):
        self._state['current_observation_config'] = config
    
    def set_user_settings(self, settings: Dict[str, Any]):
        self._state['user_settings'].update(settings)
    
    def set_app_settings(self, settings: Dict[str, Any]):
        self._state['app_settings'].update(settings)
    
    # Update methods
    def update_config(self, config_index: int):
        """Update current observation configuration"""
        try:
            config_path = resource_path("config.json")
            with open(config_path, "r") as f:
                full_config = json.load(f)
            observation_configs = full_config.get("observation_configs", [])
            if 0 <= config_index < len(observation_configs):
                self._state['current_observation_config'] = observation_configs[config_index].copy()
                self._state['current_observation_config']['colors'] = full_config.get("colors", {})
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass
