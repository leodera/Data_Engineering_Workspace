import pandas as pd

# Load raw dataset
df = pd.read_csv('01_raw_datasets/ecommerce_supply_chain.csv')

# Vectorized calculations matching your Excel logic
df['Gross_Revenue'] = df['Quantity'] * df['Unit_Price']
df['Total_Cost'] = df['Gross_Revenue'] + df['Shipping_Cost']

# Calculate aggregate metrics
total_rev = df['Gross_Revenue'].sum()
total_cost = df['Total_Cost'].sum()
avg_rev_per_order = df['Gross_Revenue'].mean()

print("--- EXCEL 2016 DATA METRICS VERIFICATION ---")
print(f"Total Gross Revenue:   ${total_rev:,.2f}")
print(f"Total Cost (Inc. Ship): ${total_cost:,.2f}")
print(f"Average Revenue/Order:  ${avg_rev_per_order:,.2f}")