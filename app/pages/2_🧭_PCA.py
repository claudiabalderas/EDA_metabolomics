# app/pages/2_🧭_PCA.py
import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.decomposition import PCA

# --- Dependencia del proyecto ---
import cimcb_lite as cb  # requiere scipy<=1.11.4 o el shim numpy.interp según tu entorno

st.set_page_config(page_title="PCA", page_icon="🧭", layout="wide")

# ===============================
# 1) CONFIG & CARGA DE DATOS
# ===============================
DEFAULT_XLSX = r"C:\Users\Momentum\Desktop\Claudia\Cursos\Bootcamp_Data_e_IA\Proyecto_EDA\study_data.xlsx"

st.header("🧭 PCA — Metabolomics")

xlsx_path = st.text_input("Ruta del archivo Excel (study_data.xlsx):", DEFAULT_XLSX)
if not os.path.exists(xlsx_path):
    st.error(f"No se encuentra el archivo: {xlsx_path}")
    st.stop()

@st.cache_data(show_spinner=False)
def load_sheets(path):
    sample_metadata = pd.read_excel(path, sheet_name="sample_metadata")
    data_matrix     = pd.read_excel(path, sheet_name="data_matrix")
    data_dictionary = pd.read_excel(path, sheet_name="data_dictionary")
    return sample_metadata, data_matrix, data_dictionary

sample_metadata, data_matrix, data_dictionary = load_sheets(xlsx_path)

# ===============================
# 2) CONSTRUIR hoja2 (como en tu notebook)
#    - data_matrix_pca -> transpose -> dataTable
#    - añadir Idx, Class, SampleID en primeras n filas
# ===============================
@st.cache_data(show_spinner=False)
def build_hoja2(sample_metadata: pd.DataFrame, data_matrix: pd.DataFrame):
    # Copia y añade Idx al data_matrix (como en tu notebook)
    data_matrix_pca = data_matrix.copy()
    data_matrix_pca["Idx"] = range(1, len(data_matrix_pca) + 1)

    # Transponer a "matrix" y volver a DataFrame
    matrix = data_matrix_pca.transpose()

    # Añadir Idx secuencial a la matriz transpuesta
    rn1 = range(1, len(matrix) + 1)
    dataTable = matrix.assign(Idx=list(rn1))

    # Crear columnas Class y SampleID en las primeras n filas (n = número de muestras)
    n_samples = len(sample_metadata)
    sample_rows = dataTable.iloc[:n_samples].copy()

    # Asegúrate de que existen las columnas en sample_metadata
    # En tu notebook usas 'Health' para clase y 'sample_id' para IDs
    if "Health" not in sample_metadata.columns or "sample_id" not in sample_metadata.columns:
        raise ValueError("El sample_metadata debe contener columnas 'Health' y 'sample_id'.")

    # Asignar
    sample_rows = sample_rows.assign(
        Class    = list(sample_metadata["Health"]),
        SampleID = list(sample_metadata["sample_id"])
    )
    # Reconstruir dataTable
    hoja2 = pd.concat([sample_rows, dataTable.iloc[n_samples:]], axis=0)
    hoja2 = hoja2.reset_index(drop=True)

    return hoja2

hoja2 = build_hoja2(sample_metadata, data_matrix)

# ===============================
# 3) CONSTRUIR hoja3 (como en tu notebook)
#    - Idx = rango
#    - renombrar compound_id->Name, BIOCHEMICAL->Label
# ===============================
@st.cache_data(show_spinner=False)
def build_hoja3(data_dictionary: pd.DataFrame):
    hoja3 = data_dictionary.copy()
    hoja3 = hoja3.reset_index(drop=True)
    hoja3["Idx"] = range(1, len(hoja3) + 1)
    if "compound_id" in hoja3.columns:
        hoja3 = hoja3.rename(columns={"compound_id": "Name"})
    if "BIOCHEMICAL" in hoja3.columns:
        hoja3 = hoja3.rename(columns={"BIOCHEMICAL": "Label"})
    return hoja3

hoja3 = build_hoja3(data_dictionary)

# ===============================
# 4) ARREGLO DE CABECERAS EN hoja2
#    - Promociona primera fila a cabecera si columnas numeradas (0..N)
#    - Preserva Idx, Class, SampleID
#    - Convierte features (compound_####) a numérico
#    - Alinea con hoja3['Name']
# ===============================
def _norm(s: str) -> str:
    return str(s).strip().lower().replace(" ", "_").replace("-", "_")

@st.cache_data(show_spinner=False)
def clean_and_match(hoja2_in: pd.DataFrame, hoja3_in: pd.DataFrame):
    h2 = hoja2_in.copy()

    # Reordenar para dejar meta al final (sin perder columnas)
    meta_cols = [c for c in ["Idx", "Class", "SampleID"] if c in h2.columns]
    other_cols = [c for c in h2.columns if c not in meta_cols]
    h2 = h2[other_cols + meta_cols]

    # Detecta columnas numeradas y renómbralas usando la primera fila como cabecera si aplica
    num_like_cols = [
        c for c in h2.columns
        if isinstance(c, (int, np.integer)) or (isinstance(c, str) and c.isdigit())
    ]
    if num_like_cols:
        header_row = h2.loc[h2.index[0], num_like_cols].astype(str)
        # ¿Se parecen a 'compound_####' o 'compound_id'?
        mask_names = header_row.str.fullmatch(r"(compound_\d+|compound_id)", case=False)
        if mask_names.mean() > 0.8:
            rename_map = dict(zip(num_like_cols, header_row))
            h2 = h2.rename(columns=rename_map)
            # Si esa fila era textual, elimínala
            is_header = pd.to_numeric(h2.loc[h2.index[0], list(rename_map.values())], errors="coerce").isna().any()
            if is_header:
                h2 = h2.iloc[1:].reset_index(drop=True)

    # Normaliza ID si viene como compound_id
    if "compound_id" in h2.columns and "SampleID" not in h2.columns:
        h2 = h2.rename(columns={"compound_id": "SampleID"})

    # Limpia filas sin SampleID
    if "SampleID" in h2.columns:
        h2 = h2[h2["SampleID"].notna()].reset_index(drop=True)

    # Features = columnas que empiezan por 'compound_'
    meta_cols = [c for c in ["Idx", "Class", "SampleID"] if c in h2.columns]
    feature_cols = [c for c in h2.columns if isinstance(c, str) and c.startswith("compound_") and c not in meta_cols]
    # A numérico solo features
    if feature_cols:
        h2[feature_cols] = h2[feature_cols].apply(pd.to_numeric, errors="coerce")

    # Alinear con hoja3['Name']
    if "Name" not in hoja3_in.columns:
        raise ValueError("La hoja3 debe tener una columna 'Name' con los compound_id.")

    peaklist_raw = hoja3_in["Name"].dropna().astype(str).tolist()
    presentes = [c for c in peaklist_raw if c in h2.columns]
    if not presentes:
        col_map = {_norm(c): c for c in feature_cols}
        presentes = [col_map[_norm(p)] for p in peaklist_raw if _norm(p) in col_map]

    return h2, presentes, peaklist_raw

hoja2, presentes, peaklist_raw = clean_and_match(hoja2, hoja3)
st.caption(f"Emparejadas (hoja2 vs hoja3['Name']): {len(presentes)} / {len(peaklist_raw)}")

# ===============================
# 5) UI: método de escalado y filtro de clases
# ===============================
ALLOWED = {"auto", "pareto", "vast", "level", "range"}
ALIASES = {
    "autoscale": "auto", "zscore": "auto", "z-score": "auto", "standard": "auto",
    "paretto": "pareto", "pareto scaling": "pareto",
    "vast scaling": "vast", "level scaling": "level", "range scaling": "range",
    "none": "auto", "": "auto", None: "auto",
}

def sanitize_scale_method(value):
    key = "auto" if value is None else str(value).strip().lower()
    key = ALIASES.get(key, key)
    return key if key in ALLOWED else "auto"

col1, col2 = st.columns(2)
with col1:
    options = {
        "Auto (z-score)": "auto",
        "Pareto": "pareto",
        "VAST": "vast",
        "Level": "level",
        "Range": "range",
    }
    choice = st.selectbox("Scaling method", list(options.keys()))
    scale_method = sanitize_scale_method(options[choice])
with col2:
    filter_two = st.checkbox("Mostrar PCA solo para Healthy vs diabetic", value=False)

# ===============================
# 6) PCA PIPELINE (log10 seguro + scale + KNN + PCA Plotly)
# ===============================
def pca_pipeline(df: pd.DataFrame, feat_cols: list, class_col: str = "Class", method: str = "auto"):
    if not feat_cols:
        st.error("No hay columnas de features para PCA.")
        st.stop()

    X = df[feat_cols].to_numpy()

    # Log10 seguro
    pos_mask = (X > 0)
    minpos = np.nanmin(X[pos_mask]) if np.any(pos_mask) else 1e-6
    X = np.where(~pos_mask | np.isnan(X), minpos * 0.5, X)
    Xlog = np.log10(X)

    # Escalado con cimcb_lite (sanitizado)
    method = sanitize_scale_method(method)
    try:
        Xscale = cb.utils.scale(Xlog, method=method)
    except ValueError:
        st.info(f"Método '{method}' no válido para cimcb_lite. Se usa 'auto'.")
        Xscale = cb.utils.scale(Xlog, method="auto")
        method = "auto"

    # Imputación kNN
    Xknn = cb.utils.knnimpute(Xscale, k=3)
    st.write(f"Xknn: {Xknn.shape[0]} filas × {Xknn.shape[1]} variables | método: **{method}**")

    # PCA con scikit-learn (para graficar estable en Streamlit)
    pca = PCA(n_components=2, random_state=42)
    scores = pca.fit_transform(Xknn)
    var_exp = pca.explained_variance_ratio_

    # DataFrame de scores
    if class_col in df.columns:
        classes = df[class_col].astype(str).values
    else:
        classes = np.array(["NA"] * len(df))

    sample_ids = df["SampleID"].astype(str).values if "SampleID" in df.columns else np.arange(len(df)).astype(str)

    df_scores = pd.DataFrame({
        "PC1": scores[:, 0],
        "PC2": scores[:, 1],
        "Class": classes,
        "SampleID": sample_ids
    })

    title = f"PCA — PC1 {var_exp[0]:.1%} | PC2 {var_exp[1]:.1%}"
    fig = px.scatter(
        df_scores, x="PC1", y="PC2", color="Class",
        hover_data=["SampleID"], title=title
    )
    st.plotly_chart(fig, use_container_width=True)

    return Xknn, var_exp, df_scores

# --- PCA (todos los grupos)
st.subheader("PCA — Todos los grupos")
Xknn_all, var_all, scores_all = pca_pipeline(hoja2, presentes, class_col="Class", method=scale_method)

# --- PCA filtrado (Healthy vs diabetic)
if filter_two:
    st.subheader("PCA — Healthy vs diabetic")
    if "Class" in hoja2.columns:
        filt = hoja2["Class"].isin(["Healthy", "diabetic"])
        df_two = hoja2.loc[filt].copy()
        common_feats = [c for c in presentes if c in df_two.columns]
        if len(df_two) > 0 and common_feats:
            Xknn_two, var_two, scores_two = pca_pipeline(df_two, common_feats, class_col="Class", method=scale_method)
        else:
            st.warning("No hay datos suficientes tras el filtro.")
    else:
        st.warning("No existe la columna 'Class' para filtrar grupos.")
