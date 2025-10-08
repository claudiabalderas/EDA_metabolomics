"""
Configuration loader for paths and parameters.
"""
import yaml
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


def get_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Parameters
    ----------
    config_path : str
        Path to config.yaml file.

    Returns
    -------
    Dict[str, Any]
        Configuration dictionary.
    """
    config_file = Path(config_path)
    if not config_file.exists():
        logger.warning(f"Config file {config_path} not found, using defaults.")
        return {
            "data": {
                "path": "data/study_data.xlsx",
                "sheets": {
                    "metadata": "sample_metadata",
                    "matrix": "data_matrix",
                    "dictionary": "data_dictionary",
                },
            },
            "preprocessing": {"scale_method": "auto", "knn_k": 3, "log_offset": 0.5},
            "pca": {"pcx": 1, "pcy": 2},
            "stats": {"parametric": True, "pvalue_threshold": 0.05},
        }

    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    logger.info(f"Configuration loaded from {config_path}")
    return config


def get_paths(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract data paths from configuration.

    Parameters
    ----------
    config : Dict[str, Any]
        Configuration dictionary.

    Returns
    -------
    Dict[str, str]
        Dictionary with keys: 'data_path', 'meta_sheet', 'matrix_sheet', 'dict_sheet'.
    """
    data_cfg = config.get("data", {})
    sheets = data_cfg.get("sheets", {})
    return {
        "data_path": data_cfg.get("path", "data/study_data.xlsx"),
        "meta_sheet": sheets.get("metadata", "sample_metadata"),
        "matrix_sheet": sheets.get("matrix", "data_matrix"),
        "dict_sheet": sheets.get("dictionary", "data_dictionary"),
    }
