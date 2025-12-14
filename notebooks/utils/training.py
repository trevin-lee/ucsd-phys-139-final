import pandas as pd
import numpy as np
import argparse
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import os

def train_model(data_path, output_dir="models", test_size=0.25, random_state=42):
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        return

    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)

    FEATURES = [
        "period",
        "Q31",
        "Amp",
        "W",
        "K",
        "Std",
        "gamma1",
        "gamma2",
        "R21",
        "R31",
        "phi21",
        "phi31"
    ]

    missing_features = [f for f in FEATURES if f not in df.columns]
    if missing_features:
        print(f"Error: Missing feature columns: {missing_features}")
        return

    potential_labels = [c for c in df.columns if c not in FEATURES and c != 'star_id']
    
    if 'label' in df.columns:
        LABEL_COL = 'label'
    elif len(potential_labels) > 0:
        LABEL_COL = potential_labels[-1]
    else:
        print("Error: Could not identify a label column.")
        return

    print("Using label column:", LABEL_COL)
    
    print("Class distribution:\n", df[LABEL_COL].value_counts())

    X = df[FEATURES].values
    y = df[LABEL_COL].astype(str).values

    if np.isnan(X).any():
        print("Warning: NaNs found in features. Filling with 0.")
        X = np.nan_to_num(X)

    class_counts = pd.Series(y).value_counts()
    valid_classes = class_counts[class_counts >= 2].index
    mask = pd.Series(y).isin(valid_classes)
    
    if (~mask).any():
        print(f"Dropping {sum(~mask)} samples from classes with < 2 instances for stratification.")
        X = X[mask]
        y = y[mask]

    print(f"Splitting data (test_size={test_size})...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    print("Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("Training Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=300,
        random_state=random_state,
        n_jobs=-1,
        class_weight="balanced"
    )
    rf.fit(X_train_scaled, y_train)

    print("\n--- Evaluation ---")
    y_pred = rf.predict(X_test_scaled)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    
    unique_labels = np.unique(np.concatenate([y_test, y_pred]))
    print("\nClassification Report:\n", classification_report(y_test, y_pred, labels=unique_labels, zero_division=0))

    print("\n--- Feature Importances ---")
    importances = rf.feature_importances_
    for fname, val in sorted(zip(FEATURES, importances), key=lambda x: -x[1]):
        print(f"{fname:10s} : {val:.4f}")

    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, "random_forest_model.pkl")
    scaler_path = os.path.join(output_dir, "scaler.pkl")
    
    joblib.dump(rf, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"\nModel saved to: {model_path}")
    print(f"Scaler saved to: {scaler_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Random Forest model.")
    parser.add_argument("--data_path", type=str, default="data/labeled_features.csv", help="Path to input CSV")
    parser.add_argument("--output_dir", type=str, default="models", help="Directory to save model")
    
    args = parser.parse_args()
    
    train_model(args.data_path, args.output_dir)

