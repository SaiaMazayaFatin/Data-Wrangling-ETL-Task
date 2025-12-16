from prefect import flow
from src.extract import extract_data
from src.transform import transform_data
from src.load import load_data

@flow(name="ETL Pipeline - Technical Test", log_prints=True)
def main_flow():
    # Definisi Path (Gunakan Relative Path)
    input_path = "data/raw/dirty_logs.txt"
    output_path = "data/processed/cleaned_data.csv"

    # Eksekusi Flow
    raw_df = extract_data(input_path)
    clean_df = transform_data(raw_df)
    load_data(clean_df, output_path)

if __name__ == "__main__":
    main_flow()