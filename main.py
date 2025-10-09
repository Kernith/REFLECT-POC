import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from pages.home_page import HomePage
from pages.observation_page import ObservationPage
from pages.analysis_page import AnalysisPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.stack = QStackedWidget()

        self.pages = [
            HomePage(self.switch_page),
            ObservationPage(self.switch_page),
            AnalysisPage(self.switch_page)
        ]

        for page in self.pages:
            self.stack.addWidget(page)

        self.setCentralWidget(self.stack)
        self.setWindowTitle("REFLECT App")
        self.resize(1280, 720)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
