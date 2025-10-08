"""
Statistical analysis utilities for metabolomics.
"""
import pandas as pd
import logging
from typing import Tuple
import cimcb_lite as cb

logger = logging.getLogger(__name__)


def univariate_2class_wrapper(
    hoja2: pd.DataFrame,
    hoja3: pd.DataFrame,
    group_col: str = "Class",
    posclass: str = "Diabetes",
    parametric: bool = True,
    pvalue_threshold: float = 0.05,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Perform univariate 2-class statistical tests using cimcb_lite.

    Parameters
    ----------
    hoja2 : pd.DataFrame
        Feature matrix with 'Class' column and compound columns.
    hoja3 : pd.DataFrame
        Compound dictionary (Name, Label, Idx).
    group_col : str
        Column in hoja2 defining groups (e.g., 'Class').
    posclass : str
        Positive class for comparison ('Diabetes' or 'Healthy').
    parametric : bool
        Whether to use parametric tests.
    pvalue_threshold : float
        P-value threshold for filtering significant results.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        (full_stats_table, filtered_table)
        - full_stats_table: all statistical results.
        - filtered_table: filtered for p ≤ threshold and Sign=1.
    """
    logger.info(f"Running univariate 2-class test: posclass={posclass}...")

    # Filter hoja2 to include only relevant classes
    if posclass == "Diabetes":
        classes = ["diabetic", "Healthy", "Diabetes"]
    elif posclass == "Healthy":
        classes = ["Healthy", "diabetic", "Diabetes"]
    else:
        classes = [posclass]

    stat_hoja2 = hoja2[hoja2[group_col].isin(classes)].copy()

    # Normalize 'diabetic' → 'Diabetes'
    stat_hoja2[group_col] = stat_hoja2[group_col].replace(
        {"diabetic": "Diabetes"}
    )

    if stat_hoja2.empty:
        logger.warning(f"No samples found for classes {classes}.")
        return pd.DataFrame(), pd.DataFrame()

    try:
        stats_table = cb.utils.univariate_2class(
            stat_hoja2, hoja3, group=group_col, posclass=posclass, parametric=parametric
        )
    except Exception as e:
        logger.error(f"Univariate 2-class test failed: {e}")
        raise

    # Sort by TTestPvalue
    stats_table = stats_table.sort_values(by="TTestPvalue", ascending=True)

    # Filter: p ≤ threshold and Sign=1 (significantly higher in posclass)
    filtered = stats_table[
        (stats_table["TTestPvalue"] <= pvalue_threshold) & (stats_table["Sign"] == 1)
    ].copy()

    logger.info(
        f"Found {len(filtered)} significant metabolites (p≤{pvalue_threshold}, Sign=1)."
    )

    return stats_table, filtered
