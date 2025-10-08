"""
Label normalization utilities.
"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def normalize_health_status(df: pd.DataFrame, col: str = "HEALTH_STATUS") -> pd.DataFrame:
    """
    Normalize health status labels: 'diabetic' → 'Diabetes', etc.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing health status column.
    col : str
        Column name for health status.

    Returns
    -------
    pd.DataFrame
        DataFrame with normalized labels.
    """
    df = df.copy()
    if col not in df.columns:
        logger.warning(f"Column {col} not found in DataFrame.")
        return df

    mapping = {
        "diabetic": "Diabetes",
        "Diabetic": "Diabetes",
        "healthy": "Healthy",
        "Healthy": "Healthy",
    }
    df[col] = df[col].map(lambda x: mapping.get(str(x).strip(), x))
    logger.info(f"Normalized {col}: {df[col].unique()}")
    return df


def normalize_sex(df: pd.DataFrame, col: str = "sex") -> pd.DataFrame:
    """
    Normalize sex labels: 'male'/'female' → 'M'/'F'.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing sex column.
    col : str
        Column name for sex.

    Returns
    -------
    pd.DataFrame
        DataFrame with normalized sex labels.
    """
    df = df.copy()
    if col not in df.columns:
        logger.warning(f"Column {col} not found in DataFrame.")
        return df

    mapping = {
        "male": "M",
        "Male": "M",
        "m": "M",
        "female": "F",
        "Female": "F",
        "f": "F",
    }
    df[col] = df[col].map(lambda x: mapping.get(str(x).strip().lower(), x))
    logger.info(f"Normalized {col}: {df[col].unique()}")
    return df


def normalize_class_column(df: pd.DataFrame, col: str = "Class") -> pd.DataFrame:
    """
    Normalize 'Class' column for PCA/stats: 'diabetic' → 'Diabetes', 'Healthy' stays.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing Class column.
    col : str
        Column name for class.

    Returns
    -------
    pd.DataFrame
        DataFrame with normalized class labels.
    """
    df = df.copy()
    if col not in df.columns:
        logger.warning(f"Column {col} not found in DataFrame.")
        return df

    mapping = {
        "diabetic": "Diabetes",
        "Diabetic": "Diabetes",
        "healthy": "Healthy",
        "Healthy": "Healthy",
    }
    df[col] = df[col].map(lambda x: mapping.get(str(x).strip(), x))
    logger.info(f"Normalized {col}: {df[col].unique()}")
    return df
