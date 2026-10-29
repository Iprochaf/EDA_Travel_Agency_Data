"""Tratamento do Travel Agency Data (Kaggle: nhatnguyentran/travel-agency-data).

Usado pelo notebook `notebooks/preparacao-dados.ipynb` para gerar `data/clean/dataset.csv`.
Fica num módulo (e não só no notebook) para que o mesmo tratamento possa ser reaproveitado e testado.
"""

import numpy as np
import pandas as pd

COLUNAS_DATA = ["date_time", "srch_ci", "srch_co"]

# Colunas removidas por privacidade: identificam o usuário ou a sua localização fina.
# Mesmo anonimizadas, não são usadas pelo app, então não vão para o repositório.
COLUNAS_SENSIVEIS = ["user_id", "user_location_region", "user_location_city"]

FAIXAS_ANTECEDENCIA = {
    "bins": [-1, 0, 7, 30, 90, 180, np.inf],
    "labels": ["Mesmo dia", "1–7 dias", "8–30 dias", "31–90 dias", "91–180 dias", "180+ dias"],
}


def preparar(raw: pd.DataFrame) -> pd.DataFrame:
    """Recebe o CSV bruto e devolve o dataframe tratado, pronto para o app."""
    df = raw.drop(columns=[c for c in raw.columns if c.startswith("Unnamed")])

    # Duplicadas são checadas antes de remover o user_id (senão buscas de usuários diferentes colapsariam)
    df = df.drop_duplicates()
    df = df.drop(columns=COLUNAS_SENSIVEIS, errors="ignore")

    for coluna in COLUNAS_DATA:
        df[coluna] = pd.to_datetime(df[coluna], errors="coerce")
    df = df.dropna(subset=COLUNAS_DATA)

    # Variáveis derivadas das datas
    df["antecedencia_dias"] = (df["srch_ci"] - df["date_time"].dt.normalize()).dt.days
    df["noites"] = (df["srch_co"] - df["srch_ci"]).dt.days
    df["total_hospedes"] = df["srch_adults_cnt"] + df["srch_children_cnt"]

    # Remove buscas impossíveis: check-in antes da busca, check-out antes do check-in, sem hóspede ou sem quarto
    validas = (
        (df["antecedencia_dias"] >= 0)
        & (df["noites"] >= 1)
        & (df["total_hospedes"] > 0)
        & (df["srch_rm_cnt"] >= 1)
    )
    df = df[validas].copy()

    # Rótulos legíveis para os gráficos
    df["resultado"] = np.where(df["is_booking"] == 1, "Reserva", "Só busca")
    df["dispositivo"] = np.where(df["is_mobile"] == 1, "Mobile", "Desktop")
    df["tipo_compra"] = np.where(df["is_package"] == 1, "Pacote", "Avulso")
    df["canal"] = "Canal " + df["channel"].astype(int).astype(str)
    df["mes"] = df["date_time"].dt.to_period("M").astype(str)
    df["faixa_antecedencia"] = pd.cut(df["antecedencia_dias"], **FAIXAS_ANTECEDENCIA).astype(str)

    return df.reset_index(drop=True)
