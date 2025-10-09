import time, csv
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

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timer_label = QLabel("Timer: 0.0 s")
        self.timer_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.timer_label)

        btn_start = QPushButton("Start Survey")
        btn_start.clicked.connect(self.start_survey)
        layout.addWidget(btn_start)

        btn_row = QHBoxLayout()
        for label in ["👍", "👎", "❓"]:
            b = QPushButton(label)
            b.setFixedSize(80, 50)
            b.clicked.connect(lambda _, l=label: self.record_response(l))
            btn_row.addWidget(b)
        layout.addLayout(btn_row)

        btn_stop = QPushButton("Stop & Save")
        btn_stop.clicked.connect(self.stop_survey)
        layout.addWidget(btn_stop)

        btn_back = QPushButton("Back to Home")
        btn_back.clicked.connect(lambda: switch_page(0))
        layout.addWidget(btn_back)

        self.setLayout(layout)

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
