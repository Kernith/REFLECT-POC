import pandas as pd
import json
from typing import Dict, Any, Optional
from core.util_functions import resource_path


class DataLoadResult:
    """Result object for data loading operations"""
    def __init__(self, success: bool, data: Optional[pd.DataFrame] = None, error: Optional[str] = None):
        self.success = success
        self.data = data
        self.error = error


class DataProcessor:
    """Service for data loading, validation, and ordering"""
    
    def __init__(self):
        self._config_ordering = None
        self._load_config_ordering()
    
    def _load_config_ordering(self):
        """Load category and response ordering from config.json"""
        try:
            config_path = resource_path("config.json")
            with open(config_path, "r") as f:
                config = json.load(f)
            
            # Get category order from colors section
            category_order = list(config.get("colors", {}).keys())
            
            # Get response orderings for each category from observation configs
            response_orderings = {}
            for obs_config in config.get("observation_configs", []):
                # Student actions
                student_actions = [action["label"] for action in obs_config.get("student_actions", [])]
                if student_actions:
                    response_orderings["student"] = student_actions
                
                # Instructor actions  
                instructor_actions = [action["label"] for action in obs_config.get("instructor_actions", [])]
                if instructor_actions:
                    response_orderings["instructor"] = instructor_actions
                
                # Engagement levels
                engagement_levels = [level["label"] for level in obs_config.get("engagement_images", [])]
                if engagement_levels:
                    response_orderings["engagement"] = engagement_levels
            
            self._config_ordering = {
                'categories': category_order,
                'responses': response_orderings
            }
            
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            # Fallback ordering if config can't be loaded
            self._config_ordering = {
                'categories': ['student', 'instructor', 'comments', 'engagement'],
                'responses': {
                    'engagement': ['High', 'Medium', 'Low']
                }
            }
    
    def load_and_validate_data(self, file_path: str) -> DataLoadResult:
        """Load CSV data and validate format"""
        try:
            # Read the file and skip comment lines (lines starting with #)
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # Extract header information from comment lines
            header_info = {}
            data_start_line = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('#'):
                    # Parse header information
                    line_content = line.strip()[1:].strip()  # Remove # and whitespace
                    if ':' in line_content:
                        key, value = line_content.split(':', 1)
                        header_info[key.strip()] = value.strip()
                else:
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
            
            # Apply config-based ordering
            df = self._apply_config_ordering(df)
            
            # Store header information in the dataframe as metadata
            df.attrs['header_info'] = header_info
            
            return DataLoadResult(True, df)
            
        except Exception as e:
            return DataLoadResult(False, None, f"Failed to load file: {e}")
    
    def _apply_config_ordering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply ordering based on config.json"""
        if not self._config_ordering:
            return df
        
        # Create category ordering
        category_order = self._config_ordering['categories']
        category_mapping = {cat: i for i, cat in enumerate(category_order)}
        
        # Add temporary columns for sorting
        df['_category_order'] = df['category'].map(category_mapping).fillna(999)
        
        # Create response ordering for each category
        response_orderings = self._config_ordering['responses']
        df['_response_order'] = 0  # Default order
        
        for category, responses in response_orderings.items():
            response_mapping = {resp: i for i, resp in enumerate(responses)}
            category_mask = df['category'].str.lower() == category.lower()
            df.loc[category_mask, '_response_order'] = df.loc[category_mask, 'response'].map(response_mapping).fillna(999)
        
        # Sort by config-based ordering
        df = df.sort_values(['_category_order', 'time_s', '_response_order', 'response', 'value']).reset_index(drop=True)
        
        # Remove temporary columns
        df = df.drop(['_category_order', '_response_order'], axis=1)
        
        return df
