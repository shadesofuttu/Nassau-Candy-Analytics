"""
Core profitability analysis engine
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from src.config.settings import PARETO_THRESHOLD, HIGH_MARGIN_THRESHOLD, LOW_MARGIN_THRESHOLD


class ProfitabilityAnalyzer:
    """
    Analyze product profitability, margins, and performance metrics
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize analyzer with dataset
        
        Args:
            data: DataFrame containing order and product data
        """
        self.data = data.copy()
        
    def product_level_analysis(self) -> pd.DataFrame:
        """
        Perform product-level profitability analysis
        
        Returns:
            DataFrame with product-level metrics
        """
        # Group by product
        product_metrics = self.data.groupby('Product Name').agg({
            'Sales': 'sum',
            'Cost': 'sum',
            'Gross Profit': 'sum',
            'Units': 'sum',
            'Division': 'first'
        }).reset_index()
        
        # Calculate metrics with safe division
        product_metrics['Gross Margin %'] = np.where(
            product_metrics['Sales'] > 0,
            product_metrics['Gross Profit'] / product_metrics['Sales'] * 100,
            0
        )
        product_metrics['Profit per Unit'] = np.where(
            product_metrics['Units'] > 0,
            product_metrics['Gross Profit'] / product_metrics['Units'],
            0
        )
        
        # Calculate contribution percentages
        total_sales = product_metrics['Sales'].sum()
        total_profit = product_metrics['Gross Profit'].sum()
        
        product_metrics['Revenue Contribution %'] = (
            product_metrics['Sales'] / total_sales * 100
        )
        product_metrics['Profit Contribution %'] = (
            product_metrics['Gross Profit'] / total_profit * 100
        )
        
        # Classify products
        product_metrics['Margin Category'] = pd.cut(
            product_metrics['Gross Margin %'],
            bins=[-np.inf, LOW_MARGIN_THRESHOLD * 100, HIGH_MARGIN_THRESHOLD * 100, np.inf],
            labels=['Low Margin', 'Medium Margin', 'High Margin']
        )
        
        # Rank products
        product_metrics['Profit Rank'] = product_metrics['Gross Profit'].rank(ascending=False, method='dense')
        product_metrics['Margin Rank'] = product_metrics['Gross Margin %'].rank(ascending=False, method='dense')
        
        return product_metrics.sort_values('Gross Profit', ascending=False)
    
    def division_level_analysis(self) -> pd.DataFrame:
        """
        Perform division-level performance analysis
        
        Returns:
            DataFrame with division-level metrics
        """
        division_metrics = self.data.groupby('Division').agg({
            'Sales': 'sum',
            'Cost': 'sum',
            'Gross Profit': 'sum',
            'Units': 'sum'
        }).reset_index()
        
        # Calculate average metrics with safe division
        division_metrics['Avg Gross Margin %'] = np.where(
            division_metrics['Sales'] > 0,
            division_metrics['Gross Profit'] / division_metrics['Sales'] * 100,
            0
        )
        
        # Calculate contribution to total
        total_sales = division_metrics['Sales'].sum()
        total_profit = division_metrics['Gross Profit'].sum()
        
        division_metrics['Revenue Contribution %'] = (
            division_metrics['Sales'] / total_sales * 100
        )
        division_metrics['Profit Contribution %'] = (
            division_metrics['Gross Profit'] / total_profit * 100
        )
        
        # Calculate revenue vs profit imbalance
        division_metrics['Revenue-Profit Imbalance'] = (
            division_metrics['Revenue Contribution %'] - division_metrics['Profit Contribution %']
        )
        
        return division_metrics.sort_values('Gross Profit', ascending=False)
    
    def pareto_analysis(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Perform Pareto (80/20) analysis for revenue and profit
        
        Returns:
            Tuple of (revenue_pareto, profit_pareto) DataFrames
        """
        # Product-level data sorted by sales
        products = self.product_level_analysis()
        
        # Revenue Pareto
        revenue_sorted = products.sort_values('Sales', ascending=False).copy()
        revenue_sorted['Cumulative Revenue %'] = (
            revenue_sorted['Sales'].cumsum() / revenue_sorted['Sales'].sum() * 100
        )
        revenue_sorted['Product Rank'] = range(1, len(revenue_sorted) + 1)
        revenue_pareto = revenue_sorted[revenue_sorted['Cumulative Revenue %'] <= PARETO_THRESHOLD * 100]
        
        # Profit Pareto
        profit_sorted = products.sort_values('Gross Profit', ascending=False).copy()
        profit_sorted['Cumulative Profit %'] = (
            profit_sorted['Gross Profit'].cumsum() / profit_sorted['Gross Profit'].sum() * 100
        )
        profit_sorted['Product Rank'] = range(1, len(profit_sorted) + 1)
        profit_pareto = profit_sorted[profit_sorted['Cumulative Profit %'] <= PARETO_THRESHOLD * 100]
        
        return revenue_pareto, profit_pareto
    
    def identify_margin_risks(self) -> Dict[str, pd.DataFrame]:
        """
        Identify products with margin risks
        
        Returns:
            Dictionary containing different risk categories
        """
        products = self.product_level_analysis()
        
        risks = {
            'low_margin_high_sales': products[
                (products['Gross Margin %'] < LOW_MARGIN_THRESHOLD * 100) &
                (products['Revenue Contribution %'] > 5)
            ],
            'negative_margin': products[products['Gross Margin %'] < 0],
            'high_margin_low_sales': products[
                (products['Gross Margin %'] > HIGH_MARGIN_THRESHOLD * 100) &
                (products['Revenue Contribution %'] < 1)
            ],
            'underperforming': products[
                (products['Gross Margin %'] < 15) &
                (products['Profit Contribution %'] < 2)
            ]
        }
        
        return risks
    
    def cost_structure_analysis(self) -> pd.DataFrame:
        """
        Analyze cost structure and identify pricing issues
        
        Returns:
            DataFrame with cost-sales relationships
        """
        products = self.product_level_analysis()
        
        # Calculate cost ratio with safe division
        products['Cost-to-Sales Ratio'] = np.where(
            products['Sales'] > 0,
            products['Cost'] / products['Sales'],
            0
        )
        
        # Identify overpriced/underpriced products
        avg_cost_ratio = products['Cost-to-Sales Ratio'].mean()
        std_cost_ratio = products['Cost-to-Sales Ratio'].std()
        
        products['Pricing Status'] = 'Normal'
        products.loc[
            products['Cost-to-Sales Ratio'] > avg_cost_ratio + std_cost_ratio,
            'Pricing Status'
        ] = 'Overpriced/Inefficient'
        products.loc[
            products['Cost-to-Sales Ratio'] < avg_cost_ratio - std_cost_ratio,
            'Pricing Status'
        ] = 'Underpriced/Opportunity'
        
        return products[[
            'Product Name', 'Division', 'Sales', 'Cost', 'Gross Profit',
            'Cost-to-Sales Ratio', 'Gross Margin %', 'Pricing Status'
        ]].sort_values('Cost-to-Sales Ratio', ascending=False)
    
    def get_summary_metrics(self) -> Dict:
        """
        Generate overall summary metrics
        
        Returns:
            Dictionary of key metrics
        """
        products = self.product_level_analysis()
        divisions = self.division_level_analysis()
        revenue_pareto, profit_pareto = self.pareto_analysis()
        
        # Check if Order ID exists for distinct counting
        total_orders = self.data['Order ID'].nunique() if 'Order ID' in self.data.columns else len(self.data)
        
        return {
            'total_revenue': self.data['Sales'].sum(),
            'total_profit': self.data['Gross Profit'].sum(),
            'overall_margin': (self.data['Gross Profit'].sum() / self.data['Sales'].sum() * 100),
            'total_products': len(products),
            'total_orders': total_orders,
            'avg_order_value': self.data['Sales'].mean(),
            'top_division': divisions.iloc[0]['Division'],
            'top_division_profit': divisions.iloc[0]['Gross Profit'],
            'products_in_revenue_pareto': len(revenue_pareto),
            'products_in_profit_pareto': len(profit_pareto),
            'pareto_revenue_concentration': revenue_pareto['Revenue Contribution %'].sum(),
            'pareto_profit_concentration': profit_pareto['Profit Contribution %'].sum(),
            'high_margin_products': len(products[products['Gross Margin %'] > HIGH_MARGIN_THRESHOLD * 100]),
            'low_margin_products': len(products[products['Gross Margin %'] < LOW_MARGIN_THRESHOLD * 100])
        }
