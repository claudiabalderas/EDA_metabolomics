"""
Streamlit page: Data Dictionary (compound classes and pathways).
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.config import get_config, get_paths
from src.io_utils import load_excel
from src.viz import bar_super_pathway
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Data Dictionary", page_icon="📚", layout="wide")

# ---- Load config ----
config = get_config()
paths = get_paths(config)


@st.cache_data
def load_data():
    meta, matrix, data_dict = load_excel(
        paths["data_path"],
        paths["meta_sheet"],
        paths["matrix_sheet"],
        paths["dict_sheet"],
    )
    return meta, matrix, data_dict


# ---- Main ----
st.title("📚 Data Dictionary - Compound Classes")

meta, matrix, data_dict = load_data()

st.header("1. Compound Information")
st.markdown(
    f"""
    The **data dictionary** contains {len(data_dict)} compounds with:
    - **compound_id** (or Name)
    - **BIOCHEMICAL** (or Label)
    - **SUPER_PATHWAY** (biochemical class)
    - **SUB_PATHWAY** (sub-class)
    """
)

st.dataframe(data_dict.head(20))

st.markdown("---")

# ---- Super Pathway Bar Chart ----
st.header("2. Compound Count by Super Pathway")
fig_pathway = bar_super_pathway(data_dict, col="SUPER_PATHWAY")
st.plotly_chart(fig_pathway, use_container_width=True)

st.markdown("---")

# ---- Summary Stats ----
st.header("3. Summary Statistics")
pathway_counts = data_dict["SUPER_PATHWAY"].value_counts()
st.write("**Top 10 Super Pathways:**")
st.dataframe(pathway_counts.head(10))

st.markdown("---")
st.success("✅ Data dictionary exploration complete!")
