import os
import json
import joblib
import pandas as pd
from app.models.schemas import myPredictionInput

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

# Load model and types once
with open('./app/utils/form_types.json', 'r') as f:
    form_types = json.load(f)

loaded_model = joblib.load('./app/utils//best_model.pkl')
columns = list(form_types.keys())

router = APIRouter()

def predict(input: myPredictionInput):
    try:
        features = input.data

        # Build DataFrame
        df = pd.DataFrame(features, index=[0])
        df = df.reindex(columns=columns)

        # 🔍 Check for missing or NaN features
        missing_or_nan = [
            col for col in columns
            if col not in df.columns or pd.isna(df[col].iloc[0])
        ]

        if missing_or_nan:
            raise HTTPException(
                status_code=400,
                detail=f"Missing or NaN features: {missing_or_nan}"
            )

        # Apply proper dtypes
        for col in df.columns:
            df[col] = df[col].astype(form_types[col])

        # Predict probability
        probability = float(loaded_model.predict_proba(df)[:, 1][0])
        return {"probability": probability}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")