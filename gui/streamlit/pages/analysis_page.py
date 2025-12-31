import streamlit as st
import pandas as pd
from backend.analysis.orchestrator import AnalysisOrchestrator
from backend.analysis.statistics_calculator import StatisticsCalculator
from backend.analysis.insights_generator import InsightsGenerator
from backend.visualization.plot_factory import PlotFactory
from backend.export.pdf_exporter import PDFExporter
from gui.streamlit.adapters.plot_adapter import StreamlitPlotAdapter


def render_analysis_page():
    """Render the analysis page"""
    # Initialize services
    if 'analysis_orchestrator' not in st.session_state:
        colors = st.session_state.get('colors', {})
        config_manager = st.session_state.get('config_manager')
        st.session_state.analysis_orchestrator = AnalysisOrchestrator(colors, config_manager)
        st.session_state.plot_factory = PlotFactory()
        st.session_state.plot_adapter = StreamlitPlotAdapter(st.session_state.plot_factory)
        st.session_state.statistics_calculator = StatisticsCalculator()
        st.session_state.insights_generator = InsightsGenerator()
        st.session_state.pdf_exporter = PDFExporter(
            st.session_state.statistics_calculator,
            st.session_state.insights_generator,
            st.session_state.plot_factory
        )
    
    orchestrator = st.session_state.analysis_orchestrator
    plot_adapter = st.session_state.plot_adapter
    pdf_exporter = st.session_state.pdf_exporter
    
    # render UI 
    # header section
    header_col1, header_col2, header_col3 = st.columns([1, 2, 1])
    
    with header_col1:
        st.title("Data Analysis")
    
    with header_col2:
        if 'current_data' in st.session_state and 'current_data_filename' in st.session_state:
            display_export_options(
                st.session_state.current_data, 
                pdf_exporter, 
                orchestrator, 
                st.session_state.current_data_filename
            )

    with header_col3:
        if st.button("Back to Home"):
            # Clear all analysis-related data when leaving the page
            analysis_keys = ['current_data', 'current_data_filename',
                             'comparison_data', 'comparison_data_filename',
                             'analysis_orchestrator', 'plot_factory', 'plot_adapter',
                             'statistics_calculator', 'insights_generator', 'pdf_exporter']
            
            for key in analysis_keys:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.session_state.page = "home"
            st.rerun()

    st.markdown("---")
    
    # file upload section
    data1_col, data2_col = st.columns([1,1])

    with data1_col:
        if 'current_data' not in st.session_state or 'current_data_filename' not in st.session_state:
            uploaded_file = st.file_uploader("Upload observation file", type=['csv'], help="Upload a CSV file with observation data")
        
            if uploaded_file is not None:
                # Save uploaded file temporarily
                with st.spinner("Loading and validating data..."):
                    # Create a temporary file path
                    temp_path = f"temp_{uploaded_file.name}_1"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Load and validate data
                    result = orchestrator.load_and_validate_data(temp_path)
                    
                    # Clean up temp file
                    import os
                    os.remove(temp_path)
                
                    if result.success:
                        df = result.data
                        st.session_state.current_data = df        
                        filename = uploaded_file.name.rsplit('.', 1)[0] if '.' in uploaded_file.name else uploaded_file.name
                        st.session_state.current_data_filename = filename
                        st.rerun()
            
        elif 'current_data' in st.session_state:
            st.success(f"{st.session_state.current_data_filename} loaded successfully! {len(st.session_state.current_data)} records")
        else:
            st.error("No data loaded")
                
    with data2_col:
        if 'current_data' in st.session_state and 'current_data_filename' in st.session_state:
            if 'comparison_data' not in st.session_state or 'comparison_data_filename' not in st.session_state:
                comparison_file = st.file_uploader("Upload file for comparison", type=['csv'], help="Upload a CSV file with observation data")
            
                if comparison_file is not None:
                    # Save uploaded file temporarily
                    with st.spinner("Loading and validating data..."):
                        # Create a temporary file path
                        temp_path = f"temp_{comparison_file.name}_1"
                        with open(temp_path, "wb") as f:
                            f.write(comparison_file.getbuffer())
                        
                        # Load and validate data
                        result = orchestrator.load_and_validate_data(temp_path)
                        
                        # Clean up temp file
                        import os
                        os.remove(temp_path)
                    
                        if result.success:
                            df = result.data
                            st.session_state.comparison_data = df        
                            filename = comparison_file.name.rsplit('.', 1)[0] if '.' in comparison_file.name else comparison_file.name
                            st.session_state.comparison_data_filename = filename
                            st.rerun()
                
            elif 'comparison_data' in st.session_state:
                st.success(f"{st.session_state.comparison_data_filename} loaded successfully! {len(st.session_state.comparison_data)} records")
            else:
                st.error("No data loaded")
    
    st.markdown("---")

    # Display visual summaries
    if 'current_data' in st.session_state and 'current_data_filename' in st.session_state:
        df = st.session_state.current_data
        timeseries_col, pie_col = st.columns([2, 2])
        with timeseries_col:
            display_time_series_plot(df, plot_adapter, orchestrator)
        with pie_col:
            display_distribution_plot(df, plot_adapter, orchestrator)

    if 'comparison_data' in st.session_state and 'comparison_data_filename' in st.session_state:
        df = st.session_state.comparison_data
        timeseries_col, pie_col = st.columns([2, 2])
        with timeseries_col:
            display_time_series_plot(df, plot_adapter, orchestrator)
        with pie_col:
            display_distribution_plot(df, plot_adapter, orchestrator)

    if 'current_data' in st.session_state and 'current_data_filename' in st.session_state:
        st.markdown("---")
    
    if 'current_data' in st.session_state and 'current_data_filename' in st.session_state:
        df = st.session_state.current_data
        # Display text summaries
        summary_col, insights_col = st.columns([1, 1])
        with summary_col:
            display_summary_statistics(df, orchestrator)
        with insights_col:
            display_insights(df, orchestrator)
        
    
    if 'comparison_data' in st.session_state and 'comparison_data_filename' in st.session_state:
        df = st.session_state.comparison_data
        # Display text summaries
        summary_col, insights_col = st.columns([1, 1])
        with summary_col:
            display_summary_statistics(df, orchestrator)
        with insights_col:
            display_insights(df, orchestrator)

    if 'current_data' in st.session_state and 'current_data_filename' in st.session_state:
        st.markdown("---")
        
    if 'current_data' in st.session_state and 'current_data_filename' in st.session_state:
        df = st.session_state.current_data
        display_statistics_table(df, orchestrator)
    
    if 'comparison_data' in st.session_state and 'comparison_data_filename' in st.session_state:
        df = st.session_state.comparison_data
        display_statistics_table(df, orchestrator)


def display_time_series_plot(df, plot_adapter, orchestrator):
    """Display time series plot"""
    st.subheader("Observation Timeline")
    plot_adapter.display_time_series_plot(df, orchestrator.get_color_manager())


def display_distribution_plot(df, plot_adapter, orchestrator):
    """Display distribution plot"""
    st.subheader("Activity Distribution")
    plot_adapter.display_category_distribution_plot(df, orchestrator.get_color_manager())


def display_summary_statistics(df, orchestrator):
    """Display summary statistics"""
    st.subheader("Data Summary")
    summary = orchestrator.generate_summary_statistics(df)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Responses", summary['total_responses'])
    with col2:
        st.metric("Categories", summary['unique_categories'])
    with col3:
        st.metric("Time Span (min)", f"{summary['time_span_minutes']:.1f}")
    with col4:
        st.metric("Avg Response Time", f"{summary['avg_response_time']:.1f}s")
    
    # Display categories
    st.markdown(f"**Categories observed:** {', '.join(summary['categories'])}")
    
    # Display header information if available
    header_info = summary.get('header_info', {})
    if header_info:
        st.markdown("**Session Information:**")
        for key, value in header_info.items():
            st.markdown(f"- **{key}:** {value}")


def display_insights(df, orchestrator):
    """Display insights"""
    st.subheader("Timeline Analysis & Insights")
    insights = orchestrator.generate_insights(df)
    
    for insight in insights:
        st.markdown(f"• {insight}")


def display_statistics_table(df, orchestrator):
    """Display statistics table"""
    st.subheader("Response Statistics by Category")
    stats = orchestrator.generate_response_statistics(df)
    
    # Convert to DataFrame for better display
    stats_df = pd.DataFrame(stats)
    st.dataframe(stats_df, width='stretch')


def display_export_options(df, pdf_exporter, orchestrator, filename):
    """Display export options"""
    st.subheader("Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV Export
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"{filename}_analysis.csv",
            mime="text/csv",
            help="Download the analyzed data as CSV"
        )
    
    with col2:
        # PDF Export
        if st.button("Generate PDF Report", help="Generate a comprehensive PDF report"):
            with st.spinner("Generating PDF report..."):
                # Create a temporary file for PDF
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    temp_path = tmp_file.name
                
                success = pdf_exporter.export_analysis_report(
                    df, temp_path, filename, orchestrator.get_color_manager()
                )
                
                if success:
                    with open(temp_path, "rb") as pdf_file:
                        pdf_data = pdf_file.read()
                    
                    st.download_button(
                        label="Download PDF Report",
                        data=pdf_data,
                        file_name=f"{filename}_report.pdf",
                        mime="application/pdf",
                        help="Download comprehensive analysis report as PDF"
                    )
                    
                    # Clean up temp file
                    os.unlink(temp_path)
                else:
                    st.error("Failed to generate PDF report")
