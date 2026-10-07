"""
Main Streamlit Dashboard Application
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.data_loader import DataLoader
from src.analytics.profitability_analyzer import ProfitabilityAnalyzer
from src.visualization.charts import ChartGenerator
from src.config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #555;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_and_process_data():
    """
    Load and process data with caching
    """
    try:
        loader = DataLoader()
        # Try to load from processed data first, then raw
        try:
            df = loader.load_from_database('orders')
        except:
            # Load from raw data (user needs to upload CSV)
            st.warning("No database found. Please upload data in the sidebar.")
            return None
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None


def main():
    # Header
    st.markdown('<h1 class="main-header">🍬 Nassau Candy Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Product Line Profitability & Margin Performance Analysis</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Navigation")
        page = st.radio(
            "Select Dashboard",
            [
                "Overview",
                "Product Profitability",
                "Division Performance",
                "Pareto Analysis",
                "Cost Structure",
                "Risk Identification"
            ]
        )
        
        st.markdown("---")
        st.header("📁 Data Upload")
        uploaded_file = st.file_uploader(
            "Upload CSV/Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload your order data file"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_upload = pd.read_csv(uploaded_file)
                else:
                    df_upload = pd.read_excel(uploaded_file)
                
                loader = DataLoader()
                df_clean = loader.clean_data(df_upload)
                df_processed = loader.calculate_metrics(df_clean)
                loader.load_to_database(df_processed, 'orders')
                
                st.success("✅ Data uploaded successfully!")
                st.info(f"Loaded {len(df_processed)} records")
                
                # Clear cache to reload new data
                st.cache_data.clear()
                
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        
        st.markdown("---")
        st.markdown("### 💡 About")
        st.info(
            "This dashboard provides comprehensive profitability analysis "
            "for Nassau Candy Distributor, including product-level insights, "
            "division performance, and margin optimization recommendations."
        )
    
    # Load data
    data = load_and_process_data()
    
    if data is None:
        st.warning("⚠️ Please upload data using the sidebar to begin analysis.")
        return
    
    # Initialize analyzer and chart generator
    analyzer = ProfitabilityAnalyzer(data)
    chart_gen = ChartGenerator()
    
    # Page routing
    if page == "Overview":
        show_overview(analyzer, chart_gen)
    elif page == "Product Profitability":
        show_product_profitability(analyzer, chart_gen)
    elif page == "Division Performance":
        show_division_performance(analyzer, chart_gen)
    elif page == "Pareto Analysis":
        show_pareto_analysis(analyzer, chart_gen)
    elif page == "Cost Structure":
        show_cost_structure(analyzer, chart_gen)
    elif page == "Risk Identification":
        show_risk_identification(analyzer, chart_gen)


def show_overview(analyzer, chart_gen):
    st.header("📈 Executive Overview")
    
    # Get summary metrics
    summary = analyzer.get_summary_metrics()
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", f"${summary['total_revenue']:,.0f}")
        st.metric("Total Orders", f"{summary['total_orders']:,}")
    
    with col2:
        st.metric("Total Profit", f"${summary['total_profit']:,.0f}")
        st.metric("Avg Order Value", f"${summary['avg_order_value']:,.2f}")
    
    with col3:
        st.metric("Overall Margin", f"{summary['overall_margin']:.2f}%")
        st.metric("Total Products", f"{summary['total_products']}")
    
    with col4:
        st.metric("Top Division", summary['top_division'])
        st.metric("Division Profit", f"${summary['top_division_profit']:,.0f}")
    
    st.markdown("---")
    
    # Division performance
    col1, col2 = st.columns(2)
    
    with col1:
        division_data = analyzer.division_level_analysis()
        fig = chart_gen.create_division_performance(division_data)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Key Insights")
        st.markdown(f"""
        - **Revenue Concentration**: {summary['products_in_revenue_pareto']} products generate 80% of revenue
        - **Profit Concentration**: {summary['products_in_profit_pareto']} products generate 80% of profit
        - **High Margin Products**: {summary['high_margin_products']} products with >30% margin
        - **Low Margin Products**: {summary['low_margin_products']} products with <10% margin
        """)
        
        # Division table
        st.subheader("Division Summary")
        st.dataframe(
            division_data[['Division', 'Sales', 'Gross Profit', 'Avg Gross Margin %']].style.format({
                'Sales': '${:,.0f}',
                'Gross Profit': '${:,.0f}',
                'Avg Gross Margin %': '{:.2f}%'
            }),
            use_container_width=True
        )


def show_product_profitability(analyzer, chart_gen):
    st.header("💰 Product Profitability Analysis")
    
    product_data = analyzer.product_level_analysis()
    
    # Top products chart
    top_n = st.slider("Number of top products to display", 5, 20, 10)
    fig = chart_gen.create_top_products_chart(product_data, top_n)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        selected_division = st.multiselect(
            "Filter by Division",
            options=product_data['Division'].unique(),
            default=product_data['Division'].unique()
        )
    
    with col2:
        margin_filter = st.selectbox(
            "Margin Category",
            options=['All'] + list(product_data['Margin Category'].unique())
        )
    
    # Apply filters
    filtered_data = product_data[product_data['Division'].isin(selected_division)]
    if margin_filter != 'All':
        filtered_data = filtered_data[filtered_data['Margin Category'] == margin_filter]
    
    # Product table
    st.subheader("Product Details")
    st.dataframe(
        filtered_data[[
            'Product Name', 'Division', 'Sales', 'Gross Profit', 
            'Gross Margin %', 'Profit per Unit', 'Margin Category'
        ]].style.format({
            'Sales': '${:,.0f}',
            'Gross Profit': '${:,.0f}',
            'Gross Margin %': '{:.2f}%',
            'Profit per Unit': '${:.2f}'
        }),
        use_container_width=True,
        height=400
    )


def show_division_performance(analyzer, chart_gen):
    st.header("🏢 Division Performance Analysis")
    
    division_data = analyzer.division_level_analysis()
    product_data = analyzer.product_level_analysis()
    
    # Revenue vs Profit comparison
    fig = chart_gen.create_revenue_profit_comparison(division_data)
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Margin distribution
        fig = chart_gen.create_margin_distribution(product_data)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Division Metrics")
        st.dataframe(
            division_data.style.format({
                'Sales': '${:,.0f}',
                'Gross Profit': '${:,.0f}',
                'Avg Gross Margin %': '{:.2f}%',
                'Revenue Contribution %': '{:.2f}%',
                'Profit Contribution %': '{:.2f}%',
                'Revenue-Profit Imbalance': '{:.2f}%'
            }),
            use_container_width=True
        )


def show_pareto_analysis(analyzer, chart_gen):
    st.header("📊 Pareto Analysis (80/20 Rule)")
    
    revenue_pareto, profit_pareto = analyzer.pareto_analysis()
    
    st.info(
        "🎯 The Pareto Principle suggests that 80% of results come from 20% of causes. "
        "This analysis identifies which products drive the majority of revenue and profit."
    )
    
    tab1, tab2 = st.tabs(["Revenue Concentration", "Profit Concentration"])
    
    with tab1:
        fig = chart_gen.create_pareto_chart(revenue_pareto, 'Sales', 'Revenue ($)')
        st.plotly_chart(fig, use_container_width=True)
        
        st.metric(
            "Products driving 80% of revenue",
            f"{len(revenue_pareto)} out of {analyzer.product_level_analysis().shape[0]}"
        )
    
    with tab2:
        fig = chart_gen.create_pareto_chart(profit_pareto, 'Gross Profit', 'Gross Profit ($)')
        st.plotly_chart(fig, use_container_width=True)
        
        st.metric(
            "Products driving 80% of profit",
            f"{len(profit_pareto)} out of {analyzer.product_level_analysis().shape[0]}"
        )


def show_cost_structure(analyzer, chart_gen):
    st.header("💵 Cost Structure Diagnostics")
    
    cost_data = analyzer.cost_structure_analysis()
    
    # Scatter plot
    product_data = analyzer.product_level_analysis()
    fig = chart_gen.create_scatter_matrix(product_data)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Pricing status breakdown
    col1, col2, col3 = st.columns(3)
    
    with col1:
        overpriced = cost_data[cost_data['Pricing Status'] == 'Overpriced/Inefficient']
        st.metric("Overpriced/Inefficient", len(overpriced))
    
    with col2:
        normal = cost_data[cost_data['Pricing Status'] == 'Normal']
        st.metric("Normal Pricing", len(normal))
    
    with col3:
        underpriced = cost_data[cost_data['Pricing Status'] == 'Underpriced/Opportunity']
        st.metric("Underpriced/Opportunity", len(underpriced))
    
    # Cost structure table
    st.subheader("Cost-Sales Analysis")
    st.dataframe(
        cost_data.style.format({
            'Sales': '${:,.0f}',
            'Cost': '${:,.0f}',
            'Gross Profit': '${:,.0f}',
            'Cost-to-Sales Ratio': '{:.3f}',
            'Gross Margin %': '{:.2f}%'
        }),
        use_container_width=True,
        height=400
    )


def show_risk_identification(analyzer, chart_gen):
    st.header("⚠️ Margin Risk Identification")
    
    risks = analyzer.identify_margin_risks()
    
    # Risk categories
    st.subheader("Risk Categories")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Low Margin, High Sales", len(risks['low_margin_high_sales']))
        st.metric("Negative Margin", len(risks['negative_margin']))
    
    with col2:
        st.metric("High Margin, Low Sales", len(risks['high_margin_low_sales']))
        st.metric("Underperforming", len(risks['underperforming']))
    
    st.markdown("---")
    
    # Risk details
    risk_category = st.selectbox(
        "Select Risk Category",
        [
            "Low Margin, High Sales (Priority)",
            "Negative Margin (Critical)",
            "High Margin, Low Sales (Opportunity)",
            "Underperforming (Review)"
        ]
    )
    
    if "Low Margin, High Sales" in risk_category:
        display_data = risks['low_margin_high_sales']
        st.warning("⚠️ These products have high sales volume but low margins. Consider repricing.")
    elif "Negative Margin" in risk_category:
        display_data = risks['negative_margin']
        st.error("🚨 These products are losing money. Immediate action required.")
    elif "High Margin, Low Sales" in risk_category:
        display_data = risks['high_margin_low_sales']
        st.info("💡 These products are profitable but underutilized. Marketing opportunity.")
    else:
        display_data = risks['underperforming']
        st.warning("📉 These products should be reviewed for discontinuation or repositioning.")
    
    if len(display_data) > 0:
        st.dataframe(
            display_data[[
                'Product Name', 'Division', 'Sales', 'Gross Profit',
                'Gross Margin %', 'Revenue Contribution %', 'Profit Contribution %'
            ]].style.format({
                'Sales': '${:,.0f}',
                'Gross Profit': '${:,.0f}',
                'Gross Margin %': '{:.2f}%',
                'Revenue Contribution %': '{:.2f}%',
                'Profit Contribution %': '{:.2f}%'
            }),
            use_container_width=True,
            height=400
        )
    else:
        st.success("✅ No products in this risk category!")


if __name__ == "__main__":
    main()
