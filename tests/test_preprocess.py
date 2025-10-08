"""
Tests for preprocess module.
"""
import pytest
import pandas as pd
import numpy as np
from src.preprocess import build_feature_matrix


def test_build_feature_matrix_synthetic():
    """Test build_feature_matrix with synthetic data."""
    # Synthetic data_matrix (compounds as rows, samples as columns)
    matrix = pd.DataFrame(
        {
            "compound_id": ["compound_001", "compound_002", "compound_003"],
            "S1": [100, 200, 300],
            "S2": [150, 250, 350],
            "S3": [120, 220, 320],
        }
    )

    # Synthetic data_dict
    data_dict = pd.DataFrame(
        {
            "compound_id": ["compound_001", "compound_002", "compound_003"],
            "BIOCHEMICAL": ["Glucose", "Lactate", "Pyruvate"],
            "SUPER_PATHWAY": ["Carbohydrate", "Carbohydrate", "Carbohydrate"],
        }
    )

    # Synthetic sample_metadata
    meta = pd.DataFrame(
        {
            "sample_id": ["S1", "S2", "S3"],
            "Health": ["Healthy", "Diabetes", "Healthy"],
            "BMI": [22, 30, 25],
            "hba1c": [5.0, 7.5, 5.5],
        }
    )

    hoja2, Xknn, peaklist = build_feature_matrix(
        matrix, data_dict, meta, scale_method="auto", knn_k=3, log_offset=0.5
    )

    assert hoja2.shape[0] == 3, "Expected 3 samples"
    assert Xknn.shape[0] == 3, "Expected 3 samples in Xknn"
    assert Xknn.shape[1] > 0, "Expected at least one feature"
    assert not np.isnan(Xknn).any(), "Xknn should have no NaNs after imputation"
