import pandas as pd
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from backend.analysis.statistics_calculator import StatisticsCalculator


class SummarySection:
    """Component for creating summary statistics section"""
    
    def __init__(self, statistics_calculator: StatisticsCalculator):
        self.statistics_calculator = statistics_calculator
    
    def create_section(self, df: pd.DataFrame) -> QFrame:
        """Create summary statistics section"""
        summary_frame = QFrame()
        summary_layout = QVBoxLayout()
        
        title = QLabel("Data Summary")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        summary_layout.addWidget(title)
        
        # Use statistics calculator to get summary statistics
        summary = self.statistics_calculator.generate_summary_statistics(df)
        
        # Build summary text with header information
        summary_text = f"""
        <b>Dataset Overview:</b><br>
        • Total Responses: {summary['total_responses']}<br>
        • Categories: {summary['unique_categories']} ({', '.join(summary['categories'])})
        • Time Span: {summary['time_span_seconds']:.1f} seconds ({summary['time_span_minutes']:.1f} minutes)<br>
        • Average Response Time: {summary['avg_response_time']:.1f} seconds<br>
        • Value Range: {summary['value_range'][0]} - {summary['value_range'][1]}<br>
        """
        
        # Add header information if available
        header_info = summary.get('header_info', {})
        if header_info:
            summary_text += "<br><b>Session Information:</b><br>"
            for key, value in header_info.items():
                summary_text += f"• {key}: {value}<br>"
        
        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        summary_layout.addWidget(summary_label)
        
        summary_frame.setLayout(summary_layout)
        return summary_frame
