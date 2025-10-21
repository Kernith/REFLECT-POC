from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFileDialog, QMessageBox, QScrollArea, 
                            QFrame, QTextEdit, QSplitter)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from utils.analysis_service import AnalysisService
from utils.pdf_exporter import PDFExporter

class AnalysisPage(QWidget):
    def __init__(self, switch_page, app_state):
        super().__init__()
        self.switch_page = switch_page
        self.app_state = app_state
        self.df = None
        
        # Get color configuration from app state
        colors = self.get_colors_from_app_state()
        
        # Initialize services
        self.analysis_service = AnalysisService(colors)
        self.pdf_exporter = PDFExporter(self.analysis_service)

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
        
        # Content widget for scrollable area
        self.content_widget = QWidget()
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
        
        # Use analysis service to load and validate data
        result = self.analysis_service.load_and_validate_data(path)
        
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
        """Create comprehensive analysis content"""
        if self.df is None:
            return  
        self.clear_content()

        # 1. Summary Statistics
        self.add_summary_section()
        
        # 2. Time Series Plot
        self.add_time_series_plot()
        
        # 3. Category Distribution
        self.add_category_distribution()
        
        # 4. Response Statistics by Category
        self.add_response_statistics()
        
        # 5. Timeline Analysis
        self.add_timeline_analysis()

    def add_summary_section(self):
        """Add summary statistics section"""
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.Shape.Box)
        summary_layout = QVBoxLayout()
        
        title = QLabel("Data Summary")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        summary_layout.addWidget(title)
        
        # Use analysis service to get summary statistics
        summary = self.analysis_service.generate_summary_statistics(self.df)
        
        summary_text = f"""
        <b>Dataset Overview:</b><br>
        • Total Responses: {summary['total_responses']}<br>
        • Categories: {summary['unique_categories']} ({', '.join(summary['categories'])})
        • Time Span: {summary['time_span_seconds']:.1f} seconds ({summary['time_span_minutes']:.1f} minutes)<br>
        • Average Response Time: {summary['avg_response_time']:.1f} seconds<br>
        • Value Range: {summary['value_range'][0]} - {summary['value_range'][1]}<br>
        """
        
        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        summary_layout.addWidget(summary_label)
        
        summary_frame.setLayout(summary_layout)
        self.content_layout.addWidget(summary_frame)

    def add_time_series_plot(self):
        """Add time series scatter plot"""
        plot_frame = QFrame()
        plot_frame.setFrameStyle(QFrame.Shape.Box)
        plot_layout = QVBoxLayout()
        
        title = QLabel("Response Timeline")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        plot_layout.addWidget(title)
        
        # Use plot generator to create the plot
        canvas = self.analysis_service.get_plot_generator().create_time_series_plot(self.df)
        
        plot_layout.addWidget(canvas)
        plot_frame.setLayout(plot_layout)
        self.content_layout.addWidget(plot_frame)

    def add_category_distribution(self):
        """Add three pie charts for engagement, instructor, and student actions"""
        plot_frame = QFrame()
        plot_frame.setFrameStyle(QFrame.Shape.Box)
        plot_layout = QVBoxLayout()
        
        title = QLabel("Response Distribution by Category")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        plot_layout.addWidget(title)
        
        # Use plot generator to create the plot
        canvas = self.analysis_service.get_plot_generator().create_category_distribution_plot(self.df)
        
        plot_layout.addWidget(canvas)
        plot_frame.setLayout(plot_layout)
        self.content_layout.addWidget(plot_frame)

    def add_response_statistics(self):
        """Add response statistics by category"""
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Shape.Box)
        stats_layout = QVBoxLayout()
        
        title = QLabel("Response Statistics by Category")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        stats_layout.addWidget(title)
        
        # Use analysis service to get statistics
        response_stats = self.analysis_service.generate_response_statistics(self.df)
        
        # Create HTML table
        stats_text = "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        stats_text += "<tr><th>Category</th><th>Count</th><th>Mean</th><th>Std Dev</th><th>Min</th><th>Max</th></tr>"
        
        for stat in response_stats:
            stats_text += f"<tr>"
            stats_text += f"<td>{stat['category']}</td>"
            stats_text += f"<td>{stat['count']}</td>"
            
            # Handle mean - format as float if numeric, otherwise display as string
            if isinstance(stat['mean'], (int, float)):
                stats_text += f"<td>{stat['mean']:.2f}</td>"
            else:
                stats_text += f"<td>{stat['mean']}</td>"
            
            # Handle std - format as float if numeric, otherwise display as string
            if isinstance(stat['std'], (int, float)):
                stats_text += f"<td>{stat['std']:.2f}</td>"
            else:
                stats_text += f"<td>{stat['std']}</td>"
            
            stats_text += f"<td>{stat['min']}</td>"
            stats_text += f"<td>{stat['max']}</td>"
            stats_text += f"</tr>"
        
        stats_text += "</table>"
        
        stats_label = QLabel(stats_text)
        stats_label.setWordWrap(True)
        stats_layout.addWidget(stats_label)
        
        stats_frame.setLayout(stats_layout)
        self.content_layout.addWidget(stats_frame)

    def add_timeline_analysis(self):
        """Add timeline analysis with insights"""
        analysis_frame = QFrame()
        analysis_frame.setFrameStyle(QFrame.Shape.Box)
        analysis_layout = QVBoxLayout()
        
        title = QLabel("Timeline Analysis & Insights")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        analysis_layout.addWidget(title)
        
        # Use analysis service to get insights
        insights = self.analysis_service.generate_insights(self.df)
        
        insights_text = f"""
        <b>Key Insights:</b><br>
        {''.join([f'• {insight}<br>' for insight in insights])}
        """
        
        insights_label = QLabel(insights_text)
        insights_label.setWordWrap(True)
        analysis_layout.addWidget(insights_label)
        
        analysis_frame.setLayout(analysis_layout)
        self.content_layout.addWidget(analysis_frame)


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
            
        # Use PDF exporter service
        success = self.pdf_exporter.export_analysis_report(
            self.df, path, self.label.text()
        )
        
        if success:
            QMessageBox.information(self, "Success", f"PDF report saved to: {path}")
        else:
            QMessageBox.critical(self, "Error", "Failed to export PDF")
    