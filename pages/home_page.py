from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
import json
from utils.paths import resource_path

class HomePage(QWidget):
    def __init__(self, switch_page, get_current_config):
        super().__init__()
        self.switch_page = switch_page
        self.get_current_config = get_current_config
        
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

        btn_new = QPushButton("Start New Observation")
        btn_view = QPushButton("View Observation Data")
        btn_settings = QPushButton("Settings")
        
        for b in (btn_new, btn_view, btn_settings):
            b.setFixedHeight(40)
            layout.addWidget(b)

        btn_new.clicked.connect(self.start_new_observation)
        btn_view.clicked.connect(lambda: switch_page(3))  # Analysis page
        btn_settings.clicked.connect(lambda: switch_page(4))  # Settings page

        self.setLayout(layout)
    
    def start_new_observation(self):
        """Route to the appropriate observation page based on current config"""
        current_config = self.get_current_config()
        timer_method = current_config.get("timer_method", "interval")
        
        if timer_method == "interval":
            self.switch_page(1)  # ObservationIntervalPage
        else:  # timepoint
            self.switch_page(2)  # ObservationTimepointPage