import os
import sys
import warnings

# Add 'src' to python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
warnings.simplefilter(action='ignore', category=FutureWarning)

from data_loader import load_data
from preprocessing import get_clean_data
from model_training import train_and_evaluate
from visualization import generate_visualizations
from predict import interactive_menu

def main():
    print("------------------------------------------------")
    print("   ICU SEPSIS EARLY WARNING SYSTEM - Main.py    ")
    print("------------------------------------------------")
    
    # Step 1: Check Database
    db_path = os.path.join('database', 'sepsis.db')
    if not os.path.exists(db_path):
        print("\n[Step 1] Database not found. Please run 'python database/init_db.py' first!")
        return
    else:
        print("\n[Step 1] Database found.")

    # Step 2: Load Data Check
    if os.path.getsize(db_path) < 100000:
        print("\n[Step 2] Database empty. Loading data...")
        load_data()
    else:
        print("\n[Step 2] Database populated. Skipping load.")

    # Step 3: Train Model
    print("\n[Step 3] Verifying/Training Model...")
    train_and_evaluate()

    # Step 4: Visualize
    print("\n[Step 4] Generating Visualizations...")
    generate_visualizations()
    
    # Step 5: Interactive App
    print("\n[Step 5] Launching Application...")
    interactive_menu()

if __name__ == "__main__":
    main()