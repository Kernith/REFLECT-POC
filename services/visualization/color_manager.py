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
        """Generate a spectrum of lighter and darker shades of a base color using HSV color space"""
        if num_colors <= 0:
            return []

        # Convert hex to RGB, then to HSV for easier lightness (V) scaling
        rgb = mcolors.hex2color(base_color)
        hsv = mcolors.rgb_to_hsv(rgb)
        
        colors = []
        for i in range(num_colors):
            # Create a new HSV color with the same hue
            new_hsv = hsv.copy()
            
            # Vary saturation and value (brightness) while keeping hue constant
            # Start from lighter (higher value, lower saturation) to darker (lower value, higher saturation)
            if num_colors > 1:
                #new_hsv[1] = 0.7 + (0.2 * i / (num_colors - 1))  # 70% to 90% saturation
                new_hsv[2] = 0.6 + (0.3 * i / (num_colors - 1))  # 60% to 90% brightness (value)
            
            # Convert back to RGB and then to hex
            new_rgb = mcolors.hsv_to_rgb(new_hsv)
            colors.append(mcolors.rgb2hex(new_rgb))
        
        return colors
    
    def get_all_colors(self):
        """Get all configured colors"""
        return self.colors.copy()
    
    def update_colors(self, new_colors):
        """Update color configuration"""
        self.colors.update(new_colors)