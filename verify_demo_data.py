import pandas as pd

df = pd.read_csv('data/raw/demo_test_data.csv')
print(f'Demo CSV has {len(df)} records')
print(f'Total Sales: ${df["Sales"].sum():,.0f}')
print(f'Total Profit: ${df["Gross Profit"].sum():,.0f}')
print(f'Unique Products: {df["Product Name"].nunique()}')
