import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from pages.home_page import HomePage
from pages.observation.interval_observation_page import ObservationIntervalPage
from pages.observation.timepoint_observation_page import ObservationTimepointPage
from pages.analysis.analysis_page import AnalysisPage
from pages.settings_page import SettingsPage
from core.app_state import AppState

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stack = QStackedWidget()
        self.app_state = AppState()
        
        self.resize(int(1532/1.25), int(659/1.25))

        # Define page classes in order
        self.page_classes = [
            HomePage,
            ObservationIntervalPage,
            ObservationTimepointPage,
            AnalysisPage,
            SettingsPage
        ]
        
        # Add a placeholder widget initially
        from PyQt6.QtWidgets import QWidget
        placeholder = QWidget()
        self.stack.addWidget(placeholder)

        self.setCentralWidget(self.stack)
        self.setWindowTitle("REFLECT App")

    def switch_page(self, index):
        # Validate index
        if 0 <= index < len(self.page_classes):
            # Create new page instance
            page_class = self.page_classes[index]
            new_page = page_class(self.switch_page, self.app_state)
            self.stack.addWidget(new_page)
            self.stack.setCurrentWidget(new_page)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    # Start with home page
    window.switch_page(0)
    sys.exit(app.exec())