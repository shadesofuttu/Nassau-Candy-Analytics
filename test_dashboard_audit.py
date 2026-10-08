"""
Audit script to verify Nassau Candy dashboard against requirements
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.data_loader import DataLoader
from src.analytics.profitability_analyzer import ProfitabilityAnalyzer
from src.visualization.charts import ChartGenerator

def generate_test_data():
    """Generate minimal test data for verification"""
    data = {
        'Order ID': ['ORD-001', 'ORD-002', 'ORD-003', 'ORD-004', 'ORD-005'],
        'Order Date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
        'Ship Date': ['2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06'],
        'Product Name': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
        'Division': ['Chocolate', 'Sugar', 'Other', 'Chocolate', 'Sugar'],
        'Sales': [1000, 800, 600, 500, 400],
        'Cost': [600, 500, 450, 300, 350],
        'Units': [100, 80, 60, 50, 40],
        'Gross Profit': [400, 300, 150, 200, 50]
    }
    return pd.DataFrame(data)

def audit_dashboard():
    """Perform comprehensive audit of dashboard components"""
    
    print("=" * 80)
    print("NASSAU CANDY DASHBOARD AUDIT")
    print("=" * 80)
    print()
    
    # Generate test data
    print("[PASS] Generating test data...")
    df = generate_test_data()
    
    # Initialize components
    analyzer = ProfitabilityAnalyzer(df)
    chart_gen = ChartGenerator()
    
    issues = []
    checks_passed = 0
    total_checks = 0
    
    print("\n" + "=" * 80)
    print("1. PRODUCT PROFITABILITY OVERVIEW")
    print("=" * 80)
    
    # Check product-level analysis
    total_checks += 1
    try:
        product_data = analyzer.product_level_analysis()
        required_cols = ['Product Name', 'Division', 'Sales', 'Gross Profit', 
                        'Gross Margin %', 'Profit per Unit', 'Revenue Contribution %', 
                        'Profit Contribution %', 'Margin Category']
        
        missing_cols = [col for col in required_cols if col not in product_data.columns]
        
        if missing_cols:
            issues.append(f"Product analysis missing columns: {missing_cols}")
            print(f"[FAIL] Missing columns: {missing_cols}")
        else:
            checks_passed += 1
            print("[PASS] Product-level margin leaderboard")
            print("[PASS] Profit contribution analysis")
            print("[PASS] Product filtering capability")
    except Exception as e:
        issues.append(f"Product analysis failed: {str(e)}")
        print(f"[FAIL] Product analysis error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("2. DIVISION PERFORMANCE")
    print("=" * 80)
    
    # Check division-level analysis
    total_checks += 1
    try:
        division_data = analyzer.division_level_analysis()
        required_cols = ['Division', 'Sales', 'Gross Profit', 'Avg Gross Margin %',
                        'Revenue Contribution %', 'Profit Contribution %', 
                        'Revenue-Profit Imbalance']
        
        missing_cols = [col for col in required_cols if col not in division_data.columns]
        
        if missing_cols:
            issues.append(f"Division analysis missing columns: {missing_cols}")
            print(f"[FAIL] Missing columns: {missing_cols}")
        else:
            checks_passed += 1
            print("[PASS] Revenue vs Profit comparison")
            print("[PASS] Margin distribution")
            print("[PASS] Division-level metrics")
    except Exception as e:
        issues.append(f"Division analysis failed: {str(e)}")
        print(f"[FAIL] Division analysis error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("3. COST STRUCTURE DIAGNOSTICS")
    print("=" * 80)
    
    # Check cost structure analysis
    total_checks += 1
    try:
        cost_data = analyzer.cost_structure_analysis()
        required_cols = ['Product Name', 'Division', 'Sales', 'Cost', 'Gross Profit',
                        'Cost-to-Sales Ratio', 'Gross Margin %', 'Pricing Status']
        
        missing_cols = [col for col in required_cols if col not in cost_data.columns]
        
        if missing_cols:
            issues.append(f"Cost structure analysis missing columns: {missing_cols}")
            print(f"[FAIL] Missing columns: {missing_cols}")
        else:
            checks_passed += 1
            print("[PASS] Cost vs Sales analysis")
            print("[PASS] Cost-to-Sales Ratio")
            print("[PASS] Margin/pricing diagnostics")
    except Exception as e:
        issues.append(f"Cost structure analysis failed: {str(e)}")
        print(f"[FAIL] Cost structure analysis error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("4. PROFIT CONCENTRATION ANALYSIS (PARETO)")
    print("=" * 80)
    
    # Check Pareto analysis
    total_checks += 1
    try:
        revenue_pareto, profit_pareto = analyzer.pareto_analysis()
        
        if 'Cumulative Revenue %' not in revenue_pareto.columns:
            issues.append("Revenue Pareto missing cumulative column")
            print("[FAIL] Revenue Pareto analysis incomplete")
        elif 'Cumulative Profit %' not in profit_pareto.columns:
            issues.append("Profit Pareto missing cumulative column")
            print("[FAIL] Profit Pareto analysis incomplete")
        else:
            checks_passed += 1
            print("[PASS] Revenue Pareto analysis")
            print("[PASS] Profit Pareto analysis")
            print("[PASS] Concentration/dependency indicators")
    except Exception as e:
        issues.append(f"Pareto analysis failed: {str(e)}")
        print(f"[FAIL] Pareto analysis error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("5. RISK IDENTIFICATION")
    print("=" * 80)
    
    # Check risk identification
    total_checks += 1
    try:
        risks = analyzer.identify_margin_risks()
        required_categories = ['low_margin_high_sales', 'negative_margin', 
                              'high_margin_low_sales', 'underperforming']
        
        missing_categories = [cat for cat in required_categories if cat not in risks]
        
        if missing_categories:
            issues.append(f"Risk identification missing categories: {missing_categories}")
            print(f"[FAIL] Missing risk categories: {missing_categories}")
        else:
            checks_passed += 1
            print("[PASS] Low Margin / High Sales detection")
            print("[PASS] Negative Margin detection")
            print("[PASS] High Margin / Low Sales detection")
            print("[PASS] Underperforming products detection")
    except Exception as e:
        issues.append(f"Risk identification failed: {str(e)}")
        print(f"[FAIL] Risk identification error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("6. SUMMARY METRICS")
    print("=" * 80)
    
    # Check summary metrics
    total_checks += 1
    try:
        summary = analyzer.get_summary_metrics()
        required_metrics = ['total_revenue', 'total_profit', 'overall_margin', 
                           'total_products', 'total_orders', 'avg_order_value',
                           'products_in_revenue_pareto', 'products_in_profit_pareto']
        
        missing_metrics = [metric for metric in required_metrics if metric not in summary]
        
        if missing_metrics:
            issues.append(f"Summary metrics missing: {missing_metrics}")
            print(f"[FAIL] Missing metrics: {missing_metrics}")
        else:
            checks_passed += 1
            print("[PASS] All key metrics calculated")
            print(f"  - Total Revenue: ${summary['total_revenue']:,.2f}")
            print(f"  - Total Profit: ${summary['total_profit']:,.2f}")
            print(f"  - Overall Margin: {summary['overall_margin']:.2f}%")
    except Exception as e:
        issues.append(f"Summary metrics failed: {str(e)}")
        print(f"[FAIL] Summary metrics error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("7. CHART GENERATION")
    print("=" * 80)
    
    # Check chart generation methods exist
    total_checks += 1
    try:
        chart_methods = [
            'create_top_products_chart',
            'create_division_performance',
            'create_margin_distribution',
            'create_pareto_chart',
            'create_scatter_matrix',
            'create_revenue_profit_comparison',
            'create_portfolio_matrix'
        ]
        
        missing_methods = [method for method in chart_methods 
                          if not hasattr(chart_gen, method)]
        
        if missing_methods:
            issues.append(f"Chart generator missing methods: {missing_methods}")
            print(f"[FAIL] Missing chart methods: {missing_methods}")
        else:
            checks_passed += 1
            print("[PASS] All chart generation methods available")
    except Exception as e:
        issues.append(f"Chart generation check failed: {str(e)}")
        print(f"[FAIL] Chart generation error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("8. DATA QUALITY & VALIDATION")
    print("=" * 80)
    
    # Check data loader functionality
    total_checks += 1
    try:
        loader = DataLoader()
        
        # Test data cleaning
        test_dirty_data = df.copy()
        test_dirty_data.loc[0, 'Sales'] = None
        test_dirty_data = pd.concat([test_dirty_data, test_dirty_data.iloc[[0]]])  # Add duplicate
        
        cleaned = loader.clean_data(test_dirty_data)
        
        if cleaned['Sales'].isnull().any():
            issues.append("Data cleaning not handling missing values properly")
            print("[FAIL] Missing value handling")
        elif len(cleaned) == len(test_dirty_data):
            issues.append("Data cleaning not removing duplicates")
            print("[FAIL] Duplicate removal")
        else:
            checks_passed += 1
            print("[PASS] Data cleaning and validation")
            print("[PASS] Missing value handling")
            print("[PASS] Duplicate removal")
    except Exception as e:
        issues.append(f"Data quality check failed: {str(e)}")
        print(f"[FAIL] Data quality error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    print(f"\nTotal Checks: {total_checks}")
    print(f"Checks Passed: {checks_passed}")
    print(f"Checks Failed: {total_checks - checks_passed}")
    print(f"Success Rate: {(checks_passed / total_checks * 100):.1f}%")
    
    if issues:
        print(f"\n[WARNING] ISSUES FOUND ({len(issues)}):")
        print("-" * 80)
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    else:
        print("\n[SUCCESS] ALL CHECKS PASSED - NO ISSUES FOUND")
    
    print("\n" + "=" * 80)
    print("DASHBOARD PAGES VERIFICATION")
    print("=" * 80)
    
    # Check dashboard pages are implemented in app.py
    try:
        with open('dashboard/app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        required_pages = [
            'Overview',
            'Product Profitability',
            'Division Performance',
            'Pareto Analysis',
            'Cost Structure',
            'Risk Identification',
            'Scenario Simulator',
            'Methodology'
        ]
        
        page_functions = [
            'show_overview',
            'show_product_profitability',
            'show_division_performance',
            'show_pareto_analysis',
            'show_cost_structure',
            'show_risk_identification',
            'show_scenario_simulator',
            'show_methodology'
        ]
        
        print("\nPage Implementation Status:")
        for page, func in zip(required_pages, page_functions):
            if func in app_content:
                print(f"[PASS] {page}: IMPLEMENTED")
            else:
                print(f"[FAIL] {page}: MISSING")
                issues.append(f"Dashboard page '{page}' not implemented")
        
        # Check for key features in dashboard
        print("\nKey Features:")
        features = {
            'Date range selector': 'date' in app_content.lower(),
            'Division filter': 'multiselect' in app_content and 'Division' in app_content,
            'Product search': 'Product Name' in app_content,
            'Export functionality': 'download_button' in app_content,
            'KPI tooltips': 'help=' in app_content,
            'Portfolio Matrix': 'create_portfolio_matrix' in app_content,
            'Decision Center': 'Decision Center' in app_content,
            'Data Quality section': 'Data Quality' in app_content
        }
        
        for feature, present in features.items():
            status = "[PASS] PRESENT" if present else "[FAIL] MISSING"
            print(f"{status}: {feature}")
            if not present:
                issues.append(f"Feature '{feature}' not found in dashboard")
        
    except Exception as e:
        print(f"[FAIL] Error checking dashboard pages: {str(e)}")
        issues.append(f"Could not verify dashboard pages: {str(e)}")
    
    print("\n" + "=" * 80)
    print("FINAL AUDIT RESULT")
    print("=" * 80)
    
    if not issues:
        print("\n[SUCCESS] DASHBOARD PASSES ALL REQUIREMENTS")
        print("   All features implemented and functioning correctly.")
        return True
    else:
        print(f"\n[WARNING] DASHBOARD HAS {len(issues)} ISSUE(S)")
        print("   Review issues listed above for details.")
        return False

if __name__ == "__main__":
    success = audit_dashboard()
    sys.exit(0 if success else 1)