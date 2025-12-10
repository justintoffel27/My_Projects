import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict
from sklearn.metrics import (
    classification_report, roc_auc_score, confusion_matrix,
    roc_curve, auc, precision_recall_curve, average_precision_score
)
from preprocessing import get_clean_data
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def bootstrap_auc(y_true, y_prob, n_bootstraps=1000, random_state=42):
    rng = np.random.RandomState(random_state)
    bootstrapped_scores = []
    n = len(y_true)
    for i in range(n_bootstraps):
        # Sample with replacement
        idx = rng.randint(0, n, n)
        if len(np.unique(y_true[idx])) < 2:
            # Skip if only one class in the given bootstrap sample
            continue
        score = roc_auc_score(y_true[idx], y_prob[idx])
        bootstrapped_scores.append(score)
    sorted_scores = np.array(bootstrapped_scores)
    sorted_scores.sort()
    lower = sorted_scores[int(0.025 * len(sorted_scores))]
    upper = sorted_scores[int(0.975 * len(sorted_scores))]
    return np.mean(sorted_scores), lower, upper

def train_and_evaluate():
    df = get_clean_data()
    if df is None:
        return

    X = df.drop(['patient_id', 'SepsisLabel', 'HospAdmTime'], axis=1)
    y = df['SepsisLabel'].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=100, max_depth=10, random_state=42, n_jobs=-1, class_weight='balanced'
    )
    model.fit(X_train, y_train)

    # Get the probabilities for the positive class
    if hasattr(model, "predict_proba"):
        # Find index of positive class
        pos_idx = list(model.classes_).index(1) if 1 in model.classes_ else 1
        y_probs = model.predict_proba(X_test)[:, pos_idx]
    elif hasattr(model, "decision_function"):
        y_probs = model.decision_function(X_test)  
    else:
        # Use predictions
        y_probs = model.predict(X_test)
    y_pred = model.predict(X_test)

    # Report & Confusion matrix
    print(classification_report(y_test, y_pred))
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.title('Confusion Matrix')
    plt.savefig(os.path.join(RESULTS_DIR, 'confusion_matrix.png'))
    plt.close()

    # AUROC
    roc_score = roc_auc_score(y_test, y_probs)
    mean_auc, lower_ci, upper_ci = bootstrap_auc(y_test, y_probs, n_bootstraps=1000)
    print(f"AUROC: {roc_score:.4f} (bootstrap mean {mean_auc:.4f}, 95% CI [{lower_ci:.4f}, {upper_ci:.4f}])")

    # ROC Curve Plot
    fpr, tpr, _ = roc_curve(y_test, y_probs)
    roc_auc = auc(fpr, tpr)
    plt.figure(figsize=(6,6))
    plt.plot(fpr, tpr, label=f'ROC (AUC = {roc_auc:.3f})')
    plt.plot([0,1], [0,1], linestyle='--', label='Random')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend(loc='lower right')
    plt.savefig(os.path.join(RESULTS_DIR, 'roc_curve.png'))
    plt.close()

    # Precision Recall Fct
    avg_prec = average_precision_score(y_test, y_probs)
    precision, recall, _ = precision_recall_curve(y_test, y_probs)
    plt.figure(figsize=(6,6))
    plt.plot(recall, precision, label=f'PR (AP = {avg_prec:.3f})')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend(loc='lower left')
    plt.savefig(os.path.join(RESULTS_DIR, 'pr_curve.png'))
    plt.close()

    # Top 10 Most Importnat Features/Variables
    importances = model.feature_importances_
    feat_df = pd.DataFrame({'feature': X.columns, 'importance': importances})
    feat_df = feat_df.sort_values('importance', ascending=False).head(10)
    plt.figure(figsize=(8,5))
    sns.barplot(x='importance', y='feature', data=feat_df)
    plt.title('Top 10 Feature Importances')
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'feature_importance.png'))
    plt.close()

    # Save Model (To Results)
    MODELS_DIR = os.path.join(BASE_DIR, 'models')
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(MODELS_DIR, 'sepsis_rf_model.pkl'))

if __name__ == '__main__':
    train_and_evaluate()
