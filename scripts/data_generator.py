import pandas as pd
import numpy as np
import os

def generate_raw_data(output_path="data/raw/pos_transactions.csv", num_rows=50000):
    """
    Generates synthetic POS transaction logs at scale (50,000+ records) 
    with intentionally injected anomalies for validation testing.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    np.random.seed(42)
    
    print(f"🏭 Generating {num_rows:,} synthetic POS transaction records...")
    
    transaction_ids = range(100001, 100001 + num_rows)
    dates = pd.date_range(start="2026-01-01", periods=num_rows, freq="min").strftime('%Y-%m-%d %H:%M:%S')
    
    # FIXED: Use np.random.choice
    stores = np.random.choice(['STORE-01', 'STORE-02', 'STORE-03', 'STORE-04'], size=num_rows)
    categories = np.random.choice(['Electronics', 'Apparel', 'Home Goods', 'Groceries'], size=num_rows)
    
    quantities = np.random.randint(1, 10, size=num_rows)
    unit_prices = np.round(np.random.uniform(10.0, 500.0, size=num_rows), 2)
    
    df = pd.DataFrame({
        'transaction_id': transaction_ids,
        'date': dates,
        'store_id': stores,
        'product_category': categories,
        'quantity': quantities,
        'unit_price': unit_prices
    })
    
    # --- Deliberately Inject Anomalies for Testing Validator ---
    df.loc[10, 'unit_price'] = -49.99
    df.loc[500, 'unit_price'] = -150.00
    df.loc[25, 'transaction_id'] = None
    df.loc[1000, 'transaction_id'] = None
    df.loc[50, 'date'] = 'INVALID-TIMESTAMP'
    df.loc[2500, 'date'] = '2026-13-99'
    df.loc[100, 'quantity'] = 0
    df.loc[750, 'quantity'] = -2
    
    df.to_csv(output_path, index=False)
    print(f"   └── Successfully wrote raw POS data to '{output_path}'.")

if __name__ == "__main__":
    generate_raw_data()