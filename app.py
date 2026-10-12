import json
import sys
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).parent / "src"))
from tabular_model import train_tabular_model, save_model_bundle, load_model_bundle


st.set_page_config(page_title="MediMind AI", page_icon="ÃƒÆ’Ã†â€™Ãƒâ€šÃ‚Â°ÃƒÆ’Ã¢â‚¬Â¦Ãƒâ€šÃ‚Â¸ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â©ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Âº")
# MediMind AI visual theme
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(ellipse at 10% 0%, rgba(35, 110, 120, 0.20), transparent 34%),
            linear-gradient(145deg, #0b1220 0%, #101827 55%, #111b2c 100%);
    }

    [data-testid="stAppViewContainer"] .main .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    h1 {
        letter-spacing: -0.04em;
        font-weight: 750 !important;
    }

    h2, h3 {
        letter-spacing: -0.025em;
    }

    [data-testid="stMetric"] {
        background: rgba(25, 38, 55, 0.78);
        border: 1px solid rgba(148, 163, 184, 0.18);
        padding: 1rem 1.1rem;
        border-radius: 14px;
    }

    [data-testid="stFileUploader"] {
        background: rgba(25, 38, 55, 0.55);
        border: 1px dashed rgba(94, 234, 212, 0.45);
        border-radius: 14px;
        padding: 0.6rem;
    }

    div.stButton > button[kind="primary"] {
        border: 0;
        border-radius: 10px;
        font-weight: 650;
        padding: 0.65rem 1rem;
        background: linear-gradient(90deg, #0f9f9a, #2563eb);
        color: white;
    }

    div.stButton > button[kind="primary"]:hover {
        border: 0;
        filter: brightness(1.12);
        color: white;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 12px;
        overflow: hidden;
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
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
st.write(f"{len(data)} rows ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â· {len(data.columns)} columns")
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
st.subheader("Dataset health")

duplicate_count = int(data.duplicated().sum())
missing_cells = int(data.isna().sum().sum())
missing_percent = round(
    missing_cells / (len(data) * len(data.columns)) * 100, 1
)

id_like_columns = [
    column for column in data.columns
    if any(word in str(column).lower() for word in ["id", "name", "record", "patient"])
]

col1, col2, col3 = st.columns(3)
col1.metric("Rows", f"{len(data):,}")
col2.metric("Missing cells", f"{missing_cells:,}", f"{missing_percent}% of cells")
col3.metric("Duplicate rows", f"{duplicate_count:,}")

if id_like_columns:
    st.warning(
        "These columns may identify people or records. Review them before training: "
        + ", ".join(map(str, id_like_columns))
    )
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
suggested_features = [
    column for column in available_features if column not in id_like_columns
]
feature_columns = st.multiselect(
    "Which columns should the model use as inputs?",
    options=available_features,
    default=suggested_features,
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
            save_model_bundle(results)
        st.success("Model saved to models/medimind_model.joblib")

        st.session_state["trained_pipeline"] = results["pipeline"]
        st.session_state["trained_features"] = results["feature_columns"]
        st.session_state["trained_target"] = results["target_column"]
        st.session_state["trained_task"] = results["task"]
        st.session_state["trained_target_labels"] = results["target_labels"]
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
                f"Accuracy: {metrics['cv_accuracy_mean']} ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â± {metrics['cv_accuracy_std']}"
            )
            st.write(
                f"Weighted F1: {metrics['cv_f1_mean']} ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â± {metrics['cv_f1_std']}"
            )
        else:
            st.subheader("3-fold cross-validation")
            st.write(f"MAE: {metrics['cv_mae_mean']} ÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â± {metrics['cv_mae_std']}")

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
            st.metric("RÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â² score", metrics["r2"])
            st.write("RÃƒÆ’Ã†â€™ÃƒÂ¢Ã¢â€šÂ¬Ã…Â¡ÃƒÆ’Ã¢â‚¬Å¡Ãƒâ€šÃ‚Â² compares the model with predicting the average target value.")

        st.info(
            "These scores use one train/test split. They are a starting estimate, "
            "not proof that a model will work well on new data."
        )
        if results.get("feature_importance"):
            st.subheader("Most influential features")
            st.caption(
                "These show which inputs influenced this model most. "
                "They do not prove cause or medical importance."
            )
            st.dataframe(
                pd.DataFrame(results["feature_importance"]),
                width="stretch",
            )
        report = {
            "task": results["task"],
            "target_column": results["target_column"],
            "rows_used": results["rows_used"],
            "feature_columns": results["feature_columns"],
            "metrics": results["metrics"],
        }
        report_text = json.dumps(report, indent=2, default=str)
        st.download_button(
            "Download results report (JSON)",
            data=report_text,
            file_name="medimind_results_report.json",
            mime="application/json",
        )
    except Exception as error:
        st.error(f"Model training failed. Details: {error}")
    finally:
        Path(temp_path).unlink(missing_ok=True)






if st.button("Load saved model"):
    try:
        bundle = load_model_bundle()
        if bundle is None:
            st.warning("No saved model found yet. Train a model first.")
        else:
            st.session_state["trained_pipeline"] = bundle["pipeline"]
            st.session_state["trained_features"] = bundle["feature_columns"]
            st.session_state["trained_target"] = bundle["target_column"]
            st.session_state["trained_task"] = bundle["task"]
            st.session_state["trained_target_labels"] = bundle["target_labels"]
            st.success("Saved model loaded. You can now upload a new CSV for predictions.")
    except Exception as error:
        st.error(f"Could not load the saved model: {error}")


if "trained_pipeline" in st.session_state:
    st.divider()
    st.subheader("Predict on a new CSV")
    st.write("Upload a CSV containing the same input columns used to train this model.")
    new_file = st.file_uploader(
        "Upload new, unlabeled rows",
        type=["csv"],
        key="new_prediction_file",
    )

    if new_file is not None:
        try:
            new_data = pd.read_csv(new_file)
            required_columns = st.session_state["trained_features"]
            missing_columns = [
                column for column in required_columns if column not in new_data.columns
            ]

            if missing_columns:
                st.error(f"This file is missing required input columns: {missing_columns}")
            elif new_data.empty:
                st.error("The uploaded CSV has no rows.")
            else:
                st.dataframe(new_data.head(10), width="stretch")

                if st.button("Predict these rows", key="predict_new_rows"):
                    pipeline = st.session_state["trained_pipeline"]
                    task = st.session_state["trained_task"]
                    predicted_values = pipeline.predict(new_data[required_columns])

                    if task == "classification":
                        labels = st.session_state["trained_target_labels"]
                        predicted_values = [
                            labels[int(value)] for value in predicted_values
                        ]

                    output_data = new_data.copy()
                    output_data[
                        "predicted_" + st.session_state["trained_target"]
                    ] = predicted_values

                    if task == "classification" and hasattr(pipeline, "predict_proba"):
                        confidence = pipeline.predict_proba(
                            new_data[required_columns]
                        ).max(axis=1)
                        output_data["model_confidence"] = confidence.round(3)
                        st.caption(
                            "Model confidence is the highest predicted class probability. "
                            "It is not a guarantee of correctness."
                        )
                    st.subheader("Predictions")
                    st.dataframe(output_data, width="stretch")
                    st.download_button(
                        "Download new predictions",
                        data=output_data.to_csv(index=False).encode("utf-8"),
                        file_name="medimind_new_predictions.csv",
                        mime="text/csv",
                        key="download_new_predictions",
                    )
        except Exception as error:
            st.error(f"Could not read or predict this CSV. Details: {error}")
            



    

        

            
