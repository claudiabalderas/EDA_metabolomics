"""
Preprocessing utilities for metabolomics data: transpose, log, scale, impute.
"""
import pandas as pd
import numpy as np
import logging
from typing import Tuple, List
import cimcb_lite as cb

logger = logging.getLogger(__name__)


def build_feature_matrix(
    data_matrix: pd.DataFrame,
    data_dict: pd.DataFrame,
    sample_metadata: pd.DataFrame,
    scale_method: str = "auto",
    knn_k: int = 3,
    log_offset: float = 0.5,
) -> Tuple[pd.DataFrame, np.ndarray, List[str]]:
    """
    Build preprocessed feature matrix (hoja2-style) for PCA/stats.

    Steps:
    1. Transpose data_matrix so samples are rows, compounds are columns.
    2. Add Idx, Class (from sample_metadata['Health']), SampleID.
    3. Rename data_dict columns: compound_id → Name, BIOCHEMICAL → Label.
    4. Extract peaklist from data_dict['Name'].
    5. Log10 transform (handle zeros), scale, KNN impute.

    Parameters
    ----------
    data_matrix : pd.DataFrame
        Raw metabolite matrix (samples as columns, compounds as rows).
    data_dict : pd.DataFrame
        Compound dictionary (compound_id, BIOCHEMICAL, SUPER_PATHWAY, etc.).
    sample_metadata : pd.DataFrame
        Sample metadata (sample_id, Health, sex, BMI, hba1c, etc.).
    scale_method : str
        Scaling method for cb.utils.scale ('auto', 'pareto', 'vast', 'level').
    knn_k : int
        Number of neighbors for KNN imputation.
    log_offset : float
        Offset multiplier for min positive value to handle zeros.

    Returns
    -------
    Tuple[pd.DataFrame, np.ndarray, List[str]]
        (hoja2_df, Xknn, peaklist)
        - hoja2_df: DataFrame with Idx, Class, SampleID, and compound columns.
        - Xknn: preprocessed numpy array (log10 + scaled + imputed).
        - peaklist: list of compound names aligned with columns.
    """
    logger.info("Building feature matrix (hoja2-style)...")

    # --- 1) Transpose data_matrix ---
    matrix_t = data_matrix.copy()
    # Assume first row is compound_id (or first column), samples are columns
    # We want samples as rows → transpose
    if "compound_id" in matrix_t.columns:
        matrix_t = matrix_t.set_index("compound_id").T
    else:
        # If compound_id is the first column name or index
        matrix_t = matrix_t.T

    # Add Idx
    matrix_t = matrix_t.reset_index(drop=False)
    matrix_t.columns.name = None
    matrix_t = matrix_t.rename(columns={matrix_t.columns[0]: "SampleID"})
    matrix_t["Idx"] = range(1, len(matrix_t) + 1)

    # --- 2) Add Class from sample_metadata['Health'] ---
    # Match SampleID with sample_metadata['sample_id']
    if "Health" in sample_metadata.columns and "sample_id" in sample_metadata.columns:
        health_map = dict(
            zip(sample_metadata["sample_id"], sample_metadata["Health"])
        )
        matrix_t["Class"] = matrix_t["SampleID"].map(health_map)
        logger.info(f"Mapped Class column: {matrix_t['Class'].unique()}")
    else:
        logger.warning("'Health' or 'sample_id' not found in sample_metadata.")
        matrix_t["Class"] = "Unknown"

    hoja2 = matrix_t.copy()

    # --- 3) Prepare hoja3 (data_dict) ---
    hoja3 = data_dict.copy()
    hoja3["Idx"] = range(1, len(hoja3) + 1)
    hoja3 = hoja3.rename(
        columns={"compound_id": "Name", "BIOCHEMICAL": "Label"}, errors="ignore"
    )

    # --- 4) Extract peaklist ---
    if "Name" not in hoja3.columns:
        logger.error("'Name' column not found in hoja3 (data_dict).")
        raise ValueError("Missing 'Name' column in data_dict.")

    peaklist_raw = hoja3["Name"].dropna().astype(str).tolist()

    # --- 5) Align hoja2 columns with peaklist ---
    meta_cols = [c for c in ["Idx", "Class", "SampleID"] if c in hoja2.columns]
    feature_cols = [c for c in hoja2.columns if c not in meta_cols]

    # Normalize column names for matching
    def _norm(s):
        return str(s).strip().lower().replace(" ", "_").replace("-", "_")

    col_map = {_norm(c): c for c in feature_cols}
    presentes = [
        col_map[_norm(p)] for p in peaklist_raw if _norm(p) in col_map
    ]

    if not presentes:
        logger.warning("No compound columns matched between hoja2 and hoja3.")
        presentes = feature_cols[:100]  # fallback: use first 100 numeric columns

    logger.info(f"Matched {len(presentes)}/{len(peaklist_raw)} compounds.")

    # --- 6) Extract X matrix ---
    X = hoja2[presentes].apply(pd.to_numeric, errors="coerce").to_numpy()

    # --- 7) Log10 transform (handle zeros/negatives/NaN) ---
    minpos = np.nanmin(X[X > 0]) if np.any(X > 0) else 1e-6
    X_safe = np.where((X <= 0) | np.isnan(X), minpos * log_offset, X)
    Xlog = np.log10(X_safe)

    # --- 8) Scale ---
    # Validate scale_method before passing to cimcb_lite
    ALLOWED_METHODS = {"auto", "pareto", "vast", "level", "range"}
    if scale_method not in ALLOWED_METHODS:
        logger.warning(
            f"Invalid scale_method '{scale_method}'. Falling back to 'auto'. "
            f"Valid options: {ALLOWED_METHODS}"
        )
        scale_method = "auto"

    Xscale = cb.utils.scale(Xlog, method=scale_method)
    logger.info(f"Scaled data with method='{scale_method}'")

    # --- 9) KNN impute ---
    Xknn = cb.utils.knnimpute(Xscale, k=knn_k)
    logger.info(f"KNN imputed with k={knn_k}. Shape: {Xknn.shape}")

    return hoja2, Xknn, presentes
