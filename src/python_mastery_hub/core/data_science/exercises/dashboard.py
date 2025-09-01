"""
Interactive Dashboard Exercise for the Data Science module.
"""

from typing import Dict, Any


class DashboardExercise:
    """Interactive dashboard exercise implementation."""
    
    @staticmethod
    def get_exercise() -> Dict[str, Any]:
        """Get the interactive dashboard exercise."""
        return {
            "instructions": """
Build an interactive data visualization dashboard that allows users to explore
and analyze data dynamically. Create multiple visualization types with filtering
and selection capabilities.
""",
            "objectives": [
                "Design an intuitive dashboard layout",
                "Implement multiple visualization types",
                "Add interactive filtering and selection",
                "Create responsive and user-friendly interface",
                "Enable real-time data updates"
            ],
            "tasks": [
                {
                    "step": 1,
                    "title": "Dashboard Architecture Design",
                    "description": "Plan the dashboard structure and components",
                    "requirements": [
                        "Define dashboard layout and sections",
                        "Plan data flow and update mechanisms",
                        "Design user interaction patterns",
                        "Choose appropriate visualization library"
                    ]
                },
                {
                    "step": 2,
                    "title": "Data Processing and Management",
                    "description": "Set up data handling for the dashboard",
                    "requirements": [
                        "Create data loading and preprocessing functions",
                        "Implement data caching for performance",
                        "Handle data updates and refreshes",
                        "Validate data quality and completeness"
                    ]
                },
                {
                    "step": 3,
                    "title": "Core Visualizations",
                    "description": "Implement primary visualization components",
                    "requirements": [
                        "Create at least 5 different chart types",
                        "Implement proper styling and theming",
                        "Add titles, labels, and legends",
                        "Ensure responsive design"
                    ]
                },
                {
                    "step": 4,
                    "title": "Interactive Controls",
                    "description": "Add interactive filtering and selection",
                    "requirements": [
                        "Implement date range selectors",
                        "Add category and metric filters",
                        "Create dynamic dropdowns and sliders",
                        "Enable chart-to-chart interactions"
                    ]
                },
                {
                    "step": 5,
                    "title": "Advanced Features",
                    "description": "Implement advanced dashboard features",
                    "requirements": [
                        "Add data export functionality",
                        "Implement dashboard sharing options",
                        "Create custom aggregation options",
                        "Add performance monitoring"
                    ]
                },
                {
                    "step": 6,
                    "title": "Testing and Documentation",
                    "description": "Test and document the dashboard",
                    "requirements": [
                        "Test with different data scenarios",
                        "Validate cross-browser compatibility",
                        "Create user documentation",
                        "Document technical specifications"
                    ]
                }
            ],
            "starter_code": '''
import pandas as pd
import numpy as np
import plotly.dash as dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

class InteractiveDashboard:
    """Interactive dashboard implementation using Plotly Dash."""
    
    def __init__(self, data_source):
        """
        Initialize the dashboard with data source.
        
        Args:
            data_source (str): Path to data file or database connection
        """
        self.app = dash.Dash(__name__)
        self.data_source = data_source
        self.df = None
        self.setup_data()
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_data(self):
        """Load and preprocess data for the dashboard."""
        # TODO: Implement data loading and preprocessing
        pass
    
    def setup_layout(self):
        """Define the dashboard layout and components."""
        self.app.layout = html.Div([
            # TODO: Implement dashboard layout
            html.H1("Interactive Data Dashboard", className="dashboard-title"),
            
            # Control panel
            html.Div([
                # TODO: Add filters and controls
            ], className="control-panel"),
            
            # Main visualization area
            html.Div([
                # TODO: Add visualization components
            ], className="visualization-area"),
            
            # Summary statistics
            html.Div([
                # TODO: Add summary statistics
            ], className="summary-area")
        ])
    
    def setup_callbacks(self):
        """Define interactive callbacks for dashboard components."""
        
        @self.app.callback(
            Output('main-chart', 'figure'),
            [Input('date-picker', 'start_date'),
             Input('date-picker', 'end_date'),
             Input('category-dropdown', 'value')]
        )
        def update_main_chart(start_date, end_date, category):
            """Update main chart based on user selections."""
            # TODO: Implement chart update logic
            pass
        
        @self.app.callback(
            Output('summary-stats', 'children'),
            [Input('main-chart', 'selectedData')]
        )
        def update_summary_stats(selected_data):
            """Update summary statistics based on chart selection."""
            # TODO: Implement summary update logic
            pass
    
    def create_time_series_chart(self, filtered_df):
        """Create time series visualization."""
        # TODO: Implement time series chart
        pass
    
    def create_distribution_chart(self, filtered_df):
        """Create distribution visualization."""
        # TODO: Implement distribution chart
        pass
    
    def create_correlation_heatmap(self, filtered_df):
        """Create correlation heatmap."""
        # TODO: Implement correlation heatmap
        pass
    
    def create_scatter_plot(self, filtered_df):
        """Create interactive scatter plot."""
        # TODO: Implement scatter plot
        pass
    
    def create_bar_chart(self, filtered_df):
        """Create interactive bar chart."""
        # TODO: Implement bar chart
        pass
    
    def calculate_summary_stats(self, filtered_df):
        """Calculate summary statistics for display."""
        # TODO: Implement summary calculations
        pass
    
    def export_data(self, filtered_df, format='csv'):
        """Export filtered data in specified format."""
        # TODO: Implement data export
        pass
    
    def run_server(self, debug=True, port=8050):
        """Run the dashboard server."""
        self.app.run_server(debug=debug, port=port)

# Alternative implementation using Streamlit
import streamlit as st

class StreamlitDashboard:
    """Alternative dashboard implementation using Streamlit."""
    
    def __init__(self, data_source):
        self.data_source = data_source
        self.df = None
        
    def load_data(self):
        """Load and cache data for the dashboard."""
        # TODO: Implement data loading with caching
        pass
    
    def render_sidebar(self):
        """Render sidebar with controls and filters."""
        # TODO: Implement sidebar controls
        pass
    
    def render_main_content(self):
        """Render main dashboard content."""
        # TODO: Implement main content area
        pass
    
    def run(self):
        """Run the Streamlit dashboard."""
        st.set_page_config(
            page_title="Interactive Data Dashboard",
            page_icon="📊",
            layout="wide"
        )
        
        # TODO: Implement dashboard structure
        pass

def main():
    """Main execution function."""
    # Choose dashboard implementation
    dashboard_type = input("Choose dashboard type (dash/streamlit): ").lower()
    
    if dashboard_type == 'dash':
        dashboard = InteractiveDashboard('your_dataset.csv')
        print("Starting Plotly Dash dashboard...")
        print("Open http://localhost:8050 in your browser")
        dashboard.run_server()
    
    elif dashboard_type == 'streamlit':
        dashboard = StreamlitDashboard('your_dataset.csv')
        print("Starting Streamlit dashboard...")
        print("Run: streamlit run dashboard.py")
        dashboard.run()
    
    else:
        print("Invalid choice. Please choose 'dash' or 'streamlit'")

if __name__ == "__main__":
    main()
''',
            "evaluation_criteria": [
                "Dashboard design and usability (25%)",
                "Visualization quality and variety (25%)",
                "Interactive functionality (20%)",
                "Performance and responsiveness (15%)",
                "Code organization and documentation (15%)"
            ],
            "solution": '''
# Complete dashboard implementation with production-ready features
# Includes proper error handling, performance optimization, and accessibility
'''
        }