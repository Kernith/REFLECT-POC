from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
import pandas as pd
import json
from widgets.mpl_canvas import MplCanvas
from utils.paths import resource_path

class AnalysisPage(QWidget):
    def __init__(self, switch_page):
        super().__init__()
        self.switch_page = switch_page
        
        # Load color configuration
        self.colors = self.load_colors()

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

    def load_colors(self):
        """Load color configuration from config.json"""
        try:
            config_path = resource_path("config.json")
            with open(config_path, "r") as f:
                config = json.load(f)
                return config.get("colors", {})
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback colors if config is not available
            return {
                "student": "#FFA500",
                "engagement": "#4169E1", 
                "instructor": "#32CD32",
                "comments": "#808080"
            }

    def get_bar_color(self, category):
        """Determine the color for a response based on its category"""
        if category == "Student":
            return self.colors.get("student", "#FFA500")
        elif category == "Instructor":
            return self.colors.get("instructor", "#32CD32")
        elif category == "Engagement":
            return self.colors.get("engagement", "#4169E1")
        elif category == "Comment":
            return self.colors.get("comments", "#808080")
        else:
            return "#CCCCCC"  # Default gray for unknown categories

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
        if "time_s" in df.columns and "category" in df.columns and "response" in df.columns:
            # Create scatter plot with responses on y-axis
            for category in df["category"].unique():
                category_data = df[df["category"] == category]
                x_values = category_data["time_s"]
                y_values = category_data["response"]
                
                # Plot points for this category with appropriate color
                self.canvas.ax.scatter(x_values, y_values, 
                                    c=self.get_bar_color(category), 
                                    label=category, 
                                    alpha=0.7, 
                                    s=50)
            
            # Set up the plot
            self.canvas.ax.set_xlabel("Time (seconds)")
            self.canvas.ax.set_ylabel("Response")
            self.canvas.ax.set_title("Survey Responses Over Time")
            
            # Add legend
            self.canvas.ax.legend()
            
            # Add grid for better readability
            self.canvas.ax.grid(True, alpha=0.3)
            
        else:
            self.canvas.ax.text(0.5, 0.5, "Invalid CSV format - requires 'time_s', 'category', and 'response' columns",
                            ha='center', va='center')
        self.canvas.draw()
    