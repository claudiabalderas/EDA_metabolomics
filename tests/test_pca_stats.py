"""
Tests for PCA and stats utilities.
"""
import pytest
import pandas as pd
import numpy as np
from src.pca_utils import run_pca_cimcb
from src.stats_utils import univariate_2class_wrapper


def test_run_pca_cimcb_no_crash():
    """Test that PCA function doesn't crash with synthetic data."""
    Xknn = np.random.randn(20, 50)
    group_label = pd.Series(["A"] * 10 + ["B"] * 10)

    # Should not raise
    try:
        run_pca_cimcb(Xknn, group_label, pcx=1, pcy=2)
    except Exception as e:
        pytest.fail(f"PCA function raised exception: {e}")


def test_univariate_2class_synthetic():
    """Test univariate_2class_wrapper with synthetic data."""
    # Synthetic hoja2
    hoja2 = pd.DataFrame(
        {
            "Idx": range(1, 21),
            "Class": ["Healthy"] * 10 + ["Diabetes"] * 10,
            "SampleID": [f"S{i}" for i in range(1, 21)],
            "compound_001": np.random.rand(20),
            "compound_002": np.random.rand(20),
            "compound_003": np.random.rand(20),
        }
    )

    # Synthetic hoja3
    hoja3 = pd.DataFrame(
        {
            "Idx": [1, 2, 3],
            "Name": ["compound_001", "compound_002", "compound_003"],
            "Label": ["Glucose", "Lactate", "Pyruvate"],
        }
    )

    stats_full, stats_filt = univariate_2class_wrapper(
        hoja2,
        hoja3,
        group_col="Class",
        posclass="Diabetes",
        parametric=True,
        pvalue_threshold=0.05,
    )

    assert isinstance(stats_full, pd.DataFrame), "Expected DataFrame"
    assert isinstance(stats_filt, pd.DataFrame), "Expected filtered DataFrame"
