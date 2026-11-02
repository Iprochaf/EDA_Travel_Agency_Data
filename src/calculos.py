"""Cálculos em pandas usados pelo app (separados do Streamlit para facilitar teste no notebook)."""

import numpy as np
import pandas as pd


def limites(serie: pd.Series):
    """Mínimo e máximo de uma variável, no formato que o slider espera (int ou float arredondado)."""
    serie = serie.dropna()
    if pd.api.types.is_integer_dtype(serie):
        return int(serie.min()), int(serie.max())
    return float(np.floor(serie.min())), float(np.ceil(serie.max()))


def aplicar_intervalos(df: pd.DataFrame, intervalos: dict, limites_originais: dict) -> pd.DataFrame:
    """Mantém só as linhas dentro dos intervalos escolhidos.

    Um intervalo que continua no valor completo não filtra nada; assim linhas com valor ausente
    (ex.: distância desconhecida) só saem quando o usuário realmente mexe no slider daquela variável.
    """
    mascara = pd.Series(True, index=df.index)
    for var, (inicio, fim) in intervalos.items():
        if (inicio, fim) != limites_originais[var]:
            mascara &= df[var].between(inicio, fim)
    return df[mascara]


def matriz_correlacao(df: pd.DataFrame, variaveis: list, metodo: str) -> pd.DataFrame:
    """Triângulo inferior (sem diagonal) da matriz de correlação, em formato longo."""
    corr = (
        df[variaveis]
        .corr(method=metodo)
        .rename_axis(index="var_y", columns=None)
        .reset_index()
        .melt(id_vars="var_y", var_name="var_x", value_name="correlacao")
    )
    ordem = {var: i for i, var in enumerate(variaveis)}
    return corr[corr["var_y"].map(ordem) > corr["var_x"].map(ordem)].reset_index(drop=True)


def histograma(df: pd.DataFrame, var: str, por: str | None = None, max_bins: int = 30) -> pd.DataFrame:
    """Contagens por faixa (bin), calculadas no pandas.

    O Altair poderia fazer o bin sozinho, mas teria de receber as ~100 mil linhas em cada gráfico;
    mandando só as contagens o app fica bem mais leve.
    Variáveis inteiras com poucos valores (adultos, quartos...) ganham uma barra por valor.
    """
    dados = df[[var] + ([por] if por else [])].dropna(subset=[var])
    if dados.empty:
        return pd.DataFrame(columns=["inicio", "fim", "contagem"] + ([por] if por else []))

    minimo, maximo = dados[var].min(), dados[var].max()
    discreta = pd.api.types.is_integer_dtype(dados[var]) and (maximo - minimo) <= max_bins
    if discreta:
        bordas = np.arange(minimo - 0.5, maximo + 1.5, 1.0)
    elif minimo == maximo:
        bordas = np.array([minimo - 0.5, maximo + 0.5])
    else:
        bordas = np.histogram_bin_edges(dados[var], bins=max_bins)

    dados = dados.assign(_bin=pd.cut(dados[var], bordas, include_lowest=True, labels=False))
    grupos = ["_bin"] + ([por] if por else [])
    contagem = dados.groupby(grupos, observed=True).size().rename("contagem").reset_index()
    contagem["inicio"] = bordas[contagem["_bin"].astype(int)]
    contagem["fim"] = bordas[contagem["_bin"].astype(int) + 1]
    return contagem.drop(columns="_bin")


def taxa(reservas, buscas):
    return reservas / buscas if buscas else np.nan


def conversao_por(df: pd.DataFrame, grupos: list) -> pd.DataFrame:
    """Buscas, reservas e taxa de conversão por grupo."""
    agg = (
        df.groupby(grupos, observed=True)
        .agg(buscas=("is_booking", "size"), reservas=("is_booking", "sum"))
        .reset_index()
    )
    agg["taxa_conversao"] = agg["reservas"] / agg["buscas"]
    return agg


def kpis(df: pd.DataFrame) -> dict:
    """Métricas do Dashboard 2 (ver entregas/justificativa-metricas.md)."""
    reservas = df[df["is_booking"] == 1]
    return {
        "buscas": len(df),
        "taxa_conversao": df["is_booking"].mean() if len(df) else np.nan,
        "antecedencia_mediana": reservas["antecedencia_dias"].median() if len(reservas) else np.nan,
        "estadia_media": reservas["noites"].mean() if len(reservas) else np.nan,
        "pct_pacote": reservas["is_package"].mean() if len(reservas) else np.nan,
    }
