import pandas as pd
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from services.analysis.statistics_calculator import StatisticsCalculator


class StatisticsSection:
    """Component for creating response statistics section"""
    
    def __init__(self, statistics_calculator: StatisticsCalculator):
        self.statistics_calculator = statistics_calculator
    
    def create_section(self, df: pd.DataFrame) -> QFrame:
        """Create response statistics by category section"""
        stats_frame = QFrame()
        stats_layout = QVBoxLayout()
        
        title = QLabel("Response Statistics by Category")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        stats_layout.addWidget(title)
        
        # Use statistics calculator to get statistics
        response_stats = self.statistics_calculator.generate_response_statistics(df)
        
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
        return stats_frame
