"""
Detailed validation of calculations, consistency, and edge cases
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.data_loader import DataLoader
from src.analytics.profitability_analyzer import ProfitabilityAnalyzer

def test_calculation_consistency():
    """Test that calculations are consistent across different views"""
    
    print("=" * 80)
    print("DETAILED VALIDATION - CALCULATION CONSISTENCY")
    print("=" * 80)
    print()
    
    # Create test data with known values
    data = {
        'Order ID': ['ORD-001', 'ORD-002', 'ORD-003', 'ORD-004', 'ORD-005'],
        'Order Date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'],
        'Product Name': ['Product A', 'Product B', 'Product A', 'Product C', 'Product B'],
        'Division': ['Chocolate', 'Sugar', 'Chocolate', 'Other', 'Sugar'],
        'Sales': [1000.0, 800.0, 600.0, 500.0, 400.0],
        'Cost': [600.0, 500.0, 360.0, 450.0, 350.0],
        'Units': [100, 80, 60, 50, 40],
        'Gross Profit': [400.0, 300.0, 240.0, 50.0, 50.0]
    }
    df = pd.DataFrame(data)
    
    analyzer = ProfitabilityAnalyzer(df)
    issues = []
    
    print("Testing calculation consistency...")
    print()
    
    # Test 1: Gross Profit calculation
    print("1. GROSS PROFIT CALCULATION")
    product_data = analyzer.product_level_analysis()
    
    for _, row in product_data.iterrows():
        product_name = row['Product Name']
        calculated_profit = row['Sales'] - row['Cost']
        reported_profit = row['Gross Profit']
        
        if not np.isclose(calculated_profit, reported_profit, rtol=1e-5):
            issue = f"Product {product_name}: Gross Profit mismatch (calc: {calculated_profit}, reported: {reported_profit})"
            issues.append(issue)
            print(f"[FAIL] {issue}")
        else:
            print(f"[PASS] Product {product_name}: Gross Profit = ${reported_profit:,.2f}")
    
    # Test 2: Gross Margin % calculation
    print("\n2. GROSS MARGIN % CALCULATION")
    for _, row in product_data.iterrows():
        product_name = row['Product Name']
        if row['Sales'] > 0:
            calculated_margin = (row['Gross Profit'] / row['Sales']) * 100
            reported_margin = row['Gross Margin %']
            
            if not np.isclose(calculated_margin, reported_margin, rtol=1e-5):
                issue = f"Product {product_name}: Margin % mismatch (calc: {calculated_margin:.2f}%, reported: {reported_margin:.2f}%)"
                issues.append(issue)
                print(f"[FAIL] {issue}")
            else:
                print(f"[PASS] Product {product_name}: Margin = {reported_margin:.2f}%")
    
    # Test 3: Contribution percentages sum to 100%
    print("\n3. CONTRIBUTION PERCENTAGES")
    revenue_contrib_sum = product_data['Revenue Contribution %'].sum()
    profit_contrib_sum = product_data['Profit Contribution %'].sum()
    
    if not np.isclose(revenue_contrib_sum, 100.0, rtol=1e-2):
        issue = f"Revenue contributions don't sum to 100% (sum: {revenue_contrib_sum:.2f}%)"
        issues.append(issue)
        print(f"[FAIL] {issue}")
    else:
        print(f"[PASS] Revenue contributions sum to 100.00%")
    
    if not np.isclose(profit_contrib_sum, 100.0, rtol=1e-2):
        issue = f"Profit contributions don't sum to 100% (sum: {profit_contrib_sum:.2f}%)"
        issues.append(issue)
        print(f"[FAIL] {issue}")
    else:
        print(f"[PASS] Profit contributions sum to 100.00%")
    
    # Test 4: Division-level aggregation consistency
    print("\n4. DIVISION AGGREGATION CONSISTENCY")
    division_data = analyzer.division_level_analysis()
    
    # Sum of division sales should equal total sales
    total_sales_from_divisions = division_data['Sales'].sum()
    total_sales_original = df['Sales'].sum()
    
    if not np.isclose(total_sales_from_divisions, total_sales_original, rtol=1e-5):
        issue = f"Division sales sum mismatch (divisions: {total_sales_from_divisions}, original: {total_sales_original})"
        issues.append(issue)
        print(f"[FAIL] {issue}")
    else:
        print(f"[PASS] Division sales sum matches original data")
    
    # Test 5: Summary metrics consistency
    print("\n5. SUMMARY METRICS CONSISTENCY")
    summary = analyzer.get_summary_metrics()
    
    # Check overall margin calculation
    expected_margin = (summary['total_profit'] / summary['total_revenue']) * 100
    if not np.isclose(expected_margin, summary['overall_margin'], rtol=1e-5):
        issue = f"Overall margin mismatch (calc: {expected_margin:.2f}%, reported: {summary['overall_margin']:.2f}%)"
        issues.append(issue)
        print(f"[FAIL] {issue}")
    else:
        print(f"[PASS] Overall margin: {summary['overall_margin']:.2f}%")
    
    # Test 6: Pareto analysis
    print("\n6. PARETO ANALYSIS CONSISTENCY")
    revenue_pareto, profit_pareto = analyzer.pareto_analysis()
    
    # Last product in pareto should be at or just over 80%
    last_revenue_cumulative = revenue_pareto.iloc[-1]['Cumulative Revenue %']
    last_profit_cumulative = profit_pareto.iloc[-1]['Cumulative Profit %']
    
    if last_revenue_cumulative < 80.0:
        issue = f"Revenue Pareto doesn't reach 80% threshold (reached: {last_revenue_cumulative:.2f}%)"
        issues.append(issue)
        print(f"[FAIL] {issue}")
    else:
        print(f"[PASS] Revenue Pareto reaches {last_revenue_cumulative:.2f}%")
    
    if last_profit_cumulative < 80.0:
        issue = f"Profit Pareto doesn't reach 80% threshold (reached: {last_profit_cumulative:.2f}%)"
        issues.append(issue)
        print(f"[FAIL] {issue}")
    else:
        print(f"[PASS] Profit Pareto reaches {last_profit_cumulative:.2f}%")
    
    # Test 7: Risk identification logic
    print("\n7. RISK IDENTIFICATION LOGIC")
    risks = analyzer.identify_margin_risks()
    
    # Test low margin, high sales
    low_margin_high_sales = risks['low_margin_high_sales']
    for _, row in low_margin_high_sales.iterrows():
        if row['Gross Margin %'] >= 10:
            issue = f"Product {row['Product Name']} in low_margin_high_sales but has {row['Gross Margin %']:.2f}% margin"
            issues.append(issue)
            print(f"[FAIL] {issue}")
        elif row['Revenue Contribution %'] <= 5:
            issue = f"Product {row['Product Name']} in low_margin_high_sales but only {row['Revenue Contribution %']:.2f}% revenue contribution"
            issues.append(issue)
            print(f"[FAIL] {issue}")
        else:
            print(f"[PASS] {row['Product Name']} correctly identified as low margin, high sales")
    
    # Test negative margin
    negative_margin = risks['negative_margin']
    for _, row in negative_margin.iterrows():
        if row['Gross Margin %'] >= 0:
            issue = f"Product {row['Product Name']} in negative_margin but has {row['Gross Margin %']:.2f}% margin"
            issues.append(issue)
            print(f"[FAIL] {issue}")
        else:
            print(f"[PASS] {row['Product Name']} correctly identified as negative margin")
    
    if len(negative_margin) == 0:
        print("[INFO] No negative margin products in test data")
    
    # Test 8: Cost structure analysis
    print("\n8. COST STRUCTURE ANALYSIS")
    cost_data = analyzer.cost_structure_analysis()
    
    for _, row in cost_data.iterrows():
        calculated_ratio = row['Cost'] / row['Sales'] if row['Sales'] > 0 else 0
        reported_ratio = row['Cost-to-Sales Ratio']
        
        if not np.isclose(calculated_ratio, reported_ratio, rtol=1e-5):
            issue = f"Product {row['Product Name']}: Cost-to-Sales ratio mismatch"
            issues.append(issue)
            print(f"[FAIL] {issue}")
        else:
            print(f"[PASS] {row['Product Name']}: Cost-to-Sales ratio = {reported_ratio:.3f}")
    
    print("\n" + "=" * 80)
    print("EDGE CASES TESTING")
    print("=" * 80)
    print()
    
    # Test edge case: Zero sales
    print("9. EDGE CASE: Zero Sales")
    edge_data = pd.DataFrame({
        'Order ID': ['E001'],
        'Order Date': ['2023-01-01'],
        'Product Name': ['Zero Sales Product'],
        'Division': ['Other'],
        'Sales': [0.0],
        'Cost': [100.0],
        'Units': [0],
        'Gross Profit': [-100.0]
    })
    
    try:
        edge_analyzer = ProfitabilityAnalyzer(edge_data)
        edge_product_data = edge_analyzer.product_level_analysis()
        
        # Check for NaN or inf in margins
        if edge_product_data['Gross Margin %'].isnull().any():
            print("[FAIL] Zero sales produces NaN in margin calculation")
            issues.append("Zero sales handling produces NaN")
        elif np.isinf(edge_product_data['Gross Margin %'].values).any():
            print("[FAIL] Zero sales produces infinity in margin calculation")
            issues.append("Zero sales handling produces infinity")
        else:
            print("[PASS] Zero sales handled correctly (no NaN or infinity)")
    except Exception as e:
        print(f"[FAIL] Zero sales causes exception: {str(e)}")
        issues.append(f"Zero sales exception: {str(e)}")
    
    # Test edge case: Negative profit
    print("\n10. EDGE CASE: Negative Profit")
    neg_data = pd.DataFrame({
        'Order ID': ['N001'],
        'Order Date': ['2023-01-01'],
        'Product Name': ['Loss Product'],
        'Division': ['Other'],
        'Sales': [100.0],
        'Cost': [150.0],
        'Units': [10],
        'Gross Profit': [-50.0]
    })
    
    try:
        neg_analyzer = ProfitabilityAnalyzer(neg_data)
        neg_product_data = neg_analyzer.product_level_analysis()
        neg_risks = neg_analyzer.identify_margin_risks()
        
        if len(neg_risks['negative_margin']) == 0:
            print("[FAIL] Negative margin product not detected in risk analysis")
            issues.append("Negative margin detection not working")
        else:
            print("[PASS] Negative margin product correctly detected")
    except Exception as e:
        print(f"[FAIL] Negative profit causes exception: {str(e)}")
        issues.append(f"Negative profit exception: {str(e)}")
    
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print()
    
    if issues:
        print(f"[WARNING] FOUND {len(issues)} ISSUE(S):")
        print("-" * 80)
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        return False
    else:
        print("[SUCCESS] ALL VALIDATION TESTS PASSED")
        print("- All calculations are mathematically correct")
        print("- Aggregations are consistent across views")
        print("- Edge cases handled properly")
        print("- No runtime errors or invalid values")
        return True

if __name__ == "__main__":
    success = test_calculation_consistency()
    sys.exit(0 if success else 1)
