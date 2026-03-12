from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import numpy as np
import pickle
import os

import models
from database import get_db
from auth import get_current_user

router = APIRouter()

# Global variables for the ML artifacts
model = None
feature_names = None
label_encoder = None

def load_artifacts():
    global model, feature_names, label_encoder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "career_model.pkl")
    features_path = os.path.join(base_dir, "career_model_features.pkl")
    encoder_path = os.path.join(base_dir, "career_roles_encoder.pkl")

    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            model = pickle.load(f)
    if os.path.exists(features_path):
        with open(features_path, "rb") as f:
            feature_names = pickle.load(f)
    if os.path.exists(encoder_path):
        with open(encoder_path, "rb") as f:
            label_encoder = pickle.load(f)

# Initialize on startup
load_artifacts()

@router.post("/predict")
def predict_career(
    skills: List[str] = Body(..., description="List of skill strings"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not model or not feature_names or not label_encoder:
        raise HTTPException(status_code=500, detail="Model artifacts not loaded on the server.")

    # Construct an input DataFrame mapping 1 or 0 for the user's available skills
    input_vector = {}

    # Inject CGPA. Default 7.0 if not set.
    input_vector["CGPA"] = current_user.cgpa if current_user.cgpa else 7.0
    input_vector["Project_Count"] = 2

    for feat in feature_names:
        if feat in ["CGPA", "Project_Count"]:
            continue
        # One-hot skills vector
        input_vector[feat] = 1 if feat in skills else 0

    df_input = pd.DataFrame([input_vector], columns=feature_names)

    # Predict probabilities
    probabilities = model.predict_proba(df_input)[0]

    # Match probabilities to classes
    classes = label_encoder.classes_
    role_probs = [(classes[i], float(prob)) for i, prob in enumerate(probabilities)]

    # Sort descending
    role_probs = sorted(role_probs, key=lambda x: x[1], reverse=True)

    # Save the top prediction to DB
    top_role, top_score = role_probs[0]

    prediction_record = models.Prediction(
        user_id=current_user.user_id,
        predicted_role=top_role,
        confidence_score=top_score
    )
    db.add(prediction_record)
    db.commit()
    db.refresh(prediction_record)

    return {
        "prediction_id": prediction_record.prediction_id,
        "top_prediction": top_role,
        "confidence_score": top_score,
        "all_probabilities": [{"role": r, "probability": p} for r, p in role_probs]
    }
