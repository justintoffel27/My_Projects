import pandas as pd
import joblib
import sqlite3
import os
import warnings
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'sepsis.db')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'sepsis_rf_model.pkl')

warnings.simplefilter(action='ignore', category=FutureWarning)

# The program will only prompt for these (most important to concise). All others will be auto-filled to mean/average.
CRITICAL_FEATURES = [
    'HR', 'O2Sat', 'Temp', 'SBP', 'MAP', 'Resp', 
    'pH', 'Lactate', 'BUN', 'Creatinine', 
    'WBC', 'Platelets', 'Age', 'ICULOS'
]

def load_model():
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file not found at {MODEL_PATH}")
        return None
    return joblib.load(MODEL_PATH)

def get_db_stats():
    """Finds Min/Max/Mean for defaults."""
    if not os.path.exists(DB_PATH): return {}
    conn = sqlite3.connect(DB_PATH)
    stats = {}
    try:
        query = "SELECT * FROM sepsis_data LIMIT 1"
        columns = pd.read_sql(query, conn).columns.tolist()
        cols_to_scan = [c for c in columns if c not in ['patient_id', 'SepsisLabel', 'HospAdmTime']]
        
        select_parts = []
        for c in cols_to_scan:
            select_parts.append(f"AVG({c}) as {c}_avg")
            select_parts.append(f"MIN({c}) as {c}_min")
            select_parts.append(f"MAX({c}) as {c}_max")
            
        final_query = f"SELECT {', '.join(select_parts)} FROM sepsis_data"
        result = pd.read_sql(final_query, conn).iloc[0]
        
        for c in cols_to_scan:
            stats[c] = {
                'mean': result.get(f"{c}_avg", 0.0),
                'min': result.get(f"{c}_min", 0.0),
                'max': result.get(f"{c}_max", 0.0)
            }
            if pd.isna(stats[c]['mean']): stats[c]['mean'] = 0.0
            if pd.isna(stats[c]['max']): stats[c]['max'] = 0.0
            
    except Exception as e:
        print(f"Error fetching DB stats: {e}")
    finally:
        conn.close()
    return stats

def get_patient_history(conn, patient_id):
    query = f"SELECT * FROM sepsis_data WHERE patient_id = '{patient_id}' ORDER BY ICULOS"
    return pd.read_sql(query, conn).ffill().bfill().fillna(0)

def run_random_demo(model):
    print("\n OPTION 1: Random Patient Demo")
    conn = sqlite3.connect(DB_PATH)
    try:
        sick_id = pd.read_sql("SELECT patient_id FROM sepsis_data WHERE SepsisLabel = 1 ORDER BY RANDOM() LIMIT 1", conn).iloc[0,0]
        healthy_id = pd.read_sql("SELECT patient_id FROM sepsis_data WHERE SepsisLabel = 0 ORDER BY RANDOM() LIMIT 1", conn).iloc[0,0]
    except: return

    def diagnose(pid, expected_label):
        df_hist = get_patient_history(conn, pid)
        
        # If expected is sick, try to find a sick row. Else random row.
        if expected_label == 1:
            row = df_hist[df_hist['SepsisLabel'] == 1].sample(1)
            if row.empty: row = df_hist.sample(1)
        else:
            row = df_hist.sample(1)
        
        features = row[model.feature_names_in_]
        prob = model.predict_proba(features)[0][1]
        
        print("-" * 40)
        print(f"Patient: {pid} | Hour: {row['ICULOS'].values[0]}")
        print(f"Vitals: HR={row['HR'].values[0]:.1f}, Temp={row['Temp'].values[0]:.1f}, Lactate={row['Lactate'].values[0]:.1f}")
        
        if prob >= 0.50:
            print(f"Prediction: CRITICAL SEPSIS RISK (Risk: {prob:.1%})")
        elif prob >= 0.35:
            print(f"Prediction: MODERATE RISK (Risk: {prob:.1%})")
        else:
            print(f"Prediction: HEALTHY / STABLE (Risk: {prob:.1%})")
            
        print(f"Actual:     {'SEPSIS' if expected_label == 1 else 'HEALTHY'}")
        print("-" * 40)

    diagnose(sick_id, 1)
    diagnose(healthy_id, 0)
    conn.close()
    input("\nPress Enter...")

def run_specific_patient(model):
    print("\n OPTION 3: Specific Patient Lookup")
    conn = sqlite3.connect(DB_PATH)
    target_id = input("Enter Patient ID (e.g., p000001): ").strip()
    
    df_hist = get_patient_history(conn, target_id)
    if df_hist.empty:
        print(f"Error: Patient '{target_id}' not found.")
        conn.close(); input(); return

    print(f"\nFound {target_id} | Total Hours: {len(df_hist)}")
    hour_input = input(f"Enter hour (1-{len(df_hist)}) or Enter for LAST: ").strip()
    
    try:
        row = df_hist[df_hist['ICULOS'] == int(hour_input)] if hour_input else df_hist.tail(1)
        if row.empty: row = df_hist.tail(1)
    except: row = df_hist.tail(1)

    features = row[model.feature_names_in_]
    prob = model.predict_proba(features)[0][1]
    
    print("-" * 40)
    print(f"REPORT FOR HOUR {row['ICULOS'].values[0]}")
    print(f"HR: {row['HR'].values[0]:.1f} | Temp: {row['Temp'].values[0]:.1f} | SBP: {row['SBP'].values[0]:.1f}")
    
    if prob >= 0.50: 
        print(f"RESULT: CRITICAL SEPSIS RISK")
    elif prob >= 0.30: 
        print(f"RESULT: MODERATE RISK")
    else: 
        print(f"RESULT: PATIENT STABLE")
    
    print(f"Probability: {prob:.2%} | Actual Label: {row['SepsisLabel'].values[0]}")
    conn.close(); input("\nPress Enter...")

def run_manual_input(model):
    print("\n OPTION 2: Rapid Clinical Diagnostic")
    print("Starting...")
    
    db_stats = get_db_stats()
    feature_names = model.feature_names_in_
    input_values = {}
    
    # 1.) Auto-fill defaults for everything first
    VITAL_COLS = ['HR', 'O2Sat', 'Temp', 'SBP', 'MAP', 'DBP', 'Resp', 'Age', 'Gender', 'ICULOS', 'Unit1', 'Unit2']
    
    for feat in feature_names:
        stats = db_stats.get(feat, {'mean': 0.0, 'min': 0.0, 'max': 0.0})
        if feat in VITAL_COLS:
            input_values[feat] = stats['mean']
        else:
            input_values[feat] = 0.0 # Match training for missing labs

    print(f"\n[INSTRUCTIONS] Enter values for the {len(CRITICAL_FEATURES)} critical indicators.")
    print("Press ENTER to use Population Average.")
    print("-" * 60)
    
    # 2.) Loop through the Critical List
    for feature in CRITICAL_FEATURES:
        if feature not in feature_names: continue

        stats = db_stats.get(feature, {'mean': 0.0, 'min': 0.0, 'max': 0.0})
        current_default = input_values[feature]
        
        range_str = f"Range: {stats['min']:.1f}-{stats['max']:.1f}"

        while True:
            user_input = input(f"{feature:<15} [Avg: {current_default:6.2f} | {range_str}]: ")
            
            if user_input.strip() == "":
                break
            
            try:
                val = float(user_input)
                # CLAMPING LOGIC
                if val > stats['max'] and stats['max'] > 0:
                    print(f" **Input {val} exceeds historical max ({stats['max']:.1f}). Changing to Max.**")
                    val = stats['max']
                
                input_values[feature] = val
                break
            except ValueError:
                print("  **Invalid number.**")

    # 3.) Create DataFrame and Predict
    input_df = pd.DataFrame([input_values])[feature_names]
    prob = model.predict_proba(input_df)[0][1]
    
    print("=" * 40)
    if prob >= 0.50:
        print(f"RESULT: CRITICAL SEPSIS RISK")
    elif prob >= 0.30: 
        print(f"RESULT: MODERATE RISK")
    else: 
        print(f"RESULT: PATIENT STABLE")
        
    print(f"Calculated Probability: {prob:.2%}")
    print("=" * 40)
    input("\nPress Enter...")

# Main Hub
def interactive_menu():
    model = load_model()
    if model is None: return
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("---------------------------------------")
        print("   ICU SEPSIS EARLY WARNING SYSTEM")
        print("---------------------------------------")
        print("1. Random Patient Demo")
        print("2. Manual Input (Rapid)")
        print("3. Search Patient")
        print("4. Exit")
        choice = input("Select:")
        if choice == '1': run_random_demo(model)
        elif choice == '2': run_manual_input(model)
        elif choice == '3': run_specific_patient(model)
        elif choice == '4': break # Exit

if __name__ == "__main__":
    interactive_menu()