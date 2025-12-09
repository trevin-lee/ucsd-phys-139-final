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
    """
    Trains a Random Forest classifier on the labeled features dataset.
    
    Args:
        data_path (str): Path to the labeled features CSV file.
        output_dir (str): Directory to save the trained model.
        test_size (float): Fraction of data to use for testing.
        random_state (int): Random seed.
    """
    
    # ---------------------------------------------------------
    # Load data
    # ---------------------------------------------------------
    if not os.path.exists(data_path):
        print(f"❌ Error: Data file not found at {data_path}")
        return

    print(f"📖 Loading data from {data_path}...")
    df = pd.read_csv(data_path)

    # All 12 feature columns
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

    # Verify all features exist
    missing_features = [f for f in FEATURES if f not in df.columns]
    if missing_features:
        print(f"❌ Error: Missing feature columns: {missing_features}")
        return

    # Label column (assume it's already present)
    # Finding the one column NOT in FEATURES (and not star_id/index like columns ideally)
    # The snippet used logic: [c for c in df.columns if c not in FEATURES][0]
    # We should be safer and look for 'label' specifically or exclude known ID cols
    
    potential_labels = [c for c in df.columns if c not in FEATURES and c != 'star_id']
    
    if 'label' in df.columns:
        LABEL_COL = 'label'
    elif len(potential_labels) > 0:
        # Fallback to the user logic but skip star_id if possible
        LABEL_COL = potential_labels[-1] # Taking last column often works for appended labels
    else:
        print("❌ Error: Could not identify a label column.")
        return

    print("Using label column:", LABEL_COL)
    
    # Filter out Unknown labels if necessary? 
    # The user didn't specify, but usually we don't train on 'Unknown' unless it's a class.
    # Assuming the user wants to train on whatever is there.
    # BUT, if 'Unknown' dominates, the model might just predict 'Unknown'.
    # Let's print class distribution.
    print("Class distribution:\n", df[LABEL_COL].value_counts())

    X = df[FEATURES].values
    y = df[LABEL_COL].astype(str).values # Ensure string for classification

    # Handle NaNs in features (simple imputation if needed, though preprocessing usually handles it)
    if np.isnan(X).any():
        print("⚠️ Warning: NaNs found in features. Filling with 0.")
        X = np.nan_to_num(X)

    # ---------------------------------------------------------
    # Train/test split
    # ---------------------------------------------------------
    # Stratify requires at least 2 members per class.
    # Filter out classes with < 2 samples to avoid stratify error
    class_counts = pd.Series(y).value_counts()
    valid_classes = class_counts[class_counts >= 2].index
    mask = pd.Series(y).isin(valid_classes)
    
    if (~mask).any():
        print(f"⚠️ Dropping {sum(~mask)} samples from classes with < 2 instances for stratification.")
        X = X[mask]
        y = y[mask]

    print(f"Splitting data (test_size={test_size})...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # ---------------------------------------------------------
    # Scale features (optional but often helpful)
    # ---------------------------------------------------------
    print("Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # ---------------------------------------------------------
    # Train Random Forest
    # ---------------------------------------------------------
    print("Training Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=300,
        random_state=random_state,
        n_jobs=-1,
        class_weight="balanced"
    )
    rf.fit(X_train_scaled, y_train)

    # ---------------------------------------------------------
    # Evaluate
    # ---------------------------------------------------------
    print("\n--- Evaluation ---")
    y_pred = rf.predict(X_test_scaled)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    
    # Handle unique labels in report
    unique_labels = np.unique(np.concatenate([y_test, y_pred]))
    print("\nClassification Report:\n", classification_report(y_test, y_pred, labels=unique_labels, zero_division=0))
    # print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

    # ---------------------------------------------------------
    # Feature Importances
    # ---------------------------------------------------------
    print("\n--- Feature Importances ---")
    importances = rf.feature_importances_
    for fname, val in sorted(zip(FEATURES, importances), key=lambda x: -x[1]):
        print(f"{fname:10s} : {val:.4f}")

    # ---------------------------------------------------------
    # Save Model
    # ---------------------------------------------------------
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, "random_forest_model.pkl")
    scaler_path = os.path.join(output_dir, "scaler.pkl")
    
    joblib.dump(rf, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"\n✅ Model saved to: {model_path}")
    print(f"✅ Scaler saved to: {scaler_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Random Forest model.")
    parser.add_argument("--data_path", type=str, default="data/labeled_features.csv", help="Path to input CSV")
    parser.add_argument("--output_dir", type=str, default="models", help="Directory to save model")
    
    args = parser.parse_args()
    
    train_model(args.data_path, args.output_dir)

