import pandas as pd

def calcular_faturamento_total(df: pd.DataFrame) -> float:
    aprovadas = df[df["status"] == "aprovada"]
    return round(aprovadas["valor"].sum(), 2)


def calcular_faturamento_por_periodo(df: pd.DataFrame) -> pd.DataFrame:
    
    aprovadas = df[df["status"] == "aprovada"].copy()

    aprovadas["periodo"] = aprovadas["data"].dt.to_period("M").astype(str)

    resultado = (
        aprovadas
        .groupby("periodo")["valor"]
        .sum()
        .round(2)
        .reset_index()
        .rename(columns={"valor": "faturamento"})
        .sort_values("periodo")  # ordem cronológica
    )

    return resultado


def calcular_ticket_medio(df: pd.DataFrame) -> float:
    aprovadas = df[df["status"] == "aprovada"]

    if len(aprovadas) == 0:
        return 0.0

    return round(aprovadas["valor"].mean(), 2)


def calcular_taxa_aprovacao(df: pd.DataFrame) -> float:
    total = len(df)

    if total == 0:
        return 0.0

    aprovadas = len(df[df["status"] == "aprovada"])
    return round((aprovadas / total) * 100, 2)


def calcular_top_produtos(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    aprovadas = df[df["status"] == "aprovada"]

    resultado = (
        aprovadas
        .groupby("produto")
        .agg(
            faturamento=("valor", "sum"),
            quantidade_vendida=("quantidade", "sum") 
        )
        .round({"faturamento": 2})
        .sort_values("faturamento", ascending=False)
        .head(n)
        .reset_index()
    )

    return resultado


def calcular_breakdown_pagamento(df: pd.DataFrame) -> pd.DataFrame:
    aprovadas = df[df["status"] == "aprovada"]
    total = aprovadas["valor"].sum()

    resultado = (
        aprovadas
        .groupby("tipo_pagamento")["valor"]
        .sum()
        .round(2)
        .reset_index()
        .rename(columns={"valor": "faturamento"})
        .sort_values("faturamento", ascending=False)
    )

    if total > 0:
        resultado["percentual"] = ((resultado["faturamento"] / total) * 100).round(2)
    else:
        resultado["percentual"] = 0.0

    return resultado


def calcular_todas(df: pd.DataFrame) -> dict:
    total = len(df)
    aprovadas = len(df[df["status"] == "aprovada"])

    metricas = {
        "faturamento_total":       calcular_faturamento_total(df),
        "ticket_medio":            calcular_ticket_medio(df),
        "taxa_aprovacao":          calcular_taxa_aprovacao(df),
        "total_transacoes":        total,
        "total_aprovadas":         aprovadas,
        "total_recusadas":         total - aprovadas,
        "faturamento_por_periodo": calcular_faturamento_por_periodo(df),
        "top_produtos":            calcular_top_produtos(df),
        "breakdown_pagamento":     calcular_breakdown_pagamento(df),
    }
 
    print(f"[metrics] KPIs calculados:")
    print(f"  Faturamento total : R$ {metricas['faturamento_total']:,.2f}")
    print(f"  Ticket médio      : R$ {metricas['ticket_medio']:,.2f}")
    print(f"  Taxa de aprovação : {metricas['taxa_aprovacao']}%")
    print(f"  Total transações  : {total} ({aprovadas} aprovadas)")

    return metricas