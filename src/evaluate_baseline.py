import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

data = pd.read_csv("data/processed/heart_disease_binary.csv")
X = data.drop(columns=["target"])
y = data["target"]

model = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=1000),
)

folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

scores = cross_validate(
    model,
    X,
    y,
    cv=folds,
    scoring={
        "accuracy": "accuracy",
        "precision": "precision",
        "recall": "recall",
        "f1": "f1",
    },
)

for metric in ("accuracy", "precision", "recall", "f1"):
    values = scores[f"test_{metric}"]
    print(f"{metric}: {values.mean():.3f} ± {values.std():.3f}")
    