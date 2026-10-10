# MediMind AI

An educational tabular machine-learning app built with Python, Pandas, scikit-learn, and Streamlit.

## Features

- Upload and preview a CSV
- Inspect column types and missing values
- Select the target and input columns
- Choose classification or regression
- Train Logistic Regression or Random Forest models
- Use Quick run to train on up to 10,000 rows
- Review metrics and charts
- Download held-out test predictions

## Run locally on Windows

1. Open PowerShell in the project folder.
2. Create and activate a virtual environment:
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
3. Install the dependencies:
   python -m pip install -r requirements.txt
4. Start the app:
   python -m streamlit run .\app.py

## Important limitations

This is an educational baseline, not a medical diagnostic tool. Results depend on the data, target, selected inputs, and evaluation method. Do not upload private patient information.
