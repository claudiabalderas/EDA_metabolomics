"""
Streamlit Home page for Metabolomics EDA app.
"""
import streamlit as st
import sys
from pathlib import Path

# --- Project root & import path ---
APP_DIR = Path(__file__).resolve().parent            # .../Proyecto_EDA/app
PROJECT_ROOT = APP_DIR.parent                        # .../Proyecto_EDA
sys.path.insert(0, str(PROJECT_ROOT))               # permite importar src/*

from src.config import get_config, get_paths
from src.io_utils import load_excel, validate_align
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Metabolomics EDA - Home",
    page_icon="🧬",
    layout="wide",
)

# ---- Config ----
config = get_config()
paths = get_paths(config)

# ---- Helpers de ruta ----
def resolve_data_path(rel_or_abs: str) -> Path:
    """Devuelve una ruta absoluta válida probando primero contra la raíz del proyecto."""
    p = Path(rel_or_abs)
    if p.is_absolute():
        return p
    cand = (PROJECT_ROOT / p).resolve()
    if cand.exists():
        return cand
    # fallback: relativo al cwd si ejecutas desde raíz
    return (Path.cwd() / p).resolve()

# ---- Cached data loading ----
@st.cache_data(show_spinner=False)
def load_data_safely():
    file_path = resolve_data_path(paths["data_path"])
    meta_sheet = paths["meta_sheet"]
    matrix_sheet = paths["matrix_sheet"]
    dict_sheet = paths["dict_sheet"]

    diag = {
        "cwd": str(Path.cwd()),
        "project_root": str(PROJECT_ROOT),
        "configured_data_path": paths["data_path"],
        "resolved_data_path": str(file_path),
        "exists": file_path.exists(),
        "__file__": __file__,
    }

    if not file_path.exists():
        return None, None, None, diag

    meta, matrix, data_dict = load_excel(file_path, meta_sheet, matrix_sheet, dict_sheet)
    validate_align(meta, matrix, sample_col="sample_id")
    return meta, matrix, data_dict, diag

# ---- UI ----
st.title("🧬 Metabolomics Diabetes EDA")
st.markdown(
    """
    **Welcome to the Metabolomics Exploratory Data Analysis (EDA) application.**

    This multi-page Streamlit app provides a modular, reproducible analysis of metabolomics data
    related to diabetes, including:

    - **Sample metadata** (BMI, HbA1c, sex, health status)
    - **Metabolite intensity matrix** (~1486 compounds)
    - **Compound dictionary** (biochemical pathways, classes)

    ---

    ### 📊 Key Analyses

    1. **Basic EDA** — Sample distributions, demographic relationships (BMI vs HbA1c)
    2. **PCA** — Principal Component Analysis with preprocessing (log10, scaling, KNN imputation)
    3. **Univariate Stats** — 2-class statistical tests (Healthy vs Diabetic)
    4. **Compound Dictionary** — Biochemical pathway visualization

    ---

    ### 📂 Dataset

    - **Path:** `{}`
    - **Sheets:** `sample_metadata`, `data_matrix`, `data_dictionary`

    ---

    ### 🚀 Get Started

    Use the sidebar to navigate between pages.

    ---

    ### 📖 Documentation

    - **GitHub:** [CIMCB Metabolomics Tools](https://github.com/orgs/CIMCB/repositories)
    - **License:** MIT
    """.format(paths["data_path"])
)

with st.spinner("Loading data..."):
    meta, matrix, data_dict, diag = load_data_safely()

with st.expander("🔎 Path diagnostics"):
    st.json(diag)

if meta is None:
    st.error(
        "Excel file not found.\n\n"
        f"Searched at: **{diag['resolved_data_path']}**\n\n"
        "Fix it by either:\n"
        "1) Placing your file at that path, or\n"
        "2) Updating `paths.data_path` in `config.yaml`, or\n"
        "3) Uploading the Excel below (it will be saved to `data/study_data.xlsx`)."
    )
    up = st.file_uploader("Upload your Excel (study_data.xlsx)", type=["xlsx", "xls"])
    if up is not None:
        target = (PROJECT_ROOT / "data" / "study_data.xlsx").resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "wb") as f:
            f.write(up.read())
        st.success(f"✅ Saved to: {target}")
        st.cache_data.clear()
        st.rerun()
    st.stop()

st.success("✅ Data loaded successfully!")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Samples (Metadata)", meta.shape[0])
with col2:
    st.metric("Metabolites (Matrix)", matrix.shape[0])
with col3:
    st.metric("Compounds (Dictionary)", data_dict.shape[0])

st.markdown("---")
st.info("👈 Select a page from the sidebar to explore the analysis.")

# (Opcional) botón para limpiar caché
with st.sidebar:
    if st.button("🧹 Clear cache"):
        st.cache_data.clear()
        st.rerun()
