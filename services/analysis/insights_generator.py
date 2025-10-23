import pandas as pd
from typing import List


class InsightsGenerator:
    """Service for generating insights from data"""
    
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
