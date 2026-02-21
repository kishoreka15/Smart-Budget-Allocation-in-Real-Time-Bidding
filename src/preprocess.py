import pandas as pd
import numpy as np
import os

def preprocess_data(file_path='data/ipinyou_data.csv'):
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Try to load real data; if not found, generate dummy data
    try:
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
    except FileNotFoundError:
        print("Dataset not found. Generating dummy data for testing...")
        # Generate dummy data for 24 hours
        np.random.seed(42)
        hours = list(range(24))
        df = pd.DataFrame({
            'hour': hours,
            'impression': np.random.randint(1000, 10000, 24),
            'click': np.random.randint(10, 100, 24),
            'cost': np.random.uniform(50, 500, 24)
        })
    
    # Aggregate per hour
    aggregated = df.groupby('hour').agg({
        'impression': 'sum',
        'click': 'sum',
        'cost': 'sum'
    }).reset_index()
    
    # Compute CTR per hour
    aggregated['ctr'] = aggregated['click'] / aggregated['impression']
    aggregated['avg_ctr'] = aggregated['ctr'].expanding().mean()
    
    # Normalize traffic volume
    aggregated['traffic_volume'] = aggregated['impression'] / aggregated['impression'].max()
    
    return aggregated

if __name__ == "__main__":
    data = preprocess_data()
    data.to_csv('data/processed_ipinyou.csv', index=False)
    print("Data preprocessed and saved.")