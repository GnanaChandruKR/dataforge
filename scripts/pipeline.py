import os
import sqlite3
import pandas as pd
from data_generator import generate_raw_data
from api_extractor import fetch_online_orders_from_api
from validator import validate_and_clean_stream

DB_PATH = "data/warehouse.db"

def run_decoupled_multisource_pipeline():
    print("==================================================")
    print("🚀 STARTING DATAFORGE MULTI-SOURCE PIPELINE")
    print("==================================================\n")
    
    # --- STEP 1: INDEPENDENT EXTRACTION ---
    print("[Step 1/4] EXTRACT: Pulling disparate streams...")
    
    csv_raw_path = "data/raw/pos_transactions.csv"
    generate_raw_data(output_path=csv_raw_path, num_rows=50000)
    
    df_api = fetch_online_orders_from_api()
    api_raw_path = "data/raw/api_transactions.csv"
    os.makedirs(os.path.dirname(api_raw_path), exist_ok=True)
    df_api.to_csv(api_raw_path, index=False)
    
    # --- STEP 2: INDEPENDENT VALIDATION & STAGING ---
    print("\n[Step 2/4] TRANSFORM & VALIDATE: Processing streams separately...")
    
    clean_pos_path = "data/processed/clean_pos.csv"
    clean_api_path = "data/processed/clean_api.csv"
    
    clean_pos_df, _ = validate_and_clean_stream(csv_raw_path, clean_pos_path, source_name="POS_BATCH_CSV")
    clean_api_df, _ = validate_and_clean_stream(api_raw_path, clean_api_path, source_name="WEB_API_JSON")
    
    # --- STEP 3: LOAD INTO ISOLATED STAGING & UNIFIED VIEW ---
    print(f"\n[Step 3/4] LOAD: Writing to SQLite staging tables & global view...")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Load POS Table
    cursor.execute('DROP TABLE IF EXISTS staging_pos_transactions')
    cursor.execute('''
        CREATE TABLE staging_pos_transactions (
            transaction_id INTEGER PRIMARY KEY,
            date TEXT,
            store_id TEXT,
            product_category TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_sales REAL
        )
    ''')
    clean_pos_df.to_sql('staging_pos_transactions', conn, if_exists='append', index=False)
    
    # Load API Table
    cursor.execute('DROP TABLE IF EXISTS staging_api_orders')
    cursor.execute('''
        CREATE TABLE staging_api_orders (
            transaction_id INTEGER PRIMARY KEY,
            date TEXT,
            store_id TEXT,
            product_category TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_sales REAL
        )
    ''')
    clean_api_df.to_sql('staging_api_orders', conn, if_exists='append', index=False)
    
    # Create Unified SQL View
    cursor.execute('DROP VIEW IF EXISTS vw_global_sales')
    cursor.execute('''
        CREATE VIEW vw_global_sales AS
        SELECT transaction_id, date, store_id, product_category, quantity, unit_price, total_sales, 'POS_BATCH' as source_system 
        FROM staging_pos_transactions
        UNION ALL
        SELECT transaction_id, date, store_id, product_category, quantity, unit_price, total_sales, 'WEB_API' as source_system 
        FROM staging_api_orders;
    ''')
    
    conn.commit()
    print("   └── Staging tables and global view 'vw_global_sales' successfully provisioned.")
    
    # --- STEP 4: ADVANCED SQL ANALYTICS (CTEs + Window Functions) ---
    print("\n[Step 4/4] ANALYTICS: Executing advanced CTE and window function queries...")
    
    analytics_query = '''
        WITH DailyStoreAggregates AS (
            -- CTE to pre-aggregate daily revenue performance across sources
            SELECT 
                source_system,
                store_id,
                SUBSTR(date, 1, 10) as transaction_date,
                SUM(total_sales) as daily_revenue
            FROM vw_global_sales
            GROUP BY source_system, store_id, SUBSTR(date, 1, 10)
        )
        SELECT 
            source_system,
            store_id,
            transaction_date,
            ROUND(daily_revenue, 2) as daily_revenue,
            -- Window function to compute running total revenue over time per store
            ROUND(SUM(daily_revenue) OVER (PARTITION BY store_id ORDER BY transaction_date), 2) as running_total_revenue,
            -- Window function to calculate system-wide daily average baseline
            ROUND(AVG(daily_revenue) OVER (PARTITION BY source_system), 2) as avg_system_daily_revenue
        FROM DailyStoreAggregates
        ORDER BY store_id, transaction_date
        LIMIT 10;
    '''
    
    analytics_df = pd.read_sql_query(analytics_query, conn)
    print("\nAdvanced SQL Analytical Report (CTE + Window Functions):")
    print(analytics_df.to_string(index=False))
    
    conn.close()
    print("\n==================================================")
    print("✅ DATAFORGE MULTI-SOURCE PIPELINE COMPLETE")
    print("==================================================")

if __name__ == "__main__":
    run_decoupled_multisource_pipeline()