import pandas as pd
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from backend.analysis.insights_generator import InsightsGenerator


class TimelineSection:
    """Component for creating timeline analysis section"""
    
    def __init__(self, insights_generator: InsightsGenerator):
        self.insights_generator = insights_generator
    
    def create_section(self, df: pd.DataFrame) -> QFrame:
        """Create timeline analysis with insights section"""
        analysis_frame = QFrame()
        analysis_layout = QVBoxLayout()
        
        title = QLabel("Timeline Analysis & Insights")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        analysis_layout.addWidget(title)
        
        # Use insights generator to get insights
        insights = self.insights_generator.generate_insights(df)
        
        insights_text = f"""
        <b>Key Insights:</b><br>
        {''.join([f'• {insight}<br>' for insight in insights])}
        """
        
        insights_label = QLabel(insights_text)
        insights_label.setWordWrap(True)
        analysis_layout.addWidget(insights_label)
        
        analysis_frame.setLayout(analysis_layout)
        return analysis_frame
