import pandas as pd
import numpy as np
from typing import Dict, Any, List


class StatisticsCalculator:
    """Service for calculating summary and response statistics"""
    
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
        
        # Get header information from dataframe metadata
        header_info = df.attrs.get('header_info', {})
        
        return {
            'total_responses': total_responses,
            'unique_categories': unique_categories,
            'categories': df['category'].unique().tolist(),
            'time_span_seconds': time_span,
            'time_span_minutes': time_span / 60,
            'avg_response_time': avg_response_time,
            'value_range': value_range,
            'header_info': header_info
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
