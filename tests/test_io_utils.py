"""
Tests for io_utils module.
"""
import pytest
import pandas as pd
from src.io_utils import validate_align


def test_validate_align_perfect():
    """Test validate_align with perfect sample alignment."""
    meta = pd.DataFrame({"sample_id": ["S1", "S2", "S3"]})
    matrix = pd.DataFrame(
        {"compound_id": ["C1", "C2"], "S1": [1, 2], "S2": [3, 4], "S3": [5, 6]}
    )
    # Should not raise
    validate_align(meta, matrix, sample_col="sample_id")


def test_validate_align_partial():
    """Test validate_align with partial overlap."""
    meta = pd.DataFrame({"sample_id": ["S1", "S2", "S3", "S4"]})
    matrix = pd.DataFrame(
        {"compound_id": ["C1", "C2"], "S1": [1, 2], "S2": [3, 4]}
    )
    # Should log warning but not raise
    validate_align(meta, matrix, sample_col="sample_id")


def test_validate_align_missing_col():
    """Test validate_align with missing sample_id column."""
    meta = pd.DataFrame({"patient_id": ["P1", "P2"]})
    matrix = pd.DataFrame({"compound_id": ["C1"], "P1": [1], "P2": [2]})
    # Should log warning and return without error
    validate_align(meta, matrix, sample_col="sample_id")
