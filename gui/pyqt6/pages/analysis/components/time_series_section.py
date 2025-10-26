import pandas as pd
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from gui.pyqt6.adapters.plot_adapter import PyQt6PlotAdapter
from backend.visualization.color_manager import ColorManager


class TimeSeriesSection:
    """Component for creating time series plot section"""
    
    def __init__(self, plot_adapter: PyQt6PlotAdapter, color_manager: ColorManager):
        self.plot_adapter = plot_adapter
        self.color_manager = color_manager
    
    def create_section(self, df: pd.DataFrame) -> QFrame:
        """Create time series plot section with frame and title"""
        plot_frame = QFrame()
        plot_layout = QVBoxLayout()
        
        title = QLabel("Response Timeline")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        plot_layout.addWidget(title)
        
        # Create the plot using plot adapter
        canvas = self.plot_adapter.create_time_series_canvas(df, self.color_manager)
        plot_layout.addWidget(canvas)
        
        plot_frame.setLayout(plot_layout)
        return plot_frame
