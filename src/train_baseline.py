import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# Load the prepared dataset.
data = pd.read_csv("data/processed/heart_disease_binary.csv")

# Separate input features from the label we want to predict.
X = data.drop(columns=["target"])
y = data["target"]

# Keep some rows aside so we can evaluate on data the model didn't train on.
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

# Scale numeric features, then train logistic regression.
model = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=1000),
)
model.fit(X_train, y_train)

# Evaluate predictions on the held-out rows.
predictions = model.predict(X_test)

print("Accuracy:", round(accuracy_score(y_test, predictions), 3))
print("\nConfusion matrix:")
print(confusion_matrix(y_test, predictions))
print("\nClassification report:")
print(classification_report(y_test, predictions, target_names=["No disease", "Disease present"]))