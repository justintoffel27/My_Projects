import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from preprocessing import get_clean_data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def generate_visualizations():
    print("\nGenerating Visualizations")
    
    # Load Data
    df = get_clean_data()
    if df is None: return

    # Set style
    sns.set_style("whitegrid")

    # Class Imblanace
    print("Class Balance Chart:")
    plt.figure(figsize=(6, 4))
    sns.countplot(x='SepsisLabel', data=df, palette='coolwarm')
    plt.title('Distribution of Sepsis Cases (0=Healthy, 1=Sepsis)')
    plt.savefig(os.path.join(RESULTS_DIR, 'class_balance.png'))
    plt.close()

    # Vitals Comparison (Box Plots)
    print("Generating Vitals Box Plots...")
    # Were looking at the Top 3 features: ICULOS, Temp, Platelets (And Plus Heart Rate (HR) which is important anyways)
    key_features = ['ICULOS', 'Temp', 'Platelets', 'HR']
    
    plt.figure(figsize=(12, 8))
    for i, feature in enumerate(key_features, 1):
        plt.subplot(2, 2, i)
        # Remove outliers (99th percentile)
        upper_limit = df[feature].quantile(0.99)
        data_clean = df[df[feature] < upper_limit]
        
        sns.boxplot(x='SepsisLabel', y=feature, data=data_clean, palette='Set2')
        plt.title(f'{feature} vs Sepsis')
    
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'vitals_comparison.png'))
    plt.close()

    # Correlation Heatmap (Relationships)
    print("Generating Correlation Heatmap...")
    # Take a subset of only the important columns
    corr_cols = ['HR', 'Temp', 'SBP', 'Resp', 'WBC', 'Lactate', 'Age', 'SepsisLabel']
    corr_matrix = df[corr_cols].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
    plt.title('Correlation Matrix of Key Vitals')
    plt.savefig(os.path.join(RESULTS_DIR, 'correlation_heatmap.png'))
    plt.close()

    # The ROC Curve
    print("Generating ROC Curve...")
    
    # Quickly retrain/predict to get the probabilities for the curve
    X = df.drop(['patient_id', 'SepsisLabel', 'HospAdmTime'], axis=1)
    y = df['SepsisLabel']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Smaller Model (Faster)
    model = RandomForestClassifier(n_estimators=10, max_depth=5, class_weight='balanced', random_state=42)
    model.fit(X_train, y_train)
    y_probs = model.predict_proba(X_test)[:, 1]
    
    fpr, tpr, _ = roc_curve(y_test, y_probs)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC)')
    plt.legend(loc="lower right")
    plt.savefig(os.path.join(RESULTS_DIR, 'roc_curve.png'))
    plt.close()
    
    print(f"SUCCESS: 4 plots saved to {RESULTS_DIR}")

if __name__ == "__main__":
    generate_visualizations()