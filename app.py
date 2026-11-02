import altair as alt
import pandas as pd
import streamlit as st

from src.calculos import (
    aplicar_intervalos,
    conversao_por,
    histograma,
    kpis,
    limites,
    matriz_correlacao,
)
from src.data_loader import load_data
from src.preparacao import FAIXAS_ANTECEDENCIA

st.set_page_config(
    page_title="Agência de Viagens: Buscas e Reservas",
    page_icon="✈️",
    layout="wide",
)

df = load_data()

# ------------------------------------------------------------------------------------------------
# Identidade visual (mesmas cores do .streamlit/config.toml)
# ------------------------------------------------------------------------------------------------
COR_PRIMARIA = "#0e7490"   # azul-petróleo (mar)
COR_BUSCA = "#8ecae6"      # azul claro: "só busca" (pano de fundo)
COR_RESERVA = "#e8590c"    # laranja: "reserva" (o personagem da história)
CORES_RESULTADO = alt.Scale(domain=["Só busca", "Reserva"], range=[COR_BUSCA, COR_RESERVA])

# Variáveis quantitativas do estudo e o nome legível de cada uma
VARS_QUANT = {
    "orig_destination_distance": "Distância origem–destino",
    "antecedencia_dias": "Antecedência (dias)",
    "noites": "Noites de estadia",
    "srch_adults_cnt": "Adultos",
    "srch_children_cnt": "Crianças",
    "srch_rm_cnt": "Quartos",
    "cnt": "Eventos na sessão",
}
VARS_PADRAO = ["orig_destination_distance", "antecedencia_dias", "noites", "srch_adults_cnt"]


def rotulo(var):
    return VARS_QUANT.get(var, var)


def formatar_int(n):
    return f"{n:,.0f}".replace(",", ".")


def formatar_pct(x):
    return "—" if pd.isna(x) else f"{x:.1%}".replace(".", ",")


# ------------------------------------------------------------------------------------------------
# Sidebar: filtros (seletor de variáveis + intervalos) — valem para os dois dashboards
# ------------------------------------------------------------------------------------------------
LIMITES = {var: limites(df[var]) for var in VARS_QUANT}

with st.sidebar:
    st.header("Filtros")

    variaveis = st.multiselect(
        "Variáveis quantitativas",
        options=list(VARS_QUANT),
        default=VARS_PADRAO,
        format_func=rotulo,
        help="Variáveis analisadas no Dashboard 1. Cada uma ganha um slider de intervalo abaixo.",
    )

    st.subheader("Intervalos")
    st.caption("Exclua valores extremos e veja se a análise muda. Vale para os dois dashboards.")
    intervalos = {}
    for var in variaveis:
        minimo, maximo = LIMITES[var]
        inteiro = isinstance(minimo, int)
        intervalos[var] = st.slider(
            rotulo(var),
            min_value=minimo,
            max_value=maximo,
            value=(minimo, maximo),
            step=1 if inteiro else 1.0,
            format="%d" if inteiro else "%.0f",
            key=f"intervalo_{var}",
        )

df_filtrado = aplicar_intervalos(df, intervalos, LIMITES)

with st.sidebar:
    st.divider()
    st.caption(f"{formatar_int(len(df_filtrado))} de {formatar_int(len(df))} buscas dentro dos intervalos.")

st.title("✈️ Agência de Viagens: Buscas e Reservas")
st.caption("Buscas de hotel feitas por clientes de uma agência de viagens entre jan/2013 e dez/2014.")

aba_lab, aba_kpis = st.tabs(["🔬 Dashboard 1: Laboratório", "📊 Dashboard 2: Indicadores comerciais"])

# ================================================================================================
# DASHBOARD 1 — distribuição e correlação
# ================================================================================================
with aba_lab:
    c1, c2 = st.columns([1, 1])
    with c1:
        metodo = st.segmented_control(
            "Método de correlação",
            options=["spearman", "pearson"],
            default="spearman",
            format_func=str.capitalize,
            help="Spearman é mais robusto para variáveis assimétricas e com outliers (caso da distância e da antecedência).",
        ) or "spearman"
    with c2:
        separar = st.toggle(
            "Separar distribuição por resultado (reserva × só busca)",
            value=False,
        )

    col_corr, col_dist = st.columns([1, 1.5])

    with col_corr:
        st.subheader(f"Correlação ({metodo.capitalize()})")

        if len(variaveis) < 2:
            st.warning("Selecione pelo menos 2 variáveis para calcular a correlação.")
        elif len(df_filtrado) < 30:
            st.warning("Poucas buscas nos intervalos escolhidos para calcular a correlação.")
        else:
            corr = matriz_correlacao(df_filtrado, variaveis, metodo)
            corr["x"] = corr["var_x"].map(rotulo)
            corr["y"] = corr["var_y"].map(rotulo)
            rotulos = [rotulo(v) for v in variaveis]

            base = alt.Chart(corr).encode(
                x=alt.X("x:N", title=None, sort=rotulos[:-1], axis=alt.Axis(labelAngle=-30, labelLimit=140)),
                y=alt.Y("y:N", title=None, sort=rotulos[1:], axis=alt.Axis(labelLimit=160)),
            )
            heatmap = base.mark_rect().encode(
                color=alt.Color(
                    "correlacao:Q",
                    title=metodo.capitalize(),
                    scale=alt.Scale(scheme="blueorange", domain=[-1, 1]),
                ),
                tooltip=[
                    alt.Tooltip("x:N", title="Variável"),
                    alt.Tooltip("y:N", title="Variável"),
                    alt.Tooltip("correlacao:Q", title="Correlação", format=".2f"),
                ],
            )
            valores = base.mark_text(fontSize=14).encode(
                text=alt.Text("correlacao:Q", format=".2f"),
                color=alt.condition("abs(datum.correlacao) > 0.5", alt.value("white"), alt.value("black")),
            )
            st.altair_chart(
                (heatmap + valores).properties(height=400),
                width="stretch",
            )

            constantes = [rotulo(v) for v in variaveis if df_filtrado[v].nunique() <= 1]
            if constantes:
                st.info(
                    "Sem variação no intervalo escolhido (correlação indefinida): " + ", ".join(constantes)
                )

    with col_dist:
        st.subheader("Distribuição")

        if not variaveis:
            st.warning("Selecione pelo menos 1 variável para ver a distribuição.")
        elif df_filtrado.empty:
            st.warning("Nenhuma busca dentro dos intervalos escolhidos.")
        else:
            # Um histograma por variável selecionada, em grade de 2 colunas
            for inicio in range(0, len(variaveis), 2):
                colunas = st.columns(2)
                for coluna, var in zip(colunas, variaveis[inicio : inicio + 2]):
                    contagem = histograma(df_filtrado, var, por="resultado" if separar else None)
                    grafico = (
                        alt.Chart(contagem)
                        .mark_bar(color=COR_PRIMARIA)
                        .encode(
                            x=alt.X("inicio:Q", title=rotulo(var)),
                            x2="fim:Q",
                            y=alt.Y("sum(contagem):Q", title="Buscas", stack=True),
                            tooltip=[
                                alt.Tooltip("inicio:Q", title="De", format=",.0f"),
                                alt.Tooltip("fim:Q", title="Até", format=",.0f"),
                                alt.Tooltip("sum(contagem):Q", title="Buscas", format=",.0f"),
                            ],
                        )
                        .properties(height=210)
                    )
                    if separar:
                        grafico = grafico.encode(
                            color=alt.Color(
                                "resultado:N",
                                title=None,
                                scale=CORES_RESULTADO,
                                legend=alt.Legend(orient="top"),
                            ),
                            tooltip=[
                                "resultado:N",
                                alt.Tooltip("inicio:Q", title="De", format=",.0f"),
                                alt.Tooltip("fim:Q", title="Até", format=",.0f"),
                                alt.Tooltip("sum(contagem):Q", title="Buscas", format=",.0f"),
                            ],
                        )
                    with coluna:
                        st.altair_chart(grafico, width="stretch")

            ausentes = df_filtrado[variaveis].isna().sum()
            ausentes = ausentes[ausentes > 0]
            if not ausentes.empty:
                st.caption(
                    "Valores ausentes ignorados nos gráficos: "
                    + ", ".join(f"{rotulo(v)} ({formatar_int(n)})" for v, n in ausentes.items())
                )

# ================================================================================================
# DASHBOARD 2 — KPIs para a gerência comercial / marketing da agência
# ================================================================================================
with aba_kpis:
    st.caption(
        "Público-alvo: gerência comercial e marketing da agência. "
        "Os filtros da sidebar continuam valendo aqui."
    )

    meses = sorted(df_filtrado["mes"].unique())
    if not meses:
        st.warning("Nenhuma busca dentro dos intervalos da sidebar.")
        st.stop()

    w1, w2, w3 = st.columns([2, 1, 1])
    with w1:
        if len(meses) > 1:
            mes_ini, mes_fim = st.select_slider("Período", options=meses, value=(meses[0], meses[-1]))
        else:
            mes_ini = mes_fim = meses[0]
    with w2:
        dispositivo = st.segmented_control(
            "Dispositivo", options=["Todos", "Desktop", "Mobile"], default="Todos"
        ) or "Todos"
    with w3:
        tipo = st.segmented_control(
            "Tipo de compra", options=["Todos", "Pacote", "Avulso"], default="Todos"
        ) or "Todos"

    df_periodo = df_filtrado[df_filtrado["mes"].between(mes_ini, mes_fim)]
    df2 = df_periodo
    if dispositivo != "Todos":
        df2 = df2[df2["dispositivo"] == dispositivo]
    if tipo != "Todos":
        df2 = df2[df2["tipo_compra"] == tipo]

    if df2.empty:
        st.warning("Nenhuma busca com essa combinação de filtros.")
        st.stop()

    # --- Métricas ---------------------------------------------------------------------------------
    m = kpis(df2)
    base = kpis(df_filtrado)  # referência: todo o período, sem filtros de dispositivo/tipo

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Buscas", formatar_int(m["buscas"]), border=True)
    k2.metric(
        "Taxa de conversão",
        formatar_pct(m["taxa_conversao"]),
        delta=f"{(m['taxa_conversao'] - base['taxa_conversao']) * 100:+.1f}".replace(".", ",") + " p.p. vs. geral",
        help="Buscas que viraram reserva. O delta compara com o período completo, sem filtros de dispositivo/tipo.",
        border=True,
    )
    k3.metric(
        "Antecedência mediana",
        "—" if pd.isna(m["antecedencia_mediana"]) else f"{m['antecedencia_mediana']:.0f} dias",
        help="Entre a data da busca e o check-in, só para buscas que viraram reserva.",
        border=True,
    )
    k4.metric(
        "Estadia média",
        "—" if pd.isna(m["estadia_media"]) else f"{m['estadia_media']:.1f} noites".replace(".", ","),
        help="Noites por reserva.",
        border=True,
    )
    k5.metric(
        "Reservas em pacote",
        formatar_pct(m["pct_pacote"]),
        help="Parcela das reservas feitas como pacote (hotel + voo).",
        border=True,
    )

    # --- Visual 1: evolução mensal ------------------------------------------------------------------
    st.subheader("Volume de buscas e conversão por mês")
    mensal = conversao_por(df2, ["mes"])
    barras_mes = alt.Chart(mensal).mark_bar(color=COR_BUSCA).encode(
        x=alt.X("mes:O", title=None, axis=alt.Axis(labelAngle=-45)),
        y=alt.Y("buscas:Q", title="Buscas"),
        tooltip=[
            alt.Tooltip("mes:O", title="Mês"),
            alt.Tooltip("buscas:Q", title="Buscas", format=",.0f"),
            alt.Tooltip("reservas:Q", title="Reservas", format=",.0f"),
            alt.Tooltip("taxa_conversao:Q", title="Conversão", format=".1%"),
        ],
    )
    linha_mes = alt.Chart(mensal).mark_line(color=COR_RESERVA, point=True, strokeWidth=3).encode(
        x="mes:O",
        y=alt.Y("taxa_conversao:Q", title="Taxa de conversão", axis=alt.Axis(format="%")),
    )
    st.altair_chart(
        alt.layer(barras_mes, linha_mes).resolve_scale(y="independent").properties(height=300),
        width="stretch",
    )

    # --- Visuais 2 e 3: canal × antecedência (seleção cruzada) -------------------------------------
    st.subheader("Onde e quando a busca vira reserva")
    MIN_BUSCAS_CANAL = 100
    st.caption(
        "Clique num canal para ver a conversão por antecedência só daquele canal. Clique fora para limpar. "
        f"Canais com menos de {MIN_BUSCAS_CANAL} buscas ficam de fora (taxa pouco confiável)."
    )

    cruzado = conversao_por(df2, ["canal", "faixa_antecedencia"])
    clique = alt.selection_point(fields=["canal"])

    por_canal = (
        alt.Chart(cruzado)
        .transform_aggregate(buscas="sum(buscas)", reservas="sum(reservas)", groupby=["canal"])
        .transform_calculate(taxa="datum.reservas / datum.buscas")
        .transform_filter(f"datum.buscas >= {MIN_BUSCAS_CANAL}")
        .mark_bar(color=COR_PRIMARIA)
        .encode(
            x=alt.X("taxa:Q", title="Taxa de conversão", axis=alt.Axis(format="%")),
            y=alt.Y("canal:N", title=None, sort="-x"),
            opacity=alt.condition(clique, alt.value(1), alt.value(0.3)),
            tooltip=[
                "canal:N",
                alt.Tooltip("buscas:Q", title="Buscas", format=",.0f"),
                alt.Tooltip("taxa:Q", title="Conversão", format=".1%"),
            ],
        )
        .add_params(clique)
        .properties(title="Conversão por canal de venda", width=300, height=300)
    )

    por_antecedencia = (
        alt.Chart(cruzado)
        .transform_filter(clique)
        .transform_aggregate(buscas="sum(buscas)", reservas="sum(reservas)", groupby=["faixa_antecedencia"])
        .transform_calculate(taxa="datum.reservas / datum.buscas")
        .mark_bar(color=COR_RESERVA)
        .encode(
            x=alt.X(
                "faixa_antecedencia:N",
                title="Antecedência da busca",
                sort=FAIXAS_ANTECEDENCIA["labels"],
                axis=alt.Axis(labelAngle=0),
            ),
            y=alt.Y("taxa:Q", title="Taxa de conversão", axis=alt.Axis(format="%")),
            tooltip=[
                alt.Tooltip("faixa_antecedencia:N", title="Antecedência"),
                alt.Tooltip("buscas:Q", title="Buscas", format=",.0f"),
                alt.Tooltip("taxa:Q", title="Conversão", format=".1%"),
            ],
        )
        .properties(title="Conversão por antecedência", width=420, height=300)
    )

    st.altair_chart(por_canal | por_antecedencia, width="content")

    # --- Visual 4: dispositivo × tipo de compra ----------------------------------------------------
    st.subheader("Conversão por dispositivo e tipo de compra")
    st.caption("Usa só o período e a sidebar (ignora os botões de dispositivo e tipo), para dar a comparação completa.")
    disp_tipo = conversao_por(df_periodo, ["dispositivo", "tipo_compra"])
    st.altair_chart(
        alt.Chart(disp_tipo)
        .mark_bar()
        .encode(
            x=alt.X("dispositivo:N", title=None, axis=alt.Axis(labelAngle=0)),
            xOffset="tipo_compra:N",
            y=alt.Y("taxa_conversao:Q", title="Taxa de conversão", axis=alt.Axis(format="%")),
            color=alt.Color(
                "tipo_compra:N",
                title="Tipo de compra",
                scale=alt.Scale(domain=["Avulso", "Pacote"], range=[COR_PRIMARIA, COR_RESERVA]),
            ),
            tooltip=[
                "dispositivo:N",
                "tipo_compra:N",
                alt.Tooltip("buscas:Q", title="Buscas", format=",.0f"),
                alt.Tooltip("taxa_conversao:Q", title="Conversão", format=".1%"),
            ],
        )
        .properties(height=280),
        width="stretch",
    )
