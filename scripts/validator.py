import pandas as pd
import os

def validate_and_clean_stream(input_path, output_clean_path, source_name="SOURCE"):
    """
    Ingests a raw data path, applies validation rules, calculates error rates,
    quarantines anomalies, and saves clean records.
    """
    if not os.path.exists(input_path):
        print(f"⚠️ [{source_name}] File not found at {input_path}. Skipping stream.")
        return pd.DataFrame(), pd.DataFrame()

    df = pd.read_csv(input_path)
    total_raw_rows = len(df)
    print(f"🔍 [{source_name}] Validating {total_raw_rows:,} raw records...")

    # Initialize anomaly tracking flag
    df['is_flagged_anomaly'] = False

    # Rule 1: Check for missing mandatory fields
    mandatory_cols = ['transaction_id', 'unit_price', 'quantity']
    for col in mandatory_cols:
        if col in df.columns:
            df.loc[df[col].isnull(), 'is_flagged_anomaly'] = True

    # Rule 2: Numerical bounds (no negative prices or invalid quantities)
    if 'unit_price' in df.columns and 'quantity' in df.columns:
        df.loc[(df['unit_price'] < 0) | (df['quantity'] <= 0), 'is_flagged_anomaly'] = True

    # Rule 3: Date validation & formatting
    if 'date' in df.columns:
        parsed_dates = pd.to_datetime(df['date'], errors='coerce')
        df.loc[parsed_dates.isnull(), 'is_flagged_anomaly'] = True
        df['date'] = parsed_dates.dt.strftime('%Y-%m-%d %H:%M:%S')

    # Split clean data from anomalies
    anomalies_df = df[df['is_flagged_anomaly'] == True]
    clean_df = df[df['is_flagged_anomaly'] == False].copy()

    # Calculate Error Rate Metrics
    total_anomalies = len(anomalies_df)
    error_rate = (total_anomalies / total_raw_rows) * 100 if total_raw_rows > 0 else 0

    # Post-process clean records
    if not clean_df.empty:
        clean_df = clean_df.drop(columns=['is_flagged_anomaly'], errors='ignore')
        clean_df['total_sales'] = clean_df['quantity'] * clean_df['unit_price']
        
        if 'transaction_id' in clean_df.columns:
            clean_df = clean_df.drop_duplicates(subset=['transaction_id'])

    directory = os.path.dirname(output_clean_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
        
    clean_df.to_csv(output_clean_path, index=False)
    
    print(f"   └── [{source_name}] Validation Complete:")
    print(f"        • Passed: {len(clean_df):,} records")
    print(f"        • Quarantined Anomalies: {total_anomalies:,} records")
    print(f"        • Managed Data Error Rate: {error_rate:.2f}%")
    
    return clean_df, anomalies_df