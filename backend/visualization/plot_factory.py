import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from .color_manager import ColorManager


class PlotFactory:
    """Factory class for creating matplotlib plots - returns pure Figure objects"""
    
    def create_time_series_plot(self, df, color_manager: ColorManager) -> Figure:
        """Create horizontal interval plot showing time ranges for each category/response"""
        fig = Figure(figsize=(12, 8))
        ax = fig.add_subplot(111)
        
        # Get unique combinations of category and response
        df_sorted = df.sort_values('time_s').copy()
        
        # Create y-positions for each unique category-response combination
        unique_combinations = df_sorted.groupby(['category', 'response']).size().reset_index()
        unique_combinations['y_pos'] = range(len(unique_combinations))
        
        # Create a mapping for quick lookup
        combo_to_y = {}
        for idx, row in unique_combinations.iterrows():
            combo_to_y[(row['category'], row['response'])] = row['y_pos']
        
        # Plot horizontal intervals
        # For each category-response combination, find time intervals
        for (category, response), y_pos in combo_to_y.items():
            combo_data = df_sorted[(df_sorted['category'] == category) & 
                                  (df_sorted['response'] == response)]
            
            if len(combo_data) > 0:
                # Get color for this category
                color = color_manager.get_category_color(category)
                
                # For each occurrence, create a small interval bar
                # You can adjust the width of these bars as needed
                for _, row in combo_data.iterrows():
                    time_point = row['time_s'] / 60  # Convert seconds to minutes
                    # Create a small interval around each point (e.g., ±2 minutes)
                    # Or use actual intervals if you have start/end times
                    interval_width = 2  # Width in minutes (was 120 seconds)
                    ax.barh(y_pos, interval_width, left=time_point - interval_width/2,
                           color=color, alpha=1, height=0.6,
                           label=category if y_pos == 0 else "")
        
        # Set y-axis labels
        y_labels = [f"{row['category']}: {row['response']}" 
                   for _, row in unique_combinations.iterrows()]
        ax.set_yticks(range(len(unique_combinations)))
        ax.set_yticklabels(y_labels)
        
        # Set labels and formatting
        ax.set_xlabel("Time (minutes)")
        ax.set_ylabel("Category / Response")
        ax.set_title("Activity Timeline (Horizontal Interval Plot)")
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add legend (one entry per category)
        #handles, labels = ax.get_legend_handles_labels()
        #by_label = dict(zip(labels, handles))
        #ax.legend(by_label.values(), by_label.keys(), loc='best')
        
        return fig

    def _group_small_categories(self, counts, threshold=0.08):
        """
        Group categories with individual proportions < threshold into 'Other' category.
        Only groups if there are at least 2 categories to group.
        Returns grouped counts as a Series.
        """
        if len(counts) == 0:
            return counts
        
        total = counts.sum()
        proportions = counts / total
        
        # Find all categories with proportion < threshold
        categories_to_group = []
        for category, proportion in proportions.items():
            if proportion < threshold:
                categories_to_group.append(category)
        
        # Only group if we have at least 2 categories
        if len(categories_to_group) >= 2:
            # Create grouped counts with remaining categories
            remaining_categories = [cat for cat in counts.index if cat not in categories_to_group]
            grouped_counts = counts[remaining_categories].copy()
            
            # Sum up grouped categories into "Other"
            other_count = counts[categories_to_group].sum()
            grouped_counts['Other'] = other_count
            
            return grouped_counts
        else:
            # If less than 2 categories to group, return original counts
            return counts

    def create_category_distribution_plot(self, df, color_manager: ColorManager) -> Figure:
        """Create three pie charts for engagement, instructor, and student actions"""
        combine_threshold = 0.08  # Activities with proportion <= 8% will be grouped
        
        fig = Figure(figsize=(12, 8))
        ax1 = fig.add_subplot(131)  # Engagement
        ax2 = fig.add_subplot(132)  # Instructor
        ax3 = fig.add_subplot(133)  # Student
        
        # Filter data for each category
        engagement_data = df[df['category'] == 'Engagement']
        instructor_data = df[df['category'] == 'Instructor']
        student_data = df[df['category'] == 'Student']
        
        # Create pie chart for Engagement
        if not engagement_data.empty:
            engagement_counts = engagement_data['response'].value_counts()
            grouped_engagement = self._group_small_categories(engagement_counts, combine_threshold)
            num_engagement = len(grouped_engagement)
            engagement_colors = color_manager.generate_color_spectrum(
                color_manager.get_category_color('Engagement'), num_engagement)
            ax1.pie(grouped_engagement.values, labels=grouped_engagement.index, 
                    autopct='%1.1f%%', startangle=90, 
                    colors=engagement_colors)
            ax1.set_title('Engagement Responses')
        else:
            ax1.text(0.5, 0.5, 'No Engagement Data', ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title('Engagement')
        
        # Create pie chart for Instructor
        if not instructor_data.empty:
            instructor_counts = instructor_data['response'].value_counts()
            grouped_instructor = self._group_small_categories(instructor_counts, combine_threshold)
            num_instructor = len(grouped_instructor)
            instructor_colors = color_manager.generate_color_spectrum(
                color_manager.get_category_color('Instructor'), num_instructor)
            ax2.pie(grouped_instructor.values, labels=grouped_instructor.index, 
                    autopct='%1.1f%%', startangle=90,
                    colors=instructor_colors)
            ax2.set_title('Instructor Activities')
        else:
            ax2.text(0.5, 0.5, 'No Instructor Data', ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Instructor Activities')
        
        # Create pie chart for Student
        if not student_data.empty:
            student_counts = student_data['response'].value_counts()
            grouped_student = self._group_small_categories(student_counts, combine_threshold)
            num_student = len(grouped_student)
            student_colors = color_manager.generate_color_spectrum(
                color_manager.get_category_color('Student'), num_student)
            ax3.pie(grouped_student.values, labels=grouped_student.index, 
                    autopct='%1.1f%%', startangle=90,
                    colors=student_colors)
            ax3.set_title('Student Activities')
        else:
            ax3.text(0.5, 0.5, 'No Student Data', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Student Activities')
        
        return fig
