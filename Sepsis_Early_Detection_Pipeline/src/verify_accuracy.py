import pandas as pd
import joblib
import sqlite3
import os
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'sepsis.db')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'sepsis_rf_model.pkl')

def verify_model_performance():
    print("\nTesting Full Patient Histories")
    
    # Load Model
    if not os.path.exists(MODEL_PATH):
        print("Model not found.")
        return
    model = joblib.load(MODEL_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    
    # Get 50 Random Patient IDs (instead of random)
    print("Getting 50 random patients...")
    patient_ids = pd.read_sql("SELECT DISTINCT patient_id FROM sepsis_data ORDER BY RANDOM() LIMIT 50", conn)
    
    all_test_data = []
    
    # Get and Clean Each Patient individually
    for pid in patient_ids['patient_id']:
        query = f"SELECT * FROM sepsis_data WHERE patient_id = '{pid}' ORDER BY ICULOS"
        df_patient = pd.read_sql(query, conn)
        
        # THIS IS IMPORTANT: Forward Fill logic
        df_clean = df_patient.ffill().bfill().fillna(0)
        all_test_data.append(df_clean)
        
    conn.close()
    
    # Combine into one big test set
    full_test_df = pd.concat(all_test_data)
    
    # Prepare X and y variables
    X = full_test_df.drop(['patient_id', 'SepsisLabel', 'HospAdmTime'], axis=1)
    y_true = full_test_df['SepsisLabel']
    
    # Predict Time!
    print(f"Running AI predictions on {len(full_test_df)} rows...")
    y_pred = model.predict(X)
    y_probs = model.predict_proba(X)[:, 1]
    
    # AUROC Outcome
    acc = accuracy_score(y_true, y_pred)
    try:
        auc = roc_auc_score(y_true, y_probs)
    except:
        auc = 0.0
    
    print("-" * 40)
    print(f"Total Rows Tested: {len(full_test_df)}")
    print(f"Accuracy: {acc:.2%}")
    print(f"AUROC Score: {auc:.4f}")
    print("-" * 40)
    
    print("\nDetailed Report:")
    print(classification_report(y_true, y_pred))

if __name__ == "__main__":
    verify_model_performance()