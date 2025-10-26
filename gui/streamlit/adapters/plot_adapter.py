import streamlit as st
import pandas as pd
from backend.visualization.plot_factory import PlotFactory
from backend.visualization.color_manager import ColorManager


class StreamlitPlotAdapter:
    """Adapter to display matplotlib Figures in Streamlit"""
    
    def __init__(self, plot_factory: PlotFactory):
        self.plot_factory = plot_factory
    
    def display_time_series_plot(self, df: pd.DataFrame, color_manager: ColorManager):
        """Display time series plot in Streamlit"""
        fig = self.plot_factory.create_time_series_plot(df, color_manager)
        st.pyplot(fig)
    
    def display_category_distribution_plot(self, df: pd.DataFrame, color_manager: ColorManager):
        """Display category distribution plot in Streamlit"""
        fig = self.plot_factory.create_category_distribution_plot(df, color_manager)
        st.pyplot(fig)
