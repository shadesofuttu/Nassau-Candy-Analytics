import pandas as pd
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.data_loader import DataLoader
from src.analytics.profitability_analyzer import ProfitabilityAnalyzer

def run_audit():
    print("=" * 80)
    print("DATA INTEGRITY & CALCULATION AUDIT")
    print("=" * 80)
    
    loader = DataLoader()
    issues = []
    
    # Datasets to test
    datasets = {
        'Default_Nassau': loader.load_from_database('orders'),
        'Uploaded_Demo': loader.calculate_metrics(loader.clean_data(pd.read_csv('data/raw/demo_test_data.csv')))
    }
    
    for name, df in datasets.items():
        print(f"\n>>> Auditing Dataset: {name}")
        print("-" * 40)
        
        analyzer = ProfitabilityAnalyzer(df)
        summary = analyzer.get_summary_metrics()
        
        # 1. Total Revenue = Sum of Sales
        total_sales_raw = df['Sales'].sum()
        if not np.isclose(summary['total_revenue'], total_sales_raw, rtol=1e-5):
            msg = f"[{name}] Total Revenue mismatch: Summary={summary['total_revenue']}, Data={total_sales_raw}"
            issues.append(msg)
            print(f"FAIL: {msg}")
        else:
            print(f"PASS: Total Revenue matches sum of Sales (${total_sales_raw:,.2f})")
            
        # 2. Total Gross Profit = Sum of Gross Profit
        total_profit_raw = df['Gross Profit'].sum()
        if not np.isclose(summary['total_profit'], total_profit_raw, rtol=1e-5):
            msg = f"[{name}] Total Profit mismatch: Summary={summary['total_profit']}, Data={total_profit_raw}"
            issues.append(msg)
            print(f"FAIL: {msg}")
        else:
            print(f"PASS: Total Profit matches sum of Gross Profit (${total_profit_raw:,.2f})")
            
        # 3. Sales - Cost reconciles to Gross Profit line by line
        df['Calc_Profit'] = df['Sales'] - df['Cost']
        mismatches = df[~np.isclose(df['Calc_Profit'], df['Gross Profit'], atol=0.01)]
        if len(mismatches) > 0:
            msg = f"[{name}] Sales - Cost != Gross Profit in {len(mismatches)} rows"
            issues.append(msg)
            print(f"FAIL: {msg}")
        else:
            print("PASS: Sales - Cost exactly equals Gross Profit across all rows")
            
        # 4. Overall Gross Margin calculation consistency
        calc_margin = (total_profit_raw / total_sales_raw) * 100 if total_sales_raw > 0 else 0
        if not np.isclose(summary['overall_margin'], calc_margin, rtol=1e-5):
            msg = f"[{name}] Overall Margin mismatch: Summary={summary['overall_margin']}%, Calc={calc_margin}%"
            issues.append(msg)
            print(f"FAIL: {msg}")
        else:
            print(f"PASS: Overall Margin consistently calculated ({calc_margin:.2f}%)")
            
        # 5. Order Count Verification
        unique_orders = df['Order ID'].nunique() if 'Order ID' in df.columns else len(df)
        summary_orders = summary['total_orders']
        if unique_orders != summary_orders and 'Order ID' in df.columns:
            msg = f"[{name}] Orders count mismatch: Summary reports {summary_orders} (row count), but there are {unique_orders} unique Order IDs."
            issues.append(msg)
            print(f"FAIL: {msg}")
        else:
            print(f"PASS: Order counts logically sound ({summary_orders})")
            
        # 6. Product / Division Totals Reconciliation
        prod_df = analyzer.product_level_analysis()
        prod_sales_sum = prod_df['Sales'].sum()
        if not np.isclose(total_sales_raw, prod_sales_sum, rtol=1e-5):
            msg = f"[{name}] Product-level sales sum does not match raw sales."
            issues.append(msg)
            print(f"FAIL: {msg}")
        else:
            print("PASS: Product-level aggregations reconcile with underlying data.")
            
    print("\n" + "=" * 80)
    if issues:
        print(f"CONFIRMED FAILURES ({len(issues)}):")
        for i in issues:
            print(f"- {i}")
    else:
        print("ALL DATA INTEGRITY CHECKS PASSED")

if __name__ == '__main__':
    run_audit()
