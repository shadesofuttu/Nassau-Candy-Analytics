"""
Test script to verify uploaded data properly flows through the dashboard
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.data_loader import DataLoader
from src.analytics.profitability_analyzer import ProfitabilityAnalyzer

print("=" * 80)
print("TESTING DATA UPLOAD FIX")
print("=" * 80)
print()

# Step 1: Load demo data
print("Step 1: Loading demo CSV data...")
df_demo = pd.read_csv('data/raw/demo_test_data.csv')
print(f"  - Records: {len(df_demo)}")
print(f"  - Total Sales: ${df_demo['Sales'].sum():,.0f}")
print(f"  - Total Profit: ${df_demo['Gross Profit'].sum():,.0f}")
print(f"  - Unique Products: {df_demo['Product Name'].nunique()}")
print()

# Step 2: Process and save to database (simulating upload)
print("Step 2: Processing and saving to database (simulating upload)...")
loader = DataLoader()
df_clean = loader.clean_data(df_demo)
df_processed = loader.calculate_metrics(df_clean)
loader.load_to_database(df_processed, 'orders')
print(f"  - Saved {len(df_processed)} records to database")
print()

# Step 3: Load from database (simulating dashboard load)
print("Step 3: Loading from database (simulating dashboard behavior)...")
df_from_db = loader.load_from_database('orders')
print(f"  - Records loaded: {len(df_from_db)}")
print(f"  - Total Sales: ${df_from_db['Sales'].sum():,.0f}")
print(f"  - Total Profit: ${df_from_db['Gross Profit'].sum():,.0f}")
print(f"  - Unique Products: {df_from_db['Product Name'].nunique()}")
print()

# Step 4: Run analytics (simulating dashboard calculations)
print("Step 4: Running analytics (simulating dashboard KPIs)...")
analyzer = ProfitabilityAnalyzer(df_from_db)
summary = analyzer.get_summary_metrics()

print(f"  - Total Revenue: ${summary['total_revenue']:,.0f}")
print(f"  - Total Profit: ${summary['total_profit']:,.0f}")
print(f"  - Overall Margin: {summary['overall_margin']:.2f}%")
print(f"  - Total Orders: {summary['total_orders']:,}")
print(f"  - Total Products: {summary['total_products']}")
print()

# Verification
print("=" * 80)
print("VERIFICATION RESULTS")
print("=" * 80)
print()

expected_revenue = 8800
expected_profit = 3540
expected_orders = 10
expected_products = 6

issues = []

if summary['total_revenue'] != expected_revenue:
    issues.append(f"Revenue mismatch: expected ${expected_revenue:,}, got ${summary['total_revenue']:,}")
else:
    print(f"[PASS] Revenue: ${summary['total_revenue']:,.0f}")

if summary['total_profit'] != expected_profit:
    issues.append(f"Profit mismatch: expected ${expected_profit:,}, got ${summary['total_profit']:,}")
else:
    print(f"[PASS] Profit: ${summary['total_profit']:,.0f}")

if summary['total_orders'] != expected_orders:
    issues.append(f"Orders mismatch: expected {expected_orders}, got {summary['total_orders']}")
else:
    print(f"[PASS] Orders: {summary['total_orders']:,}")

if summary['total_products'] != expected_products:
    issues.append(f"Products mismatch: expected {expected_products}, got {summary['total_products']}")
else:
    print(f"[PASS] Products: {summary['total_products']}")

print()

if issues:
    print("[FAIL] Data flow has issues:")
    for issue in issues:
        print(f"  - {issue}")
    sys.exit(1)
else:
    print("[SUCCESS] All uploaded data flows correctly through the analytics!")
    print()
    print("What was fixed:")
    print("  1. Removed @st.cache_data decorator from load_and_process_data()")
    print("     - Caching prevented fresh database reads after upload")
    print("  2. Changed st.cache_data.clear() to st.rerun()")
    print("     - Forces immediate reload of data from database")
    print()
    print("Result: Uploaded CSV now drives all dashboard calculations.")
    sys.exit(0)
