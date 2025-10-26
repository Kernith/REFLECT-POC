import streamlit as st
import pandas as pd
import io
from backend.analysis.orchestrator import AnalysisOrchestrator
from backend.analysis.statistics_calculator import StatisticsCalculator
from backend.analysis.insights_generator import InsightsGenerator
from backend.visualization.plot_factory import PlotFactory
from backend.export.pdf_exporter import PDFExporter
from gui.streamlit.adapters.plot_adapter import StreamlitPlotAdapter


def render_analysis_page():
    """Render the analysis page"""
    st.title("📈 Data Analysis")
    
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
    
    # Navigation
    if st.button("🏠 Back to Home"):
        st.session_state.page = "home"
        st.rerun()
    
    st.markdown("---")
    
    # File upload
    uploaded_file = st.file_uploader("📁 Upload CSV file", type=['csv'], help="Upload a CSV file with observation data")
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with st.spinner("Loading and validating data..."):
            # Create a temporary file path
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Load and validate data
            result = orchestrator.load_and_validate_data(temp_path)
            
            # Clean up temp file
            import os
            os.remove(temp_path)
        
        if result.success:
            df = result.data
            st.success(f"✅ Data loaded successfully! {len(df)} records")
            
            # Store data in session state
            st.session_state.current_data = df
            
            # Display analysis sections
            display_summary_statistics(df, orchestrator)
            st.markdown("---")
            
            display_time_series_plot(df, plot_adapter, orchestrator)
            st.markdown("---")
            
            display_distribution_plot(df, plot_adapter, orchestrator)
            st.markdown("---")
            
            display_statistics_table(df, orchestrator)
            st.markdown("---")
            
            display_insights(df, orchestrator)
            st.markdown("---")
            
            # Export options
            display_export_options(df, pdf_exporter, orchestrator, uploaded_file.name)
            
        else:
            st.error(f"❌ Error loading data: {result.error}")
    
    elif 'current_data' in st.session_state:
        # Display previously loaded data
        df = st.session_state.current_data
        st.info(f"📊 Displaying previously loaded data ({len(df)} records)")
        
        display_summary_statistics(df, orchestrator)
        st.markdown("---")
        
        display_time_series_plot(df, plot_adapter, orchestrator)
        st.markdown("---")
        
        display_distribution_plot(df, plot_adapter, orchestrator)
        st.markdown("---")
        
        display_statistics_table(df, orchestrator)
        st.markdown("---")
        
        display_insights(df, orchestrator)
        st.markdown("---")
        
        # Export options
        display_export_options(df, pdf_exporter, orchestrator, "analysis_data")


def display_summary_statistics(df, orchestrator):
    """Display summary statistics"""
    st.subheader("📊 Data Summary")
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


def display_time_series_plot(df, plot_adapter, orchestrator):
    """Display time series plot"""
    st.subheader("📈 Response Timeline")
    plot_adapter.display_time_series_plot(df, orchestrator.get_color_manager())


def display_distribution_plot(df, plot_adapter, orchestrator):
    """Display distribution plot"""
    st.subheader("🥧 Response Distribution")
    plot_adapter.display_category_distribution_plot(df, orchestrator.get_color_manager())


def display_statistics_table(df, orchestrator):
    """Display statistics table"""
    st.subheader("📋 Response Statistics by Category")
    stats = orchestrator.generate_response_statistics(df)
    
    # Convert to DataFrame for better display
    stats_df = pd.DataFrame(stats)
    st.dataframe(stats_df, use_container_width=True)


def display_insights(df, orchestrator):
    """Display insights"""
    st.subheader("💡 Timeline Analysis & Insights")
    insights = orchestrator.generate_insights(df)
    
    for insight in insights:
        st.markdown(f"• {insight}")


def display_export_options(df, pdf_exporter, orchestrator, filename):
    """Display export options"""
    st.subheader("📤 Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV Export
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=f"{filename}_analysis.csv",
            mime="text/csv",
            help="Download the analyzed data as CSV"
        )
    
    with col2:
        # PDF Export
        if st.button("📊 Generate PDF Report", help="Generate a comprehensive PDF report"):
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
                        label="📊 Download PDF Report",
                        data=pdf_data,
                        file_name=f"{filename}_report.pdf",
                        mime="application/pdf",
                        help="Download comprehensive analysis report as PDF"
                    )
                    
                    # Clean up temp file
                    os.unlink(temp_path)
                else:
                    st.error("Failed to generate PDF report")
