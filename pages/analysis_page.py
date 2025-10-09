from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
import pandas as pd
from widgets.mpl_canvas import MplCanvas

class AnalysisPage(QWidget):
    def __init__(self, switch_page):
        super().__init__()
        self.switch_page = switch_page

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel("Open a CSV file to view responses")
        layout.addWidget(self.label)

        btn_open = QPushButton("Open Data File")
        btn_open.clicked.connect(self.load_data)
        layout.addWidget(btn_open)

        self.canvas = MplCanvas()
        layout.addWidget(self.canvas)

        btn_back = QPushButton("Back to Home")
        btn_back.clicked.connect(lambda: switch_page(0))
        layout.addWidget(btn_back)

        self.setLayout(layout)

    def load_data(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Data File", "", "CSV Files (*.csv)"
        )
        if not path:
            return
        try:
            df = pd.read_csv(path)
            self.label.setText(f"Loaded: {path}")
            self.plot_data(df)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{e}")

    def plot_data(self, df):
        self.canvas.ax.clear()
        if "time_s" in df.columns and "response" in df.columns:
            counts = df["response"].value_counts()
            counts.plot(kind="bar", ax=self.canvas.ax)
            self.canvas.ax.set_xlabel("Response")
            self.canvas.ax.set_ylabel("Count")
            self.canvas.ax.set_title("Survey Results")
        else:
            self.canvas.ax.text(0.5, 0.5, "Invalid CSV format",
                                ha='center', va='center')
        self.canvas.draw()
