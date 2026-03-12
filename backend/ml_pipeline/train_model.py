import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb
import pickle
import os

def train():
    data_path = "data/synthetic_career_data.csv"
    if not os.path.exists(data_path):
        print("Data file not found. Run generate_data.py first.")
        return

    print("Loading dataset...")
    df = pd.read_csv(data_path)
    
    # Features (X) and Target (y)
    X = df.drop(columns=["Role"])
    y = df["Role"]
    
    # Store feature names to ensure inference is aligned
    feature_names = list(X.columns)
    with open("career_model_features.pkl", "wb") as f:
        pickle.dump(feature_names, f)
        
    # We must encode the target labels to numeric for XGBoost
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    with open("career_roles_encoder.pkl", "wb") as f:
        pickle.dump(le, f)

    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    print("Training Logistic Regression...")
    lr = LogisticRegression(max_iter=1000)
    lr.fit(X_train, y_train)
    lr_preds = lr.predict(X_test)
    lr_acc = accuracy_score(y_test, lr_preds)
    
    print("Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_preds = rf.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_preds)
    
    print("Training XGBoost...")
    xb = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)
    xb.fit(X_train, y_train)
    xb_preds = xb.predict(X_test)
    xb_acc = accuracy_score(y_test, xb_preds)
    
    print(f"\nAccuracy Scores:\nLR: {lr_acc:.4f}\nRF: {rf_acc:.4f}\nXGB: {xb_acc:.4f}")
    
    # Select best model
    best_model = None
    best_name = ""
    scores = {"Logistic Regression": (lr_acc, lr), "Random Forest": (rf_acc, rf), "XGBoost": (xb_acc, xb)}
    
    for name, (acc, model) in scores.items():
        if best_model is None or acc > scores[best_name][0]:
            best_model = model
            best_name = name
            
    print(f"\nSelected Best Model: {best_name} with accuracy {scores[best_name][0]:.4f}")
    
    with open("career_model.pkl", "wb") as f:
        pickle.dump(best_model, f)
    print("Model saved as career_model.pkl")

if __name__ == "__main__":
    train()
