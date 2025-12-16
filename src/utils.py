import pandas as pd
from datetime import datetime, timezone

def parse_timestamp(ts):
    """Mencoba parsing timestamp dari berbagai format menjadi ISO 8601 UTC."""
    if pd.isna(ts):
        return None
    
    ts_str = str(ts).strip()

    # 1. Cek Unix Timestamp
    if ts_str.replace('.', '', 1).isdigit():
        try:
            dt = datetime.fromtimestamp(float(ts_str), tz=timezone.utc)
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        except:
            pass

    # 2. Cek Format Eropa
    try:
        dt = datetime.strptime(ts_str, "%d/%m/%Y %H:%M:%S")
        return dt.replace(tzinfo=timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    except:
        pass

    # 3. Cek ISO 8601
    try:
        dt = pd.to_datetime(ts_str, utc=True)
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    except:
        pass

    return None

def standardize_uid(uid):
    """Standardisasi User ID menjadi format string U-XXXX."""
    s_uid = str(uid).strip()
    if s_uid.isdigit():
        return f"U-{s_uid}"
    return s_uid