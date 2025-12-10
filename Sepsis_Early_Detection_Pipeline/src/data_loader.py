import pandas as pd
import glob
import os
import sqlite3
from sqlalchemy import create_engine

# OS code will start at this file, then go to 'src', then go to 'CS210FP'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Defines where the data is at
RAW_DATA_PATH = os.path.join(BASE_DIR, 'data') 
DB_PATH = os.path.join(BASE_DIR, 'database', 'sepsis.db')

# Setup SQLAlchemy
engine = create_engine(f'sqlite:///{DB_PATH}')

def load_data():
    print(f"Sepsis Data Loader")
    print(f"Project Root detected as: {BASE_DIR}")
    print(f"Looking for .psv files in: {RAW_DATA_PATH}")

    # Find all .psv files recursively
    search_path = os.path.join(RAW_DATA_PATH, '**', '*.psv')
    all_files = glob.glob(search_path, recursive=True)
    
    total_files = len(all_files)
        
    print(f"Found {total_files} patient files. Importing...")

    # Process in chunks in Batch Processing rather all 20k+ file all at once. Running at 500 per.
    BATCH_SIZE = 500
    batch_buffer = []
    
    for i, file_path in enumerate(all_files):
        # Extract Patient ID from filename (ex., 'p000001.psv' -> 'p000001')
        filename = os.path.basename(file_path)
        patient_id = os.path.splitext(filename)[0]
        
        try:
            # Read the Pipe-Separated Value (psv) files
            df = pd.read_csv(file_path, sep='|')
            
            # Attach the Patient ID column to the psv (keep organized)
            df['patient_id'] = patient_id
            batch_buffer.append(df)
            
        except Exception as e:
            print(f"Error reading {filename}: {e}")

        # When the buffer (500) is filled OR we are at the very last file, write to DB (recursively)
        if len(batch_buffer) >= BATCH_SIZE or (i + 1) == total_files:
            # All buffer data into one database
            combined_df = pd.concat(batch_buffer, ignore_index=True)
            
            # Write to SQLite, if_exists='append'
            combined_df.to_sql('sepsis_data', engine, if_exists='append', index=False)
            
            # Print progress
            batch_buffer = []
            print(f"Progress: Loaded {i + 1}/{total_files} files...")
    print("Completed: All data loaded into database.")

if __name__ == "__main__":
    load_data()