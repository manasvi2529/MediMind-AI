import pandas as pd

# Load the original dataset.
data = pd.read_csv("data/raw/heart_disease.csv")

# Remove rows where ca or thal is missing.
data = data.dropna(subset=["ca", "thal"]).copy()

# Convert num into a binary target: 0 = no disease, 1 = disease present.
data["target"] = (data["num"] > 0).astype(int)

# Remove the original five-level target to prevent using it as an input.
data = data.drop(columns=["num"])

# Save this prepared copy separately.
output_path = "data/processed/heart_disease_binary.csv"
data.to_csv(output_path, index=False)

print("Saved prepared dataset to:", output_path)
print("Shape:", data.shape)
print("\nTarget counts:")
print(data["target"].value_counts().sort_index())
print("\nMissing values remaining:", int(data.isna().sum().sum()))