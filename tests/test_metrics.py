import pytest
import pandas as pd

from src.metrics import (
    calcular_faturamento_total,
    calcular_faturamento_por_periodo,
    calcular_ticket_medio,
    calcular_taxa_aprovacao,
    calcular_top_produtos,
    calcular_breakdown_pagamento,
    calcular_todas,
)

@pytest.fixture
def df_base() -> pd.DataFrame:
    return pd.DataFrame({
        "id_transacao":   ["T01", "T02", "T03", "T04", "T05"],
        "data": pd.to_datetime([
            "2025-11-10",  # aprovada
            "2025-11-20",  # aprovada
            "2025-12-05",  # aprovada
            "2025-12-15",  # aprovada
            "2026-01-10",  # recusada — não entra no faturamento
        ]),
        "numero_cartao":  ["4532015112830366"] * 5,
        "valor":          [100.0, 200.0, 150.0, 50.0, 300.0],
        "tipo_pagamento": ["credito", "credito", "debito", "digital", "credito"],
        "produto":        ["Produto A", "Produto A", "Produto B", "Produto C", "Produto A"],
        "quantidade":     [1, 2, 1, 1, 3],
        "status":         ["aprovada", "aprovada", "aprovada", "aprovada", "recusada"],
    })


@pytest.fixture
def df_vazio() -> pd.DataFrame:
    return pd.DataFrame(columns=[
        "id_transacao", "data", "numero_cartao", "valor",
        "tipo_pagamento", "produto", "quantidade", "status"
    ])


@pytest.fixture
def df_todas_recusadas() -> pd.DataFrame:
    return pd.DataFrame({
        "id_transacao":   ["T01", "T02"],
        "data":           pd.to_datetime(["2026-01-10", "2026-01-11"]),
        "numero_cartao":  ["4532015112830366", "5425233430109903"],
        "valor":          [100.0, 200.0],
        "tipo_pagamento": ["credito", "debito"],
        "produto":        ["Produto A", "Produto B"],
        "quantidade":     [1, 1],
        "status":         ["recusada", "recusada"],
    })


class TestFaturamentoTotal:

    def test_soma_apenas_aprovadas(self, df_base):
        resultado = calcular_faturamento_total(df_base)
        assert resultado == 500.0

    def test_df_vazio_retorna_zero(self, df_vazio):
        resultado = calcular_faturamento_total(df_vazio)
        assert resultado == 0.0

    def test_todas_recusadas_retorna_zero(self, df_todas_recusadas):
        resultado = calcular_faturamento_total(df_todas_recusadas)
        assert resultado == 0.0

    def test_retorna_float(self, df_base):
        resultado = calcular_faturamento_total(df_base)
        assert isinstance(resultado, float)


class TestTicketMedio:

    def test_calculo_correto(self, df_base):
        resultado = calcular_ticket_medio(df_base)
        assert resultado == 125.0

    def test_df_vazio_retorna_zero(self, df_vazio):
        resultado = calcular_ticket_medio(df_vazio)
        assert resultado == 0.0

    def test_todas_recusadas_retorna_zero(self, df_todas_recusadas):
        resultado = calcular_ticket_medio(df_todas_recusadas)
        assert resultado == 0.0

    def test_transacao_unica(self):
        df = pd.DataFrame({
            "valor": [250.0], "status": ["aprovada"],
            "data": pd.to_datetime(["2026-01-10"]),
            "tipo_pagamento": ["credito"], "produto": ["X"],
            "quantidade": [1], "id_transacao": ["T01"],
            "numero_cartao": ["4532015112830366"],
        })
        assert calcular_ticket_medio(df) == 250.0

class TestTaxaAprovacao:

    def test_calculo_correto(self, df_base):
        resultado = calcular_taxa_aprovacao(df_base)
        assert resultado == 80.0

    def test_todas_aprovadas(self):
        df = pd.DataFrame({
            "status": ["aprovada", "aprovada", "aprovada"],
            "valor": [100.0, 200.0, 300.0],
        })
        assert calcular_taxa_aprovacao(df) == 100.0

    def test_nenhuma_aprovada(self, df_todas_recusadas):
        assert calcular_taxa_aprovacao(df_todas_recusadas) == 0.0

    def test_df_vazio_retorna_zero(self, df_vazio):
        assert calcular_taxa_aprovacao(df_vazio) == 0.0

    def test_retorna_float(self, df_base):
        resultado = calcular_taxa_aprovacao(df_base)
        assert isinstance(resultado, float)

class TestFaturamentoPorPeriodo:

    def test_retorna_dataframe(self, df_base):
        resultado = calcular_faturamento_por_periodo(df_base)
        assert isinstance(resultado, pd.DataFrame)

    def test_tem_colunas_corretas(self, df_base):
        resultado = calcular_faturamento_por_periodo(df_base)
        assert "periodo" in resultado.columns
        assert "faturamento" in resultado.columns

    def test_faturamento_novembro(self, df_base):
        resultado = calcular_faturamento_por_periodo(df_base)
        nov = resultado[resultado["periodo"] == "2025-11"]
        assert not nov.empty
        assert nov["faturamento"].values[0] == 300.0

    def test_faturamento_dezembro(self, df_base):
        resultado = calcular_faturamento_por_periodo(df_base)
        dez = resultado[resultado["periodo"] == "2025-12"]
        assert not dez.empty
        assert dez["faturamento"].values[0] == 200.0

    def test_recusadas_nao_aparecem(self, df_base):
        resultado = calcular_faturamento_por_periodo(df_base)
        jan = resultado[resultado["periodo"] == "2026-01"]
        assert jan.empty

    def test_ordem_cronologica(self, df_base):
        resultado = calcular_faturamento_por_periodo(df_base)
        periodos = resultado["periodo"].tolist()
        assert periodos == sorted(periodos)

class TestTopProdutos:

    def test_retorna_dataframe(self, df_base):
        resultado = calcular_top_produtos(df_base)
        assert isinstance(resultado, pd.DataFrame)

    def test_produto_a_e_o_primeiro(self, df_base):
        resultado = calcular_top_produtos(df_base)
        assert resultado.iloc[0]["produto"] == "Produto A"
        assert resultado.iloc[0]["faturamento"] == 300.0

    def test_respeita_limite_n(self, df_base):
        resultado = calcular_top_produtos(df_base, n=2)
        assert len(resultado) == 2

    def test_recusadas_nao_entram(self, df_base):
        resultado = calcular_top_produtos(df_base)
        produto_a = resultado[resultado["produto"] == "Produto A"]
        assert produto_a["faturamento"].values[0] == 300.0


class TestBreakdownPagamento:

    def test_retorna_dataframe(self, df_base):
        resultado = calcular_breakdown_pagamento(df_base)
        assert isinstance(resultado, pd.DataFrame)

    def test_tem_colunas_corretas(self, df_base):
        resultado = calcular_breakdown_pagamento(df_base)
        assert "tipo_pagamento" in resultado.columns
        assert "faturamento" in resultado.columns
        assert "percentual" in resultado.columns

    def test_faturamento_credito(self, df_base):
        resultado = calcular_breakdown_pagamento(df_base)
        credito = resultado[resultado["tipo_pagamento"] == "credito"]
        assert credito["faturamento"].values[0] == 300.0

    def test_soma_percentuais_igual_100(self, df_base):
        resultado = calcular_breakdown_pagamento(df_base)
        soma = resultado["percentual"].sum()
        assert abs(soma - 100.0) < 0.1

class TestCalcularTodas:

    def test_retorna_dicionario(self, df_base):
        resultado = calcular_todas(df_base)
        assert isinstance(resultado, dict)

    def test_tem_todas_as_chaves(self, df_base):
        resultado = calcular_todas(df_base)
        chaves_esperadas = {
            "faturamento_total",
            "ticket_medio",
            "taxa_aprovacao",
            "total_transacoes",
            "total_aprovadas",
            "total_recusadas",
            "faturamento_por_periodo",
            "top_produtos",
            "breakdown_pagamento",
        }
        assert chaves_esperadas == set(resultado.keys())

    def test_contagens_corretas(self, df_base):
        resultado = calcular_todas(df_base)
        assert resultado["total_transacoes"] == 5
        assert resultado["total_aprovadas"] == 4
        assert resultado["total_recusadas"] == 1

    def test_integracao_com_pipeline_completo(self):
        from src.loader import load_file
        from src.validator import processar

        df_bruto = load_file("data/exemplo_transacoes.csv")
        df_validos, _ = processar(df_bruto)
        metricas = calcular_todas(df_validos)
     
        assert metricas["faturamento_total"] > 0

        assert metricas["ticket_medio"] > 0

        assert 0 <= metricas["taxa_aprovacao"] <= 100

        assert (
            metricas["total_aprovadas"] + metricas["total_recusadas"]
            == metricas["total_transacoes"]
        )