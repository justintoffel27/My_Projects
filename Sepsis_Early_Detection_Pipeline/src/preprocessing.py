import pandas as pd
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'sepsis.db')

def get_clean_data():
    """
    Connects to the DB, load the raw data, cleans NaNs (if any), and then returns a ML DataFrame.
    """
    print("Preprocessing:")
    
    # Connect to Database (data from data_loader.py)
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run data_loader.py.")
    conn = sqlite3.connect(DB_PATH)
    print("Loading data from SQLite...)")

    # Load everything into memory
    query = "SELECT * FROM sepsis_data ORDER BY patient_id, ICULOS"
    df = pd.read_sql(query, conn)
    conn.close()
    
    print(f"Raw Data Shape: {df.shape}")

    # Data Cleaning (Getting Rid of NaN); Vitals (HR, Temp, etc): "Forward Fill" per patient. 
    # If a value is missing, use the last known value.
    print("Cleaning Data: ")
    
    # Group by patient so we don't fill data from Patient A into Patient B
    df_clean = df.groupby('patient_id').apply(lambda x: x.ffill().bfill())
    
    # Reset index after groupby
    df_clean = df_clean.reset_index(drop=True)
    
    # If there are still any NaNs (ex., a patient had NO lactate tests at all), fill with -1 or 0.
    df_clean = df_clean.fillna(0)
    
    if 'SepsisLabel' not in df_clean.columns:
        print("ERROR: SepsisLabel column missing!")
        return None

    print(f"Cleaned Data Shape: {df_clean.shape}")
    print(f"Missing Values Remaining: {df_clean.isna().sum().sum()}")
    
    return df_clean

if __name__ == "__main__":
    # Test
    df = get_clean_data()
    print("\nSample of Cleaned Data:")
    print(df.head())