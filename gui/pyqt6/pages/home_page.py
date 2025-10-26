# gui/pyqt6/pages/home_page.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt

class HomePage(QWidget):
    def __init__(self, switch_page, app_state):
        super().__init__()
        self.switch_page = switch_page
        self.app_state = app_state
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel()
        title.setText("""
        <b style="font-size:24px;">REFLECT</b>
        <br>
        <span style="font-size:18px;">
        <b><span style="color:#007ACC;">R</span></b>esearch &amp;
        <b><span style="color:#007ACC;">E</span></b>valuation
        <b><span style="color:#007ACC;">F</span></b>ramework for
        <br>
        <b><span style="color:#007ACC;">L</span></b>earning,
        <b><span style="color:#007ACC;">E</span></b>ngagement,
        <b><span style="color:#007ACC;">C</span></b>ollaboration, and
        <b><span style="color:#007ACC;">T</span></b>racking
        </span>
        """)
        layout.addWidget(title)

        self.btn_new = QPushButton()  # Store reference to button
        self.btn_view = QPushButton("View Observation Data")
        self.btn_settings = QPushButton("Settings")
        
        for b in (self.btn_new, self.btn_view, self.btn_settings):
            b.setFixedHeight(40)
            layout.addWidget(b)

        self.btn_new.clicked.connect(self.start_new_observation)
        self.btn_view.clicked.connect(lambda: switch_page(3))
        self.btn_settings.clicked.connect(lambda: switch_page(4))

        self.setLayout(layout)
        
        # Initial update of button text
        self.update_display()
    
    def update_display(self):
        """Update the display with current configuration"""
        current_config = self.app_state.get_current_config()
        config_name = current_config.get('name', 'no config')
        self.btn_new.setText(f"Start New Observation ({config_name})")
    
    def showEvent(self, event):
        """Called when the page becomes visible"""
        super().showEvent(event)
        self.update_display()
    
    def start_new_observation(self):
        """Route to the appropriate observation page based on current config"""
        current_config = self.app_state.get_current_config()
        timer_method = current_config.get("timer_method", "interval")
        
        if timer_method == "interval":
            self.switch_page(1)
        else:
            self.switch_page(2)
    