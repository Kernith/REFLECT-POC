import matplotlib.colors as mcolors

class ColorManager:
    """Centralized color management for the application"""
    
    def __init__(self, color_config):
        """Initialize with color configuration"""
        self.colors = color_config or {}
        self._set_default_colors()
    
    def _set_default_colors(self):
        """Set default colors if not provided"""
        if not self.colors:
            self.colors = {
                "student": "#FFA500",
                "engagement": "#4169E1", 
                "instructor": "#32CD32",
                "comments": "#808080"
            }
    
    def get_category_color(self, category):
        """Get color for a specific category"""
        if category == "Student":
            return self.colors.get("student", "#FFA500")
        elif category == "Instructor":
            return self.colors.get("instructor", "#32CD32")
        elif category == "Engagement":
            return self.colors.get("engagement", "#4169E1")
        elif category == "Comment":
            return self.colors.get("comments", "#808080")
        else:
            return "#CCCCCC"  # Default gray for unknown categories
    
    def generate_color_spectrum(self, base_color, num_colors):
        """Generate a spectrum of lighter and darker shades of a base color"""
        if num_colors <= 0:
            return []
        
        # Convert hex to RGB
        rgb = mcolors.hex2color(base_color)
        
        # Create color variations
        colors = []
        for i in range(num_colors):
            # Create a gradient from lighter to darker
            # Start lighter (higher values) and go darker (lower values)
            factor = 0.6 + (0.4 * i / (num_colors - 1)) if num_colors > 1 else 0.8
            
            # Apply the factor to each RGB component
            new_rgb = [min(1.0, c * factor) for c in rgb]
            colors.append(mcolors.rgb2hex(new_rgb))
        
        return colors
    
    def get_all_colors(self):
        """Get all configured colors"""
        return self.colors.copy()
    
    def update_colors(self, new_colors):
        """Update color configuration"""
        self.colors.update(new_colors)
