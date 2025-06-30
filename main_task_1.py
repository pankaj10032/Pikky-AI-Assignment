# main.py
from fastapi import FastAPI
from pydantic import BaseModel, Field
import pandas as pd
import joblib

# --- Load Artifacts ---
app = FastAPI(title="Churn Prediction API")
model = joblib.load('churn_model.pkl')
scaler = joblib.load('scaler.pkl')
model_columns = joblib.load('model_columns.pkl')
numerical_cols = joblib.load('numerical_cols.pkl')

# --- Define Input Schema ---
class CustomerData(BaseModel):
    gender: str = Field(..., example="Male")
    SeniorCitizen: int = Field(..., example=0)
    Partner: str = Field(..., example="Yes")
    Dependents: str = Field(..., example="No")
    tenure: int = Field(..., example=24)
    PhoneService: str = Field(..., example="Yes")
    MultipleLines: str = Field(..., example="No")
    InternetService: str = Field(..., example="DSL")
    OnlineSecurity: str = Field(..., example="Yes")
    OnlineBackup: str = Field(..., example="No")
    DeviceProtection: str = Field(..., example="Yes")
    TechSupport: str = Field(..., example="No")
    StreamingTV: str = Field(..., example="No")
    StreamingMovies: str = Field(..., example="No")
    Contract: str = Field(..., example="One year")
    PaperlessBilling: str = Field(..., example="Yes")
    PaymentMethod: str = Field(..., example="Mailed check")
    MonthlyCharges: float = Field(..., example=59.9)
    TotalCharges: float = Field(..., example=1400.55)

# --- Define API Endpoint ---
@app.post("/predict")
def predict_churn(data: CustomerData):
    input_df = pd.DataFrame([data.dict()])
    
    # Feature Engineering
    input_df['tenure_group'] = pd.cut(input_df['tenure'], bins=[0, 12, 24, 48, 60, 72], labels=['0-12M', '13-24M', '25-48M', '49-60M', '61-72M'], include_lowest=True)
    service_cols = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies']
    input_df['services_count'] = input_df[service_cols].apply(lambda row: sum(x == 'Yes' for x in row), axis=1)

    # Preprocessing
    input_processed = pd.get_dummies(input_df).reindex(columns=model_columns, fill_value=0)
    input_processed[numerical_cols] = scaler.transform(input_processed[numerical_cols])

    # Prediction
    probability = model.predict_proba(input_processed)[:, 1][0]
    
    return {
        "churn_probability": float(probability),
        "prediction": "Churn" if probability > 0.5 else "Stay"
    }