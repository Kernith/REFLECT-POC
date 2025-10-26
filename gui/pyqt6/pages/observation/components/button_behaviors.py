"""
Button behavior classes for different observation page types.
These classes define how buttons should behave and look.
"""

class ToggleButtonBehavior:
    """Behavior for toggle buttons used in interval observations"""
    
    def __init__(self):
        self.is_toggle = True
    
    def get_style_sheet(self, color):
        """Return stylesheet for toggle buttons"""
        return f"""
            QPushButton {{ 
                background-color: {color}; 
                color: white; 
                font-weight: bold; 
                border: 2px solid {color};
            }}
            QPushButton:checked {{ 
                background-color: #FFD700; 
                color: black; 
                border: 2px solid #FFD700;
            }}
        """
    
    def connect_button(self, btn, button_data, category, page):
        """Connect toggle button to appropriate handler"""
        btn.toggled.connect(lambda checked, label=button_data["label"], cat=category: 
                          page.toggle_button(cat, label, checked))


class ClickButtonBehavior:
    """Behavior for simple click buttons used in timepoint observations"""
    
    def __init__(self):
        self.is_toggle = False
    
    def get_style_sheet(self, color):
        """Return stylesheet for click buttons"""
        return f"QPushButton {{ background-color: {color}; color: white; font-weight: bold; overflow-wrap: break-word; }}"
    
    def connect_button(self, btn, button_data, category, page):
        """Connect click button to appropriate handler"""
        btn.clicked.connect(lambda _, label=button_data["label"]: 
                          page.record_response(category, label))
