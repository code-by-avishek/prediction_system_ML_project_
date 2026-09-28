from math import isfinite
from pathlib import Path

from flask import Flask, render_template, request
import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)

model_data = joblib.load(BASE_DIR / "model.pkl")
preprocessor = model_data["preprocessor"]
model = model_data["model"]
best_model = model_data["model_name"]
cluster_map = model_data["cluster_map"]

CATEGORICAL_OPTIONS = {
    "Gender": {"Female", "Male"},
    "Physical_Activity": {"High", "Low", "Moderate"},
    "Smoking_Status": {"Current", "Former", "Never"},
    "Alcohol_Consumption": {"Frequent", "Occasional"},
    "Stress_Level": {"High", "Low", "Moderate"},
    "Diet_Quality": {"Average", "Good", "Poor"},
}

NUMERIC_FIELDS = {
    "Age": float,
    "BMI": float,
    "Systolic_BP": float,
    "Fasting_Glucose": float,
    "Postmeal_Glucose": float,
    "Insulin_Level": float,
    "Family_History_Diabetes": int,
    "Hypertension": int,
    "Heart_Disease": int,
    "Sleep_Hours": float,
}


def parse_form_data():
    data = {}

    for field, converter in NUMERIC_FIELDS.items():
        value = request.form.get(field, "").strip()
        try:
            parsed_value = converter(value)
        except ValueError as exc:
            raise ValueError(f"Enter a valid value for {field.replace('_', ' ')}.") from exc

        if isinstance(parsed_value, float) and not isfinite(parsed_value):
            raise ValueError(f"Enter a finite value for {field.replace('_', ' ')}.")

        if converter is int and parsed_value not in (0, 1):
            raise ValueError(f"{field.replace('_', ' ')} must be Yes or No.")

        data[field] = parsed_value

    for field, options in CATEGORICAL_OPTIONS.items():
        value = request.form.get(field, "")
        if value not in options:
            raise ValueError(f"Select a valid {field.replace('_', ' ').lower()}.")
        data[field] = value

    return data


def render_home(prediction_score=None, risk_level=None, error_message=None, status=200):
    return (
        render_template(
            "index.html",
            prediction_score=prediction_score,
            risk_level=risk_level,
            best_model=best_model,
            error_message=error_message,
        ),
        status,
    )


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_home()

    try:
        input_data = pd.DataFrame([parse_form_data()])
    except ValueError as exc:
        return render_home(error_message=str(exc), status=400)

    input_processed = preprocessor.transform(input_data)

    if best_model == "K-Means":
        cluster = model.predict(input_processed)[0]
        prediction = cluster_map.get(cluster, 0)
        prediction_score = 100.0 if prediction == 1 else 0.0
    elif best_model == "Linear Regression":
        prediction = model.predict(input_processed)[0]
        prediction_score = max(0.0, min(100.0, float(prediction) * 100))
    else:
        prediction = model.predict(input_processed)[0]
        if hasattr(model, "predict_proba"):
            classes = list(model.classes_)
            positive_class_index = classes.index(1)
            probability = model.predict_proba(input_processed)[0][positive_class_index]
            prediction_score = probability * 100
        else:
            prediction_score = 100.0 if prediction == 1 else 0.0

    prediction_score = round(prediction_score, 1)

    if prediction_score >= 70:
        risk_level = "High Risk"
    elif prediction_score >= 40:
        risk_level = "Moderate Risk"
    else:
        risk_level = "Low Risk"

    return render_home(prediction_score, risk_level)


if __name__ == "__main__":
    app.run()
