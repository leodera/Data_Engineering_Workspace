# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: Python (Jupyter_env)
#     language: python
#     name: jupyter_env
# ---

# %% editable=true deletable=true slideshow={"slide_type": ""}
# %%writefile data_cleaner.py
import os
import re
import numpy as np
import pandas as pd

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cleaned_cols = []
    for col in df.columns:
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", str(col))
        col_snake = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
        col_clean = re.sub(r"[^\w\s]", "", col_snake)
        col_clean = re.sub(r"[\s_]+", "_", col_clean).strip("_")
        cleaned_cols.append(col_clean)
    df.columns = cleaned_cols
    return df

def handle_missing_values(
    df: pd.DataFrame,
    column_strategies: dict = None,
    default_num_strategy: str = "median",
    default_cat_strategy: str = "N/A",
    drop_threshold: float = 0.5,
) -> pd.DataFrame:
    """
    Handles missing data using column-specific strategies or default fallbacks.
    
    column_strategies example:
    {
        "age": "median",
        "salary": "mean",
        "department": "mode",
        "status": "Inactive",
        "score": 0
    }
    """
    df = df.copy()

    # Drop columns exceeding missing threshold
    null_percentages = df.isnull().mean()
    cols_to_drop = null_percentages[null_percentages > drop_threshold].index
    if len(cols_to_drop) > 0:
        df = df.drop(columns=cols_to_drop)

    column_strategies = column_strategies or {}

    for col in df.columns:
        if df[col].isnull().sum() == 0:
            continue

        # Check if column has a custom rule specified
        if col in column_strategies:
            strategy = column_strategies[col]

            if strategy == "mean":
                df[col] = df[col].fillna(df[col].mean())
            elif strategy == "median":
                df[col] = df[col].fillna(df[col].median())
            elif strategy == "mode":
                mode_val = df[col].mode()
                if not mode_val.empty:
                    df[col] = df[col].fillna(mode_val[0])
            else:
                # Direct replacement value (e.g., 'Unknown', -1, 0, 'N/A')
                df[col] = df[col].fillna(strategy)

        # Fallback to default behavior if column not in dictionary
        else:
            if np.issubdtype(df[col].dtype, np.number):
                if default_num_strategy == "median":
                    df[col] = df[col].fillna(df[col].median())
                elif default_num_strategy == "mean":
                    df[col] = df[col].fillna(df[col].mean())
            else:
                if default_cat_strategy == "mode":
                    mode_val = df[col].mode()
                    if not mode_val.empty:
                        df[col] = df[col].fillna(mode_val[0])
                else:
                    df[col] = df[col].fillna(default_cat_strategy)

    return df

def auto_cast_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()
            if any(term in col for term in ["date", "time", "timestamp", "created", "at"]):
                try:
                    df[col] = pd.to_datetime(df[col], format="mixed")
                except Exception:
                    pass
            else:
                try:
                    converted = pd.to_numeric(df[col], errors="coerce")
                    if converted.notnull().sum() / max(len(df[col].dropna()), 1) > 0.8:
                        df[col] = converted
                except Exception:
                    pass
    return df

def remove_duplicates(df: pd.DataFrame, subset: list = None) -> pd.DataFrame:
    df = df.copy()
    initial_count = len(df)
    df = df.drop_duplicates(subset=subset, keep="first")
    removed = initial_count - len(df)
    if removed > 0:
        print(f"[INFO] Removed {removed} duplicate rows.")
    return df

def remove_outliers_iqr(df: pd.DataFrame, columns: list = None, factor: float = 1.5) -> pd.DataFrame:
    df = df.copy()
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - (factor * IQR)
        upper_bound = Q3 + (factor * IQR)
        df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
    return df

def run_pipeline(
    df: pd.DataFrame,
    id_column: str = None,
    column_strategies: dict = None,
    default_num_strategy: str = "median",
    default_cat_strategy: str = "N/A",
    clean_outliers: bool = False,
    outlier_cols: list = None,
) -> pd.DataFrame:
    print("--- Starting Data Cleaning Pipeline ---")
    print(f"Initial Shape: {df.shape}")
    df = clean_column_names(df)
    if id_column:
        id_column = re.sub(r"[^\w\s]", "", re.sub(r"[\s_]+", "_", id_column)).lower()
    df = auto_cast_types(df)
    df = remove_duplicates(df, subset=[id_column] if id_column in df.columns else None)
    df = handle_missing_values(
        df,
        column_strategies=column_strategies,
        default_num_strategy=default_num_strategy,
        default_cat_strategy=default_cat_strategy,
        drop_threshold=0.5,
    )
    if clean_outliers:
        df = remove_outliers_iqr(df, columns=outlier_cols)
    print(f"Final Shape: {df.shape}")
    print("--- Pipeline Execution Complete ---")
    return df

# %% [markdown] editable=true deletable=true slideshow={"slide_type": ""}
# # Data Cleaning Pipeline: Notebook Usage Example
#
# Import `run_pipeline` from `data_cleaner.py` and pass a custom imputation rule dictionary to handle missing values on a per-column basis:
#
# ```python
# import pandas as pd
# from data_cleaner import run_pipeline
#
# # 1. Load raw dataset
# df_raw = pd.read_csv("banking_synthetic_data.csv")
#
# # 2. Define column-specific imputation rules
# # Note: Ensure key names match the snake_case formatted headers
# imputation_rules = {
#     "age": "median",              # Replaces missing age values with median
#     "balance": "mean",            # Replaces missing balances with mean
#     "employment_status": "mode",  # Replaces missing text with the most frequent value
#     "credit_score": 600,          # Replaces missing credit score with exact constant 600
#     "city": "Unknown"             # Replaces missing city text with 'Unknown'
# }
#
# # 3. Execute pipeline
# df_cleaned = run_pipeline(
#     df=df_raw,
#     id_column="customer_id",
#     column_strategies=imputation_rules,
#     default_num_strategy="median",
#     default_cat_strategy="N/A",
#     clean_outliers=True
# )
#
# # 4. Verify output
# df_cleaned.head()

# %%
