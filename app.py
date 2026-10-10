import sys
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).parent / "src"))
from tabular_model import train_tabular_model

st.set_page_config(page_title="MediMind AI", page_icon="🩺")
st.title("MediMind AI")
st.write("Upload a tabular CSV, choose what to predict, and train a baseline model.")
st.caption("Educational project only. Not for diagnosis or clinical decisions.")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is None:
    st.info("Upload a CSV to begin.")
    st.stop()

try:
    data = pd.read_csv(uploaded_file)
except Exception as error:
    st.error(f"Could not read this CSV. Details: {error}")
    st.stop()

if data.empty:
    st.error("This CSV has no data rows.")
    st.stop()

if len(data.columns) < 2:
    st.error("The CSV needs a target column and at least one other column.")
    st.stop()

st.subheader("Dataset preview")
st.write(f"{len(data)} rows · {len(data.columns)} columns")
st.dataframe(data.head(10), width="stretch")

profile = pd.DataFrame({
    "column": data.columns,
    "data_type": [str(data[column].dtype) for column in data.columns],
    "missing_values": [int(data[column].isna().sum()) for column in data.columns],
    "missing_percent": [
        round(float(data[column].isna().mean() * 100), 1)
        for column in data.columns
    ],
})
st.subheader("Dataset profile")
st.dataframe(profile, width="stretch")
st.subheader("Choose the prediction")
target_column = st.selectbox(
    "Which column should the model predict?",
    options=data.columns,
)

available_features = [
    column for column in data.columns if column != target_column
]
feature_columns = st.multiselect(
    "Which columns should the model use as inputs?",
    options=available_features,
    default=available_features,
)

task = st.radio(
    "What kind of value is the target?",
    options=["classification", "regression"],
    horizontal=True,
    help="Classification predicts categories. Regression predicts numeric values.",
)

model_choice = st.selectbox(
    "Choose a model",
    options=["Logistic Regression", "Random Forest"],
)

if task == "classification":
    st.write(f"The model will predict categories in **{target_column}**.")
    counts = data[target_column].dropna().value_counts()
    st.write("Target categories and counts:")
    if len(counts) <= 30:
        st.bar_chart(counts)
    else:
        st.info("This target has many categories; the chart is hidden to keep it readable.")
    st.dataframe(
        counts.rename_axis("category").reset_index(name="rows"),
        width="stretch",
    )
    if len(counts) < 2:
        st.error("Classification requires at least two target categories.")
        st.stop()
else:
    st.write(f"The model will estimate the numeric value in **{target_column}**.")
    numeric_target = pd.to_numeric(data[target_column], errors="coerce")
    if numeric_target.dropna().nunique() < 2:
        st.error("Regression requires at least two different numeric target values.")
        st.stop()
    if numeric_target.isna().any():
        st.error("Regression requires a numeric target with no text values.")
        st.stop()

if data[target_column].notna().sum() < 10:
    st.error("At least 10 rows with a target value are needed.")
    st.stop()

quick_run = st.checkbox("Quick run: use up to 10,000 rows", value=True)
training_data = data

if quick_run and len(data) > 10000:
    if task == "classification":
        sample_source = data.dropna(subset=[target_column])
        try:
            training_data, _ = train_test_split(
                sample_source,
                train_size=10000,
                random_state=42,
                stratify=sample_source[target_column],
            )
        except ValueError:
            training_data = sample_source.sample(n=10000, random_state=42)
    else:
        training_data = data.sample(n=10000, random_state=42)

    st.info(
        f"Quick run uses {len(training_data):,} rows out of {len(data):,}. "
        "Turn it off to use the full dataset."
    )
if st.button("Train and evaluate model", type="primary"):
    if not feature_columns:
        st.error("Select at least one input column.")
        st.stop()

    with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as temp_file:
        temp_file.write(training_data.to_csv(index=False).encode("utf-8"))
        temp_path = temp_file.name

    try:
        with st.spinner("Training and evaluating the model..."):
            results = train_tabular_model(
                temp_path,
                target_column,
                task,
                feature_columns=feature_columns,
                model_choice=model_choice,
            )

        st.subheader("Results")
        st.write(f"**Model:** {model_choice}")
        st.write(f"**Task:** {results['task']}")
        st.write(f"**Target:** {results['target_column']}")
        st.write(f"**Rows used:** {results['rows_used']}")
        st.write(f"**Input columns:** {', '.join(results['feature_columns'])}")
        if task == "classification":
            st.subheader("Confusion matrix")
            st.write("Rows show actual categories; columns show predicted categories.")
            confusion = pd.crosstab(
                pd.Series(results["actual"], name="Actual"),
                pd.Series(results["predictions"], name="Predicted"),
            )
            st.bar_chart(confusion)
            st.dataframe(confusion, width="stretch")
        else:
            st.subheader("Actual vs predicted")
            plot_data = pd.DataFrame({
                "Actual": results["actual"],
                "Predicted": results["predictions"],
            })
            if len(plot_data) > 5000:
                plot_data = plot_data.sample(n=5000, random_state=42)
            st.scatter_chart(plot_data, x="Actual", y="Predicted")
        predictions_table = pd.DataFrame({
            "actual": results["actual"],
            "predicted": results["predictions"],
        })
        st.download_button(
            "Download test-set predictions",
            data=predictions_table.to_csv(index=False).encode("utf-8"),
            file_name="medimind_test_predictions.csv",
            mime="text/csv",
        )

        metrics = results["metrics"]
        if task == "classification":
            st.subheader("3-fold cross-validation")
            st.write(
                f"Accuracy: {metrics['cv_accuracy_mean']} ± {metrics['cv_accuracy_std']}"
            )
            st.write(
                f"Weighted F1: {metrics['cv_f1_mean']} ± {metrics['cv_f1_std']}"
            )
        else:
            st.subheader("3-fold cross-validation")
            st.write(f"MAE: {metrics['cv_mae_mean']} ± {metrics['cv_mae_std']}")

        if task == "classification":
            st.metric("Accuracy", metrics["accuracy"])
            st.write("Accuracy is the share of test rows classified correctly.")
            st.metric("Weighted F1 score", metrics["f1_weighted"])
            st.write(
                "Weighted F1 combines precision and recall across categories. "
                "The detailed report shows precision, recall, and F1 for each category."
            )
            st.code(metrics["classification_report"])
        else:
            st.metric("Mean absolute error (MAE)", metrics["mae"])
            st.write("MAE is the average prediction error in the target's units.")
            st.metric("Root mean squared error (RMSE)", metrics["rmse"])
            st.write("RMSE is in the target's units and penalizes larger errors more.")
            st.metric("R² score", metrics["r2"])
            st.write("R² compares the model with predicting the average target value.")

        st.info(
            "These scores use one train/test split. They are a starting estimate, "
            "not proof that a model will work well on new data."
        )
    except Exception as error:
        st.error(f"Model training failed. Details: {error}")
    finally:
        Path(temp_path).unlink(missing_ok=True)







