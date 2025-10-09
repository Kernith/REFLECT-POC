from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt

class HomePage(QWidget):
    def __init__(self, switch_page):
        super().__init__()
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
        for b in (btn_new, btn_view):
            b.setFixedHeight(40)
            layout.addWidget(b)

        btn_new.clicked.connect(lambda: switch_page(1))
        btn_view.clicked.connect(lambda: switch_page(2))

        self.setLayout(layout)
