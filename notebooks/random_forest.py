import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

#load data
df = pd.read_csv("features.csv") 

#12 features
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

#label column
LABEL_COL = [c for c in df.columns if c not in FEATURES][0]
print("Using label column:", LABEL_COL)

X = df[FEATURES].values
y = df[LABEL_COL].values

#train test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

#scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

#train
rf = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)

rf.fit(X_train_scaled, y_train)

#evaluate
y_pred = rf.predict(X_test_scaled)

#give these metrics
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

#print feature importance
print("\nFeature Importance:\n")
importances = rf.feature_importances_
for fname, val in sorted(zip(FEATURES, importances), key=lambda x: -x[1]):
    print(f"{fname:10s} : {val:.4f}")
