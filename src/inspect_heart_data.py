from ucimlrepo import fetch_ucirepo

heart_disease = fetch_ucirepo(id=45)

features = heart_disease.data.features
targets = heart_disease.data.targets
data = features.join(targets)

print("First five records:")
print(data.head())

print("\nDataset shape (rows, columns):")
print(data.shape)

print("\nColumn names:")
print(data.columns.tolist())

print("\nMissing values by column:")
print(data.isna().sum())

output_path = "data/raw/heart_disease.csv"
data.to_csv(output_path, index=False)

print(f"\nSaved dataset to {output_path}")