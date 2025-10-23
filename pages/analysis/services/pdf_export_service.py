import pandas as pd
from services.export.pdf_exporter import PDFExporter
from services.analysis.statistics_calculator import StatisticsCalculator
from services.analysis.insights_generator import InsightsGenerator
from services.visualization.plot_factory import PlotFactory
from services.visualization.color_manager import ColorManager


class PDFExportService:
    """Page-specific PDF export service wrapper"""
    
    def __init__(self, statistics_calculator: StatisticsCalculator, insights_generator: InsightsGenerator, 
                 plot_factory: PlotFactory, color_manager: ColorManager):
        """Initialize with required services"""
        self.pdf_exporter = PDFExporter(statistics_calculator, insights_generator, plot_factory)
        self.color_manager = color_manager
    
    def export_analysis_report(self, df: pd.DataFrame, output_path: str, file_name: str = "") -> bool:
        """Export analysis report to PDF with color management"""
        return self.pdf_exporter.export_analysis_report(df, output_path, file_name, self.color_manager)
