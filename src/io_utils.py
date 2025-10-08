"""
Data loading and validation utilities.
"""
import pandas as pd
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def load_excel(
    file_path: str, meta_sheet: str, matrix_sheet: str, dict_sheet: str
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load three sheets from Excel file.

    Parameters
    ----------
    file_path : str
        Path to Excel file.
    meta_sheet : str
        Name of metadata sheet.
    matrix_sheet : str
        Name of data matrix sheet.
    dict_sheet : str
        Name of data dictionary sheet.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        (sample_metadata, data_matrix, data_dictionary)
    """
    logger.info(f"Loading data from {file_path}")
    try:
        meta = pd.read_excel(file_path, sheet_name=meta_sheet)
        matrix = pd.read_excel(file_path, sheet_name=matrix_sheet)
        data_dict = pd.read_excel(file_path, sheet_name=dict_sheet)
        logger.info(
            f"Loaded: meta={meta.shape}, matrix={matrix.shape}, dict={data_dict.shape}"
        )
        return meta, matrix, data_dict
    except Exception as e:
        logger.error(f"Error loading Excel file: {e}")
        raise


def validate_align(
    meta: pd.DataFrame, data_matrix: pd.DataFrame, sample_col: str = "sample_id"
) -> None:
    """
    Validate that sample IDs align between metadata and data matrix.

    Parameters
    ----------
    meta : pd.DataFrame
        Sample metadata.
    data_matrix : pd.DataFrame
        Data matrix (samples as rows or columns).
    sample_col : str
        Column name for sample IDs in metadata.

    Raises
    ------
    ValueError
        If alignment is poor (<50% overlap).
    """
    if sample_col not in meta.columns:
        logger.warning(f"Sample column '{sample_col}' not found in metadata.")
        return

    meta_samples = set(meta[sample_col].dropna().astype(str))
    matrix_samples = set(data_matrix.columns.astype(str)) - {"compound_id"}

    overlap = meta_samples & matrix_samples
    pct = len(overlap) / max(len(meta_samples), 1) * 100

    logger.info(
        f"Sample alignment: {len(overlap)}/{len(meta_samples)} ({pct:.1f}%) matched."
    )

    if pct < 50:
        logger.warning(f"Low sample alignment: {pct:.1f}%")
