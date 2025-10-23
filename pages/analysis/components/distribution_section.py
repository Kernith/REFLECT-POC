import pandas as pd
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from services.visualization.plot_factory import PlotFactory
from services.visualization.color_manager import ColorManager


class DistributionSection:
    """Component for creating category distribution section"""
    
    def __init__(self, plot_factory: PlotFactory, color_manager: ColorManager):
        self.plot_factory = plot_factory
        self.color_manager = color_manager
    
    def create_section(self, df: pd.DataFrame) -> QFrame:
        """Create category distribution section with frame and title"""
        plot_frame = QFrame()
        plot_layout = QVBoxLayout()
        
        title = QLabel("Response Distribution by Category")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        plot_layout.addWidget(title)
        
        # Create the plot using plot factory
        canvas = self.plot_factory.create_category_distribution_plot(df, self.color_manager, for_pdf=False)
        plot_layout.addWidget(canvas)
        
        plot_frame.setLayout(plot_layout)
        return plot_frame
