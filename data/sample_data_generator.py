"""
Generate sample data for testing the analytics platform
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration
NUM_ORDERS = 500
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2023, 12, 31)

# Product catalog
products = {
    'Chocolate': [
        'Wonka Bar - Nutty Crunch Surprise',
        'Wonka Bar - Fudge Mallow',
        'Wonka Bar - Scrumdiddlyumptious',
        'Wonka Bar - Milk Chocolate',
        'Wonka Bar - Triple Dazzle Caramel'
    ],
    'Sugar': [
        'Laffy Taffy',
        'SweeTARTS',
        'Nerds',
        'Fun Dip',
        'Everlasting Gobstopper',
        'Pixy Stix'
    ],
    'Other': [
        'Jawbreaker',
        'Hubba Bubba',
        'Jolly Rancher',
        'Runts'
    ]
}

# Factories
factories = {
    'Chocolate': "Wicked Choco's",
    'Sugar': 'Sugar Shack',
    'Other': 'The Other Factory'
}

# Generate orders
orders = []

for i in range(NUM_ORDERS):
    # Random order date
    days_diff = (END_DATE - START_DATE).days
    order_date = START_DATE + timedelta(days=random.randint(0, days_diff))
    ship_date = order_date + timedelta(days=random.randint(1, 5))
    
    # Random division
    division = random.choice(list(products.keys()))
    
    # Random product from division
    product_name = random.choice(products[division])
    
    # Factory
    factory = factories[division]
    
    # Random units (with some products selling more than others)
    if 'Wonka Bar' in product_name:
        units = random.randint(50, 200)
    elif division == 'Sugar':
        units = random.randint(30, 150)
    else:
        units = random.randint(20, 100)
    
    # Cost per unit varies by division
    if division == 'Chocolate':
        cost_per_unit = random.uniform(2.5, 4.5)
        sales_per_unit = cost_per_unit * random.uniform(1.15, 1.45)  # 15-45% margin
    elif division == 'Sugar':
        cost_per_unit = random.uniform(1.5, 3.0)
        sales_per_unit = cost_per_unit * random.uniform(1.20, 1.50)  # 20-50% margin
    else:
        cost_per_unit = random.uniform(1.0, 2.5)
        sales_per_unit = cost_per_unit * random.uniform(1.10, 1.40)  # 10-40% margin
    
    # Calculate totals
    cost = cost_per_unit * units
    sales = sales_per_unit * units
    gross_profit = sales - cost
    
    # Create order
    order = {
        'Order ID': f'ORD-{i+1:05d}',
        'Order Date': order_date.strftime('%Y-%m-%d'),
        'Ship Date': ship_date.strftime('%Y-%m-%d'),
        'Ship Mode': random.choice(['Standard', 'Express', 'Overnight']),
        'Customer ID': f'CUST-{random.randint(1, 100):03d}',
        'Customer Name': f'Customer {random.randint(1, 100)}',
        'Segment': random.choice(['Consumer', 'Corporate', 'Home Office']),
        'Country/Region': 'United States',
        'City': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
        'State/Province': random.choice(['NY', 'CA', 'IL', 'TX', 'AZ']),
        'Region': random.choice(['East', 'West', 'Central', 'South']),
        'Product ID': f'PROD-{hash(product_name) % 10000:04d}',
        'Division': division,
        'Product Name': product_name,
        'Factory': factory,
        'Sales': round(sales, 2),
        'Units': units,
        'Cost': round(cost, 2),
        'Gross Profit': round(gross_profit, 2)
    }
    
    orders.append(order)

# Create DataFrame
df = pd.DataFrame(orders)

# Add some negative margin products (edge cases)
negative_indices = random.sample(range(len(df)), 5)
for idx in negative_indices:
    df.loc[idx, 'Cost'] = df.loc[idx, 'Sales'] * 1.1  # Cost > Sales
    df.loc[idx, 'Gross Profit'] = df.loc[idx, 'Sales'] - df.loc[idx, 'Cost']

# Sort by date
df = df.sort_values('Order Date').reset_index(drop=True)

# Save to CSV
output_path = 'raw/nassau_candy_sample_data.csv'
df.to_csv(output_path, index=False)

print(f"Sample data generated successfully!")
print(f"File: {output_path}")
print(f"Total orders: {len(df)}")
print(f"\nDivision breakdown:")
print(df['Division'].value_counts())
print(f"\nDate range: {df['Order Date'].min()} to {df['Order Date'].max()}")
print(f"\nTotal Sales: ${df['Sales'].sum():,.2f}")
print(f"Total Profit: ${df['Gross Profit'].sum():,.2f}")
print(f"Overall Margin: {(df['Gross Profit'].sum() / df['Sales'].sum() * 100):.2f}%")
