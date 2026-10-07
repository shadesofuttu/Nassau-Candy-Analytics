"""
Visualization components for analytics dashboard
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional
from src.config.settings import CHART_HEIGHT, CHART_WIDTH, COLOR_SCHEME


class ChartGenerator:
    """
    Generate interactive charts for profitability analysis
    """
    
    def __init__(self):
        self.colors = COLOR_SCHEME
        self.height = CHART_HEIGHT
        self.width = CHART_WIDTH
    
    def create_margin_distribution(self, data: pd.DataFrame) -> go.Figure:
        """
        Create margin distribution by division
        """
        fig = px.box(
            data,
            x='Division',
            y='Gross Margin %',
            color='Division',
            title='Gross Margin Distribution by Division',
            labels={'Gross Margin %': 'Gross Margin (%)'},
            height=self.height
        )
        fig.update_layout(showlegend=False)
        return fig
    
    def create_top_products_chart(self, data: pd.DataFrame, top_n: int = 10) -> go.Figure:
        """
        Create top products by profit contribution
        """
        top_products = data.nlargest(top_n, 'Gross Profit')
        
        fig = px.bar(
            top_products,
            x='Gross Profit',
            y='Product Name',
            orientation='h',
            color='Gross Margin %',
            color_continuous_scale='RdYlGn',
            title=f'Top {top_n} Products by Gross Profit',
            labels={'Gross Profit': 'Gross Profit ($)', 'Gross Margin %': 'Margin (%)'},
            height=self.height
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        return fig
    
    def create_division_performance(self, data: pd.DataFrame) -> go.Figure:
        """
        Create division performance comparison
        """
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Revenue by Division', 'Profit by Division'),
            specs=[[{'type': 'pie'}, {'type': 'pie'}]]
        )
        
        # Revenue pie chart
        fig.add_trace(
            go.Pie(
                labels=data['Division'],
                values=data['Sales'],
                name='Revenue',
                marker_colors=[self.colors['primary'], self.colors['secondary'], self.colors['success']]
            ),
            row=1, col=1
        )
        
        # Profit pie chart
        fig.add_trace(
            go.Pie(
                labels=data['Division'],
                values=data['Gross Profit'],
                name='Profit',
                marker_colors=[self.colors['primary'], self.colors['secondary'], self.colors['success']]
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text='Division Performance Comparison',
            height=self.height
        )
        return fig
    
    def create_pareto_chart(self, data: pd.DataFrame, value_col: str, label: str) -> go.Figure:
        """
        Create Pareto chart for concentration analysis
        """
        # Sort by value
        sorted_data = data.sort_values(value_col, ascending=False).reset_index(drop=True)
        sorted_data['Cumulative %'] = (sorted_data[value_col].cumsum() / sorted_data[value_col].sum()) * 100
        sorted_data['Product Number'] = range(1, len(sorted_data) + 1)
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add bars for individual values
        fig.add_trace(
            go.Bar(
                x=sorted_data['Product Number'],
                y=sorted_data[value_col],
                name=label,
                marker_color=self.colors['primary']
            ),
            secondary_y=False
        )
        
        # Add line for cumulative percentage
        fig.add_trace(
            go.Scatter(
                x=sorted_data['Product Number'],
                y=sorted_data['Cumulative %'],
                name='Cumulative %',
                mode='lines+markers',
                line=dict(color=self.colors['danger'], width=2)
            ),
            secondary_y=True
        )
        
        # Add 80% reference line
        fig.add_hline(
            y=80,
            line_dash="dash",
            line_color="red",
            annotation_text="80% Line",
            secondary_y=True
        )
        
        fig.update_xaxes(title_text="Product Rank")
        fig.update_yaxes(title_text=label, secondary_y=False)
        fig.update_yaxes(title_text="Cumulative %", secondary_y=True)
        
        fig.update_layout(
            title_text=f'Pareto Analysis - {label}',
            height=self.height,
            showlegend=True
        )
        
        return fig
    
    def create_scatter_matrix(self, data: pd.DataFrame) -> go.Figure:
        """
        Create scatter plot for cost vs sales analysis
        """
        fig = px.scatter(
            data,
            x='Sales',
            y='Cost',
            size='Gross Profit',
            color='Division',
            hover_data=['Product Name', 'Gross Margin %'],
            title='Cost vs Sales Analysis',
            labels={'Sales': 'Sales ($)', 'Cost': 'Cost ($)'},
            height=self.height
        )
        
        # Add diagonal reference line (break-even)
        max_val = max(data['Sales'].max(), data['Cost'].max())
        fig.add_trace(
            go.Scatter(
                x=[0, max_val],
                y=[0, max_val],
                mode='lines',
                name='Break-even Line',
                line=dict(dash='dash', color='red')
            )
        )
        
        return fig
    
    def create_revenue_profit_comparison(self, data: pd.DataFrame) -> go.Figure:
        """
        Create revenue vs profit contribution comparison by division
        """
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Revenue Contribution %',
            x=data['Division'],
            y=data['Revenue Contribution %'],
            marker_color=self.colors['primary']
        ))
        
        fig.add_trace(go.Bar(
            name='Profit Contribution %',
            x=data['Division'],
            y=data['Profit Contribution %'],
            marker_color=self.colors['success']
        ))
        
        fig.update_layout(
            title='Revenue vs Profit Contribution by Division',
            xaxis_title='Division',
            yaxis_title='Contribution (%)',
            barmode='group',
            height=self.height
        )
        
        return fig
    
    def create_margin_trend(self, data: pd.DataFrame) -> go.Figure:
        """
        Create margin trend over time (if date data available)
        """
        if 'Order Date' in data.columns:
            # Aggregate by month
            data['Month'] = pd.to_datetime(data['Order Date']).dt.to_period('M').astype(str)
            monthly_data = data.groupby('Month').agg({
                'Sales': 'sum',
                'Gross Profit': 'sum'
            }).reset_index()
            monthly_data['Gross Margin %'] = (monthly_data['Gross Profit'] / monthly_data['Sales']) * 100
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=monthly_data['Month'],
                y=monthly_data['Gross Margin %'],
                mode='lines+markers',
                name='Gross Margin %',
                line=dict(color=self.colors['primary'], width=3)
            ))
            
            fig.update_layout(
                title='Gross Margin Trend Over Time',
                xaxis_title='Month',
                yaxis_title='Gross Margin (%)',
                height=self.height
            )
            
            return fig
        else:
            return None
    
    def create_kpi_cards_data(self, summary_metrics: dict) -> dict:
        """
        Prepare data for KPI cards display
        """
        return {
            'Total Revenue': f"${summary_metrics['total_revenue']:,.0f}",
            'Total Profit': f"${summary_metrics['total_profit']:,.0f}",
            'Overall Margin': f"{summary_metrics['overall_margin']:.2f}%",
            'Total Products': f"{summary_metrics['total_products']}",
            'Avg Order Value': f"${summary_metrics['avg_order_value']:,.2f}",
            'Top Division': summary_metrics['top_division'],
            'Products (80% Revenue)': f"{summary_metrics['products_in_revenue_pareto']}",
            'Products (80% Profit)': f"{summary_metrics['products_in_profit_pareto']}"
        }
