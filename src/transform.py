# src/transform.py
import pandas as pd
import numpy as np
from prefect import task
from src.utils import parse_timestamp, standardize_uid

@task(name="Transform & Quality Check")
def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    print("🔄 Running transformation logic...")
    
    # --- STEP 1: Filter Event Tidak Relevan ---
    # Aturan: Hapus "system_heartbeat", "ad_load", None
    irrelevant = ["system_heartbeat", "ad_load", None, np.nan]
    df = df[~df['event_type'].isin(irrelevant)].copy()

    # --- STEP 2: Validasi User ID ---
    # Aturan: Hapus None, string kosong, "guest"
    df['user_id'] = df['user_id'].replace({np.nan: None})
    df = df[(df['user_id'].notna()) & (df['user_id'] != "") & (df['user_id'] != "guest")].copy()

    # --- STEP 3: Standardisasi User ID ---
    # Aturan: Integer (12345) -> String ("U-12345")
    df['user_id'] = df['user_id'].apply(standardize_uid)

    # --- STEP 4: Standardisasi Platform ---
    # Aturan: Mapping ke Android, iOS, Web
    platform_map = {
        "android": "Android", "Android": "Android", "google": "Android",
        "ios": "iOS", "iOS": "iOS", "Apple": "iOS",
        "web": "Web", "WebApp": "Web"
    }
    df['device_platform'] = df['device_platform'].map(platform_map).fillna("Other")

    # --- STEP 5: Pembersihan Durasi Sesi ---
    # Aturan: Hapus 's', convert int, handle negatif
    df['session_duration_sec'] = (
        df['session_duration_sec'].astype(str)
        .str.replace('s', '', regex=False)
    )
    # Convert ke numeric (error jadi NaN), fillna 0, clip negatif jadi 0
    df['session_duration_sec'] = pd.to_numeric(df['session_duration_sec'], errors='coerce').fillna(0)
    df['session_duration_sec'] = df['session_duration_sec'].clip(lower=0).astype(int)

    # --- STEP 6: Normalisasi Timestamp ---
    # Aturan: 3 format -> ISO 8601 UTC
    df['timestamp'] = df['timestamp'].apply(parse_timestamp)
    # Hapus baris yang timestamp-nya gagal diparsing (Integritas Data)
    df = df.dropna(subset=['timestamp'])

    # --- STEP 7: Rekayasa Fitur (Feature Engineering) ---
    # Aturan: device_type dari platform
    def get_device_type(platform):
        if platform in ["Android", "iOS"]: return "Mobile"
        if platform == "Web": return "Desktop"
        return "Other"
    
    df['device_type'] = df['device_platform'].apply(get_device_type)

    # --- FINAL STEP: DATA INTEGRITY CHECK (PENTING!) ---
    # Memastikan Output benar-benar bersih sesuai permintaan "Output Integrity"
    assert df['user_id'].isnull().sum() == 0, "Masih ada User ID Null!"
    assert df['timestamp'].isnull().sum() == 0, "Masih ada Timestamp Null!"
    assert (df['session_duration_sec'] < 0).sum() == 0, "Masih ada durasi negatif!"
    
    print(f"✅ Data Cleaned & Validated. Rows remaining: {len(df)}")
    return df