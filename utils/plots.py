import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from widgets.mpl_canvas import MplCanvas
from utils.color_manager import ColorManager


class PlotGenerator:
    """Class to handle all plot generation for analysis"""
    
    def __init__(self, color_manager: ColorManager):
        """Initialize with color manager"""
        self.color_manager = color_manager

    def create_time_series_plot(self, df):
        """Create time series scatter plot with moving average for engagement"""
        canvas = MplCanvas()
        canvas.fig.set_size_inches(10, 6)
        
        # Create scatter plot
        for category in df["category"].unique():
            category_data = df[df["category"] == category]
            x_values = category_data["time_s"]
            y_values = category_data["response"]
            
            canvas.ax.scatter(x_values, y_values, 
                            c=self.color_manager.get_category_color(category), 
                            label=category, 
                            alpha=0.7, 
                            s=50)
        
        # Add 3-point moving average for engagement data
        engagement_data = df[df["category"] == "Engagement"]
        if not engagement_data.empty and len(engagement_data) >= 3:
            # Sort by time to ensure proper order and convert value to numeric
            engagement_sorted = engagement_data.sort_values('time_s')
            engagement_sorted = engagement_sorted.copy()
            engagement_sorted['value'] = pd.to_numeric(engagement_sorted['value'], errors='coerce')

            moving_avg_values = []
            moving_avg_times = []
            
            # First point - just use the first value
            moving_avg_values.append(engagement_sorted.iloc[0]['value'])
            moving_avg_times.append(engagement_sorted.iloc[0]['time_s'])
            
            # Second point - average of first two points
            avg_value = engagement_sorted.iloc[0:2]['value'].mean()
            moving_avg_values.append(avg_value)
            moving_avg_times.append(engagement_sorted.iloc[1]['time_s'])
        
            # Remaining points - 3 point moving average
            for i in range(2, len(engagement_sorted)):
                window_data = engagement_sorted.iloc[i-2:i+1]
                avg_value = window_data['value'].mean()
                moving_avg_values.append(avg_value)
                moving_avg_times.append(engagement_sorted.iloc[i]['time_s'])
            
            # Plot the moving average line
            canvas.ax.plot(moving_avg_times, moving_avg_values,
                          color=self.color_manager.get_category_color('Engagement'), linewidth=2,
                          label='Engagement Moving Average',
                          linestyle='--')
        
        canvas.ax.set_xlabel("Time (seconds)")
        canvas.ax.set_ylabel("Response")
        canvas.ax.set_title("Survey Responses Over Time")
        canvas.ax.grid(True, alpha=0.3)
        canvas.draw()
        
        return canvas

    def create_category_distribution_plot(self, df):
        """Create three pie charts for engagement, instructor, and student actions"""
        canvas = MplCanvas()
        canvas.fig.set_size_inches(12, 8)
        
        # Create three subplots for pie charts
        fig = canvas.fig
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
            num_engagement = len(engagement_counts)
            engagement_colors = self.color_manager.generate_color_spectrum(
                self.color_manager.get_category_color('Engagement'), num_engagement)
            ax1.pie(engagement_counts.values, labels=engagement_counts.index, 
                    autopct='%1.1f%%', startangle=90, 
                    colors=engagement_colors)
            ax1.set_title('Engagement Responses')
        else:
            ax1.text(0.5, 0.5, 'No Engagement Data', ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title('Engagement Responses')
        
        # Create pie chart for Instructor
        if not instructor_data.empty:
            instructor_counts = instructor_data['response'].value_counts()
            num_instructor = len(instructor_counts)
            instructor_colors = self.color_manager.generate_color_spectrum(
                self.color_manager.get_category_color('Instructor'), num_instructor)
            ax2.pie(instructor_counts.values, labels=instructor_counts.index, 
                    autopct='%1.1f%%', startangle=90,
                    colors=instructor_colors)
            ax2.set_title('Instructor Actions')
        else:
            ax2.text(0.5, 0.5, 'No Instructor Data', ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Instructor Actions')
        
        # Create pie chart for Student
        if not student_data.empty:
            student_counts = student_data['response'].value_counts()
            num_student = len(student_counts)
            student_colors = self.color_manager.generate_color_spectrum(
                self.color_manager.get_category_color('Student'), num_student)
            ax3.pie(student_counts.values, labels=student_counts.index, 
                    autopct='%1.1f%%', startangle=90,
                    colors=student_colors)
            ax3.set_title('Student Actions')
        else:
            ax3.text(0.5, 0.5, 'No Student Data', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Student Actions')
        
        canvas.draw()
        return canvas

    def create_pdf_time_series_plot(self, df, fig_width=8.5, fig_height=11.0):
        """Create time series plot for PDF export"""
        fig = Figure(figsize=(fig_width, fig_height))
        ax = fig.add_subplot(111)
        
        for category in df["category"].unique():
            category_data = df[df["category"] == category]
            x_values = category_data["time_s"]
            y_values = category_data["response"]
            
            ax.scatter(x_values, y_values, 
                     c=self.color_manager.get_category_color(category), 
                     label=category, 
                     alpha=0.7, 
                     s=50)
        
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Activity")
        ax.set_title("Class Activity Over Time")
        ax.grid(True, alpha=0.3)
        
        return fig

    def create_pdf_category_distribution_plot(self, df, fig_width=8.5, fig_height=11.0):
        """Create category distribution plot for PDF export"""
        fig = Figure(figsize=(fig_width, fig_height))
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
            num_engagement = len(engagement_counts)
            engagement_colors = self.color_manager.generate_color_spectrum(
                self.color_manager.get_category_color('Engagement'), num_engagement)
            ax1.pie(engagement_counts.values, labels=engagement_counts.index, 
                    autopct='%1.1f%%', startangle=90, 
                    colors=engagement_colors)
            ax1.set_title('Engagement Responses')
        else:
            ax1.text(0.5, 0.5, 'No Engagement Data', ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title('Engagement Responses')

        # Create pie chart for Instructor
        if not instructor_data.empty:
            instructor_counts = instructor_data['response'].value_counts()
            num_instructor = len(instructor_counts)
            instructor_colors = self.color_manager.generate_color_spectrum(
                self.color_manager.get_category_color('Instructor'), num_instructor)
            ax2.pie(instructor_counts.values, labels=instructor_counts.index, 
                    autopct='%1.1f%%', startangle=90,
                    colors=instructor_colors)
            ax2.set_title('Instructor Actions')
        else:
            ax2.text(0.5, 0.5, 'No Instructor Data', ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Instructor Actions')

        # Create pie chart for Student
        if not student_data.empty:
            student_counts = student_data['response'].value_counts()
            num_student = len(student_counts)
            student_colors = self.color_manager.generate_color_spectrum(
                self.color_manager.get_category_color('Student'), num_student)
            ax3.pie(student_counts.values, labels=student_counts.index, 
                    autopct='%1.1f%%', startangle=90,
                    colors=student_colors)
            ax3.set_title('Student Actions')
        else:
            ax3.text(0.5, 0.5, 'No Student Data', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Student Actions')

        return fig
