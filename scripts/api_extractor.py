import requests
import pandas as pd
import os

def fetch_online_orders_from_api():
    """
    Fetches live product records from a public REST API,
    handles network exceptions, and harmonizes the schema.
    """
    api_url = "https://dummyjson.com/products?limit=50"
    
    try:
        print(f"🌐 Connecting to live public API endpoint: {api_url}...")
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        json_data = response.json()
        products_list = json_data.get("products", [])
        
        if not products_list:
            print("⚠️ API returned empty data.")
            return pd.DataFrame()
            
        df_api = pd.DataFrame(products_list)
        
        # --- Schema Harmonization ---
        df_api['transaction_id'] = df_api['id'] + 900000  # Unique ID offset
        df_api['date'] = "2026-03-04 12:00:00"
        df_api['store_id'] = "ONLINE-WEB-01"
        
        df_api = df_api.rename(columns={
            "category": "product_category",
            "stock": "quantity",
            "price": "unit_price"
        })
        
        df_api = df_api[['transaction_id', 'date', 'store_id', 'product_category', 'quantity', 'unit_price']]
        
        # Inject an anomaly to test validator resilience
        df_api.loc[0, 'unit_price'] = -99.99
        
        print(f"   └── Successfully fetched and harmonized {len(df_api)} records from REST API.")
        return df_api

    except requests.exceptions.RequestException as e:
        print(f"❌ API Request Failed: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    df = fetch_online_orders_from_api()
    print(df.head())