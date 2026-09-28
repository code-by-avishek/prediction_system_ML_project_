# Diabetes Risk Predictor

A Flask application that accepts health and lifestyle information and returns an experimental model-generated diabetes risk score. It is for educational use only and is not a diagnosis or a substitute for professional medical advice.

## Project files

- `app.py` — Flask page and prediction route.
- `train_model.py` — trains and compares candidate models.
- `model.pkl` — pre-trained model and preprocessing data used by the app.
- `diabetes_risk_dataset.csv` — training data used by `train_model.py`.
- `templates/index.html` and `static/` — web interface.

## Setup and run

Use Python 3.11 or newer. The requirements pin scikit-learn to the version used to serialize the included model.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in a browser. The app loads `model.pkl` relative to its own location, so it can be started from another working directory.

To retrain the model from the supplied CSV:

```powershell
python train_model.py
```

Training replaces `model.pkl` and `best_model.txt` in the project directory. If you retrain with a different scikit-learn version, install the matching version when running the app; scikit-learn does not guarantee compatibility of serialized models across versions.

The trainer reports both accuracy and balanced accuracy, selects by balanced accuracy to account for the dataset's uneven class distribution, and refits the selected classifier on the full dataset. The displayed percentage is a model score, not a calibrated probability.

## Input data

The predictor uses age, gender, BMI, systolic blood pressure, fasting and post-meal glucose, insulin, physical activity, smoking and alcohol consumption, family history, hypertension, heart disease, sleep, stress, and diet quality. Categorical form options match the categories in the supplied training dataset.

Prediction history is stored in the browser's local storage. Health inputs are processed by the local Flask app and are not saved by the application.

## Important

The output is an experimental estimate from this dataset and model, not a calibrated clinical risk assessment. Do not use it to make medical decisions. The built-in Flask server is for local development; use a production WSGI server if deploying the app.
