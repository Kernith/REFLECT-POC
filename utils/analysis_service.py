import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from utils.color_manager import ColorManager
from utils.plots import PlotGenerator

class DataLoadResult:
    """Result object for data loading operations"""
    def __init__(self, success: bool, data: Optional[pd.DataFrame] = None, error: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error

class AnalysisService:
    """Service class to handle data processing and analysis logic"""
    
    def __init__(self, color_config):
        """Initialize with color configuration"""
        self.color_manager = ColorManager(color_config)
        self.plot_generator = PlotGenerator(self.color_manager)
        self.df = None
    
    def load_and_validate_data(self, file_path: str) -> DataLoadResult:
        """Load CSV data and validate format"""
        try:
            # Read the file and skip comment lines (lines starting with #)
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # Find the first non-comment line (should be the header)
            data_start_line = 0
            for i, line in enumerate(lines):
                if not line.strip().startswith('#'):
                    data_start_line = i
                    break
            
            # Read CSV starting from the data header line
            df = pd.read_csv(file_path, skiprows=data_start_line)
            
            # Validate required columns
            required_columns = ["time_s", "category", "response", "value"]
            if not all(col in df.columns for col in required_columns):
                return DataLoadResult(
                    False, 
                    None, 
                    f"Invalid CSV format - requires {', '.join(required_columns)} columns"
                )
            
            self.df = df
            return DataLoadResult(True, df)
            
        except Exception as e:
            return DataLoadResult(False, None, f"Failed to load file: {e}")
    
    def generate_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate and return summary statistics"""
        total_responses = len(df)
        unique_categories = df['category'].nunique()
        time_span = df['time_s'].max() - df['time_s'].min()
        avg_response_time = df['time_s'].mean()
        
        # Handle value column - convert to numeric and get range
        numeric_values = pd.to_numeric(df['value'], errors='coerce').dropna()
        if len(numeric_values) > 0:
            value_range = (numeric_values.min(), numeric_values.max())
        else:
            value_range = ('N/A', 'N/A')
        
        return {
            'total_responses': total_responses,
            'unique_categories': unique_categories,
            'categories': df['category'].unique().tolist(),
            'time_span_seconds': time_span,
            'time_span_minutes': time_span / 60,
            'avg_response_time': avg_response_time,
            'value_range': value_range
        }
    
    def generate_response_statistics(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate response statistics by category"""
        stats = []
        
        for category in df['category'].unique():
            cat_data = df[df['category'] == category]['value']
            
            # Convert to numeric, coercing errors to NaN
            numeric_data = pd.to_numeric(cat_data, errors='coerce')
            
            # Filter out NaN values for statistics
            valid_data = numeric_data.dropna()
            
            if len(valid_data) > 0:
                stats.append({
                    'category': category,
                    'count': len(valid_data),
                    'mean': valid_data.mean(),
                    'std': valid_data.std(),
                    'min': valid_data.min(),
                    'max': valid_data.max()
                })
            else:
                # If no numeric data, provide basic info
                stats.append({
                    'category': category,
                    'count': len(cat_data),
                    'mean': 'N/A (non-numeric data)',
                    'std': 'N/A (non-numeric data)',
                    'min': 'N/A (non-numeric data)',
                    'max': 'N/A (non-numeric data)'
                })
        
        return stats
    
    def generate_insights(self, df: pd.DataFrame) -> List[str]:
        """Calculate key insights from the data"""
        insights = []
        
        # Response frequency analysis
        total_responses = len(df)
        time_span = df['time_s'].max() - df['time_s'].min()
        response_rate = total_responses / (time_span / 60) if time_span > 0 else 0
        
        insights.append(f"Response rate: {response_rate:.1f} responses per minute")
        
        # Category analysis
        category_counts = df['category'].value_counts()
        most_active = category_counts.index[0]
        insights.append(f"Most active category: {most_active} ({category_counts.iloc[0]} responses)")
        
        # Time distribution
        first_quarter = df['time_s'].quantile(0.25)
        last_quarter = df['time_s'].quantile(0.75)
        early_responses = len(df[df['time_s'] <= first_quarter])
        late_responses = len(df[df['time_s'] >= last_quarter])
        
        insights.append(f"Early responses (first 25% of time): {early_responses}")
        insights.append(f"Late responses (last 25% of time): {late_responses}")
        
        # Response value analysis
        numeric_values = pd.to_numeric(df['value'], errors='coerce').dropna()
        if len(numeric_values) > 0:
            avg_value = numeric_values.mean()
            insights.append(f"Average value: {avg_value:.2f}")
        else:
            insights.append("Average value: N/A (no numeric values found)")
        
        return insights
    
    def create_analysis_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Create comprehensive analysis report"""
        return {
            'summary': self.generate_summary_statistics(df),
            'response_stats': self.generate_response_statistics(df),
            'insights': self.generate_insights(df),
            'data': df
        }
    
    def get_plot_generator(self) -> PlotGenerator:
        """Get the plot generator instance"""
        return self.plot_generator
    
    def get_color_manager(self) -> ColorManager:
        """Get the color manager instance"""
        return self.color_manager
