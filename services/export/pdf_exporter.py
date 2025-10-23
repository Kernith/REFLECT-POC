import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
from typing import Optional
from services.analysis.statistics_calculator import StatisticsCalculator
from services.analysis.insights_generator import InsightsGenerator
from services.visualization.plot_factory import PlotFactory


class PDFExporter:
    """Handles PDF export functionality for analysis reports"""
    
    def __init__(self, statistics_calculator: StatisticsCalculator, insights_generator: InsightsGenerator, plot_factory: PlotFactory):
        """Initialize with analysis services and plot factory"""
        self.statistics_calculator = statistics_calculator
        self.insights_generator = insights_generator
        self.plot_factory = plot_factory
    
    def export_analysis_report(self, df: pd.DataFrame, output_path: str, file_name: str = "", color_manager=None) -> bool:
        """Export comprehensive analysis report to PDF"""
        try:
            with PdfPages(output_path) as pdf:
                # Set up the page size (A4)
                fig_width, fig_height = 8.5, 11.0  # 8.5 x 11 inches
                
                # 1. Title page
                self._create_title_page(pdf, df, file_name, fig_width, fig_height)
                
                # 2. Summary statistics
                self._create_summary_page(pdf, df, fig_width, fig_height)
                
                # 3. Time series plot
                self._create_time_series_page(pdf, df, fig_width, fig_height, color_manager)
                
                # 4. Category distribution
                self._create_category_distribution_page(pdf, df, fig_width, fig_height, color_manager)
                
                # 5. Response statistics table
                self._create_statistics_table_page(pdf, df, fig_width, fig_height)
                
                # 6. Insights page
                self._create_insights_page(pdf, df, fig_width, fig_height)
                
            return True
            
        except Exception as e:
            print(f"Failed to export PDF: {e}")
            return False
    
    def _create_title_page(self, pdf, df: pd.DataFrame, file_name: str, fig_width: float, fig_height: float):
        """Create title page"""
        fig = Figure(figsize=(fig_width, fig_height))
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.7, "Survey Analysis Report", 
               ha='center', va='center', fontsize=24, weight='bold')
        ax.text(0.5, 0.6, f"Generated from: {file_name}", 
               ha='center', va='center', fontsize=12)
        ax.text(0.5, 0.5, f"Total Responses: {len(df)}", 
               ha='center', va='center', fontsize=14)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        fig.clear()
    
    def _create_summary_page(self, pdf, df: pd.DataFrame, fig_width: float, fig_height: float):
        """Create summary statistics page"""
        fig = Figure(figsize=(fig_width, fig_height))
        ax = fig.add_subplot(111)
        ax.text(0.1, 0.9, "Data Summary", fontsize=16, weight='bold')
        
        # Calculate and display summary
        summary = self.statistics_calculator.generate_summary_statistics(df)
        
        summary_text = f"""
        Total Responses: {summary['total_responses']}
        Categories: {summary['unique_categories']} ({', '.join(summary['categories'])})
        Time Span: {summary['time_span_seconds']:.1f} seconds ({summary['time_span_minutes']:.1f} minutes)
        Average Response Time: {summary['avg_response_time']:.1f} seconds
        Value Range: {summary['value_range'][0]} - {summary['value_range'][1]}
        """
        
        # Add header information if available
        header_info = summary.get('header_info', {})
        if header_info:
            summary_text += "\n\nSession Information:\n"
            for key, value in header_info.items():
                summary_text += f"{key}: {value}\n"
        
        ax.text(0.1, 0.7, summary_text, fontsize=12, va='top')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        fig.clear()
    
    def _create_time_series_page(self, pdf, df: pd.DataFrame, fig_width: float, fig_height: float, color_manager):
        """Create time series plot page"""
        fig = self.plot_factory.create_time_series_plot(df, color_manager, for_pdf=True)
        pdf.savefig(fig, bbox_inches='tight')
        fig.clear()
    
    def _create_category_distribution_page(self, pdf, df: pd.DataFrame, fig_width: float, fig_height: float, color_manager):
        """Create category distribution page"""
        fig = self.plot_factory.create_category_distribution_plot(df, color_manager, for_pdf=True)
        pdf.savefig(fig, bbox_inches='tight')
        fig.clear()
    
    def _create_statistics_table_page(self, pdf, df: pd.DataFrame, fig_width: float, fig_height: float):
        """Create response statistics table page"""
        fig = Figure(figsize=(fig_width, fig_height))
        ax = fig.add_subplot(111)
        ax.set_title("Response Statistics by Category", fontsize=16, weight='bold')
        
        # Create table data
        response_stats = self.statistics_calculator.generate_response_statistics(df)
        table_data = []
        headers = ['Category', 'Count', 'Mean', 'Std Dev', 'Min', 'Max']
        
        for stat in response_stats:
            row = [
                stat['category'],
                str(stat['count']),
                f"{stat['mean']:.2f}",
                f"{stat['std']:.2f}",
                str(stat['min']),
                str(stat['max'])
            ]
            table_data.append(row)
        
        # Create table
        table = ax.table(cellText=table_data, colLabels=headers,
                       cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        ax.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        fig.clear()
    
    def _create_insights_page(self, pdf, df: pd.DataFrame, fig_width: float, fig_height: float):
        """Create insights page"""
        fig = Figure(figsize=(fig_width, fig_height))
        ax = fig.add_subplot(111)
        ax.text(0.1, 0.9, "Timeline Analysis & Insights", fontsize=16, weight='bold')
        
        insights = self.insights_generator.generate_insights(df)
        insights_text = '\n'.join(insights)
        ax.text(0.1, 0.7, insights_text, fontsize=12, va='top')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        pdf.savefig(fig, bbox_inches='tight')
        fig.clear()