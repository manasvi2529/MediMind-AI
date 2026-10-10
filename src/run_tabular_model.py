from pathlib import Path

import pandas as pd
from tabular_model import train_tabular_model

default_path = "data/processed/heart_disease_binary.csv"
csv_path = input(f"CSV path [{default_path}]: ").strip() or default_path

try:
    preview = pd.read_csv(csv_path, nrows=5)
except FileNotFoundError:
    print(f"File not found: {csv_path}")
    raise SystemExit(1)
except Exception as error:
    print(f"Could not read that CSV: {error}")
    raise SystemExit(1)

print("\nColumns in this dataset:")
for column in preview.columns:
    print(f"- {column}")

target_column = input("\nWhich column should the model predict? ").strip()
if target_column not in preview.columns:
    print(f"Column not found. Choose one of: {preview.columns.tolist()}")
    raise SystemExit(1)

task = input("Task type (classification or regression): ").strip().lower()
if task not in {"classification", "regression"}:
    print("Please enter classification or regression.")
    raise SystemExit(1)

try:
    results = train_tabular_model(csv_path, target_column, task)
except Exception as error:
    print(f"\nCould not train the model: {error}")
    raise SystemExit(1)

print("\nTask:", results["task"])
print("Target column:", results["target_column"])
print("Rows used:", results["rows_used"])
print("Feature columns:", results["feature_columns"])
print("Metrics:")

for name, value in results["metrics"].items():
    print(f"\n{name}:")
    print(value)
