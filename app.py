import pandas as pd
import streamlit as st

from src.data_loader import load_data

# Esqueleto da Aula 21, gerado a partir de entregas/rascunho-dashboard1.png
# (prompt em prompts/layout-skeleton-prompt.md). Os gráficos entram na Aula 22.

st.set_page_config(page_title="Agência de Viagens: Buscas e Reservas", layout="wide")

df = load_data()

VARS_QUANT = {
    "orig_destination_distance": "Distância origem–destino",
    "antecedencia_dias": "Antecedência (dias)",
    "noites": "Noites de estadia",
    "srch_adults_cnt": "Adultos",
    "srch_children_cnt": "Crianças",
    "srch_rm_cnt": "Quartos",
    "cnt": "Eventos na sessão",
}

# Sidebar: seletor de variáveis + um slider de intervalo por variável
with st.sidebar:
    st.header("Filtros")

    variaveis = st.multiselect(
        "Variáveis quantitativas",
        options=list(VARS_QUANT),
        default=["orig_destination_distance", "antecedencia_dias", "noites", "srch_adults_cnt"],
        format_func=lambda v: VARS_QUANT[v],
    )

    intervalos = {}
    for var in variaveis:
        minimo, maximo = int(df[var].min()), int(df[var].max())
        intervalos[var] = st.slider(
            VARS_QUANT[var], min_value=minimo, max_value=maximo, value=(minimo, maximo), key=f"intervalo_{var}"
        )

# Aplica os intervalos (só filtra a variável cujo slider saiu do valor completo)
df_filtrado = df
for var, (inicio, fim) in intervalos.items():
    if (inicio, fim) != (int(df[var].min()), int(df[var].max())):
        df_filtrado = df_filtrado[df_filtrado[var].between(inicio, fim)]

st.title("Agência de Viagens: Buscas e Reservas")
st.caption(f"{len(df_filtrado):,} de {len(df):,} buscas dentro dos intervalos.".replace(",", "."))

col_corr, col_dist = st.columns([1, 1.5])

with col_corr:
    st.subheader("Correlação")
    # TODO (Aula 22): heatmap de correlação das variáveis selecionadas
    if len(variaveis) < 2:
        st.warning("Selecione pelo menos 2 variáveis.")
    else:
        st.dataframe(df_filtrado[variaveis].corr(method="spearman").round(2))

with col_dist:
    st.subheader("Distribuição")
    # TODO (Aula 22): um histograma por variável selecionada
    if not variaveis:
        st.warning("Selecione pelo menos 1 variável.")
    else:
        st.dataframe(df_filtrado[variaveis].describe().T.round(1))

# TODO (Aula 22): Dashboard 2 — KPIs, em abas (st.tabs)
