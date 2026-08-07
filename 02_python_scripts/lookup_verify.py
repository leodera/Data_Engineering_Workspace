import pandas as pd

df = pd.read_csv('01_raw_datasets/ecommerce_supply_chain.csv')
df['Gross_Revenue'] = df['Quantity'] * df['Unit_Price']

# Query specific ID matching Excel drill
target_id = "TXN-100003"
match_row = df[df['Transaction_ID'] == target_id]

print(f"--- LOOKUP ENGINE VERIFICATION FOR {target_id} ---")
if not match_row.empty:
    region = match_row['Region'].values[0]
    revenue = match_row['Gross_Revenue'].values[0]
    print(f"Region:        {region}")
    print(f"Gross Revenue: ${revenue:,.2f}")
else:
    print("Transaction ID not found!")