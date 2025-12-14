import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from datetime import datetime, timedelta
from .color_manager import ColorManager


class PlotFactory:
    """Factory class for creating matplotlib plots - returns pure Figure objects"""
    
    def create_time_series_plot(self, df, color_manager: ColorManager) -> Figure:
        """Create horizontal interval plot showing time ranges for each category/response"""
        print("")
        print(df)
        
        fig = Figure(figsize=(12, 8))
        ax = fig.add_subplot(111)
        
        # Group by category first, then by response within each category
        df_sorted = df.sort_values('time_s').copy()

        # Replace strings in value column with 1, then convert to numeric
        df_sorted['value'] = pd.to_numeric(df_sorted['value'], errors='coerce').fillna(1)

        unique_combinations = df_sorted.groupby(['category', 'response']).agg({
            'value': 'mean'  # Aggregate value (you can use 'max', 'min', or 'first' instead)
        }).reset_index()
        unique_combinations = unique_combinations.sort_values(['category', 'value', 'response'], ascending=[True, True, False])
        
        # Create y-positions with spacing between categories
        y_pos_counter = 0
        category_positions = {}  # Track where each category starts/ends
        combo_to_y = {}
        
        for category in unique_combinations['category'].unique():
            category_data = unique_combinations[unique_combinations['category'] == category]
            category_start = y_pos_counter
            
            for _, row in category_data.iterrows():
                combo_to_y[(row['category'], row['response'])] = y_pos_counter
                y_pos_counter += 1
            
            category_end = y_pos_counter - 1
            category_positions[category] = (category_start, category_end)
        
        # Plot horizontal intervals
        for (category, response), y_pos in combo_to_y.items():
            combo_data = df_sorted[(df_sorted['category'] == category) & 
                                (df_sorted['response'] == response)]
            
            if len(combo_data) > 0:
                # Get color for this category
                color = color_manager.get_category_color(category)
                
                # For each occurrence, create a small interval bar
                for _, row in combo_data.iterrows():
                    time_point = row['time_s'] / 60  # Convert seconds to minutes
                    interval_width = 2  # Width in minutes
                    ax.barh(y_pos, interval_width, left=time_point - interval_width/2,
                        color=color, alpha=1, height=0.6,
                        label=category if y_pos == 0 else "")
        
        # Add horizontal dividers between categories
        for category, (start, end) in category_positions.items():
            if category != list(category_positions.keys())[-1]:  # Not the last category
                divider_y = end + 0.5
                ax.axhline(y=divider_y, color='gray', linestyle='--', linewidth=1, alpha=0.5)
        
        # Set main y-axis labels to response
        y_labels = []
        y_ticks = []
        for category in unique_combinations['category'].unique():
            category_data = unique_combinations[unique_combinations['category'] == category]
            for _, row in category_data.iterrows():
                y_pos = combo_to_y[(row['category'], row['response'])]
                y_ticks.append(y_pos)
                y_labels.append(row['response'])  # Only show response, not category
        
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)
        
        # Create secondary y-axis for category labels
        sec = ax.secondary_yaxis(location=1)  # location=0 means left side
        
        # Calculate middle position for each category group
        category_ticks = []
        category_labels = []
        for category, (start, end) in category_positions.items():
            mid_y = (start + end) / 2
            category_ticks.append(mid_y)
            if category.lower() == 'comment':
                category_labels.append('')
            else:
                category_labels.append(f'{category}')
        
        sec.set_yticks(category_ticks)
        sec.set_yticklabels(category_labels)
        sec.tick_params('y', length=0, rotation=-90)
        for label in sec.get_yticklabels(): # tick_params doesn't support 'va' directly
            label.set_verticalalignment('center')
        
        # Set labels and formatting
        ax.set_xlabel("Time (minutes)")
#        ax.set_ylabel("Response")
#        ax.set_title("Activity Timeline (Grouped by Category)")
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add secondary x-axis with start and end time labels
        header_info = df.attrs.get('header_info', {})
        if 'Observation Started' in header_info:
            try:
                # Parse the start time from header metadata
                start_time_str = header_info['Observation Started']
                start_datetime = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
                
                # Calculate end time: start time + max elapsed time
                max_elapsed_seconds = float(df['time_s'].max()) if len(df) > 0 else 0
                max_elapsed_minutes = max_elapsed_seconds / 60
                end_datetime = start_datetime + timedelta(seconds=max_elapsed_seconds)
                
                # Ensure x-axis limits are set to show the full range
                # Get current limits and adjust if needed
                x_min, x_max = ax.get_xlim()
                if x_max < max_elapsed_minutes:
                    x_max = max_elapsed_minutes
                if x_min > 0:
                    x_min = 0
                ax.set_xlim(x_min, x_max)
                
                # Create secondary x-axis at location=0 (bottom)
                sec_x = ax.secondary_xaxis(location=0)
                
                # Set ticks at the start (0) and end (max_elapsed_minutes) positions
                sec_x.set_xticks([0, max_elapsed_minutes])
                
                # Format datetime labels (show time only, on new line to avoid primary label)
                start_label = '\n' + start_datetime.strftime('%H:%M')
                end_label = '\n' + end_datetime.strftime('%H:%M')
                sec_x.set_xticklabels([start_label, end_label])
                
            except (ValueError, KeyError) as e:
                # If parsing fails, skip the secondary axis
                print(f"Warning: Could not parse observation start time: {e}")
        
        return fig

    def _group_small_categories(self, counts, threshold=0.06499999999999999):
        """
        Group categories with individual proportions <= threshold into 'Other' category.
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
            if proportion <= threshold:
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
        """Create four pie charts in a 2x2 grid: instructor, student, engagement, and interval capture rate"""
        combine_threshold = 0.06499999999999999  # Activities with proportion < this will be grouped
        
        fig = Figure(figsize=(8, 8))
        # 2x2 grid layout: top row (221, 222), bottom row (223, 224)
        ax1 = fig.add_subplot(221)  # Instructor (top left)
        ax2 = fig.add_subplot(222)  # Student (top right)
        ax3 = fig.add_subplot(223)  # Engagement (bottom left)
        ax4 = fig.add_subplot(224)  # Interval Capture (bottom right)
        
        # Filter data for each category
        engagement_data = df[df['category'] == 'Engagement']
        instructor_data = df[df['category'] == 'Instructor']
        student_data = df[df['category'] == 'Student']
        
        # Calculate interval capture statistics
        interval_duration = 120  # Default 2 minutes in seconds
        # Try to get interval from header info if available
        header_info = df.attrs.get('header_info', {})
        if 'timer_interval' in header_info:
            try:
                interval_duration = int(header_info['timer_interval'])
            except (ValueError, TypeError):
                pass
        
        # Calculate expected and captured intervals
        if len(df) > 0:
            min_time = df['time_s'].min()
            max_time = df['time_s'].max()
            time_span = max_time - min_time
            
            # Calculate expected number of intervals
            expected_intervals = int(np.ceil(time_span / interval_duration)) if time_span > 0 else 0
            
            # Calculate unique intervals that have data
            # Round each time to the nearest interval start
            interval_indices = ((df['time_s'] - min_time) / interval_duration).astype(int)
            captured_intervals = interval_indices.nunique()
            
            # Calculate missed intervals
            missed_intervals = max(0, expected_intervals - captured_intervals)
            
            # Calculate percentages
            if expected_intervals > 0:
                pct_captured = (captured_intervals / expected_intervals) * 100
                pct_missed = (missed_intervals / expected_intervals) * 100
            else:
                pct_captured = 0
                pct_missed = 0
        else:
            pct_captured = 0
            pct_missed = 0
        
        # Create pie chart for Instructor (top left)
        if not instructor_data.empty:
            instructor_counts = instructor_data['response'].value_counts()
            grouped_instructor = self._group_small_categories(instructor_counts, combine_threshold)
            num_instructor = len(grouped_instructor)
            instructor_colors = color_manager.generate_color_spectrum(
                color_manager.get_category_color('Instructor'), num_instructor)
            ax1.pie(grouped_instructor.values, labels=grouped_instructor.index, 
                    autopct='%1.0f%%', startangle=90,
                    colors=instructor_colors, pctdistance=0.75)
            ax1.set_title('Instructor Activities')
        else:
            ax1.text(0.5, 0.5, 'No Instructor Data', ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title('Instructor Activities')
        
        # Create pie chart for Student (top right)
        if not student_data.empty:
            student_counts = student_data['response'].value_counts()
            grouped_student = self._group_small_categories(student_counts, combine_threshold)
            num_student = len(grouped_student)
            student_colors = color_manager.generate_color_spectrum(
                color_manager.get_category_color('Student'), num_student)
            ax2.pie(grouped_student.values, labels=grouped_student.index, 
                    autopct='%1.0f%%', startangle=90,
                    colors=student_colors, pctdistance=0.75)
            ax2.set_title('Student Activities')
        else:
            ax2.text(0.5, 0.5, 'No Student Data', ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Student Activities')
        
        # Create pie chart for Engagement (bottom left)
        if not engagement_data.empty:
            engagement_counts = engagement_data['response'].value_counts()
            grouped_engagement = self._group_small_categories(engagement_counts, combine_threshold)
            num_engagement = len(grouped_engagement)
            engagement_colors = color_manager.generate_color_spectrum(
                color_manager.get_category_color('Engagement'), num_engagement)
            ax3.pie(grouped_engagement.values, labels=grouped_engagement.index, 
                    autopct='%1.0f%%', startangle=90, 
                    colors=engagement_colors, pctdistance=0.75)
            ax3.set_title('Engagement Responses')
        else:
            ax3.text(0.5, 0.5, 'No Engagement Data', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Engagement')
        
        # Create pie chart for Interval Capture (bottom right)
        capture_data = [pct_captured, pct_missed]
        capture_labels = ['% Intervals Captured', '% Intervals Missed']
        # Generate grey color spectrum using the same method as other charts
        base_grey = color_manager.colors.get('comments', '#808080')
        capture_colors = color_manager.generate_color_spectrum(base_grey, 2)
        ax4.pie(capture_data, labels=capture_labels, 
                autopct='%1.1f%%', startangle=90,
                colors=capture_colors, pctdistance=0.75)
        ax4.set_title('Interval Capture Rate')
        
        return fig
