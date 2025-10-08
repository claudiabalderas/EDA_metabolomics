🧬 Metabolomics Diabetes EDA

Modular, reproducible Streamlit application for exploratory data analysis (EDA) of metabolomics data related to diabetes.

Includes robust path handling, dynamic data upload, and modular pages for PCA, univariate statistics, and dictionary visualization.
---

## 📂 Project Structure

```
Proyecto_EDA/
├─ app/
│  ├─ Home.py                      # Streamlit home page (robust path + upload handling)
│  ├─ pages/
│  │  ├─ 1_📊_EDA_basico.py        # Basic EDA (distributions, BMI–HbA1c)
│  │  ├─ 2_🧭_PCA.py               # Principal Component Analysis
│  │  ├─ 3_🧪_Univariante.py       # Univariate 2-class statistical tests
│  │  └─ 4_📚_Diccionario.py       # Data dictionary exploration
├─ src/
│  ├─ config.py                    # Configuration loader (YAML)
│  ├─ io_utils.py                  # Data loading, path resolution, validation
│  ├─ labels.py                    # Label normalization (sex, HEALTH_STATUS)
│  ├─ preprocess.py                # Preprocessing (log10, scale, KNN)
│  ├─ pca_utils.py                 # PCA wrapper (cimcb_lite)
│  ├─ stats_utils.py               # Univariate statistics wrappers
│  └─ viz.py                       # Visualization utilities (Matplotlib, Seaborn, Plotly)
├─ config/
│  └─ config.yaml                  # Configuration file (paths, preprocessing, PCA, stats)
├─ data/
│  └─ study_data.xlsx              # Default metabolomics dataset (3 sheets)
├─ tests/
│  ├─ test_io_utils.py             # Tests for I/O and validation
│  ├─ test_preprocess.py           # Tests for preprocessing
│  └─ test_pca_stats.py            # Tests for PCA & univariate stats
├─ requirements.txt                # Python dependencies
└─ README.md                       # This file
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Ensure your data is in place
Expected structure:
```
Proyecto_EDA/
└─ data/
   └─ study_data.xlsx
```

The file `study_data.xlsx` should contain three sheets:
- `sample_metadata` — clinical metadata (BMI, HbA1c, sex, HEALTH_STATUS)
- `data_matrix` — metabolite intensities (~1486 compounds)
- `data_dictionary` — compound information (SUPER_PATHWAY, BIOCHEMICAL)

### 3. Run the Streamlit app

```bash
streamlit run app/Home.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 📊 Features

### 1. **Basic EDA** (`1_📊_EDA_basico.py`)
- Sample distribution by health status (bar + donut charts)
- BMI vs HbA1c scatter plots (by health status & sex)
- Grouped bar charts (Plotly) comparing BMI and HbA1c
- Sample count catplot (sex × HEALTH_STATUS)

### 2. **PCA** (`2_🧭_PCA.py`)
- Preprocessing pipeline:
  - Transpose data matrix (samples as rows)
  - Log10 transform (handle zeros)
  - Scaling (`auto`, `pareto`, `vast`, `level`)
  - KNN imputation (k=3)
- PCA plot using `cimcb_lite.plot.pca`
- Filter by class (Healthy, Diabetes, All)

### 3. **Univariate Statistics** (`3_🧪_Univariante.py`)
- 2-class tests (Healthy vs Diabetes, both directions)
- Filter significant metabolites (p ≤ 0.05, Sign=1)
- Display full and filtered statistics tables

### 4. **Data Dictionary** (`4_📚_Diccionario.py`)
- Compound class distribution (SUPER_PATHWAY)
- Interactive Plotly bar chart
- Summary statistics

---

## ⚙️ Configuration

Edit `config/config.yaml` to customize:
- Data paths and sheet names
- Preprocessing parameters (scale method, KNN k, log offset)
- PCA components (pcx, pcy)
- Statistical test parameters (parametric, p-value threshold)

**Example:**

```yaml
data:
  path: "study_data.xlsx"
  sheets:
    metadata: "sample_metadata"
    matrix: "data_matrix"
    dictionary: "data_dictionary"

preprocessing:
  scale_method: "auto"
  knn_k: 3
  log_offset: 0.5

pca:
  pcx: 1
  pcy: 2

stats:
  parametric: true
  pvalue_threshold: 0.05
```

---

## 🧪 Testing

Run tests with `pytest`:

```bash
pytest tests/
```

Tests cover:
- Data loading & sample alignment
- Preprocessing pipeline (no NaNs after imputation)
- PCA wrapper (non-crash test)
- Univariate statistics wrapper

---

## 📚 Dependencies

- **Streamlit** — multi-page web app framework
- **Pandas** — data manipulation
- **NumPy** — numerical computing
- **SciPy** — scientific computing
- **scikit-learn** — machine learning utilities
- **Matplotlib / Seaborn** — static plotting
- **Plotly** — interactive plotting
- **openpyxl** — Excel file reading
- **cimcb_lite** — metabolomics-specific utilities (PCA, stats)
- **PyYAML** — configuration file parsing
- **pytest** — testing framework

---

## 📖 References

- **CIMCB Metabolomics Tools:** [GitHub](https://github.com/orgs/CIMCB/repositories)
- **Streamlit Documentation:** [streamlit.io](https://streamlit.io/)
- **Metabolomics Best Practices:** [Metabolomics Society](https://metabolomicssociety.org/)

---

## 📝 License

MIT License — see `LICENSE` file for details.

---

## 👥 Authors

**Claudia Balderas** 

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

---

## 📧 Contact
claudia.balderas@iqog.csic.es
For questions or suggestions, please open an issue or contact the author.

---

**Enjoy exploring metabolomics data! 🧬📊**
