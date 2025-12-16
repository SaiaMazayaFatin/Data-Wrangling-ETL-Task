import pandas as pd
from prefect import task
import os

@task(name="Load Data")
def load_data(df: pd.DataFrame, output_path: str):
    # Pastikan folder output ada
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Reorder kolom agar rapi
    cols = ['log_id', 'timestamp', 'user_id', 'device_type', 
            'device_platform', 'event_type', 'session_duration_sec']
    available_cols = [c for c in cols if c in df.columns]
    
    print(f"Saving to {output_path}...")
    df[available_cols].to_csv(output_path, index=False)