import pandas as pd
from prefect import task

@task(name="Extract Data")
def extract_data(file_path: str) -> pd.DataFrame:
    print(f"Reading data from {file_path}...")
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # File uses Python-style assignment but JSON-style null values
        content = content.replace(': null', ': None')
        
        local_vars = {}
        exec(content, {}, local_vars)
        data = local_vars['logs']
        
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        raise RuntimeError(f"Gagal membaca file: {e}")