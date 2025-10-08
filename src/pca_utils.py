"""
PCA utilities using cimcb_lite.
"""
import numpy as np
import pandas as pd
import logging
import cimcb_lite as cb

logger = logging.getLogger(__name__)


def run_pca_cimcb(
    Xknn: np.ndarray,
    group_label: pd.Series,
    pcx: int = 1,
    pcy: int = 2,
) -> None:
    """
    Run PCA using cimcb_lite and plot scores/loadings.

    Parameters
    ----------
    Xknn : np.ndarray
        Preprocessed feature matrix (samples × features).
    group_label : pd.Series
        Sample group labels for coloring (e.g., 'Class').
    pcx : int
        Principal component for x-axis.
    pcy : int
        Principal component for y-axis.

    Returns
    -------
    None
        Displays PCA plot via cb.plot.pca.
    """
    logger.info(f"Running PCA with pcx={pcx}, pcy={pcy}...")
    try:
        cb.plot.pca(Xknn, pcx=pcx, pcy=pcy, group_label=group_label)
        logger.info("PCA plot generated successfully.")
    except Exception as e:
        logger.error(f"PCA plotting failed: {e}")
        raise
