import pandas as pd
import joblib
from pathlib import Path

from sklearn.base import clone
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.calibration import CalibratedClassifierCV

from sklearn.metrics import accuracy_score, balanced_accuracy_score


BASE_DIR = Path(__file__).resolve().parent


# ==========================================
# 1. LOAD DATA
# ==========================================

df = pd.read_csv(BASE_DIR / "diabetes_risk_dataset.csv")

print("\nDataset loaded successfully!")
print("Rows:", len(df))


# ==========================================
# 2. INPUT & TARGET
# ==========================================

X = df.drop(columns=["Patient_ID", "Diabetes"])
y = df["Diabetes"]


# ==========================================
# 3. COLUMNS
# ==========================================

categorical = [
    "Gender",
    "Physical_Activity",
    "Smoking_Status",
    "Alcohol_Consumption",
    "Stress_Level",
    "Diet_Quality"
]

numeric = [
    "Age",
    "BMI",
    "Systolic_BP",
    "Fasting_Glucose",
    "Postmeal_Glucose",
    "Insulin_Level",
    "Family_History_Diabetes",
    "Hypertension",
    "Heart_Disease",
    "Sleep_Hours"
]


# ==========================================
# 4. PREPROCESSING
# ==========================================

preprocessor = ColumnTransformer([

    (
        "numeric",
        Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]),
        numeric
    ),

    (
        "categorical",
        Pipeline([
            (
                "imputer",
                SimpleImputer(strategy="most_frequent")
            ),

            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False
                )
            )
        ]),
        categorical
    )

])


# ==========================================
# 5. TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ==========================================
# 6. PREPARE DATA
# ==========================================

X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)


# ==========================================
# 7. MODELS
# ==========================================

models = {

    "Logistic Regression":
        LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight="balanced"
        ),

    "Random Forest":
        RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced"
        ),

    "Decision Tree":
        DecisionTreeClassifier(
            random_state=42,
            class_weight="balanced"
        ),

    "SVM":
        CalibratedClassifierCV(
            estimator=SVC(
                random_state=42,
                class_weight="balanced"
            ),
            method="sigmoid",
            cv=5,
            ensemble=False
        ),

    "KNN":
        KNeighborsClassifier(
            n_neighbors=5
        ),

    "Naive Bayes":
        GaussianNB()
}


# ==========================================
# 8. TRAIN MODELS
# ==========================================

results = {}

best_model = None
best_name = ""
best_balanced_accuracy = -1


for name, model in models.items():

    print(f"\nTraining: {name}")

    model.fit(
        X_train_processed,
        y_train
    )

    prediction = model.predict(
        X_test_processed
    )


    # ======================================
    # ACCURACY
    # ======================================

    accuracy = accuracy_score(
        y_test,
        prediction
    )
    balanced_accuracy = balanced_accuracy_score(
        y_test,
        prediction
    )

    results[name] = {
        "accuracy": accuracy,
        "balanced_accuracy": balanced_accuracy
    }

    print(
        f"Accuracy: {accuracy * 100:.2f}% | "
        f"Balanced accuracy: {balanced_accuracy * 100:.2f}%"
    )


    # ======================================
    # SELECT BEST MODEL
    # ======================================

    if balanced_accuracy > best_balanced_accuracy:

        best_balanced_accuracy = balanced_accuracy
        best_model = model
        best_name = name


# ==========================================
# 9. MODEL COMPARISON
# ==========================================

print("\n")
print("=" * 50)
print("MODEL COMPARISON")
print("=" * 50)

for name, metrics in results.items():

    print(
        f"{name:<25}"
        f"Accuracy: {metrics['accuracy'] * 100:.2f}% | "
        f"Balanced accuracy: {metrics['balanced_accuracy'] * 100:.2f}%"
    )

print("=" * 50)

print(
    f"BEST MODEL: {best_name}"
)

print(
    f"BEST BALANCED ACCURACY: "
    f"{best_balanced_accuracy * 100:.2f}%"
)

print("=" * 50)


# ==========================================
# 10. REFIT WINNER ON ALL DATA
# ==========================================

preprocessor = clone(preprocessor)
best_model = clone(best_model)
X_processed = preprocessor.fit_transform(X)
best_model.fit(X_processed, y)


# ==========================================
# 11. SAVE MODEL
# ==========================================

model_data = {

    "preprocessor": preprocessor,

    "model": best_model,

    "model_name": best_name,

    "cluster_map": None,

    "accuracy": results[best_name]["accuracy"],

    "balanced_accuracy": best_balanced_accuracy

}


joblib.dump(
    model_data,
    BASE_DIR / "model.pkl"
)


# ==========================================
# 12. SAVE MODEL NAME
# ==========================================

with open(
    BASE_DIR / "best_model.txt",
    "w"
) as file:

    file.write(best_name)


print("\nBest model saved successfully!")
print("File: model.pkl")
print("Model:", best_name)
print(
    f"Hold-out balanced accuracy: "
    f"{best_balanced_accuracy * 100:.2f}%"
)