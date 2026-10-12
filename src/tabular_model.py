from pathlib import Path

import pandas as pd
import numpy as np
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split, cross_validate, StratifiedKFold, KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

def save_model_bundle(results: dict, path: str = "models/medimind_model.joblib") -> None:
    model_bundle = {
        "pipeline": results["pipeline"],
        "task": results["task"],
        "target_column": results["target_column"],
        "feature_columns": results["feature_columns"],
        "target_labels": results["target_labels"],
    }

    model_path = Path(path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_bundle, model_path)

def load_model_bundle(path: str = "models/medimind_model.joblib") -> dict | None:
    model_path = Path(path)
    if not model_path.exists():
        return None
    return joblib.load(model_path)    

def train_tabular_model(
    csv_path: str,
    target_column: str,
    task: str,
    feature_columns: list[str] | None = None,
    model_choice: str = "Logistic Regression",
) -> dict:
    csv_file = Path(csv_path)

    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file}")

    if task not in {"classification", "regression"}:
        raise ValueError("task must be 'classification' or 'regression'")

    data = pd.read_csv(csv_file)

    if target_column not in data.columns:
        raise ValueError(f"Target column '{target_column}' not found.")

    if feature_columns is None:
        feature_columns = [
            column for column in data.columns if column != target_column
        ]

    if not feature_columns:
        raise ValueError("Choose at least one input feature column.")

    if target_column in feature_columns:
        raise ValueError("The target cannot also be an input feature.")

    unknown_columns = [
        column for column in feature_columns if column not in data.columns
    ]
    if unknown_columns:
        raise ValueError(f"Feature columns not found: {unknown_columns}")

    data = data.dropna(subset=[target_column]).copy()
    X = data[feature_columns].copy()
    y = data[target_column].copy()

    if task == "classification":
        y, target_labels = pd.factorize(y)
        if len(target_labels) < 2:
            raise ValueError("Classification requires at least two target categories.")
        class_counts = pd.Series(y).value_counts()
        stratify = y if class_counts.min() >= 2 else None
        model = (
            RandomForestClassifier(n_estimators=50, random_state=42, class_weight="balanced")
            if model_choice == "Random Forest"
            else LogisticRegression(max_iter=1000)
        )
    else:
        y = pd.to_numeric(y, errors="coerce")
        valid_rows = y.notna()
        X = X.loc[valid_rows]
        y = y.loc[valid_rows]
        if len(y) < 2:
            raise ValueError("Regression needs at least two numeric target values.")
        if y.nunique() < 2:
            raise ValueError("Regression needs at least two different target values.")
        stratify = None
        model = (
            RandomForestRegressor(n_estimators=50, random_state=42)
            if model_choice == "Random Forest"
            else Ridge()
        )

    numeric_columns = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = X.select_dtypes(exclude=["number"]).columns.tolist()

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("one_hot", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=10, max_categories=100)),
        ]
    )

    preprocessing = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_columns),
            ("categorical", categorical_pipeline, categorical_columns),
        ]
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessing", preprocessing),
            ("model", model),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=stratify,
    )

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    if task == "classification":
        metrics = {
            "accuracy": round(accuracy_score(y_test, predictions), 3),
            "f1_weighted": round(
                f1_score(y_test, predictions, average="weighted", zero_division=0), 3
            ),
            "classification_report": classification_report(
                y_test, predictions, zero_division=0
            ),
        }
    else:
        metrics = {
            "mae": round(mean_absolute_error(y_test, predictions), 3),
            "rmse": round(mean_squared_error(y_test, predictions) ** 0.5, 3),
            "r2": round(r2_score(y_test, predictions), 3),
        }

    if task == "classification":
        cv_folds = min(2, int(class_counts.min()))
        if cv_folds < 2:
            raise ValueError("Cross-validation needs at least two examples in every target category.")
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
        cv_scoring = {"accuracy": "accuracy", "f1_weighted": "f1_weighted"}
    else:
        cv_folds = min(2, len(y))
        cv = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
        cv_scoring = {"mae": "neg_mean_absolute_error"}

    cv_scores = cross_validate(
        pipeline, X, y, cv=cv, scoring=cv_scoring, n_jobs=1
    )

    if task == "classification":
        metrics["cv_accuracy_mean"] = round(cv_scores["test_accuracy"].mean(), 3)
        metrics["cv_accuracy_std"] = round(cv_scores["test_accuracy"].std(), 3)
        metrics["cv_f1_mean"] = round(cv_scores["test_f1_weighted"].mean(), 3)
        metrics["cv_f1_std"] = round(cv_scores["test_f1_weighted"].std(), 3)
    else:
        cv_mae = -cv_scores["test_mae"]
        metrics["cv_mae_mean"] = round(cv_mae.mean(), 3)
        metrics["cv_mae_std"] = round(cv_mae.std(), 3)
    feature_importance = []
    try:
        estimator = pipeline.named_steps["model"]
        feature_names = pipeline.named_steps["preprocessing"].get_feature_names_out()

        if hasattr(estimator, "feature_importances_"):
            importance_values = estimator.feature_importances_
        elif hasattr(estimator, "coef_"):
            importance_values = (
                pd.DataFrame(estimator.coef_).abs().mean(axis=0).to_numpy()
            )
        else:
            importance_values = []

        if len(feature_names) == len(importance_values):
            feature_importance = [
                {"feature": str(name), "importance": round(float(value), 6)}
                for name, value in zip(feature_names, importance_values)
            ]
            feature_importance.sort(
                key=lambda item: item["importance"], reverse=True
            )
            feature_importance = feature_importance[:15]
    except (AttributeError, ValueError):
        feature_importance = []
    return {
    "task": task,
    "target_column": target_column,
    "rows_used": len(X),
    "feature_columns": feature_columns,
    "actual": (
        target_labels[y_test].tolist()
        if task == "classification"
        else y_test.tolist()
    ),
    "predictions": (
        target_labels[predictions].tolist()
        if task == "classification"
        else predictions.tolist()
    ),
    "pipeline": pipeline,
    "target_labels": target_labels.tolist() if task == "classif        "feature_importance": feature_importance,
ication" else None,
    "metrics": metrics,
}






