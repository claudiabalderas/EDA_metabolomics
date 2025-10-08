"""
Streamlit page: Basic EDA (sample distributions, BMI–HbA1c relationships).
"""
import streamlit as st
import sys, os
from pathlib import Path

# --- Import paths so src/* sea importable desde /app/pages/*
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.config import get_config, get_paths
from src.io_utils import load_excel
from src.labels import normalize_health_status, normalize_sex
from src.viz import (
    plot_group_counts_bar,
    plot_group_counts_donut,
    scatter_bmi_hba1c,
    bars_bmi_hba1c_plotly,
    sex_by_group_catplot,
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="EDA Básico", page_icon="📊", layout="wide")

# ---- Load config ----
config = get_config()
paths = get_paths(config)

# ---- Helpers de ruta ----
def project_root_from_this_file() -> Path:
    # app/pages/XX.py -> raíz del proyecto = tres niveles arriba
    return Path(__file__).resolve().parents[2]

def resolve_data_path(rel_or_abs: str) -> Path:
    p = Path(rel_or_abs)
    if p.is_absolute():
        return p
    root = project_root_from_this_file()
    cand = (root / p).resolve()
    if cand.exists():
        return cand
    # fallback: relativo al cwd
    return (Path.cwd() / p).resolve()

@st.cache_data(show_spinner=False)
def load_data_safely():
    file_path = resolve_data_path(paths["data_path"])
    meta_sheet = paths["meta_sheet"]
    matrix_sheet = paths["matrix_sheet"]
    dict_sheet = paths["dict_sheet"]

    diag = {
        "cwd": str(Path.cwd()),
        "project_root": str(project_root_from_this_file()),
        "configured_data_path": paths["data_path"],
        "resolved_data_path": str(file_path),
        "exists": file_path.exists(),
    }

    if not file_path.exists():
        return None, None, None, diag

    meta, matrix, data_dict = load_excel(file_path, meta_sheet, matrix_sheet, dict_sheet)
    meta = normalize_health_status(meta, col="HEALTH_STATUS")
    meta = normalize_sex(meta, col="sex")
    return meta, matrix, data_dict, diag

# ---- Main ----
st.title("📊 Exploratory Data Analysis - Basics")

meta, matrix, data_dict, path_info = load_data_safely()

with st.expander("🔎 Diagnóstico de rutas"):
    st.json(path_info)

# Si falta el Excel, ofrece soluciones y subida
if meta is None:
    st.error(
        "No se encontró el archivo Excel configurado.\n\n"
        f"Busqué: **{path_info['resolved_data_path']}**\n\n"
        "Soluciones:\n"
        "1) Copia tu Excel a esa ruta, o\n"
        "2) Ajusta `paths.data_path` en `config.yaml` a una ruta válida, o\n"
        "3) Súbelo aquí abajo y lo guardo en `data/study_data.xlsx`."
    )

    up = st.file_uploader("Sube tu Excel (study_data.xlsx)", type=["xlsx", "xls"])
    if up is not None:
        target = project_root_from_this_file() / "data" / "study_data.xlsx"
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "wb") as f:
            f.write(up.read())
        st.success(f"✅ Guardado en: {target}")
        st.cache_data.clear()
        st.rerun()
    st.stop()

# ---- Contenido EDA ----
st.header("1. Sample Group Distribution")
st.markdown("Distribution of samples by **HEALTH_STATUS**.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Bar Chart")
    fig_bar = plot_group_counts_bar(meta, col="HEALTH_STATUS")
    st.pyplot(fig_bar)

with col2:
    st.subheader("Donut Chart")
    fig_donut = plot_group_counts_donut(meta, col="HEALTH_STATUS")
    st.pyplot(fig_donut)

st.markdown("---")

# ---- BMI vs HbA1c ----
st.header("2. BMI vs HbA1c Relationship")

st.subheader("2.1 Scatter Plot (by Health Status)")
fig_scatter_health = scatter_bmi_hba1c(meta, hue_col="HEALTH_STATUS", figsize=(12, 6))
st.pyplot(fig_scatter_health)

st.subheader("2.2 Scatter Plot (by Sex)")
fig_scatter_sex = scatter_bmi_hba1c(meta, hue_col="sex", figsize=(12, 6))
st.pyplot(fig_scatter_sex)

st.markdown("---")

st.subheader("2.3 Grouped Bar Chart (Plotly)")
fig_bars = bars_bmi_hba1c_plotly(meta, group_col="HEALTH_STATUS")
st.plotly_chart(fig_bars, use_container_width=True)

st.markdown("---")

# ---- Sex by group ----
st.header("3. Sample Count by Sex and Health Status")
fig_catplot = sex_by_group_catplot(meta, col="HEALTH_STATUS")
st.pyplot(fig_catplot)

st.markdown("---")
st.success("✅ Basic EDA complete!")

# (Opcional) botón para limpiar caché desde la barra lateral
with st.sidebar:
    if st.button("🧹 Limpiar caché"):
        st.cache_data.clear()
        st.rerun()
