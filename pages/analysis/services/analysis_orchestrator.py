import pandas as pd
from typing import Dict, Any, List
from services.analysis.data_processor import DataProcessor, DataLoadResult
from services.analysis.statistics_calculator import StatisticsCalculator
from services.analysis.insights_generator import InsightsGenerator
from services.visualization.color_manager import ColorManager


class AnalysisOrchestrator:
    """Orchestrates analysis services and provides unified interface"""
    
    def __init__(self, color_config):
        """Initialize with color configuration"""
        self.color_manager = ColorManager(color_config)
        self.data_processor = DataProcessor()
        self.statistics_calculator = StatisticsCalculator()
        self.insights_generator = InsightsGenerator()
        self.df = None
    
    def load_and_validate_data(self, file_path: str) -> DataLoadResult:
        """Load CSV data and validate format"""
        result = self.data_processor.load_and_validate_data(file_path)
        if result.success:
            self.df = result.data
        return result
    
    def generate_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate and return summary statistics"""
        return self.statistics_calculator.generate_summary_statistics(df)
    
    def generate_response_statistics(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate response statistics by category"""
        return self.statistics_calculator.generate_response_statistics(df)
    
    def generate_insights(self, df: pd.DataFrame) -> List[str]:
        """Calculate key insights from the data"""
        return self.insights_generator.generate_insights(df)
    
    def create_analysis_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create comprehensive analysis report"""
        return {
            'summary': self.generate_summary_statistics(df),
            'response_stats': self.generate_response_statistics(df),
            'insights': self.generate_insights(df),
            'data': df
        }
    
    def get_color_manager(self) -> ColorManager:
        """Get the color manager instance"""
        return self.color_manager
