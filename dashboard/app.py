"""
Main Streamlit Dashboard Application
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

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
    
    # Load data early so it's available in sidebar
    data = load_and_process_data()
    
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
                "Risk Identification",
                "Scenario Simulator",
                "Methodology"
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
        
        st.markdown("---")
        st.markdown("### 📥 Export Analysis")
        
        if data is not None:
            export_analyzer = ProfitabilityAnalyzer(data)
            export_product_data = export_analyzer.product_level_analysis()
            export_summary = export_analyzer.get_summary_metrics()
            export_risks = export_analyzer.identify_margin_risks()
            
            # CSV Export
            csv_buffer = BytesIO()
            export_product_data.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            st.download_button(
                label="📄 Download CSV",
                data=csv_buffer,
                file_name=f"product_profitability_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Excel Export
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                export_product_data.to_excel(writer, sheet_name='Product Analysis', index=False)
                export_analyzer.division_level_analysis().to_excel(writer, sheet_name='Division Analysis', index=False)
            excel_buffer.seek(0)
            
            st.download_button(
                label="📊 Download Excel",
                data=excel_buffer,
                file_name=f"product_profitability_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            # PDF Executive Summary
            pdf_buffer = generate_executive_summary_pdf(
                export_summary,
                export_product_data,
                export_risks
            )
            
            st.download_button(
                label="📑 Download Executive Summary (PDF)",
                data=pdf_buffer,
                file_name=f"executive_summary_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        else:
            st.warning("Upload data to enable exports")
    
    # Check if data is available
    if data is None:
        st.warning("⚠️ Please upload data using the sidebar to begin analysis.")
        return
    
    # Initialize analyzer and chart generator
    analyzer = ProfitabilityAnalyzer(data)
    chart_gen = ChartGenerator()
    
    # Page routing
    if page == "Overview":
        show_overview(analyzer, chart_gen, data)
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
    elif page == "Scenario Simulator":
        show_scenario_simulator(analyzer, chart_gen)
    elif page == "Methodology":
        show_methodology()


def show_overview(analyzer, chart_gen, data):
    st.header("📈 Executive Overview")
    
    # Get summary metrics
    summary = analyzer.get_summary_metrics()
    
        # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", f"${summary['total_revenue']:,.0f}")
        st.metric("Total Orders", f"{summary['total_orders']:,}")
    
    with col2:
        st.metric("Total Profit", f"${summary['total_profit']:,.0f}", help="Total revenue minus total costs. This is the absolute dollar amount earned after paying for products.")
        st.metric("Avg Order Value", f"${summary['avg_order_value']:,.2f}")
    
    with col3:
        st.metric("Overall Margin", f"{summary['overall_margin']:.2f}%", help="Percentage of each sales dollar kept as profit. Higher percentages mean better profitability. Formula: (Gross Profit / Sales) × 100")
        st.metric("Total Products", f"{summary['total_products']}")
    
    with col4:
        st.metric("Top Division", summary['top_division'])
        st.metric("Division Profit", f"${summary['top_division_profit']:,.0f}")
    
    st.markdown("---")
    
    # Data Quality Section
    st.subheader("🔍 Data Quality")
    
    # Note: Data shown is after cleaning, so this displays the cleaned state
    total_rows = len(data)
    
    # Since data is already cleaned, check for remaining issues
    missing_values = data.isnull().sum().sum()
    duplicate_rows = data.duplicated().sum()
    
    # Check for any remaining invalid values
    invalid_sales = 0
    if 'Sales' in data.columns:
        invalid_sales = len(data[data['Sales'] < 0])
    
    invalid_cost = 0
    if 'Cost' in data.columns:
        invalid_cost = len(data[data['Cost'] < 0])
    
    # Data is already cleaned, so status should always be Ready
    total_issues = missing_values + duplicate_rows + invalid_sales + invalid_cost
    
    # Display metrics in columns
    quality_col1, quality_col2, quality_col3 = st.columns(3)
    
    with quality_col1:
        st.metric("Total Rows Loaded", f"{total_rows:,}")
    
    with quality_col2:
        st.metric("Data Completeness", "100%" if missing_values == 0 else f"{((total_rows * len(data.columns) - missing_values) / (total_rows * len(data.columns)) * 100):.1f}%")
    
    with quality_col3:
        if total_issues == 0:
            st.success("✅ Ready for Analysis")
        else:
            st.warning("⚠️ Minor Issues Detected")
    
    st.caption("Note: Data has been automatically cleaned (duplicates removed, missing values filled, invalid records excluded).")
    
    st.markdown("---")
    
    # Decision Center
    st.subheader("🎯 Decision Center")
    
    product_data = analyzer.product_level_analysis()
    risks = analyzer.identify_margin_risks()
    
    decision_col1, decision_col2 = st.columns(2)
    
    with decision_col1:
        # Top product by gross profit
        top_product = product_data.nlargest(1, 'Gross Profit').iloc[0]
        st.markdown(f"**💰 Top Profit Generator**: {top_product['Product Name']}")
        st.caption(f"Action: Protect pricing and ensure consistent supply for this ${top_product['Gross Profit']:,.0f} profit leader.")
        
        # Margin review needed
        if len(risks['low_margin_high_sales']) > 0:
            margin_risk = risks['low_margin_high_sales'].iloc[0]
            st.markdown(f"**⚠️ Margin Review Needed**: {margin_risk['Product Name']}")
            st.caption(f"Action: Reprice or renegotiate costs - this high-volume product has only {margin_risk['Gross Margin %']:.1f}% margin.")
        else:
            st.markdown("**✅ Margin Health**: All high-volume products have acceptable margins.")
            st.caption("Action: Maintain current pricing strategy and monitor quarterly.")
    
    with decision_col2:
        # Highest-margin low-sales opportunity
        if len(risks['high_margin_low_sales']) > 0:
            opportunity = risks['high_margin_low_sales'].nlargest(1, 'Gross Margin %').iloc[0]
            st.markdown(f"**💡 Growth Opportunity**: {opportunity['Product Name']}")
            st.caption(f"Action: Boost marketing for this {opportunity['Gross Margin %']:.1f}% margin product with untapped revenue potential.")
        else:
            st.markdown("**📊 Portfolio Balance**: High-margin products are selling well.")
            st.caption("Action: Continue current sales and marketing allocation.")
        
        # Concentration insight
        pareto_pct = (summary['products_in_revenue_pareto'] / summary['total_products']) * 100
        st.markdown(f"**📈 Revenue Concentration**: {summary['products_in_revenue_pareto']} products ({pareto_pct:.0f}%) drive 80% of revenue.")
        if pareto_pct < 20:
            st.caption("Action: Maintain focus on these core products while diversifying revenue sources.")
        else:
            st.caption("Action: Strong diversification - continue balanced portfolio management.")
    
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
            use_container_width=True,
            column_config={
                'Gross Profit': st.column_config.NumberColumn(
                    'Gross Profit',
                    help='Revenue minus cost. The dollar amount earned after paying suppliers.'
                ),
                'Avg Gross Margin %': st.column_config.NumberColumn(
                    'Avg Gross Margin %',
                    help='Average profit percentage across all products in this division.'
                )
            }
        )


def show_product_profitability(analyzer, chart_gen):
    st.header("💰 Product Profitability Analysis")
    
    product_data = analyzer.product_level_analysis()
    
    # Top products chart
    top_n = st.slider("Number of top products to display", 5, 20, 10)
    fig = chart_gen.create_top_products_chart(product_data, top_n)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Product Portfolio Matrix
    st.subheader("📊 Product Portfolio Matrix")
    
    st.info(
        "**Strategic Quadrants Explained:**\n\n"
        "🟢 **Core Products** (High Sales, High Margin): Your profit engines. Maintain quality and protect pricing.\n\n"
        "🟠 **Margin Risk** (High Sales, Low Margin): High volume but thin margins. Consider repricing or cost reduction.\n\n"
        "🔵 **Growth Opportunities** (Low Sales, High Margin): Profitable but underutilized. Invest in marketing and sales.\n\n"
        "🔴 **Underperformers** (Low Sales, Low Margin): Review for potential discontinuation or repositioning."
    )
    
    portfolio_fig = chart_gen.create_portfolio_matrix(product_data)
    st.plotly_chart(portfolio_fig, use_container_width=True)
    
    # Portfolio summary metrics
    median_sales = product_data['Sales'].median()
    median_margin = product_data['Gross Margin %'].median()
    
    portfolio_summary = {
        'Core Products': len(product_data[(product_data['Sales'] >= median_sales) & (product_data['Gross Margin %'] >= median_margin)]),
        'Margin Risk': len(product_data[(product_data['Sales'] >= median_sales) & (product_data['Gross Margin %'] < median_margin)]),
        'Growth Opportunities': len(product_data[(product_data['Sales'] < median_sales) & (product_data['Gross Margin %'] >= median_margin)]),
        'Underperformers': len(product_data[(product_data['Sales'] < median_sales) & (product_data['Gross Margin %'] < median_margin)])
    }
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    with summary_col1:
        st.metric("🟢 Core Products", portfolio_summary['Core Products'])
    with summary_col2:
        st.metric("🟠 Margin Risk", portfolio_summary['Margin Risk'])
    with summary_col3:
        st.metric("🔵 Growth Opportunities", portfolio_summary['Growth Opportunities'])
    with summary_col4:
        st.metric("🔴 Underperformers", portfolio_summary['Underperformers'])
    
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
    if len(filtered_data) > 0:
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
            height=400,
            column_config={
                'Gross Profit': st.column_config.NumberColumn(
                    'Gross Profit',
                    help='Total profit from this product (Sales - Cost)'
                ),
                'Gross Margin %': st.column_config.NumberColumn(
                    'Gross Margin %',
                    help='Profit as a percentage of sales. Shows how much of each dollar becomes profit.'
                ),
                'Profit per Unit': st.column_config.NumberColumn(
                    'Profit per Unit',
                    help='Average profit earned on each unit sold. Gross Profit divided by Units.'
                )
            }
        )
    else:
        st.info("No products match the selected filters. Please adjust your filter criteria.")


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
            use_container_width=True,
            column_config={
                'Revenue Contribution %': st.column_config.NumberColumn(
                    'Revenue Contribution %',
                    help='Percentage of total company revenue from this division.'
                ),
                'Profit Contribution %': st.column_config.NumberColumn(
                    'Profit Contribution %',
                    help='Percentage of total company profit from this division.'
                ),
                'Revenue-Profit Imbalance': st.column_config.NumberColumn(
                    'Revenue-Profit Imbalance',
                    help='Difference between revenue % and profit %. Positive means lower margins than average.'
                )
            }
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
        height=400,
        column_config={
            'Cost-to-Sales Ratio': st.column_config.NumberColumn(
                'Cost-to-Sales Ratio',
                help='Cost as a fraction of sales. Lower is better. Example: 0.700 means 70 cents of cost for every sales dollar.'
            )
        }
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
            height=400,
            column_config={
                                'Revenue Contribution %': st.column_config.NumberColumn(
                    'Revenue Contribution %',
                    help="This product's share of total revenue. Higher means more important to overall sales."
                ),
                'Profit Contribution %': st.column_config.NumberColumn(
                    'Profit Contribution %',
                    help="This product's share of total profit. Compare to revenue % to see margin efficiency."
                )
            }
        )
    else:
        st.success("✅ No products in this risk category!")


def show_scenario_simulator(analyzer, chart_gen):
    st.header("🎯 Scenario Simulator")
    
    st.info(
        "💡 Simulate the impact of pricing and cost changes on product profitability. "
        "Adjust the sliders to see how different scenarios affect your margins."
    )
    
    product_data = analyzer.product_level_analysis()
    
    # Product selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_product = st.selectbox(
            "Select Product to Simulate",
            options=product_data['Product Name'].tolist(),
            help="Choose a product to run pricing and cost scenarios"
        )
    
    with col2:
        st.metric("Division", product_data[product_data['Product Name'] == selected_product]['Division'].iloc[0])
    
    # Get current product data
    current = product_data[product_data['Product Name'] == selected_product].iloc[0]
    
    st.markdown("---")
    
    # Simulation controls
    st.subheader("📊 Adjust Parameters")
    
    sim_col1, sim_col2 = st.columns(2)
    
    with sim_col1:
        price_change = st.slider(
            "Selling Price Adjustment (%)",
            min_value=-50,
            max_value=50,
            value=0,
            step=1,
            help="Adjust selling price up or down by percentage"
        )
        st.caption(f"Original Price per Unit: ${current['Sales'] / current['Units']:.2f}")
    
    with sim_col2:
        cost_change = st.slider(
            "Cost Adjustment (%)",
            min_value=-50,
            max_value=50,
            value=0,
            step=1,
            help="Adjust cost up or down by percentage (e.g., supplier negotiation)"
        )
        st.caption(f"Original Cost per Unit: ${current['Cost'] / current['Units']:.2f}")
    
    st.markdown("---")
    
    # Calculate simulated values
    sim_price_per_unit = (current['Sales'] / current['Units']) * (1 + price_change / 100)
    sim_cost_per_unit = (current['Cost'] / current['Units']) * (1 + cost_change / 100)
    
    sim_sales = sim_price_per_unit * current['Units']
    sim_cost = sim_cost_per_unit * current['Units']
    sim_profit = sim_sales - sim_cost
    sim_margin = (sim_profit / sim_sales * 100) if sim_sales > 0 else 0
    
    # Results comparison
    st.subheader("📈 Simulation Results")
    
    result_col1, result_col2, result_col3, result_col4 = st.columns(4)
    
    with result_col1:
        st.metric(
            "Projected Sales",
            f"${sim_sales:,.0f}",
            delta=f"{((sim_sales - current['Sales']) / current['Sales'] * 100):.1f}%",
            help="Total revenue with adjusted pricing"
        )
    
    with result_col2:
        st.metric(
            "Projected Cost",
            f"${sim_cost:,.0f}",
            delta=f"{((sim_cost - current['Cost']) / current['Cost'] * 100):.1f}%",
            delta_color="inverse",
            help="Total cost with adjustments"
        )
    
    with result_col3:
        st.metric(
            "Projected Gross Profit",
            f"${sim_profit:,.0f}",
            delta=f"{((sim_profit - current['Gross Profit']) / abs(current['Gross Profit']) * 100):.1f}%",
            help="Gross profit after changes"
        )
    
    with result_col4:
        st.metric(
            "Projected Margin",
            f"{sim_margin:.2f}%",
            delta=f"{(sim_margin - current['Gross Margin %']):.2f}pp",
            help="Gross margin percentage"
        )
    
    st.markdown("---")
    
    # Current vs Simulated comparison table
    st.subheader("📋 Current vs Simulated Comparison")
    
    comparison_df = pd.DataFrame({
        'Metric': ['Sales', 'Cost', 'Gross Profit', 'Gross Margin %', 'Price per Unit', 'Cost per Unit'],
        'Current': [
            f"${current['Sales']:,.0f}",
            f"${current['Cost']:,.0f}",
            f"${current['Gross Profit']:,.0f}",
            f"{current['Gross Margin %']:.2f}%",
            f"${current['Sales'] / current['Units']:.2f}",
            f"${current['Cost'] / current['Units']:.2f}"
        ],
        'Simulated': [
            f"${sim_sales:,.0f}",
            f"${sim_cost:,.0f}",
            f"${sim_profit:,.0f}",
            f"{sim_margin:.2f}%",
            f"${sim_price_per_unit:.2f}",
            f"${sim_cost_per_unit:.2f}"
        ],
        'Change': [
            f"{((sim_sales - current['Sales']) / current['Sales'] * 100):+.1f}%",
            f"{((sim_cost - current['Cost']) / current['Cost'] * 100):+.1f}%",
            f"{((sim_profit - current['Gross Profit']) / abs(current['Gross Profit']) * 100):+.1f}%",
            f"{(sim_margin - current['Gross Margin %']):+.2f}pp",
            f"{price_change:+d}%",
            f"{cost_change:+d}%"
        ]
    })
    
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Business recommendation
    st.subheader("💼 Business Recommendation")
    
    profit_change = sim_profit - current['Gross Profit']
    margin_change = sim_margin - current['Gross Margin %']
    
    if profit_change > 0 and margin_change > 0:
        st.success(
            f"✅ **Strong Positive Impact**: This scenario increases gross profit by ${abs(profit_change):,.0f} "
            f"({abs(profit_change) / abs(current['Gross Profit']) * 100:.1f}%) and improves margin by {abs(margin_change):.2f} percentage points. "
            f"Recommend implementing this change if market conditions and customer price sensitivity allow."
        )
    elif profit_change > 0 and margin_change <= 0:
        st.warning(
            f"⚠️ **Mixed Results**: Gross profit increases by ${abs(profit_change):,.0f}, but margin decreases by {abs(margin_change):.2f}pp. "
            f"This suggests volume-driven growth with compressed margins. Evaluate if increased volume justifies lower margins."
        )
    elif profit_change <= 0 and margin_change > 0:
        st.warning(
            f"⚠️ **Margin Improvement, Profit Decline**: Margin improves by {abs(margin_change):.2f}pp, but gross profit decreases by ${abs(profit_change):,.0f}. "
            f"Consider if margin quality is more important than absolute profit for this product line."
        )
    else:
        st.error(
            f"❌ **Negative Impact**: This scenario reduces gross profit by ${abs(profit_change):,.0f} "
            f"({abs(profit_change) / abs(current['Gross Profit']) * 100:.1f}%) and lowers margin by {abs(margin_change):.2f}pp. "
            f"Not recommended unless required by competitive or strategic factors."
        )
    
    # Additional context
    if price_change > 10:
        st.info("📌 Note: Price increases above 10% may impact sales volume. Consider gradual implementation or customer communication strategy.")
    elif price_change < -10:
        st.info("📌 Note: Price decreases above 10% significantly impact margins. Ensure volume increase justifies the reduction.")
    
    if cost_change > 10:
        st.info("📌 Note: Cost increases above 10% may indicate supply chain challenges. Consider alternative suppliers or hedging strategies.")
    elif cost_change < -10:
        st.info("📌 Note: Cost reductions above 10% present significant opportunity. Prioritize supplier negotiations or operational efficiencies.")


def show_methodology():
    st.header("📘 Methodology")
    
    st.markdown("""
    This section provides a comprehensive overview of the analytical framework employed in the 
    Nassau Candy Distributor profitability analysis dashboard. The methodology follows a structured 
    pipeline designed to transform raw transactional data into actionable business intelligence.
    """)
    
    st.markdown("---")
    
    # Analysis Pipeline
    st.subheader("Analysis Pipeline")
    
    st.markdown("""
    The analysis follows a seven-stage pipeline, each building upon the previous stage to provide 
    increasingly sophisticated insights:
    """)
    
    # Stage 1
    st.markdown("### 1. Data Cleaning & Validation")
    st.markdown("""
    Raw order data undergoes rigorous cleaning to ensure analytical integrity:
    - **Duplicate Removal**: Identification and elimination of duplicate transaction records
    - **Missing Value Treatment**: Numeric fields default to zero; categorical fields to 'Unknown'
    - **Data Type Validation**: Enforcement of appropriate data types (dates, numerics, categoricals)
    - **Constraint Validation**: Removal of records with negative Sales or Cost values
    - **Date Standardization**: Conversion of date fields to standardized datetime format
    
    This stage ensures data quality and prevents analytical bias from corrupted or incomplete records.
    """)
    
    # Stage 2
    st.markdown("### 2. Profitability Metric Calculation")
    st.markdown("""
    Core profitability metrics are computed using the following formulas:
    """)
    
    # Display formulas in formatted blocks
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Gross Profit**
        ```
        Gross Profit = Sales − Cost
        ```
        
        **Gross Margin (%)**
        ```
        Gross Margin (%) = (Gross Profit / Sales) × 100
        ```
        """)
    
    with col2:
        st.markdown("""
        **Profit per Unit**
        ```
        Profit per Unit = Gross Profit / Units
        ```
        
        **Cost-to-Sales Ratio**
        ```
        Cost-to-Sales Ratio = Cost / Sales
        ```
        """)
    
    st.markdown("""
    **Revenue Contribution (%)** measures each product's proportional contribution to total revenue:
    ```
    Revenue Contribution (%) = (Product Sales / Total Sales) × 100
    ```
    
    **Profit Contribution (%)** quantifies each product's proportional contribution to total profitability:
    ```
    Profit Contribution (%) = (Product Gross Profit / Total Gross Profit) × 100
    ```
    
    These metrics enable comparative analysis across products with different sales volumes and price points.
    """)
    
    # Stage 3
    st.markdown("### 3. Product-Level Analysis")
    st.markdown("""
    Aggregation of transaction-level data to the product dimension:
    - **Summation**: Total Sales, Cost, Gross Profit, and Units per product
    - **Margin Classification**: Products categorized as Low (<10%), Medium (10-30%), or High (>30%) margin
    - **Ranking**: Products ranked by Gross Profit and Gross Margin percentage
    - **Contribution Analysis**: Revenue and Profit Contribution percentages computed
    
    This stage establishes product-level performance baselines for subsequent analyses.
    """)
    
    # Stage 4
    st.markdown("### 4. Division-Level Analysis")
    st.markdown("""
    Hierarchical aggregation to the division level:
    - **Division Metrics**: Aggregate Sales, Cost, Gross Profit, and Average Gross Margin per division
    - **Contribution Analysis**: Division-level Revenue and Profit Contribution percentages
    - **Imbalance Detection**: Identification of revenue-profit misalignment through comparison of contribution percentages
    
    **Revenue-Profit Imbalance** is calculated as:
    ```
    Imbalance = Revenue Contribution (%) − Profit Contribution (%)
    ```
    
    Positive imbalance indicates a division generating disproportionately low profit relative to revenue, 
    signaling potential margin compression or cost inefficiency.
    """)
    
    # Stage 5
    st.markdown("### 5. Pareto Analysis (80/20 Principle)")
    st.markdown("""
    Application of the Pareto Principle to identify profit concentration:
    - **Revenue Pareto**: Products ordered by Sales, cumulative contribution calculated
    - **Profit Pareto**: Products ordered by Gross Profit, cumulative contribution calculated
    - **80% Threshold**: Identification of the minimum product set generating 80% of total revenue/profit
    
    This analysis reveals portfolio concentration risk and identifies high-leverage products warranting 
    strategic focus. Products in the 80th percentile represent core business drivers requiring protection 
    and optimization.
    """)
    
    # Stage 6
    st.markdown("### 6. Cost Structure Diagnostics")
    st.markdown("""
    Statistical analysis of cost-to-sales relationships:
    - **Baseline Calculation**: Mean and standard deviation of Cost-to-Sales Ratio across all products
    - **Outlier Detection**: Products exceeding ±1 standard deviation from mean flagged as pricing anomalies
    - **Classification**:
        - **Overpriced/Inefficient**: Cost-to-Sales Ratio > (Mean + 1 SD)
        - **Normal**: Cost-to-Sales Ratio within ±1 SD of mean
        - **Underpriced/Opportunity**: Cost-to-Sales Ratio < (Mean − 1 SD)
    
    This stage identifies products with atypical cost structures, suggesting either pricing inefficiencies 
    or opportunities for margin expansion.
    """)
    
    # Stage 7
    st.markdown("### 7. Risk Identification")
    st.markdown("""
    Multi-criteria segmentation to identify products requiring strategic intervention:
    
    **Risk Categories:**
    
    1. **Low Margin, High Sales (Priority)**
       - Criteria: Gross Margin < 10% AND Revenue Contribution > 5%
       - Implication: High-volume products with margin compression; immediate repricing or cost reduction required
    
    2. **Negative Margin (Critical)**
       - Criteria: Gross Margin < 0%
       - Implication: Products generating losses; discontinuation or urgent cost restructuring necessary
    
    3. **High Margin, Low Sales (Opportunity)**
       - Criteria: Gross Margin > 30% AND Revenue Contribution < 1%
       - Implication: Profitable but underutilized products; marketing investment may yield high ROI
    
    4. **Underperforming (Review)**
       - Criteria: Gross Margin < 15% AND Profit Contribution < 2%
       - Implication: Products contributing minimal value; candidates for rationalization or repositioning
    
    This segmentation enables prioritized resource allocation and strategic decision-making based on 
    risk-reward profiles.
    """)
    
    st.markdown("---")
    
    # Additional Analytical Components
    st.subheader("Additional Analytical Components")
    
    st.markdown("""
    **Product Portfolio Matrix**: Two-dimensional strategic positioning using median Sales and median 
    Gross Margin as quadrant boundaries. Products are classified as Core Products, Margin Risks, 
    Growth Opportunities, or Underperformers based on their position relative to portfolio medians.
    
    **Scenario Simulation**: Dynamic modeling of pricing and cost adjustments, enabling what-if analysis 
    of strategic decisions. Users can adjust price and cost parameters to project impact on Sales, 
    Gross Profit, and Gross Margin.
    
    **Executive Summary Export**: Automated generation of PDF reports synthesizing key findings, 
    top performers, risk products, and data-driven recommendations for executive review.
    """)
    
    st.markdown("---")
    
    # Data Quality & Limitations
    st.subheader("Data Quality & Limitations")
    
    st.markdown("""
    **Assumptions:**
    - Transaction data is representative of normal business operations
    - Product categorizations and divisions are accurately recorded
    - Sales and Cost figures reflect actual realized values
    
    **Limitations:**
    - Analysis is backward-looking; does not incorporate forward-looking demand or cost projections
    - External factors (market trends, seasonality, competitive dynamics) are not explicitly modeled
    - Product-level analysis assumes stable pricing; does not account for dynamic pricing strategies
    
    **Data Quality Checks**: The dashboard includes real-time data quality monitoring, flagging 
    missing values, duplicates, and invalid numeric entries to ensure analytical integrity.
    """)
    
    st.markdown("---")
    
    st.info("""
    **Citation**: This methodology follows established frameworks in profitability analysis and 
    activity-based costing (ABC), adapted for retail distribution contexts. The Pareto analysis 
    framework is based on the Pareto Principle (Juran, 1954), while risk segmentation follows 
    BCG Growth-Share Matrix principles.
    """)


def generate_executive_summary_pdf(summary_metrics: dict, product_data: pd.DataFrame, risks: dict) -> BytesIO:
    """
    Generate executive summary PDF report
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    story.append(Paragraph("🍬 Nassau Candy Distributor", title_style))
    story.append(Paragraph("Executive Profitability Summary", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Key Metrics Section
    story.append(Paragraph("📊 Key Performance Metrics", heading_style))
    
    metrics_data = [
        ['Metric', 'Value'],
        ['Total Revenue', f"${summary_metrics['total_revenue']:,.0f}"],
        ['Total Gross Profit', f"${summary_metrics['total_profit']:,.0f}"],
        ['Overall Gross Margin', f"{summary_metrics['overall_margin']:.2f}%"],
        ['Total Orders', f"{summary_metrics['total_orders']:,}"],
        ['Average Order Value', f"${summary_metrics['avg_order_value']:,.2f}"],
        ['Total Products', f"{summary_metrics['total_products']}"],
    ]
    
    metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Top Products Section
    story.append(Paragraph("💰 Top 3 Products by Gross Profit", heading_style))
    top_products = product_data.nlargest(3, 'Gross Profit')[['Product Name', 'Gross Profit', 'Gross Margin %']]
    
    top_products_data = [['Product Name', 'Gross Profit', 'Margin %']]
    for _, row in top_products.iterrows():
        top_products_data.append([
            row['Product Name'][:40],  # Truncate long names
            f"${row['Gross Profit']:,.0f}",
            f"{row['Gross Margin %']:.2f}%"
        ])
    
    top_products_table = Table(top_products_data, colWidths=[3*inch, 1.5*inch, 1*inch])
    top_products_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9)
    ]))
    story.append(top_products_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Highest Margin Products
    story.append(Paragraph("📈 Highest Margin Products", heading_style))
    high_margin = product_data.nlargest(3, 'Gross Margin %')[['Product Name', 'Gross Margin %', 'Sales']]
    
    high_margin_data = [['Product Name', 'Margin %', 'Sales']]
    for _, row in high_margin.iterrows():
        high_margin_data.append([
            row['Product Name'][:40],
            f"{row['Gross Margin %']:.2f}%",
            f"${row['Sales']:,.0f}"
        ])
    
    high_margin_table = Table(high_margin_data, colWidths=[3*inch, 1*inch, 1.5*inch])
    high_margin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9)
    ]))
    story.append(high_margin_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Margin Risk Products
    story.append(Paragraph("⚠️ Products Requiring Margin Review", heading_style))
    if len(risks['low_margin_high_sales']) > 0:
        margin_risks = risks['low_margin_high_sales'].head(3)[['Product Name', 'Gross Margin %', 'Sales']]
        
        margin_risk_data = [['Product Name', 'Margin %', 'Sales']]
        for _, row in margin_risks.iterrows():
            margin_risk_data.append([
                row['Product Name'][:40],
                f"{row['Gross Margin %']:.2f}%",
                f"${row['Sales']:,.0f}"
            ])
        
        margin_risk_table = Table(margin_risk_data, colWidths=[3*inch, 1*inch, 1.5*inch])
        margin_risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        story.append(margin_risk_table)
    else:
        story.append(Paragraph("✅ No high-volume products with margin concerns.", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Concentration Analysis
    story.append(Paragraph("📊 Revenue & Profit Concentration", heading_style))
    pareto_pct = (summary_metrics['products_in_revenue_pareto'] / summary_metrics['total_products']) * 100
    
    concentration_text = f"""
    • {summary_metrics['products_in_revenue_pareto']} products ({pareto_pct:.1f}%) generate 80% of revenue<br/>
    • {summary_metrics['products_in_profit_pareto']} products generate 80% of profit<br/>
    • Revenue concentration: {summary_metrics['pareto_revenue_concentration']:.1f}%<br/>
    • Profit concentration: {summary_metrics['pareto_profit_concentration']:.1f}%
    """
    story.append(Paragraph(concentration_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Business Recommendations
    story.append(Paragraph("💼 Key Business Recommendations", heading_style))
    
    recommendations = []
    
    # Recommendation 1: Top performers
    top_product = product_data.nlargest(1, 'Gross Profit').iloc[0]
    recommendations.append(
        f"<b>1. Protect Core Revenue:</b> {top_product['Product Name']} generates "
        f"${top_product['Gross Profit']:,.0f} in profit. Ensure consistent supply and maintain pricing power."
    )
    
    # Recommendation 2: Margin risks
    if len(risks['low_margin_high_sales']) > 0:
        risk_count = len(risks['low_margin_high_sales'])
        recommendations.append(
            f"<b>2. Address Margin Compression:</b> {risk_count} high-volume products have margins below 10%. "
            f"Priority action: repricing analysis or supplier cost negotiation."
        )
    else:
        recommendations.append(
            "<b>2. Margin Health:</b> All high-volume products maintain healthy margins. Continue monitoring quarterly."
        )
    
    # Recommendation 3: Growth opportunities
    if len(risks['high_margin_low_sales']) > 0:
        opp_product = risks['high_margin_low_sales'].nlargest(1, 'Gross Margin %').iloc[0]
        recommendations.append(
            f"<b>3. Unlock High-Margin Growth:</b> {opp_product['Product Name']} has {opp_product['Gross Margin %']:.1f}% margin "
            f"but low sales volume. Invest in targeted marketing to scale revenue."
        )
    
    # Recommendation 4: Portfolio concentration
    if pareto_pct < 20:
        recommendations.append(
            f"<b>4. Diversify Revenue Sources:</b> {pareto_pct:.1f}% of products drive 80% of revenue. "
            f"This concentration creates risk. Develop secondary revenue streams."
        )
    else:
        recommendations.append(
            f"<b>4. Maintain Portfolio Balance:</b> Revenue is well-distributed across {pareto_pct:.1f}% of products. "
            f"Continue balanced investment across portfolio."
        )
    
    # Recommendation 5: Overall margin improvement
    if summary_metrics['overall_margin'] < 20:
        recommendations.append(
            f"<b>5. Margin Improvement Initiative:</b> Overall margin of {summary_metrics['overall_margin']:.2f}% "
            f"is below optimal. Focus on cost reduction and strategic repricing across low-margin SKUs."
        )
    else:
        recommendations.append(
            f"<b>5. Sustain Margin Excellence:</b> Overall margin of {summary_metrics['overall_margin']:.2f}% "
            f"demonstrates strong profitability. Maintain discipline in pricing and cost management."
        )
    
    for rec in recommendations:
        story.append(Paragraph(rec, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    # Footer
    story.append(Spacer(1, 0.3*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1
    )
    story.append(Paragraph(
        "This report was generated by the Nassau Candy Analytics Dashboard | Confidential",
        footer_style
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


if __name__ == "__main__":
    main()
