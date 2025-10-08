"""
Streamlit page: Univariate 2-class statistical analysis.
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.config import get_config, get_paths
from src.io_utils import load_excel
from src.labels import normalize_class_column
from src.preprocess import build_feature_matrix
from src.stats_utils import univariate_2class_wrapper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Univariate Stats", page_icon="🧪", layout="wide")

# ---- Load config ----
config = get_config()
paths = get_paths(config)
preproc_cfg = config.get("preprocessing", {})
stats_cfg = config.get("stats", {})


# ---- Helper: map friendly scale names to cimcb_lite accepted ones ----
def map_scale_method(value: str):
    """Map common or user-friendly scale names to the 5 valid ones for cimcb_lite."""
    if value is None:
        return "auto"

    alias = str(value).strip().lower()

    # Sin escalado
    none_aliases = {"none", "no", "sin", "off", "raw", "identity"}
    if alias in none_aliases:
        return None

    mapping = {
        # auto ~ estandarización
        "auto": "auto", "zscore": "auto", "z-score": "auto", "z score": "auto",
        "standard": "auto", "standardize": "auto", "std": "auto",
        "standardscaler": "auto",

        # pareto
        "pareto": "pareto",

        # vast
        "vast": "vast",

        # level
        "level": "level", "mean": "level", "normalize_by_mean": "level",

        # range (min–max)
        "range": "range", "minmax": "range", "min-max": "range",
        "min_max": "range", "0-1": "range", "0to1": "range",
    }

    if alias in mapping:
        return mapping[alias]

    logger.warning(
        f"Método de escalado no soportado '{value}'. "
        "Se usará 'auto' por defecto. "
        "Válidos: auto, pareto, vast, level, range, o none."
    )
    return "auto"


@st.cache_data
def load_data():
    meta, matrix, data_dict = load_excel(
        paths["data_path"],
        paths["meta_sheet"],
        paths["matrix_sheet"],
        paths["dict_sheet"],
    )
    return meta, matrix, data_dict


@st.cache_data
def preprocess_data(matrix, data_dict, meta):
    # Normaliza el método de escalado
    cfg_scale = preproc_cfg.get("scale_method", "auto")
    scale_method = map_scale_method(cfg_scale)

    hoja2, Xknn, peaklist = build_feature_matrix(
        matrix,
        data_dict,
        meta,
        scale_method=scale_method if scale_method is not None else None,
        knn_k=preproc_cfg.get("knn_k", 3),
        log_offset=preproc_cfg.get("log_offset", 0.5),
    )

    hoja2 = normalize_class_column(hoja2, col="Class")

    # Prepare hoja3
    hoja3 = data_dict.copy()
    hoja3["Idx"] = range(1, len(hoja3) + 1)
    hoja3 = hoja3.rename(
        columns={"compound_id": "Name", "BIOCHEMICAL": "Label"},
        errors="ignore",
    )
    return hoja2, hoja3


# ---- Main ----
st.title("🧪 Univariate 2-Class Statistical Analysis")

meta, matrix, data_dict = load_data()
hoja2, hoja3 = preprocess_data(matrix, data_dict, meta)

st.markdown(
    """
    This page performs **univariate 2-class tests** (t-test, Mann-Whitney, etc.)
    using `cimcb_lite.utils.univariate_2class`.

    We compare **Diabetes** vs **Healthy** (both directions) and filter
    significant metabolites (p ≤ 0.05, Sign=1).
    """
)
st.markdown("---")

# ---- Analysis 1: posclass = Diabetes ----
st.header("1. Positive Class = Diabetes")

with st.spinner("Running univariate test (Diabetes vs Healthy)..."):
    stats_full_d, stats_filt_d = univariate_2class_wrapper(
        hoja2,
        hoja3,
        group_col="Class",
        posclass="Diabetes",
        parametric=stats_cfg.get("parametric", True),
        pvalue_threshold=stats_cfg.get("pvalue_threshold", 0.05),
    )

st.subheader("1.1 Full Statistics Table")
st.dataframe(stats_full_d.head(20))

st.subheader("1.2 Significant Metabolites (p ≤ 0.05, Sign=1)")
if not stats_filt_d.empty:
    st.dataframe(stats_filt_d[["Name", "Label", "Sign", "TTestPvalue"]])
    st.write(f"**Total significant:** {len(stats_filt_d)}")
else:
    st.warning("No significant metabolites found.")

st.markdown("---")

# ---- Analysis 2: posclass = Healthy ----
st.header("2. Positive Class = Healthy")

with st.spinner("Running univariate test (Healthy vs Diabetes)..."):
    stats_full_h, stats_filt_h = univariate_2class_wrapper(
        hoja2,
        hoja3,
        group_col="Class",
        posclass="Healthy",
        parametric=stats_cfg.get("parametric", True),
        pvalue_threshold=stats_cfg.get("pvalue_threshold", 0.05),
    )

st.subheader("2.1 Full Statistics Table")
st.dataframe(stats_full_h.head(20))

st.subheader("2.2 Significant Metabolites (p ≤ 0.05, Sign=1)")
if not stats_filt_h.empty:
    st.dataframe(stats_filt_h[["Name", "Label", "Sign", "TTestPvalue"]])
    st.write(f"**Total significant:** {len(stats_filt_h)}")

    # Example: filter for glucose
    glucose_row = stats_filt_h[
        stats_filt_h["Label"].str.contains("glucose", case=False, na=False)
    ]
    if not glucose_row.empty:
        st.success("✅ Glucose found in significant metabolites!")
        st.dataframe(glucose_row[["Name", "Label", "Sign", "TTestPvalue"]])
else:
    st.warning("No significant metabolites found.")

st.markdown("---")
st.success("✅ Univariate analysis complete!")
