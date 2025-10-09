import time, csv, json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
from PyQt6.QtCore import QTimer, Qt

class ObservationPage(QWidget):
    def __init__(self, switch_page):
        super().__init__()
        self.switch_page = switch_page
        self.start_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.responses = []
        
        # Load button configuration
        self.button_config = self.load_button_config()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timer_label = QLabel("Timer: 0.0 s")
        self.timer_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.timer_label)

        btn_start = QPushButton("Start Survey")
        btn_start.clicked.connect(self.start_survey)
        layout.addWidget(btn_start)

        btn_row = QHBoxLayout()
        for button_data in self.button_config:
            b = QPushButton(button_data["label"])
            b.setFixedSize(80, 50)
            b.setToolTip(button_data.get("text", ""))  # Optional tooltip
            b.clicked.connect(lambda _, label=button_data["label"]: self.record_response(label))
            btn_row.addWidget(b)
        layout.addLayout(btn_row)

        btn_stop = QPushButton("Stop & Save")
        btn_stop.clicked.connect(self.stop_survey)
        layout.addWidget(btn_stop)

        btn_back = QPushButton("Back to Home")
        btn_back.clicked.connect(lambda: switch_page(0))
        layout.addWidget(btn_back)

        self.setLayout(layout)

    def load_button_config(self):
        """Load button configuration from config.json"""
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                return config.get("observation_buttons", [])
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            # Fallback to default buttons if config is missing or invalid
            QMessageBox.critical(self, "Error", "Could not load button configuration.")
            self.switch_page(0)
            return []

    def start_survey(self):
        self.start_time = time.time()
        self.responses = []
        self.timer.start(100)

    def update_timer(self):
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.timer_label.setText(f"Timer: {elapsed:.1f} s")

    def record_response(self, label):
        if not self.start_time:
            return
        t = time.time() - self.start_time
        self.responses.append((t, label))
        print(f"Recorded {label} at {t:.1f}s")

    def stop_survey(self):
        self.timer.stop()
        if not self.responses:
            QMessageBox.information(self, "No data", "No responses recorded.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Survey Data", "", "CSV Files (*.csv)"
        )
        if path:
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["time_s", "response"])
                writer.writerows(self.responses)
            QMessageBox.information(self, "Saved", f"Survey data saved to:\n{path}")
        self.switch_page(0)