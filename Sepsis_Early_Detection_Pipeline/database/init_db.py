import sqlite3
import os

# Define file path for new database
db_path = os.path.join(os.path.dirname(__file__), 'sepsis.db')

# Connect to SQLite (creates 'sepsis.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Repeatable. Drop table if already exists.
cursor.execute("DROP TABLE IF EXISTS sepsis_data")

# Create the table
# SQLite
# 'REAL': floats
# 'INTEGER': ints
create_table_query = """
CREATE TABLE sepsis_data (
    patient_id TEXT,
    HR REAL,
    O2Sat REAL,
    Temp REAL,
    SBP REAL,
    MAP REAL,
    DBP REAL,
    Resp REAL,
    EtCO2 REAL,
    BaseExcess REAL,
    HCO3 REAL,
    FiO2 REAL,
    pH REAL,
    PaCO2 REAL,
    SaO2 REAL,
    AST REAL,
    BUN REAL,
    Alkalinephos REAL,
    Calcium REAL,
    Chloride REAL,
    Creatinine REAL,
    Bilirubin_direct REAL,
    Glucose REAL,
    Lactate REAL,
    Magnesium REAL,
    Phosphate REAL,
    Potassium REAL,
    Bilirubin_total REAL,
    TroponinI REAL,
    Hct REAL,
    Hgb REAL,
    PTT REAL,
    WBC REAL,
    Fibrinogen REAL,
    Platelets REAL,
    Age REAL,
    Gender INTEGER,
    Unit1 INTEGER,
    Unit2 INTEGER,
    HospAdmTime REAL,
    ICULOS INTEGER,
    SepsisLabel INTEGER,
    PRIMARY KEY (patient_id, ICULOS)
);
"""

cursor.execute(create_table_query)
conn.commit()
conn.close()

print(f"Database created at: {db_path}")