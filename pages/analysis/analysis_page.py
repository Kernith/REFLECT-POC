from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFileDialog, QMessageBox, QScrollArea, 
                            QFrame, QTextEdit, QSplitter)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from pages.analysis.services.analysis_orchestrator import AnalysisOrchestrator
from pages.analysis.services.pdf_export_service import PDFExportService
from pages.analysis.components.summary_section import SummarySection
from pages.analysis.components.statistics_section import StatisticsSection
from pages.analysis.components.timeline_section import TimelineSection
from pages.analysis.components.comments_section import CommentsSection
from pages.analysis.components.time_series_section import TimeSeriesSection
from pages.analysis.components.distribution_section import DistributionSection
from services.analysis.statistics_calculator import StatisticsCalculator
from services.analysis.insights_generator import InsightsGenerator
from services.visualization.plot_factory import PlotFactory

class AnalysisPage(QWidget):
    def __init__(self, switch_page, app_state):
        super().__init__()
        self.switch_page = switch_page
        self.app_state = app_state
        self.df = None
        
        # Get color configuration from app state
        colors = self.get_colors_from_app_state()
        
        # Initialize orchestrator and services
        self.orchestrator = AnalysisOrchestrator(colors)
        self.statistics_calculator = StatisticsCalculator()
        self.insights_generator = InsightsGenerator()
        self.plot_factory = PlotFactory()
        
        # Initialize PDF export service
        self.pdf_export_service = PDFExportService(
            self.statistics_calculator,
            self.insights_generator,
            self.plot_factory,
            self.orchestrator.get_color_manager()
        )
        
        # Initialize UI components
        self.summary_section = SummarySection(self.statistics_calculator)
        self.statistics_section = StatisticsSection(self.statistics_calculator)
        self.timeline_section = TimelineSection(self.insights_generator)
        self.comments_section = CommentsSection()
        self.time_series_section = TimeSeriesSection(self.plot_factory, self.orchestrator.get_color_manager())
        self.distribution_section = DistributionSection(self.plot_factory, self.orchestrator.get_color_manager())

        # Create main layout
        main_layout = QVBoxLayout()
        
        # Top controls
        controls_layout = QHBoxLayout()
        
        self.label = QLabel("Open a CSV file to view responses")
        controls_layout.addWidget(self.label)
        
        btn_open = QPushButton("Open Data File")
        btn_open.clicked.connect(self.load_data)
        controls_layout.addWidget(btn_open)
        
        self.btn_export = QPushButton("Export to PDF")
        self.btn_export.clicked.connect(self.export_to_pdf)
        self.btn_export.setEnabled(False)
        controls_layout.addWidget(self.btn_export)
        
        btn_back = QPushButton("Back to Home")
        btn_back.clicked.connect(lambda: switch_page(0))
        controls_layout.addWidget(btn_back)
        
        main_layout.addLayout(controls_layout)
        
        # Create scrollable area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("border: none; background: transparent;")
        
        # Content widget for scrollable area
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        
        # Initial message
        self.initial_label = QLabel("Open a CSV file to view analysis")
        self.initial_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.initial_label.setStyleSheet("font-size: 16px; color: gray; padding: 50px;")
        self.content_layout.addWidget(self.initial_label)
        
        scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)

    def get_colors_from_app_state(self):
        """Get color configuration from app state"""
        current_config = self.app_state.get_current_config()
        colors = current_config.get("colors", {})
        
        # If no colors in current config, try to get from app settings
        if not colors:
            app_settings = self.app_state.get_app_settings()
            colors = app_settings.get("colors", {})
        
        # Fallback colors if no colors are available
        if not colors:
            colors = {
                "student": "#FFA500",
                "engagement": "#4169E1", 
                "instructor": "#32CD32",
                "comments": "#808080"
            }
        
        return colors

    def load_data(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Data File", "data", "CSV Files (*.csv)"
        )
        if not path:
            return
        
        result = self.orchestrator.load_and_validate_data(path)
        
        if result.success:
            self.df = result.data
            self.label.setText(f"Loaded: {path.split('/')[-1]}")
            self.btn_export.setEnabled(True)
            self.create_analysis_content()
        else:
            QMessageBox.critical(self, "Error", result.error)

    def clear_content(self):
        """Clear existing content from the scrollable area"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def create_analysis_content(self):
        """Create UI components using the new component architecture"""
        if self.df is None:
            return  
        self.clear_content()

        # Create sections using individual components
        self.content_layout.addWidget(self.summary_section.create_section(self.df))  # Summary Statistics
        self.content_layout.addWidget(self.time_series_section.create_section(self.df))  # Time Series Plot
        self.content_layout.addWidget(self.comments_section.create_section(self.df))  # Comments Timeline
        self.content_layout.addWidget(self.distribution_section.create_section(self.df))  # Category Distribution
        self.content_layout.addWidget(self.statistics_section.create_section(self.df))  # Response Statistics by Category
        self.content_layout.addWidget(self.timeline_section.create_section(self.df))  # Timeline Analysis

    def export_to_pdf(self):
        """Export analysis to PDF"""
        if self.df is None:
            QMessageBox.warning(self, "No Data", "Please load data first before exporting.")
            return
            
        path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF Report", "", "PDF Files (*.pdf)"
        )
        if not path:
            return
            
        # Use PDF export service
        success = self.pdf_export_service.export_analysis_report(
            self.df, path, self.label.text()
        )
        
        if success:
            QMessageBox.information(self, "Success", f"PDF report saved to: {path}")
        else:
            QMessageBox.critical(self, "Error", "Failed to export PDF")
