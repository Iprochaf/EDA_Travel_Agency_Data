from pathlib import Path

import pandas as pd
import streamlit as st

# Caminho relativo à raiz do projeto (funciona local e no Streamlit Community Cloud)
CAMINHO_PADRAO = Path(__file__).resolve().parent.parent / "data" / "clean" / "dataset.csv"


@st.cache_data
def load_data(path=CAMINHO_PADRAO):
    """Lê o dataset já tratado (exportado pelo notebook notebooks/preparacao-dados.ipynb)."""
    return pd.read_csv(path, parse_dates=["date_time", "srch_ci", "srch_co"])
