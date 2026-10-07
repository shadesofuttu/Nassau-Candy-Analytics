"""
Unit tests for profitability analyzer
"""
import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analytics.profitability_analyzer import ProfitabilityAnalyzer


@pytest.fixture
def sample_data():
    """
    Create sample data for testing
    """
    return pd.DataFrame({
        'Order ID': ['O1', 'O2', 'O3', 'O4', 'O5'],
        'Product Name': ['Product A', 'Product B', 'Product C', 'Product A', 'Product B'],
        'Division': ['Chocolate', 'Sugar', 'Other', 'Chocolate', 'Sugar'],
        'Sales': [1000, 2000, 1500, 1200, 2500],
        'Cost': [600, 1400, 1000, 720, 1750],
        'Gross Profit': [400, 600, 500, 480, 750],
        'Units': [10, 20, 15, 12, 25]
    })


class TestProfitabilityAnalyzer:
    
    def test_initialization(self, sample_data):
        analyzer = ProfitabilityAnalyzer(sample_data)
        assert analyzer.data is not None
        assert len(analyzer.data) == 5
    
    def test_product_level_analysis(self, sample_data):
        analyzer = ProfitabilityAnalyzer(sample_data)
        result = analyzer.product_level_analysis()
        
        assert len(result) == 3  # 3 unique products
        assert 'Gross Margin %' in result.columns
        assert 'Profit per Unit' in result.columns
        assert all(result['Gross Margin %'] >= 0)
    
    def test_division_level_analysis(self, sample_data):
        analyzer = ProfitabilityAnalyzer(sample_data)
        result = analyzer.division_level_analysis()
        
        assert len(result) == 3  # 3 divisions
        assert 'Avg Gross Margin %' in result.columns
        assert 'Revenue Contribution %' in result.columns
    
    def test_pareto_analysis(self, sample_data):
        analyzer = ProfitabilityAnalyzer(sample_data)
        revenue_pareto, profit_pareto = analyzer.pareto_analysis()
        
        assert len(revenue_pareto) > 0
        assert len(profit_pareto) > 0
        assert 'Cumulative Revenue %' in revenue_pareto.columns
        assert 'Cumulative Profit %' in profit_pareto.columns
    
    def test_get_summary_metrics(self, sample_data):
        analyzer = ProfitabilityAnalyzer(sample_data)
        summary = analyzer.get_summary_metrics()
        
        assert 'total_revenue' in summary
        assert 'total_profit' in summary
        assert 'overall_margin' in summary
        assert summary['total_revenue'] == 8200
        assert summary['total_profit'] == 2730
